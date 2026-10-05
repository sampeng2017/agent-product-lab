import io
import unittest
from contextlib import redirect_stdout

from release_demo.cli import main


class CliTests(unittest.TestCase):
    def test_greeting(self):
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(main([]), 0)
        self.assertEqual(output.getvalue(), "hello from the installed wheel\n")

    def test_version(self):
        output = io.StringIO()
        with redirect_stdout(output), self.assertRaises(SystemExit) as stopped:
            main(["--version"])
        self.assertEqual(stopped.exception.code, 0)
        self.assertEqual(output.getvalue(), "release-demo 1.0.0\n")
