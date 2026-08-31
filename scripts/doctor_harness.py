#!/usr/bin/env python3
"""Explain Harness readiness without executing participant verification commands."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from check_harness import validate
from harness_lib import (
    AGENT_TOOL_CONFIG_PATHS,
    HarnessError,
    LEGACY_AGENT_TOOLS,
    installed_agent_commands,
    normalise_agent_tools,
)


def diagnose(root: Path) -> tuple[list[str], list[str]]:
    root = root.resolve()
    failures = validate(root)
    notes: list[str] = []
    try:
        payload = json.loads((root / "repos.yaml").read_text(encoding="utf-8"))
        tools = normalise_agent_tools(
            payload.get("agent_tools", list(LEGACY_AGENT_TOOLS)),
            field="repos.yaml agent_tools",
        )
    except (OSError, json.JSONDecodeError, HarnessError):
        return failures, notes

    commands = installed_agent_commands()
    notes.append("AGENTS.md is the canonical, provider-neutral instruction source")
    for tool in tools:
        adapter = AGENT_TOOL_CONFIG_PATHS.get(tool, Path("AGENTS.md"))
        state = "ready" if (root / adapter).is_file() else "missing"
        cli = commands.get(tool)
        cli_note = f"CLI detected at {cli}" if cli else "CLI not detected (IDE use is still valid)"
        notes.append(f"{tool}: {state} via {adapter.as_posix()}; {cli_note}")

    for tool, adapter in AGENT_TOOL_CONFIG_PATHS.items():
        if tool not in tools and (root / adapter).is_file():
            notes.append(
                f"{tool}: adapter exists but is not configured; it was not deleted automatically"
            )

    repositories = payload.get("repositories", {})
    if isinstance(repositories, dict):
        for repo_id, item in repositories.items():
            if isinstance(item, dict):
                notes.append(
                    f"{repo_id}: verification is an opaque language-neutral command: "
                    f"{item.get('verify', 'none')}"
                )
    return failures, notes


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    failures, notes = diagnose(args.root)
    print("Harness doctor")
    for note in notes:
        print(f"[info] {note}")
    if failures:
        for failure in failures:
            print(f"[fail] {failure}")
        return 1
    print("[ok] structural checks passed; no participant commands were executed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
