from unittest import TestCase, main

from sam_slash_slack import SAMSlashSlack
from sam_slash_slack.exceptions import NoSigningSecretException


class TestSlashSlack(TestCase):
    def test_dev_mode(self):
        def t():
            slash = SAMSlashSlack(dev=True)

        def b():
            slash = SAMSlashSlack()

        def c():
            slash = SAMSlashSlack(signing_secret="test")

        t()
        self.assertTrue(True)
        self.assertRaises(NoSigningSecretException, b)
        c()
        self.assertTrue(True)

    def test_decorator_registration(self):
        slash = SAMSlashSlack(dev=True)

        @slash.command("test")
        def a_fn(s: str):
            pass

        self.assertEqual(1, len(slash.commands))
        self.assertTrue("test" in slash.commands)
        self.assertEqual(a_fn, slash.commands["test"].func)
        self.assertEqual(0, len(slash.commands["test"].flags))
        self.assertEqual(1, len(slash.commands["test"].args_type))
        self.assertIsNone(slash.commands["test"].request_arg)


if __name__ == "__main__":
    main()
