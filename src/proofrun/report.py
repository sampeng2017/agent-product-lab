from __future__ import annotations

import shlex
from datetime import datetime, timezone
from typing import Any, Iterable

from .core import GitState, assess_receipts, audit_receipts


def _inline_code(value: object) -> str:
    text = str(value)
    fence = "`"
    while fence in text:
        fence += "`"
    padding = " " if text.startswith("`") or text.endswith("`") else ""
    return f"{fence}{padding}{text}{padding}{fence}"


def _display(value: object, fallback: str = "unknown") -> str:
    return _inline_code(value) if value not in (None, "") else fallback


def _audit_summary(audited: list[dict[str, Any]]) -> dict[str, int | str]:
    invalid = sum(item["state"] == "invalid" for item in audited)
    unsealed = sum(item["state"] == "unsealed" for item in audited)
    return {
        "state": "invalid" if invalid else "valid",
        "receipt_count": len(audited),
        "verified_count": len(audited) - invalid - unsealed,
        "unsealed_count": unsealed,
        "invalid_count": invalid,
    }


def render_markdown_report(
    receipts: Iterable[dict[str, Any]],
    *,
    current: GitState,
    max_age_hours: float,
    now: datetime | None = None,
) -> str:
    """Render current proof and chain state as deterministic Markdown."""
    receipt_list = list(receipts)
    now = now or datetime.now(timezone.utc)
    assessed = assess_receipts(
        receipt_list,
        current=current,
        max_age_hours=max_age_hours,
        now=now,
    )
    audit = _audit_summary(audit_receipts(receipt_list))
    valid_checks = sum(item["state"] == "valid" for item in assessed)

    lines = [
        "# ProofRun verification report",
        "",
        f"- Reported at: {_inline_code(now.isoformat())}",
        f"- Repository commit: {_display(current.head, 'unborn or unavailable')}",
        f"- Repository branch: {_display(current.branch)}",
        f"- Working tree: {'dirty' if current.dirty else 'clean'}",
        f"- Evidence policy: maximum age {max_age_hours:g} hours"
        if max_age_hours > 0
        else "- Evidence policy: age limit disabled",
        "",
        "## Summary",
        "",
        f"- Checks: {valid_checks}/{len(assessed)} currently valid",
        f"- Receipt chain: {str(audit['state']).upper()}",
        f"- Receipts: {audit['receipt_count']} total, "
        f"{audit['verified_count']} verified, {audit['unsealed_count']} legacy unsealed, "
        f"{audit['invalid_count']} invalid",
    ]

    if not assessed:
        lines.extend(["", "No verification receipts yet."])
        return "\n".join(lines) + "\n"

    lines.extend(["", "## Checks"])
    for item in assessed:
        receipt = item["receipt"]
        recorded_git = receipt.get("git", {})
        command = receipt.get("command", [])
        if isinstance(command, list) and all(isinstance(part, str) for part in command):
            command_text = shlex.join(command)
        else:
            command_text = "unknown"
        exit_code = receipt.get("exit_code")
        result = "passed" if exit_code == 0 else f"failed (exit {exit_code})"
        reasons = item.get("reasons", [])
        evidence = ", ".join(str(reason) for reason in reasons) or "evidence applies"
        paths = item.get("working_tree_paths", {})
        tracked = paths.get("tracked", []) if isinstance(paths, dict) else []
        untracked = paths.get("untracked", []) if isinstance(paths, dict) else []

        lines.extend(
            [
                "",
                f"### {_inline_code(item['name'])}",
                "",
                f"- Status: **{str(item['state']).upper()}** — {evidence}",
                f"- Result: {result}",
                f"- Checked at: {_display(receipt.get('started_at'))}",
                f"- Age: {item['age_hours']:g} hours",
                f"- Duration: {receipt.get('duration_ms', 'unknown')} ms",
                f"- Command: {_inline_code(command_text)}",
                f"- Receipt: {_display(receipt.get('id'))}",
                f"- Covered commit: {_display(recorded_git.get('head'))}",
            ]
        )
        if tracked:
            lines.append(
                "- Invalidating tracked paths: "
                + ", ".join(_inline_code(path) for path in tracked)
            )
        if untracked:
            lines.append(
                "- Invalidating untracked paths: "
                + ", ".join(_inline_code(path) for path in untracked)
            )

    return "\n".join(lines) + "\n"
