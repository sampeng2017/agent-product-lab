from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from agentscope.cli import main
from agentscope.core import compare_targets, inspect_targets


class AgentScopeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def write(self, relative: str, content: str = "instructions\n") -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def test_agents_md_profile_applies_nearest_and_explains_shadowing(self) -> None:
        self.write("AGENTS.md")
        self.write("packages/api/AGENTS.md")
        self.write("packages/api/src/app.py", "")

        result = inspect_targets(
            self.root, ["packages/api/src/app.py"], profile="agents-md"
        )[0]

        self.assertEqual(result.applied_count, 1)
        self.assertEqual(
            [(source.path, source.state) for source in result.sources],
            [("AGENTS.md", "shadowed"), ("packages/api/AGENTS.md", "applied")],
        )
        self.assertIn("packages/api/AGENTS.md", result.sources[0].reason)

    def test_agents_md_profile_accepts_planned_nonexistent_target(self) -> None:
        self.write("AGENTS.md")

        result = inspect_targets(self.root, ["src/new.py"])[0]

        self.assertEqual(result.target, "src/new.py")
        self.assertEqual(result.applied_count, 1)

    def test_copilot_cli_combines_supported_ancestor_formats(self) -> None:
        self.write(".github/copilot-instructions.md")
        self.write("AGENTS.md")
        self.write("packages/CLAUDE.md")
        self.write("packages/api/GEMINI.md")
        self.write("packages/api/app.py", "")

        result = inspect_targets(
            self.root, ["packages/api/app.py"], profile="copilot-cli"
        )[0]

        self.assertEqual(result.applied_count, 4)
        self.assertEqual(
            [source.kind for source in result.sources],
            ["copilot-repository", "agents-md", "claude-md", "gemini-md"],
        )
        self.assertTrue(all(source.state == "applied" for source in result.sources))

    def test_copilot_path_instructions_report_matches_and_misses(self) -> None:
        self.write(
            ".github/instructions/python.instructions.md",
            '---\napplyTo: "src/**/*.py, tests/*.py"\n---\nUse Python.\n',
        )
        self.write(
            ".github/instructions/docs.instructions.md",
            "---\napplyTo: 'docs/**'\n---\nUse prose.\n",
        )
        self.write(".github/instructions/broken.instructions.md", "No frontmatter\n")
        self.write("src/api/app.py", "")

        result = inspect_targets(
            self.root, ["src/api/app.py"], profile="copilot-cli"
        )[0]
        by_name = {source.path: source for source in result.sources}

        self.assertEqual(
            by_name[".github/instructions/python.instructions.md"].state,
            "applied",
        )
        self.assertEqual(
            by_name[".github/instructions/docs.instructions.md"].state,
            "ignored",
        )
        self.assertIn(
            "missing supported applyTo",
            by_name[".github/instructions/broken.instructions.md"].reason,
        )

        nested_test = inspect_targets(
            self.root, ["tests/unit/test_app.py"], profile="copilot-cli"
        )[0]
        nested_by_name = {source.path: source for source in nested_test.sources}
        self.assertEqual(
            nested_by_name[".github/instructions/python.instructions.md"].state,
            "ignored",
        )

    def test_target_cannot_escape_root(self) -> None:
        with self.assertRaisesRegex(ValueError, "escapes repository root"):
            inspect_targets(self.root, ["../outside.py"])

    def test_cli_json_contract_and_requirement_exit(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output):
            exit_code = main(
                [
                    "--root",
                    str(self.root),
                    "--json",
                    "--require-instructions",
                    "src/app.py",
                ]
            )

        payload = json.loads(output.getvalue())
        self.assertEqual(exit_code, 1)
        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(payload["profile"], "agents-md")
        self.assertEqual(payload["targets"][0]["applied_count"], 0)

    def test_cli_reports_invalid_root_as_usage_failure(self) -> None:
        errors = io.StringIO()
        with redirect_stderr(errors):
            exit_code = main(["--root", str(self.root / "missing")])

        self.assertEqual(exit_code, 2)
        self.assertIn("repository root is not a directory", errors.getvalue())

    def test_compare_finds_common_and_profile_specific_nested_sources(self) -> None:
        self.write("AGENTS.md")
        self.write("packages/api/AGENTS.md")
        self.write("packages/api/CLAUDE.md")
        self.write("packages/api/app.py", "")

        comparison = compare_targets(self.root, ["packages/api/app.py"])[0]

        self.assertTrue(comparison.divergent)
        self.assertEqual(comparison.common_sources, ("packages/api/AGENTS.md",))
        by_profile = {profile.profile: profile for profile in comparison.profiles}
        self.assertEqual(by_profile["agents-md"].unique_sources, ())
        self.assertEqual(
            by_profile["copilot-cli"].unique_sources,
            ("AGENTS.md", "packages/api/CLAUDE.md"),
        )

    def test_compare_ignores_unmatched_path_rules_and_preserves_target_order(self) -> None:
        self.write("AGENTS.md")
        self.write(
            ".github/instructions/python.instructions.md",
            '---\napplyTo: "src/**/*.py"\n---\nUse Python.\n',
        )

        comparisons = compare_targets(self.root, ["docs/readme.md", "src/app.py"])

        self.assertEqual(
            [comparison.target for comparison in comparisons],
            ["docs/readme.md", "src/app.py"],
        )
        self.assertFalse(comparisons[0].divergent)
        self.assertTrue(comparisons[1].divergent)
        python_profile = comparisons[1].profiles[1]
        self.assertEqual(
            python_profile.unique_sources,
            (".github/instructions/python.instructions.md",),
        )

    def test_compare_empty_guidance_is_consistent(self) -> None:
        comparison = compare_targets(self.root, ["planned/new.py"])[0]

        self.assertFalse(comparison.divergent)
        self.assertEqual(comparison.common_sources, ())
        self.assertTrue(
            all(not profile.applied_sources for profile in comparison.profiles)
        )

    def test_compare_cli_json_contract_and_divergence_gate(self) -> None:
        self.write("CLAUDE.md")
        output = io.StringIO()
        with redirect_stdout(output):
            exit_code = main(
                [
                    "compare",
                    "--root",
                    str(self.root),
                    "--json",
                    "--fail-on-divergence",
                    "src/app.py",
                ]
            )

        payload = json.loads(output.getvalue())
        self.assertEqual(exit_code, 1)
        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(payload["profiles"], ["agents-md", "copilot-cli"])
        self.assertEqual(payload["divergent_target_count"], 1)
        target = payload["targets"][0]
        self.assertTrue(target["divergent"])
        self.assertEqual(
            target["profiles"]["copilot-cli"]["unique_sources"],
            ["CLAUDE.md"],
        )

    def test_compare_cli_human_output_covers_divergent_and_empty_targets(self) -> None:
        self.write("CLAUDE.md")
        output = io.StringIO()
        with redirect_stdout(output):
            exit_code = main(
                ["compare", "--root", str(self.root), "src/app.py"]
            )
        rendered = output.getvalue()

        self.assertEqual(exit_code, 0)
        self.assertIn("src/app.py: DIVERGENT", rendered)
        self.assertIn("copilot-cli ONLY (1)", rendered)
        self.assertIn("CLAUDE.md", rendered)

        empty_root = self.root / "empty"
        empty_root.mkdir()
        output = io.StringIO()
        with redirect_stdout(output):
            exit_code = main(["compare", "--root", str(empty_root)])
        self.assertEqual(exit_code, 0)
        self.assertIn("no applied instruction sources", output.getvalue())


if __name__ == "__main__":
    unittest.main()
