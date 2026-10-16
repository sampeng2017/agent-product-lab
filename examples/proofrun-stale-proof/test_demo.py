from __future__ import annotations

import importlib.util
import io
import subprocess
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch


spec = importlib.util.spec_from_file_location("proofrun_replay", Path(__file__).with_name("demo.py"))
assert spec is not None and spec.loader is not None
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)


class ReplayLauncherTests(unittest.TestCase):
    def test_default_uses_calling_python_without_path_lookup(self) -> None:
        with patch.object(demo.sys, "executable", "/caller/python"), patch.object(demo.shutil, "which") as which:
            self.assertEqual(demo._proofrun_launcher(False), ["/caller/python", "-B", "-m", "proofrun"])
        which.assert_not_called()

    def test_explicit_mode_resolves_one_command_even_with_spaces(self) -> None:
        with patch.object(demo.shutil, "which", return_value="tool apps/proofrun") as which:
            self.assertEqual(demo._proofrun_launcher(True), [str(Path("tool apps/proofrun").resolve())])
        which.assert_called_once_with("proofrun")

    def test_missing_command_is_setup_exit_before_creating_fixture(self) -> None:
        output = io.StringIO()
        with (
            patch.object(demo.shutil, "which", side_effect=lambda name: "/usr/bin/git" if name == "git" else None),
            patch.object(demo.tempfile, "TemporaryDirectory") as temporary,
            redirect_stderr(output),
        ):
            self.assertEqual(demo.main(["--installed-command"]), 2)
        temporary.assert_not_called()
        self.assertIn("ProofRun command not found on PATH", output.getvalue())

    def test_unusable_selected_command_has_mode_specific_setup_hint(self) -> None:
        output = io.StringIO()
        selected = str(Path("tool apps/proofrun").resolve())

        def find_command(name):
            if name == "git":
                return "/usr/bin/git"
            self.assertEqual(demo.os.environ["PATH"], "original search path")
            return "tool apps/proofrun"

        with (
            patch.dict(demo.os.environ, {"PATH": "original search path"}),
            patch.object(demo.shutil, "which", side_effect=find_command),
            patch.object(demo.subprocess, "run", return_value=subprocess.CompletedProcess([], 1)) as run,
            redirect_stdout(io.StringIO()),
            redirect_stderr(output),
        ):
            self.assertEqual(demo.main(["--installed-command"]), 2)
        self.assertEqual(run.call_args.args[0], [selected, "--help"])
        self.assertTrue(run.call_args.kwargs["env"]["PATH"].startswith(str(Path(demo.sys.executable).parent)))
        self.assertIn("selected ProofRun command could not run", output.getvalue())

    def test_preflight_launch_errors_are_setup_failures(self) -> None:
        for error in (FileNotFoundError("missing interpreter"), subprocess.TimeoutExpired("proofrun", 60)):
            with self.subTest(error=type(error).__name__):
                output = io.StringIO()
                with (
                    patch.object(demo.shutil, "which", return_value="/apps/proofrun"),
                    patch.object(demo.subprocess, "run", side_effect=error),
                    redirect_stdout(io.StringIO()),
                    redirect_stderr(output),
                ):
                    self.assertEqual(demo.main(["--installed-command"]), 2)
                self.assertIn("selected ProofRun command could not run", output.getvalue())


if __name__ == "__main__":
    unittest.main()
