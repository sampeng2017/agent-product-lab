from __future__ import annotations

from typing import Any


DEFAULT_PATH_LIMIT = 10


def limited_working_tree_paths(
    raw_paths: Any,
    limit: int,
) -> tuple[dict[str, list[str]], int]:
    """Return a stable display subset and the number of paths omitted."""
    paths = {"tracked": [], "untracked": []}
    if isinstance(raw_paths, dict):
        for kind in paths:
            values = raw_paths.get(kind)
            if isinstance(values, list):
                paths[kind] = [value for value in values if isinstance(value, str)]

    remaining = max(limit, 0)
    shown: dict[str, list[str]] = {"tracked": [], "untracked": []}
    for kind in ("tracked", "untracked"):
        shown[kind] = paths[kind][:remaining]
        remaining -= len(shown[kind])

    total = sum(len(values) for values in paths.values())
    displayed = sum(len(values) for values in shown.values())
    return shown, total - displayed
