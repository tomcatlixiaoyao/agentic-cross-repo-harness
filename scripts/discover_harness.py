#!/usr/bin/env python3
"""Discover sibling Git repositories and render a reviewable manifest draft."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable

from harness_lib import (
    ID_PATTERN,
    PRODUCT_PATTERN,
    SUPPORTED_AGENT_TOOLS,
    HarnessError,
    normalise_agent_tools,
    slugify,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        required=True,
        help="direct parent containing participant repositories",
    )
    parser.add_argument("--product", required=True, help="product or workspace name")
    parser.add_argument(
        "--control-id",
        default="harness",
        help="repository id for the future control repository",
    )
    parser.add_argument(
        "--tools",
        default=",".join(SUPPORTED_AGENT_TOOLS),
        help="comma-separated coding-agent adapters",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="direct child name to exclude; may be repeated",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="write the draft to this file instead of standard output",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="replace an existing --output file",
    )
    return parser.parse_args(argv)


def _is_git_repository(path: Path) -> bool:
    marker = path / ".git"
    return marker.is_dir() or marker.is_file()


def _package_verification(path: Path) -> str | None:
    package_json = path / "package.json"
    if not package_json.is_file():
        return None
    try:
        if package_json.is_symlink() or package_json.stat().st_size > 1024 * 1024:
            return "none"
        package = json.loads(package_json.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeError):
        return "none"
    scripts = package.get("scripts", {})
    if not isinstance(scripts, dict):
        return "none"
    test_script = scripts.get("test")
    has_test = (
        isinstance(test_script, str)
        and bool(test_script.strip())
        and "no test specified" not in test_script.casefold()
    )
    has_build = isinstance(scripts.get("build"), str) and bool(scripts["build"].strip())
    if has_test and has_build:
        return "npm test && npm run build"
    if has_test:
        return "npm test"
    if has_build:
        return "npm run build"
    return "none"


def infer_verification(path: Path) -> str:
    """Return a conservative command suggestion without executing any command."""
    if (path / "pom.xml").is_file():
        if (path / "mvnw").is_file():
            return "./mvnw test"
        if (path / "mvnw.cmd").is_file():
            return "mvnw.cmd test"
        return "mvn test"
    if (path / "build.gradle").is_file() or (path / "build.gradle.kts").is_file():
        if (path / "gradlew").is_file():
            return "./gradlew test"
        if (path / "gradlew.bat").is_file():
            return "gradlew.bat test"
        return "gradle test"
    package_command = _package_verification(path)
    if package_command is not None:
        return package_command
    if (path / "go.mod").is_file():
        return "go test ./..."
    if (path / "Cargo.toml").is_file():
        return "cargo test"
    return "none"


def _unique_repo_id(name: str, used: set[str]) -> str:
    candidate = slugify(name)
    if not candidate[0].isalpha():
        candidate = f"repo-{candidate}"
    candidate = candidate[:63].rstrip("-")
    base = candidate
    suffix = 2
    while candidate in used:
        marker = f"-{suffix}"
        candidate = f"{base[: 63 - len(marker)].rstrip('-')}{marker}"
        suffix += 1
    return candidate


def discover(
    root: Path,
    product: str,
    *,
    control_id: str = "harness",
    tools: str | Iterable[str] = SUPPORTED_AGENT_TOOLS,
    exclude: Iterable[str] = (),
) -> dict:
    root = root.resolve()
    if not root.is_dir():
        raise HarnessError(f"workspace root is not a directory: {root}")
    product = product.strip()
    if not PRODUCT_PATTERN.fullmatch(product):
        raise HarnessError("product contains unsupported characters or is too long")
    control_id = control_id.strip()
    if not ID_PATTERN.fullmatch(control_id):
        raise HarnessError("control id must use lowercase kebab-case")

    tool_value = tools if isinstance(tools, str) else list(tools)
    agent_tools = normalise_agent_tools(tool_value, field="--tools")
    excluded = {item.casefold() for item in exclude}
    candidates = sorted(
        (
            child
            for child in root.iterdir()
            if child.is_dir()
            and not child.is_symlink()
            and child.name.casefold() not in excluded
            and _is_git_repository(child)
        ),
        key=lambda child: (child.name.casefold(), child.name),
    )
    if not candidates:
        raise HarnessError(f"no direct child Git repositories found beneath: {root}")

    used_ids = {control_id}
    repositories = [
        {
            "id": control_id,
            "path": ".",
            "role": "control",
            "duty": "Coordinate plans, write boundaries, and verification evidence",
            "contracts": [],
            "verify": "python scripts/check_harness.py --root .",
        }
    ]
    for candidate in candidates:
        if "\n" in candidate.name or "\r" in candidate.name:
            raise HarnessError("repository directory names must be single-line values")
        repo_id = _unique_repo_id(candidate.name, used_ids)
        used_ids.add(repo_id)
        repositories.append(
            {
                "id": repo_id,
                "path": f"../{candidate.name}",
                "role": "participant",
                "duty": f"TODO: describe the responsibility of {candidate.name}",
                "contracts": [],
                "verify": infer_verification(candidate),
            }
        )

    return {
        "version": 1,
        "product": product,
        "agent_tools": list(agent_tools),
        "repositories": repositories,
    }


def write_manifest(payload: dict, output: Path, *, force: bool = False) -> Path:
    output = output.resolve()
    if output.exists() and not force:
        raise HarnessError(f"output already exists: {output}; rerun with --force")
    if output.exists() and output.is_dir():
        raise HarnessError(f"output must be a file: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(output.name + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    temporary.replace(output)
    return output


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        payload = discover(
            args.root,
            args.product,
            control_id=args.control_id,
            tools=args.tools,
            exclude=args.exclude,
        )
        rendered = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
        if args.output is None:
            print(rendered, end="")
        else:
            destination = write_manifest(payload, args.output, force=args.force)
            print(f"wrote manifest draft: {destination}")
    except (HarnessError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
