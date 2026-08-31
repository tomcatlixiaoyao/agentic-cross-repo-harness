#!/usr/bin/env python3
"""Initialise a safe, provider-neutral cross-repository control plane."""

from __future__ import annotations

import argparse
import sys
from dataclasses import replace
from pathlib import Path

from harness_lib import (
    HarnessError,
    SUPPORTED_AGENT_TOOLS,
    detect_agent_tools,
    generated_files,
    is_dangerous_target,
    load_manifest,
    normalise_agent_tools,
    resource_root,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument(
        "--force",
        action="store_true",
        help="replace only files managed by this initializer",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="show actions without writing files"
    )
    parser.add_argument(
        "--tools",
        help=(
            "comma-separated coding-agent adapters, or 'auto'; supported: "
            + ", ".join(SUPPORTED_AGENT_TOOLS)
        ),
    )
    return parser.parse_args(argv)


def initialise(
    manifest_path: Path,
    target: Path,
    *,
    force: bool = False,
    dry_run: bool = False,
    tools: str | None = None,
) -> list[Path]:
    manifest = load_manifest(manifest_path)
    target = target.resolve()
    if is_dangerous_target(target):
        raise HarnessError(f"refusing dangerous target: {target}")
    if tools == "auto":
        manifest = replace(manifest, agent_tools=detect_agent_tools(target))
    elif tools is not None:
        manifest = replace(
            manifest, agent_tools=normalise_agent_tools(tools, field="--tools")
        )

    template_root = resource_root() / "templates" / "control"
    files = generated_files(manifest, template_root)
    conflicts = [relative for relative in files if (target / relative).exists()]
    if conflicts and not force:
        rendered = ", ".join(str(path) for path in conflicts[:8])
        suffix = "..." if len(conflicts) > 8 else ""
        raise HarnessError(
            f"managed files already exist ({rendered}{suffix}); rerun with --force"
        )

    written: list[Path] = []
    for relative, content in files.items():
        destination = target / relative
        written.append(destination)
        if dry_run:
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_name(destination.name + ".tmp")
        temporary.write_text(content, encoding="utf-8", newline="\n")
        temporary.replace(destination)
    return written


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        files = initialise(
            args.manifest,
            args.target,
            force=args.force,
            dry_run=args.dry_run,
            tools=args.tools,
        )
    except HarnessError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    verb = "would write" if args.dry_run else "wrote"
    print(f"{verb} {len(files)} managed files")
    for path in files:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
