from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from agentscope.cli import main
from agentscope.core import (
    REFERENCE_DEPTH_LIMIT,
    _matches,
    compare_targets,
    inspect_targets,
)


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
        self.write(".github/copilot-instructions.md", "Repository guidance.\n")
        self.write("AGENTS.md", "Agent guidance.\n")
        self.write("packages/CLAUDE.md", "Claude guidance.\n")
        self.write("packages/api/GEMINI.md", "Gemini guidance.\n")
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

    def test_copilot_cli_discovers_target_ancestor_standard_locations(self) -> None:
        self.write(".github/copilot-instructions.md", "Root repository.\n")
        self.write(".claude/CLAUDE.md", "Root Claude.\n")
        self.write(
            "packages/.github/copilot-instructions.md", "Package repository.\n"
        )
        self.write("packages/AGENTS.md", "Package agents.\n")
        self.write("packages/api/.claude/CLAUDE.md", "API Claude.\n")
        self.write(
            ".github/instructions/root.instructions.md",
            '---\napplyTo: "**/*.py"\n---\n',
        )
        self.write(
            "packages/.github/instructions/package.instructions.md",
            '---\napplyTo: "packages/**/*.py"\n---\n',
        )
        self.write(
            "packages/api/.github/instructions/api.instructions.md",
            '---\napplyTo: "packages/api/**/*.py"\n---\n',
        )
        self.write("packages/api/app.py", "")

        result = inspect_targets(
            self.root, ["packages/api/app.py"], profile="copilot-cli"
        )[0]

        self.assertEqual(
            [source.path for source in result.sources],
            [
                ".github/copilot-instructions.md",
                ".claude/CLAUDE.md",
                "packages/.github/copilot-instructions.md",
                "packages/AGENTS.md",
                "packages/api/.claude/CLAUDE.md",
                ".github/instructions/root.instructions.md",
                "packages/.github/instructions/package.instructions.md",
                "packages/api/.github/instructions/api.instructions.md",
            ],
        )
        self.assertTrue(all(source.state == "applied" for source in result.sources))
        self.assertTrue(
            all(
                "standard location" in source.reason
                for source in result.sources[:5]
            )
        )

    def test_copilot_session_directory_excludes_intermediate_modular_sources(
        self,
    ) -> None:
        locations = (
            ("", "root"),
            ("workspace", "intermediate"),
            ("workspace/session", "session"),
            ("workspace/session/src", "target"),
        )
        for directory, name in locations:
            prefix = f"{directory}/" if directory else ""
            self.write(f"{prefix}AGENTS.md", f"{name} standard\n")
            self.write(
                f"{prefix}.github/instructions/{name}.instructions.md",
                '---\napplyTo: "**/*.py"\n---\n',
            )

        result = inspect_targets(
            self.root,
            ["workspace/session/src/planned.py"],
            profile="copilot-cli",
            cwd="workspace/session",
        )[0]

        self.assertEqual(
            [source.path for source in result.sources],
            [
                "AGENTS.md",
                "workspace/AGENTS.md",
                "workspace/session/AGENTS.md",
                "workspace/session/src/AGENTS.md",
                ".github/instructions/root.instructions.md",
                "workspace/session/.github/instructions/session.instructions.md",
                "workspace/session/src/.github/instructions/target.instructions.md",
            ],
        )
        self.assertNotIn(
            "workspace/.github/instructions/intermediate.instructions.md",
            [source.path for source in result.sources],
        )
        self.assertIn("session intermediate", result.sources[1].reason)
        self.assertIn("session directory", result.sources[2].reason)
        self.assertIn("target-nested", result.sources[3].reason)

    def test_copilot_session_directory_handles_divergent_planned_target(self) -> None:
        locations = (
            ("session-parent", "intermediate"),
            ("session-parent/work", "session"),
            ("packages", "package"),
            ("packages/api", "target"),
        )
        for directory, name in locations:
            self.write(f"{directory}/CLAUDE.md", f"{name} standard\n")
            self.write(
                f"{directory}/.github/instructions/{name}.instructions.md",
                '---\napplyTo: "packages/**/*.py"\n---\n',
            )

        result = inspect_targets(
            self.root,
            ["packages/api/new.py"],
            profile="copilot-cli",
            cwd="session-parent/work",
        )[0]

        self.assertEqual(
            [source.path for source in result.sources],
            [
                "session-parent/CLAUDE.md",
                "session-parent/work/CLAUDE.md",
                "packages/CLAUDE.md",
                "packages/api/CLAUDE.md",
                "session-parent/work/.github/instructions/session.instructions.md",
                "packages/.github/instructions/package.instructions.md",
                "packages/api/.github/instructions/target.instructions.md",
            ],
        )
        self.assertNotIn(
            "session-parent/.github/instructions/intermediate.instructions.md",
            [source.path for source in result.sources],
        )

    def test_session_directory_defaults_to_root_and_must_be_contained_directory(
        self,
    ) -> None:
        self.write("AGENTS.md")
        self.write("src/AGENTS.md")

        default = inspect_targets(
            self.root, ["src/app.py"], profile="copilot-cli"
        )
        explicit = inspect_targets(
            self.root, ["src/app.py"], profile="copilot-cli", cwd="."
        )
        self.assertEqual(default, explicit)

        with self.assertRaisesRegex(ValueError, "session directory escapes"):
            inspect_targets(self.root, ["src/app.py"], cwd="../outside")
        self.write("not-a-directory", "file\n")
        with self.assertRaisesRegex(ValueError, "session directory is not"):
            inspect_targets(self.root, ["src/app.py"], cwd="not-a-directory")
        with tempfile.TemporaryDirectory() as outside:
            (self.root / "outside-link").symlink_to(outside)
            with self.assertRaisesRegex(ValueError, "session directory escapes"):
                inspect_targets(self.root, ["src/app.py"], cwd="outside-link")

    def test_copilot_cli_deduplicates_first_resolved_source_discovery(self) -> None:
        self.write(
            ".github/copilot-instructions.md",
            "@../CLAUDE.md\n@../GEMINI.md\n@instructions/python.instructions.md\n",
        )
        self.write("CLAUDE.md")
        self.write("GEMINI.md")
        (self.root / ".claude").mkdir()
        (self.root / ".claude" / "CLAUDE.md").symlink_to("../CLAUDE.md")
        self.write(
            ".github/instructions/python.instructions.md",
            '---\napplyTo: "**/*.py"\n---\n',
        )

        result = inspect_targets(self.root, ["src/app.py"], profile="copilot-cli")[0]

        self.assertEqual(
            [source.path for source in result.sources],
            [
                ".github/copilot-instructions.md",
                "CLAUDE.md",
                "GEMINI.md",
                ".github/instructions/python.instructions.md",
            ],
        )
        self.assertEqual(
            [source.kind for source in result.sources],
            [
                "copilot-repository",
                "copilot-reference",
                "copilot-reference",
                "copilot-reference",
            ],
        )
        self.assertEqual(result.applied_count, 4)

    def test_copilot_cli_explains_normalized_standard_content_copies(self) -> None:
        canonical = "Use Python.\n\nRun tests.\n"
        self.write("AGENTS.md", canonical)
        self.write("CLAUDE.md", "Use Python only.\nRun tests.\n")
        self.write(
            "workspace/.github/copilot-instructions.md",
            "  Use Python.\n Run tests.  \n",
        )
        self.write("workspace/session/.claude/CLAUDE.md", canonical)
        self.write("packages/GEMINI.md", canonical)
        self.write("packages/api/CLAUDE.md", canonical)
        modular = '---\napplyTo: "**/*.py"\n---\nUse Python.\n'
        self.write(".github/instructions/root.instructions.md", modular)
        self.write(
            "workspace/session/.github/instructions/session.instructions.md",
            modular,
        )

        result = inspect_targets(
            self.root,
            ["packages/api/new.py"],
            profile="copilot-cli",
            cwd="workspace/session",
        )[0]
        by_path = {source.path: source for source in result.sources}

        self.assertEqual(by_path["AGENTS.md"].state, "applied")
        self.assertEqual(by_path["CLAUDE.md"].state, "applied")
        duplicates = [
            source for source in result.sources if source.state == "duplicate"
        ]
        self.assertEqual(
            [source.path for source in duplicates],
            [
                "workspace/.github/copilot-instructions.md",
                "workspace/session/.claude/CLAUDE.md",
                "packages/GEMINI.md",
                "packages/api/CLAUDE.md",
            ],
        )
        self.assertTrue(
            all(
                "first discovered source AGENTS.md" in item.reason
                for item in duplicates
            )
        )
        self.assertEqual(
            [
                source.state
                for source in result.sources
                if source.kind == "copilot-path"
            ],
            ["applied", "applied"],
        )
        self.assertEqual(result.applied_count, 4)

        human = io.StringIO()
        with redirect_stdout(human):
            main(
                [
                    "--profile",
                    "copilot-cli",
                    "--root",
                    str(self.root),
                    "--cwd",
                    "workspace/session",
                    "packages/api/new.py",
                ]
            )
        self.assertIn(
            "DUPLICATE workspace/.github/copilot-instructions.md",
            human.getvalue(),
        )

        output = io.StringIO()
        with redirect_stdout(output):
            main(
                [
                    "--profile",
                    "copilot-cli",
                    "--root",
                    str(self.root),
                    "--cwd",
                    "workspace/session",
                    "--json",
                    "packages/api/new.py",
                ]
            )
        payload = json.loads(output.getvalue())
        self.assertEqual(payload["schema_version"], 5)
        self.assertEqual(payload["targets"][0]["sources"][2]["state"], "duplicate")

    def test_standard_copy_deduplication_preserves_relative_references(self) -> None:
        self.write("AGENTS.md", "@guide.md\nUse Python.\n")
        self.write("guide.md", "Shared guidance.\n")
        self.write("GEMINI.md", "Shared guidance.\n")
        self.write("session/CLAUDE.md", " @guide.md\n\nUse Python. \n")
        self.write("session/guide.md", "Session-specific guidance.\n")

        result = inspect_targets(
            self.root,
            ["src/app.py"],
            profile="copilot-cli",
            cwd="session",
        )[0]

        self.assertEqual(
            [(source.path, source.state) for source in result.sources],
            [
                ("AGENTS.md", "applied"),
                ("guide.md", "applied"),
                ("GEMINI.md", "applied"),
                ("session/CLAUDE.md", "duplicate"),
                ("session/guide.md", "applied"),
            ],
        )
        self.assertEqual(result.sources[-1].kind, "copilot-reference")
        self.assertEqual(result.applied_count, 4)

    def test_unreadable_standard_sources_are_invalid_without_expanding_references(
        self,
    ) -> None:
        invalid_utf8 = self.root / ".github" / "copilot-instructions.md"
        invalid_utf8.parent.mkdir(parents=True)
        invalid_utf8.write_bytes(b"@hidden-from-invalid.md\n\xff")
        self.write("hidden-from-invalid.md")
        self.write("AGENTS.md", "@valid.md\n")
        self.write("valid.md")
        self.write("CLAUDE.md", "@hidden-from-unreadable.md\n")
        self.write("hidden-from-unreadable.md")

        original_read_text = Path.read_text
        unreadable = (self.root / "CLAUDE.md").resolve()

        def read_text_with_failure(path: Path, *args: object, **kwargs: object) -> str:
            if path.resolve() == unreadable:
                raise OSError("platform-specific details must not leak")
            return original_read_text(path, *args, **kwargs)

        with patch.object(Path, "read_text", read_text_with_failure):
            result = inspect_targets(
                self.root, ["src/app.py"], profile="copilot-cli"
            )[0]

        self.assertEqual(
            [(source.path, source.state) for source in result.sources],
            [
                (".github/copilot-instructions.md", "invalid"),
                ("AGENTS.md", "applied"),
                ("valid.md", "applied"),
                ("CLAUDE.md", "invalid"),
            ],
        )
        self.assertEqual(result.applied_count, 2)
        self.assertEqual(result.invalid_source_count, 2)
        self.assertEqual(result.invalid_reference_count, 0)
        self.assertEqual(
            result.sources[0].reason, "instruction file is not valid UTF-8"
        )
        self.assertEqual(
            result.sources[-1].reason, "instruction file could not be read"
        )
        self.assertNotIn(
            "platform-specific details",
            " ".join(source.reason for source in result.sources),
        )

    def test_invalid_standard_source_policy_output_and_comparison(self) -> None:
        agents = self.root / "AGENTS.md"
        agents.write_bytes(b"@hidden.md\n\xff")
        self.write("hidden.md")

        human = io.StringIO()
        with redirect_stdout(human):
            informational_exit = main(
                ["--profile", "copilot-cli", "--root", str(self.root), "src/app.py"]
            )

        output = io.StringIO()
        with redirect_stdout(output):
            policy_exit = main(
                [
                    "--profile",
                    "copilot-cli",
                    "--root",
                    str(self.root),
                    "--json",
                    "--fail-on-invalid-sources",
                    "src/app.py",
                ]
            )

        payload = json.loads(output.getvalue())
        comparison = compare_targets(self.root, ["src/app.py"])[0]
        by_profile = {profile.profile: profile for profile in comparison.profiles}

        self.assertEqual(informational_exit, 0)
        self.assertEqual(policy_exit, 1)
        self.assertIn("invalid sources: 1", human.getvalue())
        self.assertIn("INVALID  AGENTS.md [agents-md]", human.getvalue())
        self.assertIn("not valid UTF-8", human.getvalue())
        self.assertEqual(payload["schema_version"], 5)
        self.assertEqual(payload["applied_source_count"], 0)
        self.assertEqual(payload["invalid_source_count"], 1)
        self.assertEqual(payload["invalid_reference_count"], 0)
        self.assertEqual(payload["targets"][0]["sources"][0]["state"], "invalid")
        self.assertEqual(
            [source["path"] for source in payload["targets"][0]["sources"]],
            ["AGENTS.md"],
        )
        self.assertTrue(comparison.divergent)
        self.assertEqual(comparison.invalid_source_count, 1)
        self.assertEqual(comparison.invalid_reference_count, 0)
        self.assertEqual(by_profile["agents-md"].unique_sources, ("AGENTS.md",))
        self.assertEqual(by_profile["copilot-cli"].applied_sources, ())
        self.assertEqual(by_profile["agents-md"].invalid_sources, ())
        self.assertEqual(
            [source.path for source in by_profile["copilot-cli"].invalid_sources],
            ["AGENTS.md"],
        )

    def test_copilot_references_expand_recursively_and_relative_to_each_file(self) -> None:
        self.write("AGENTS.md", "@docs/root.md\n")
        self.write("docs/root.md", "@nested/detail.md\n")
        self.write("docs/nested/detail.md", "Detailed guidance.\n")

        result = inspect_targets(self.root, ["src/app.py"], profile="copilot-cli")[0]

        self.assertEqual(
            [(source.path, source.state) for source in result.sources],
            [
                ("AGENTS.md", "applied"),
                ("docs/root.md", "applied"),
                ("docs/nested/detail.md", "applied"),
            ],
        )
        self.assertEqual(result.sources[1].kind, "copilot-reference")
        self.assertEqual(result.sources[1].reason, "referenced by AGENTS.md")
        self.assertEqual(result.applied_count, 3)

        comparison = compare_targets(self.root, ["src/app.py"])[0]
        copilot = comparison.profiles[1]
        self.assertEqual(
            copilot.unique_sources,
            ("docs/root.md", "docs/nested/detail.md"),
        )

    def test_copilot_references_report_cycle_missing_and_escape_diagnostics(self) -> None:
        self.write(
            "CLAUDE.md",
            "@docs/a.md\n@missing.md\n@../outside.md\n@/absolute.md\n@~/home.md\n",
        )
        self.write("docs/a.md", "@../CLAUDE.md\n")

        result = inspect_targets(self.root, ["src/app.py"], profile="copilot-cli")[0]
        invalid = [source for source in result.sources if source.state == "invalid"]

        self.assertEqual(len(invalid), 5)
        self.assertIn("reference cycle", invalid[0].reason)
        self.assertIn("missing", invalid[1].reason)
        self.assertIn("escapes repository root", invalid[2].reason)
        self.assertIn("absolute reference", invalid[3].reason)
        self.assertIn("home-relative reference", invalid[4].reason)
        self.assertEqual(result.applied_count, 2)

    def test_unreadable_reference_is_invalid_and_stops_recursive_expansion(
        self,
    ) -> None:
        self.write("AGENTS.md", "@guide.md\n")
        (self.root / "guide.md").write_bytes(b"@hidden.md\n\xff")
        self.write("hidden.md")

        result = inspect_targets(self.root, ["src/app.py"], profile="copilot-cli")[0]
        with redirect_stdout(io.StringIO()):
            gate_exit = main(
                [
                    "--profile",
                    "copilot-cli",
                    "--root",
                    str(self.root),
                    "--fail-on-invalid-references",
                    "src/app.py",
                ]
            )

        self.assertEqual(
            [(source.path, source.state) for source in result.sources],
            [("AGENTS.md", "applied"), ("guide.md", "invalid")],
        )
        self.assertEqual(result.applied_count, 1)
        self.assertEqual(result.invalid_source_count, 1)
        self.assertEqual(result.invalid_reference_count, 1)
        self.assertEqual(
            result.sources[-1].reason,
            "instruction file is not valid UTF-8 (referenced by AGENTS.md)",
        )
        self.assertEqual(gate_exit, 1)

    def test_reference_sources_keep_human_and_json_contracts(self) -> None:
        self.write("AGENTS.md", "@guide.md\n@missing.md\n")
        self.write("guide.md")

        human = io.StringIO()
        with redirect_stdout(human):
            human_exit = main(
                ["--profile", "copilot-cli", "--root", str(self.root), "src/app.py"]
            )
        self.assertEqual(human_exit, 0)
        self.assertIn("invalid sources: 1", human.getvalue())
        self.assertIn("invalid references: 1", human.getvalue())
        self.assertIn(
            "src/app.py: 2 applied, 1 invalid, 1 invalid reference",
            human.getvalue(),
        )
        self.assertIn("APPLIED  guide.md [copilot-reference]", human.getvalue())
        self.assertIn("INVALID  missing.md [copilot-reference]", human.getvalue())

        output = io.StringIO()
        with redirect_stdout(output):
            json_exit = main(
                [
                    "--profile",
                    "copilot-cli",
                    "--root",
                    str(self.root),
                    "--json",
                    "src/app.py",
                ]
            )
        payload = json.loads(output.getvalue())
        self.assertEqual(json_exit, 0)
        self.assertEqual(payload["schema_version"], 5)
        self.assertEqual(payload["invalid_reference_count"], 1)
        self.assertEqual(payload["invalid_source_count"], 1)
        self.assertEqual(payload["targets"][0]["applied_count"], 2)
        self.assertEqual(payload["targets"][0]["invalid_reference_count"], 1)
        self.assertEqual(payload["targets"][0]["invalid_source_count"], 1)
        self.assertEqual(payload["targets"][0]["sources"][-1]["state"], "invalid")

    def test_invalid_reference_gate_composes_with_missing_guidance(self) -> None:
        self.write("services/AGENTS.md", "@missing.md\n")
        targets = ["services/app.py", "services/worker.py", "docs/readme.md"]

        with redirect_stdout(io.StringIO()):
            informational_exit = main(
                ["--profile", "copilot-cli", "--root", str(self.root), *targets]
            )
            invalid_exit = main(
                [
                    "--profile",
                    "copilot-cli",
                    "--root",
                    str(self.root),
                    "--fail-on-invalid-references",
                    *targets,
                ]
            )
            missing_exit = main(
                ["--root", str(self.root), "--require-instructions", *targets]
            )
            agents_md_invalid_exit = main(
                [
                    "--root",
                    str(self.root),
                    "--fail-on-invalid-references",
                    "services/app.py",
                ]
            )
            broader_exit = main(
                [
                    "--profile",
                    "copilot-cli",
                    "--root",
                    str(self.root),
                    "--fail-on-invalid-sources",
                    *targets,
                ]
            )

        output = io.StringIO()
        with redirect_stdout(output):
            combined_exit = main(
                [
                    "--profile",
                    "copilot-cli",
                    "--root",
                    str(self.root),
                    "--json",
                    "--require-instructions",
                    "--fail-on-invalid-references",
                    *targets,
                ]
            )

        payload = json.loads(output.getvalue())
        self.assertEqual(informational_exit, 0)
        self.assertEqual(invalid_exit, 1)
        self.assertEqual(missing_exit, 1)
        self.assertEqual(agents_md_invalid_exit, 0)
        self.assertEqual(broader_exit, 1)
        self.assertEqual(combined_exit, 1)
        self.assertEqual(payload["invalid_reference_count"], 2)
        self.assertEqual(payload["invalid_source_count"], 2)
        self.assertEqual(
            [target["invalid_reference_count"] for target in payload["targets"]],
            [1, 1, 0],
        )
        self.assertEqual(
            [target["applied_count"] for target in payload["targets"]],
            [1, 1, 0],
        )

    def test_copilot_references_stop_at_documented_source_boundaries(self) -> None:
        self.write("GEMINI.md", "@hidden-gemini.md\n")
        self.write("hidden-gemini.md")
        self.write(
            ".github/instructions/python.instructions.md",
            '---\napplyTo: "**/*.py"\n---\n@hidden-path.md\n',
        )
        self.write("hidden-path.md")

        result = inspect_targets(self.root, ["src/app.py"], profile="copilot-cli")[0]

        self.assertEqual(
            [source.path for source in result.sources],
            ["GEMINI.md", ".github/instructions/python.instructions.md"],
        )

    def test_copilot_reference_cannot_escape_through_symlink(self) -> None:
        self.write("AGENTS.md", "@outside-link.md\n")
        with tempfile.TemporaryDirectory() as outside:
            outside_file = Path(outside) / "outside.md"
            outside_file.write_text("not repository guidance\n", encoding="utf-8")
            (self.root / "outside-link.md").symlink_to(outside_file)

            result = inspect_targets(
                self.root, ["src/app.py"], profile="copilot-cli"
            )[0]

        self.assertEqual(result.sources[-1].state, "invalid")
        self.assertIn("escapes repository root", result.sources[-1].reason)

    def test_copilot_reference_depth_has_explicit_diagnostic(self) -> None:
        self.write("AGENTS.md", "@refs/0.md\n")
        for index in range(REFERENCE_DEPTH_LIMIT + 1):
            self.write(f"refs/{index}.md", f"@{index + 1}.md\n")
        self.write(f"refs/{REFERENCE_DEPTH_LIMIT + 1}.md")

        result = inspect_targets(self.root, ["src/app.py"], profile="copilot-cli")[0]

        self.assertEqual(result.sources[-1].state, "invalid")
        self.assertIn("reference depth exceeds", result.sources[-1].reason)
        self.assertNotIn(
            f"refs/{REFERENCE_DEPTH_LIMIT}.md",
            [source.path for source in result.sources if source.state == "applied"],
        )

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
        self.assertEqual(
            by_name[".github/instructions/broken.instructions.md"].state,
            "invalid",
        )
        self.assertIn(
            "frontmatter must start",
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

    def test_apply_to_glob_compatibility_matrix(self) -> None:
        cases = (
            # GitHub's documented Copilot CLI examples.
            ("*", "root.py", True),
            ("*", "src/root.py", False),
            ("**", "root.py", True),
            ("**", "src/root.py", True),
            ("**/*", "root.py", True),
            ("**/*", "src/root.py", True),
            ("*.py", "root.py", True),
            ("*.py", "src/root.py", False),
            ("**/*.py", "root.py", True),
            ("**/*.py", "src/root.py", True),
            ("src/*.py", "src/root.py", True),
            ("src/*.py", "src/nested/root.py", False),
            ("src/**/*.py", "src/root.py", True),
            ("src/**/*.py", "src/nested/root.py", True),
            ("**/subdir/**/*.py", "subdir/root.py", True),
            ("**/subdir/**/*.py", "parent/subdir/nested/root.py", True),
            ("**/subdir/**/*.py", "root.py", False),
            # Repository-relative anchoring and the claimed '?' subset.
            ("src/*.py", "other/src/root.py", False),
            ("**/src/*.py", "other/src/root.py", True),
            ("src/file?.py", "src/file1.py", True),
            ("src/file?.py", "src/file10.py", False),
            # A leading dot is a path character, not a normalization marker.
            (".github/**/*.yml", ".github/workflows/test.yml", True),
            (".*", ".env", True),
            (".*", "README.md", False),
            # An explicit relative marker is harmless; a slash is not documented.
            ("./src/*.py", "src/root.py", True),
            ("/src/*.py", "src/root.py", False),
        )

        for pattern, target, expected in cases:
            with self.subTest(pattern=pattern, target=target):
                self.assertEqual(_matches(target, pattern), expected)

    def test_apply_to_comma_separated_patterns_use_or_semantics(self) -> None:
        self.write(
            ".github/instructions/web.instructions.md",
            '---\napplyTo: "src/**/*.ts, src/**/*.tsx"\n---\nUse TypeScript.\n',
        )

        inspections = inspect_targets(
            self.root,
            ["src/app.ts", "src/components/app.tsx", "src/app.js"],
            profile="copilot-cli",
        )

        self.assertEqual(
            [inspection.sources[0].state for inspection in inspections],
            ["applied", "applied", "ignored"],
        )

    def test_path_frontmatter_diagnostics_are_precise_and_ordered(self) -> None:
        cases = {
            "block-list": '---\napplyTo:\n  - "**/*.py"\n---\n',
            "duplicate": '---\napplyTo: "**/*.py"\napplyTo: "src/**"\n---\n',
            "empty": '---\napplyTo: ""\n---\n',
            "empty-pattern": '---\napplyTo: "**/*.py, "\n---\n',
            "inline-list": '---\napplyTo: ["**/*.py"]\n---\n',
            "malformed-key": '---\napplyTo "**/*.py"\n---\n',
            "mapping": '---\napplyTo: {glob: "**/*.py"}\n---\n',
            "missing-close": '---\napplyTo: "**/*.py"\n',
            "missing-key": '---\ndescription: Python files\n---\n',
            "missing-open": 'applyTo: "**/*.py"\n---\n',
            "multiline": '---\napplyTo: |\n  **/*.py\n---\n',
            "unmatched-close": '---\napplyTo: **/*.py"\n---\n',
            "unclosed-quote": '---\napplyTo: "**/*.py\n---\n',
        }
        for name, content in cases.items():
            self.write(f".github/instructions/{name}.instructions.md", content)

        result = inspect_targets(self.root, ["src/app.py"], profile="copilot-cli")[0]

        self.assertEqual(result.applied_count, 0)
        self.assertEqual(result.invalid_reference_count, 0)
        self.assertEqual(result.invalid_source_count, len(cases))
        self.assertEqual(
            [source.path for source in result.sources],
            sorted(source.path for source in result.sources),
        )
        reasons = {
            Path(source.path).stem.split(".")[0]: source.reason
            for source in result.sources
        }
        self.assertIn("list values", reasons["block-list"])
        self.assertIn("duplicate", reasons["duplicate"])
        self.assertIn("scalar is empty", reasons["empty"])
        self.assertIn("empty glob", reasons["empty-pattern"])
        self.assertIn("list values", reasons["inline-list"])
        self.assertIn("missing a colon", reasons["malformed-key"])
        self.assertIn("mapping values", reasons["mapping"])
        self.assertIn("closing delimiter", reasons["missing-close"])
        self.assertIn("missing applyTo", reasons["missing-key"])
        self.assertIn("must start", reasons["missing-open"])
        self.assertIn("multiline", reasons["multiline"])
        self.assertIn("unmatched closing", reasons["unmatched-close"])
        self.assertIn("unterminated", reasons["unclosed-quote"])

    def test_invalid_source_gate_is_broader_than_reference_gate(self) -> None:
        self.write(
            ".github/instructions/broken.instructions.md",
            '---\napplyTo: ["**/*.py"]\n---\n',
        )

        with redirect_stdout(io.StringIO()):
            reference_exit = main(
                [
                    "--profile",
                    "copilot-cli",
                    "--root",
                    str(self.root),
                    "--fail-on-invalid-references",
                    "src/app.py",
                ]
            )
        output = io.StringIO()
        with redirect_stdout(output):
            source_exit = main(
                [
                    "--profile",
                    "copilot-cli",
                    "--root",
                    str(self.root),
                    "--json",
                    "--fail-on-invalid-sources",
                    "src/app.py",
                ]
            )

        payload = json.loads(output.getvalue())
        self.assertEqual(reference_exit, 0)
        self.assertEqual(source_exit, 1)
        self.assertEqual(payload["schema_version"], 5)
        self.assertEqual(payload["invalid_source_count"], 1)
        self.assertEqual(payload["invalid_reference_count"], 0)
        self.assertEqual(payload["targets"][0]["sources"][0]["state"], "invalid")

    def test_additional_instruction_directories_are_ordered_and_composed(
        self,
    ) -> None:
        self.write("shared/AGENTS.md", "Shared guidance.\n@guide.md\n")
        self.write("shared/guide.md", "Imported guidance.\n")
        self.write(
            "shared/nested/python.instructions.md",
            '---\napplyTo: "**/*.py"\n---\nPython guidance.\n',
        )
        self.write("team/AGENTS.md", "Shared guidance.\n@guide.md\n")
        self.write("team/guide.md", "Team-specific guidance.\n")
        self.write(
            "team/docs.instructions.md",
            '---\napplyTo: "**/*.md"\n---\nDocs guidance.\n',
        )

        result = inspect_targets(
            self.root,
            ["src/planned.py"],
            profile="copilot-cli",
            instruction_dirs=["shared", "team", "shared/.", "."],
        )[0]

        self.assertEqual(
            [(source.path, source.state) for source in result.sources],
            [
                ("shared/AGENTS.md", "applied"),
                ("shared/guide.md", "applied"),
                ("shared/nested/python.instructions.md", "applied"),
                ("team/AGENTS.md", "duplicate"),
                ("team/guide.md", "applied"),
                ("team/docs.instructions.md", "ignored"),
            ],
        )
        self.assertIn("explicit additional", result.sources[0].reason)
        self.assertIn("explicit additional", result.sources[2].reason)
        self.assertEqual(result.applied_count, 4)

        portable = inspect_targets(
            self.root,
            ["src/planned.py"],
            profile="agents-md",
            instruction_dirs=["shared"],
        )[0]
        self.assertEqual(portable.sources, ())

    def test_additional_instruction_directories_require_contained_directories(
        self,
    ) -> None:
        self.write("custom/AGENTS.md")
        self.write("not-a-directory", "file\n")

        with self.assertRaisesRegex(
            ValueError, "additional instruction directory escapes"
        ):
            inspect_targets(
                self.root,
                ["src/app.py"],
                profile="copilot-cli",
                instruction_dirs=["../outside"],
            )
        with self.assertRaisesRegex(
            ValueError, "additional instruction directory is not"
        ):
            inspect_targets(
                self.root,
                ["src/app.py"],
                profile="copilot-cli",
                instruction_dirs=["not-a-directory"],
            )
        with tempfile.TemporaryDirectory() as outside:
            (self.root / "custom-link").symlink_to(outside)
            with self.assertRaisesRegex(
                ValueError, "additional instruction directory escapes"
            ):
                inspect_targets(
                    self.root,
                    ["src/app.py"],
                    profile="copilot-cli",
                    instruction_dirs=["custom-link"],
                )

            sources = self.root / "sources"
            sources.mkdir()
            outside_root = Path(outside)
            (outside_root / "AGENTS.md").write_text("External.\n", encoding="utf-8")
            (outside_root / "rule.instructions.md").write_text(
                '---\napplyTo: "**"\n---\nExternal.\n', encoding="utf-8"
            )
            (sources / "AGENTS.md").symlink_to(outside_root / "AGENTS.md")
            (sources / "rule.instructions.md").symlink_to(
                outside_root / "rule.instructions.md"
            )

            result = inspect_targets(
                self.root,
                ["src/app.py"],
                profile="copilot-cli",
                instruction_dirs=["sources"],
            )[0]
            self.assertEqual(
                [(source.path, source.state) for source in result.sources],
                [
                    ("sources/AGENTS.md", "invalid"),
                    ("sources/rule.instructions.md", "invalid"),
                ],
            )
            self.assertTrue(
                all(
                    "escapes repository root" in source.reason
                    for source in result.sources
                )
            )

    def test_cli_reports_effective_additional_directories_and_policy_exit(
        self,
    ) -> None:
        self.write("custom/AGENTS.md", "Custom guidance.\n")
        self.write(
            "custom/broken.instructions.md",
            '---\napplyTo: ["**/*.py"]\n---\n',
        )

        inspection_output = io.StringIO()
        with redirect_stdout(inspection_output):
            inspection_exit = main(
                [
                    "--profile",
                    "copilot-cli",
                    "--root",
                    str(self.root),
                    "--instructions-dir",
                    "custom",
                    "--instructions-dir",
                    "custom/.",
                    "--json",
                    "--fail-on-invalid-sources",
                    "src/planned.py",
                ]
            )
        inspection = json.loads(inspection_output.getvalue())

        comparison_output = io.StringIO()
        with redirect_stdout(comparison_output):
            comparison_exit = main(
                [
                    "compare",
                    "--root",
                    str(self.root),
                    "--instructions-dir",
                    "custom",
                    "--json",
                    "src/planned.py",
                ]
            )
        comparison = json.loads(comparison_output.getvalue())

        self.assertEqual(inspection_exit, 1)
        self.assertEqual(inspection["schema_version"], 5)
        self.assertEqual(inspection["additional_instruction_directories"], ["custom"])
        self.assertEqual(inspection["invalid_source_count"], 1)
        self.assertEqual(comparison_exit, 0)
        self.assertEqual(comparison["schema_version"], 5)
        self.assertEqual(comparison["additional_instruction_directories"], ["custom"])
        self.assertEqual(comparison["divergent_target_count"], 1)

        human = io.StringIO()
        with redirect_stdout(human):
            main(
                [
                    "--profile",
                    "copilot-cli",
                    "--root",
                    str(self.root),
                    "--instructions-dir",
                    "custom",
                    "src/planned.py",
                ]
            )
        self.assertIn("Additional instruction directories: custom", human.getvalue())

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
        self.assertEqual(payload["schema_version"], 5)
        self.assertEqual(payload["invalid_reference_count"], 0)
        self.assertEqual(payload["invalid_source_count"], 0)
        self.assertEqual(payload["profile"], "agents-md")
        self.assertEqual(payload["targets"][0]["applied_count"], 0)

    def test_cli_reports_invalid_root_as_usage_failure(self) -> None:
        errors = io.StringIO()
        with redirect_stderr(errors):
            exit_code = main(
                [
                    "--root",
                    str(self.root / "missing"),
                    "--fail-on-invalid-references",
                ]
            )

        self.assertEqual(exit_code, 2)
        self.assertIn("repository root is not a directory", errors.getvalue())

    def test_cli_session_directory_is_reported_in_inspection_and_comparison(
        self,
    ) -> None:
        self.write("tools/session/CLAUDE.md")

        inspection_output = io.StringIO()
        with redirect_stdout(inspection_output):
            inspection_exit = main(
                [
                    "--profile",
                    "copilot-cli",
                    "--root",
                    str(self.root),
                    "--cwd",
                    "tools/session",
                    "--json",
                    "src/planned.py",
                ]
            )
        inspection = json.loads(inspection_output.getvalue())

        comparison_output = io.StringIO()
        with redirect_stdout(comparison_output):
            comparison_exit = main(
                [
                    "compare",
                    "--root",
                    str(self.root),
                    "--cwd",
                    "tools/session",
                    "--json",
                    "src/planned.py",
                ]
            )
        comparison = json.loads(comparison_output.getvalue())

        self.assertEqual(inspection_exit, 0)
        self.assertEqual(inspection["schema_version"], 5)
        self.assertEqual(inspection["session_directory"], "tools/session")
        self.assertEqual(comparison_exit, 0)
        self.assertEqual(comparison["schema_version"], 5)
        self.assertEqual(comparison["session_directory"], "tools/session")

    def test_compare_finds_common_and_profile_specific_nested_sources(self) -> None:
        self.write("AGENTS.md", "Root agents.\n")
        self.write("packages/api/AGENTS.md", "API agents.\n")
        self.write("packages/api/CLAUDE.md", "API Claude.\n")
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

    def test_compare_retains_unmatched_path_rules_and_target_order(self) -> None:
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
        ignored = comparisons[0].profiles[1].non_applied_sources
        self.assertEqual(
            [(source.path, source.state) for source in ignored],
            [(".github/instructions/python.instructions.md", "ignored")],
        )
        python_profile = comparisons[1].profiles[1]
        self.assertEqual(
            python_profile.unique_sources,
            (".github/instructions/python.instructions.md",),
        )

    def test_compare_retains_ordered_non_applied_profile_evidence(self) -> None:
        self.write("AGENTS.md", "Shared guidance.\n")
        self.write("packages/api/AGENTS.md", "Nested guidance.\n")
        self.write("CLAUDE.md", "Shared guidance.\n")
        self.write(
            ".github/instructions/python.instructions.md",
            '---\napplyTo: "**/*.py"\n---\nPython guidance.\n',
        )
        targets = ["packages/api/app.py", "packages/api/readme.md"]

        comparisons = compare_targets(self.root, targets)
        first_portable, first_copilot = comparisons[0].profiles
        second_portable, second_copilot = comparisons[1].profiles

        self.assertEqual([item.target for item in comparisons], targets)
        self.assertEqual(
            [
                (source.path, source.state)
                for source in first_portable.non_applied_sources
            ],
            [("AGENTS.md", "shadowed")],
        )
        self.assertEqual(
            [
                (source.path, source.state)
                for source in first_copilot.non_applied_sources
            ],
            [("CLAUDE.md", "duplicate")],
        )
        self.assertEqual(
            [
                (source.path, source.state)
                for source in second_portable.non_applied_sources
            ],
            [("AGENTS.md", "shadowed")],
        )
        self.assertEqual(
            [
                (source.path, source.state)
                for source in second_copilot.non_applied_sources
            ],
            [
                ("CLAUDE.md", "duplicate"),
                (".github/instructions/python.instructions.md", "ignored"),
            ],
        )
        self.assertEqual(
            [item.non_applied_source_count for item in comparisons], [2, 3]
        )
        self.assertTrue(all(item.divergent for item in comparisons))

        output = io.StringIO()
        with redirect_stdout(output):
            exit_code = main(
                ["compare", "--root", str(self.root), "--json", *targets]
            )
        payload = json.loads(output.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["schema_version"], 5)
        self.assertEqual(payload["non_applied_source_count"], 5)
        serialized = payload["targets"][1]["profiles"]["copilot-cli"]
        self.assertEqual(serialized["non_applied_source_count"], 2)
        self.assertEqual(
            [source["state"] for source in serialized["non_applied_sources"]],
            ["duplicate", "ignored"],
        )

        human = io.StringIO()
        with redirect_stdout(human):
            main(["compare", "--root", str(self.root), *targets])
        rendered = human.getvalue()
        self.assertIn("non-applied sources: 5", rendered)
        self.assertIn("agents-md NON-APPLIED (1)", rendered)
        self.assertIn("SHADOWED AGENTS.md [agents-md]", rendered)
        self.assertIn("DUPLICATE CLAUDE.md [claude-md]", rendered)
        self.assertIn(
            "IGNORED .github/instructions/python.instructions.md", rendered
        )

    def test_ignored_source_gate_is_narrow_and_composes_across_targets(self) -> None:
        self.write("AGENTS.md", "Shared guidance.\n")
        self.write("packages/api/AGENTS.md", "Nested guidance.\n")
        self.write("CLAUDE.md", "Shared guidance.\n")
        self.write(
            ".github/instructions/python.instructions.md",
            '---\napplyTo: "**/*.py"\n---\nPython guidance.\n',
        )
        self.write(
            ".github/instructions/broken.instructions.md",
            '---\napplyTo: ["**/*.py"]\n---\n',
        )
        targets = ["packages/api/app.py", "packages/api/readme.md"]

        inspections = inspect_targets(self.root, targets, profile="copilot-cli")
        comparisons = compare_targets(self.root, targets)

        self.assertEqual(
            [item.ignored_source_count for item in inspections], [0, 1]
        )
        self.assertEqual(
            [item.ignored_source_count for item in comparisons], [0, 1]
        )
        first_non_applied = {
            source.state
            for profile in comparisons[0].profiles
            for source in profile.non_applied_sources
        }
        second_non_applied = {
            source.state
            for profile in comparisons[1].profiles
            for source in profile.non_applied_sources
        }
        self.assertEqual(first_non_applied, {"duplicate", "shadowed"})
        self.assertEqual(second_non_applied, {"duplicate", "ignored", "shadowed"})
        self.assertTrue(all(item.invalid_source_count == 1 for item in inspections))

        with redirect_stdout(io.StringIO()):
            matching_exit = main(
                [
                    "--profile",
                    "copilot-cli",
                    "--root",
                    str(self.root),
                    "--fail-on-ignored-sources",
                    targets[0],
                ]
            )
            shadowed_exit = main(
                [
                    "--root",
                    str(self.root),
                    "--fail-on-ignored-sources",
                    *targets,
                ]
            )
        with redirect_stderr(io.StringIO()):
            invalid_input_exit = main(
                [
                    "--root",
                    str(self.root / "missing"),
                    "--fail-on-ignored-sources",
                ]
            )

        inspection_output = io.StringIO()
        with redirect_stdout(inspection_output):
            inspection_exit = main(
                [
                    "--profile",
                    "copilot-cli",
                    "--root",
                    str(self.root),
                    "--json",
                    "--fail-on-ignored-sources",
                    *targets,
                ]
            )

        comparison_output = io.StringIO()
        with redirect_stdout(comparison_output):
            comparison_exit = main(
                [
                    "compare",
                    "--root",
                    str(self.root),
                    "--json",
                    "--fail-on-ignored-sources",
                    "--fail-on-invalid-sources",
                    *targets,
                ]
            )

        inspection_payload = json.loads(inspection_output.getvalue())
        comparison_payload = json.loads(comparison_output.getvalue())
        self.assertEqual(matching_exit, 0)
        self.assertEqual(shadowed_exit, 0)
        self.assertEqual(invalid_input_exit, 2)
        self.assertEqual(inspection_exit, 1)
        self.assertEqual(comparison_exit, 1)
        self.assertEqual(inspection_payload["schema_version"], 5)
        self.assertEqual(inspection_payload["target_count"], 2)
        self.assertEqual(comparison_payload["schema_version"], 5)
        self.assertEqual(comparison_payload["target_count"], 2)
        self.assertEqual(comparison_payload["invalid_source_count"], 2)

    def test_compare_empty_guidance_is_consistent(self) -> None:
        comparison = compare_targets(self.root, ["planned/new.py"])[0]

        self.assertFalse(comparison.divergent)
        self.assertFalse(comparison.has_applied_guidance)
        self.assertEqual(comparison.common_sources, ())
        self.assertTrue(
            all(not profile.applied_sources for profile in comparison.profiles)
        )

    def test_compare_requirement_rejects_only_targets_uncovered_by_all_profiles(
        self,
    ) -> None:
        self.write(
            ".github/instructions/python.instructions.md",
            '---\napplyTo: "src/**/*.py"\n---\nPython guidance.\n',
        )
        targets = ["src/app.py", "docs/readme.md"]

        with redirect_stdout(io.StringIO()):
            covered_exit = main(
                [
                    "compare",
                    "--root",
                    str(self.root),
                    "--require-instructions",
                    targets[0],
                ]
            )
            covered_divergence_exit = main(
                [
                    "compare",
                    "--root",
                    str(self.root),
                    "--require-instructions",
                    "--fail-on-divergence",
                    targets[0],
                ]
            )

        output = io.StringIO()
        with redirect_stdout(output):
            mixed_exit = main(
                [
                    "compare",
                    "--root",
                    str(self.root),
                    "--json",
                    "--require-instructions",
                    *targets,
                ]
            )
        payload = json.loads(output.getvalue())

        empty_root = self.root / "empty"
        empty_root.mkdir()
        empty_output = io.StringIO()
        with redirect_stdout(empty_output):
            informational_exit = main(["compare", "--root", str(empty_root)])
            empty_required_exit = main(
                [
                    "compare",
                    "--root",
                    str(empty_root),
                    "--require-instructions",
                ]
            )

        self.assertEqual(covered_exit, 0)
        self.assertEqual(covered_divergence_exit, 1)
        self.assertEqual(mixed_exit, 1)
        self.assertEqual(payload["schema_version"], 5)
        self.assertEqual(payload["target_count"], 2)
        self.assertTrue(payload["targets"][0]["divergent"])
        self.assertFalse(payload["targets"][1]["divergent"])
        self.assertEqual(informational_exit, 0)
        self.assertEqual(empty_required_exit, 1)
        self.assertIn("no applied instruction sources", empty_output.getvalue())

    def test_compare_retains_ordered_invalid_profile_evidence(self) -> None:
        self.write("AGENTS.md", "Shared guidance.\n")
        self.write("CLAUDE.md", "@missing.md\nClaude guidance.\n")
        invalid_utf8 = self.root / "GEMINI.md"
        invalid_utf8.write_bytes(b"\xff")
        self.write(
            ".github/instructions/broken.instructions.md",
            '---\napplyTo: ["**/*.py"]\n---\n',
        )

        comparison = compare_targets(self.root, ["src/app.py"])[0]
        by_profile = {profile.profile: profile for profile in comparison.profiles}
        portable = by_profile["agents-md"]
        copilot = by_profile["copilot-cli"]

        self.assertTrue(comparison.divergent)
        self.assertEqual(comparison.invalid_source_count, 3)
        self.assertEqual(comparison.invalid_reference_count, 1)
        self.assertEqual(portable.invalid_source_count, 0)
        self.assertEqual(portable.invalid_reference_count, 0)
        self.assertEqual(copilot.invalid_source_count, 3)
        self.assertEqual(copilot.invalid_reference_count, 1)
        self.assertEqual(
            [source.path for source in copilot.invalid_sources],
            [
                "missing.md",
                "GEMINI.md",
                ".github/instructions/broken.instructions.md",
            ],
        )
        serialized = comparison.to_dict()
        self.assertEqual(serialized["invalid_source_count"], 3)
        self.assertEqual(
            serialized["profiles"]["copilot-cli"]["invalid_sources"][0]["kind"],
            "copilot-reference",
        )

    def test_compare_invalid_source_gate_preserves_consistent_diagnostics(
        self,
    ) -> None:
        self.write(
            ".github/instructions/broken.instructions.md",
            '---\napplyTo: ["**/*.py"]\n---\n',
        )

        human = io.StringIO()
        with redirect_stdout(human):
            divergence_exit = main(
                [
                    "compare",
                    "--root",
                    str(self.root),
                    "--fail-on-divergence",
                    "src/app.py",
                ]
            )

        output = io.StringIO()
        with redirect_stdout(output):
            invalid_exit = main(
                [
                    "compare",
                    "--root",
                    str(self.root),
                    "--json",
                    "--fail-on-invalid-sources",
                    "src/app.py",
                ]
            )

        payload = json.loads(output.getvalue())
        rendered = human.getvalue()
        self.assertEqual(divergence_exit, 0)
        self.assertEqual(invalid_exit, 1)
        self.assertIn("src/app.py: UNGUIDED; 0 non-applied; 1 invalid", rendered)
        self.assertIn("no applied instruction sources", rendered)
        self.assertIn("agents-md DIAGNOSTICS (0 invalid", rendered)
        self.assertIn("copilot-cli DIAGNOSTICS (1 invalid", rendered)
        self.assertIn("broken.instructions.md [copilot-path]", rendered)
        self.assertEqual(payload["schema_version"], 5)
        self.assertEqual(payload["divergent_target_count"], 0)
        self.assertEqual(payload["invalid_source_count"], 1)
        self.assertEqual(payload["invalid_reference_count"], 0)
        target = payload["targets"][0]
        self.assertFalse(target["divergent"])
        self.assertEqual(target["invalid_source_count"], 1)
        self.assertEqual(
            target["profiles"]["copilot-cli"]["invalid_sources"][0]["state"],
            "invalid",
        )

    def test_compare_invalid_reference_gate_is_narrow_and_composes(self) -> None:
        self.write(
            ".github/instructions/broken.instructions.md",
            '---\napplyTo: ["**/*.py"]\n---\n',
        )
        targets = ["src/app.py", "docs/readme.md"]

        with redirect_stdout(io.StringIO()):
            narrow_malformed_exit = main(
                [
                    "compare",
                    "--root",
                    str(self.root),
                    "--fail-on-invalid-references",
                    *targets,
                ]
            )
            broad_malformed_exit = main(
                [
                    "compare",
                    "--root",
                    str(self.root),
                    "--fail-on-invalid-sources",
                    *targets,
                ]
            )

        self.write("AGENTS.md", "@missing.md\n")
        with redirect_stdout(io.StringIO()):
            reference_exit = main(
                [
                    "compare",
                    "--root",
                    str(self.root),
                    "--fail-on-invalid-references",
                    *targets,
                ]
            )

        self.write("CLAUDE.md", "Copilot-only guidance.\n")
        output = io.StringIO()
        with redirect_stdout(output):
            combined_exit = main(
                [
                    "compare",
                    "--root",
                    str(self.root),
                    "--json",
                    "--fail-on-divergence",
                    "--fail-on-invalid-references",
                    "--fail-on-invalid-sources",
                    *targets,
                ]
            )

        payload = json.loads(output.getvalue())
        self.assertEqual(narrow_malformed_exit, 0)
        self.assertEqual(broad_malformed_exit, 1)
        self.assertEqual(reference_exit, 1)
        self.assertEqual(combined_exit, 1)
        self.assertEqual(payload["schema_version"], 5)
        self.assertEqual(payload["target_count"], 2)
        self.assertEqual(payload["divergent_target_count"], 2)
        self.assertEqual(payload["invalid_reference_count"], 2)
        self.assertEqual(
            [target["invalid_reference_count"] for target in payload["targets"]],
            [1, 1],
        )
        self.assertTrue(
            all(
                target["profiles"]["copilot-cli"]["invalid_sources"][0]["kind"]
                == "copilot-reference"
                for target in payload["targets"]
            )
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
        self.assertEqual(payload["schema_version"], 5)
        self.assertEqual(payload["invalid_source_count"], 0)
        self.assertEqual(payload["invalid_reference_count"], 0)
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
        self.assertIn("unguided targets: 1", output.getvalue())
        self.assertIn(".: UNGUIDED", output.getvalue())
        self.assertIn("no applied instruction sources", output.getvalue())


if __name__ == "__main__":
    unittest.main()
