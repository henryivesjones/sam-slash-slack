# sam-slash-slack

![Tests + Linting](https://github.com/henryivesjones/sam-slash-slack/actions/workflows/checks.yml/badge.svg?branch=main&event=push)
![pypi](https://img.shields.io/pypi/v/sam-slash-slack)
![License](https://img.shields.io/pypi/l/sam-slash-slack)
![Downloads](https://img.shields.io/pypi/dm/sam-slash-slack)

A python framework for building slack slash bots using AWS SAM. Get input parsing and validation, command routing, async responses, auto-generated help dialog, response visibility, and response message formatting all for free.

`sam-slash-slack` utilizes the AWS Serverless Application Model (SAM) to generate serverless resources to run your `sam-slash-slack` bot. The `sam-slash-slack` bot consists of two lambda functions and one SQS queue. The `api_handler` lambda function receives the POST request from slack enqueues the request in the SQS queue for async processing, and immediately responds. Slack requires a response within 3 seconds. This architecture enables your slash commands to take longer than that to respond. The `async_handler` receives messages from the `api_handler` and executes the given command.

Most of the code for `sam-slash-slack` is shared from [`slash-slack`](https://github.com/henryivesjones/slash-slack).

View [Slack slash command documentation](https://api.slack.com/interactivity/slash-commands) here.

```python
# EX: /slash-slack math 10 * 10
# Response: 100.0
import os

from sam_slash_slack import Flag, Float, SAMSlashSlack, String

slash = SAMSlashSlack(signing_secret=os.environ['SLACK_SIGNING_SECRET'])
api_handler = slash.get_api_handler()
async_handler = slash.get_async_handler()


@slash.command("math")
def math_fn(
    x: float = Float(),
    symbol: str = Enum(values={"*", "+", "-", "/"}),
    y: float = Float(),
):
    if symbol == "*":
        return x * y
    if symbol == "+":
        return x + y
    if symbol == "-":
        return x - y
    if symbol == "/":
        return x / y
```

# Why use `sam-slash-slack`?

Building a slack slash bot can seem very straightforward at first, however there are some complexities that make it difficult. `sam-slash-slack` handles all of the complexities for you letting you focus on the bot response handlers.

You don't have to worry about deployment, as you can let SAM and lambda functions do the heavy lifting.

## Webhook signature verification

`slash-slack` will verify that incoming requests were made by slack by validating the request signature. To disable signature verification use the `dev=True` option when creating the `SAMSlashSlack` object.

## Command Response Timeout/Async responses

Slack requires that the slash bot webhook be responded to within 3 seconds.

Often times the action being taken by the bot will depend on external services which might not respond within 3 seconds.

`sam-slash-slack` sends an immediate `200` response to the webhook request, and runs the command function asynchronously. When the command function finishes, the response is sent back to slack using the `response_url` from the request.

You can optionally add content to the immediate response to let your user know that something is being
done in the background. A global/default response can be set with the `acknowledge_response` parameter on
the `SAMSlashSlack` class, or at the command level with the `acknowledge_response` parameter on the `command` decorator.
The value passed to `acknowledge_response` will be passed to `blocks._make_block_message` and can be a `str`, `block`, `list[str]`, or `list[block]`
where a `block` is a [block kit block](https://api.slack.com/block-kit/building#getting_started).
See the [example](https://github.com/henryivesjones/slash-slack/blob/main/example.py) for example usage.

## Input Arg/Flag parsing

`sam-slash-slack` takes care of parsing command input into pre-defined args and flags which let you focus on writing the command function, and not wrangling the content into the format that you need.

## Auto-generated help

`sam-slash-slack` provides help dialog auto-generated from your commands, args, and flags. Additional details can be embedded directly into the command decorator and arg/flag initializers.

To request global help:

```
/slash-slack help
```

To request command specific help:

```
/slash-slack command --help
```

## Response visibility

Slack slash command responses can be made visible only to the requestor, or to the entire channel. `sam-slash-slack` adds the ability for any command to be made visible with the `--visible` flag.

## Response formatting

Slack expects responses to be in the Slack Block Kit format. `sam-slash-slack` will automatically convert your string responses into slack `mrkdown` blocks.

# Deployment

`sam-slash-slack` utilizes SAM to generate and deploy the underlying AWS infrastructure. To initialize a new `sam-slash-slack` app. Run `init-sam-slash-slack` in the project directory. This will bootstrap the SAM template, and `app.py` file.
You must expose the underlying `api_handler`, and `async_handler` methods from the `SAMSlashSlack` bot.

```bash
sam build
sam deploy

```

# Command Inputs

The inputs and parsing for each command is determined by the parameters to the function. `SAMSlashSlack` parses the function parameters and generates an input schema.

When a request is made to a given command, `SAMSlashSlack` attempts to parse the input text into the command input schema.

## Flags

Flags are boolean options that can be added to commands anywhere within the request. During the input parsing, flags are parsed and removed, and then args are parsed.

There is no difference in doing `/slash-slack command arg --flag` and `/slash-slack command --flag arg`.

### Global Flags

There are 2 global flags: `--visible` and `--help`.

The `--visible` flag will make the response visible in the channel that the request was made. By default, responses are only visible to the user which made the request.

The `--help` flag will indicate that the `SlashSlack` app should return the relevant help message. Whether that is app level `/slash-slack --help`, or command level `/slash-slack command --help`.

## Args

All non-flag arguments to the command function make up the input schema for the command function. This means that the # of words in the command request must match up with the # of non-flag arguments. (With two exceptions: String, UnknownLengthList).

### String

When the only non-flag parameter for the function is a `String()` then the entire argument body (with flags removed) will be passed into that parameter.

```python
# EX: /slash-slack echo hello --upper world
# Response: HELLO WORLD
@slash.command("echo")
def echo(s: str, upper: bool = Flag()):
    return s
```

### Unknown Length List

To collect an arbitrary # of args from the user use the `UnknownLengthList` arg type. This arg type will be passed a list of all of the values passed to it parsed into the given type.

Because this consumes args till the end of the arg list, this must be the last non-flag param for the command function.

```python
# EX: /slash-slack avg 10, 20, 30
# Response: 20.0
@slash.command("avg")
def avg(numbers = UnknownLengthList(arg_type=Float())):
    return sum(numbers) / len(numbers)
```

### SlashSlackRequest

If you want to have access to the complete request as sent from the slack servers. Add a param with the type annotation of `SlashSlackRequest` to the command function.

```python
# EX: /slash-slack echo hello world
# Response: hello world This request was made by John Doe
@slash.command("echo")
def echo(content: str, slash_slack_request: SlashSlackRequest):
    return f"{content} This request was made by {slash_slack_request.user_name}"

```
