from pathlib import Path

import sam_slash_slack

TEMPLATE = """
AWSTemplateFormatVersion: '2010-09-09'
Transform: 'AWS::Serverless-2016-10-31'

Description: SAM app bootstrapped with the aws-slash-slack framework.

Resources:
  Receptionist:
    Type: 'AWS::Serverless::Function'
    Properties:
      Handler: src/app.api_handler
      Runtime: python3.9
      CodeUri: .
      Description: Receives requests from slack, enqueues async processing, and acknowledges.
      MemorySize: 128
      Timeout: 30
      Environment:
        Variables:
          QUEUE_URL:
            Ref: AWSSlashSlackAsyncQueue
          SLACK_SIGNING_SECRET: ''
      Events:
        HttpPost:
          Type: Api
          Properties:
            Path: '/aws-slash-slack'
            Method: post

  AsyncHandler:
    Type: 'AWS::Serverless::Function'
    Properties:
      Handler: src/app.async_handler
      Runtime: python3.9
      CodeUri: .
      Description: Processes async requests.
      MemorySize: 128
      Timeout: 30
      Events:
        MySQSEvent:
          Type: SQS
          Properties:
            Queue: !GetAtt AWSSlashSlackAsyncQueue.Arn
            BatchSize: 1

  AWSSlashSlackAsyncQueue:
    Type: 'AWS::SQS::Queue'

"""

APP_TEMPLATE = """
import os
from sam_slash_slack import AWSSlashSlack, String

slash = AWSSlashSlack(signing_secret=os.environ.get('SLACK_SIGNING_SECRET'))
api_handler = slash.get_api_handler()
async_handler = slash.get_async_handler()

"""

REQUIREMENTS_TEMPLATE = f"""
aws-slash-slack=={sam_slash_slack.__version__}
""".strip()


def make_template():
    Path().joinpath("template.yaml").write_text(TEMPLATE)
    Path().joinpath("requirements.txt").write_text(REQUIREMENTS_TEMPLATE)
    src = Path().joinpath("src")
    src.mkdir(exist_ok=True)
    src.joinpath("app.py").write_text(APP_TEMPLATE)


def cli():
    make_template()


if __name__ == "__main__":
    cli()
