#!/usr/bin/env python3
"""Validate a generated cross-repository Harness without modifying siblings."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path, PurePosixPath
from typing import Any

from harness_lib import ALLOWED_ROLES, HarnessError, ID_PATTERN


REQUIRED_FILES = (
    "AGENTS.md",
    "README.md",
    "repos.yaml",
    ".agents/PLANS.md",
    ".agents/plans/TEMPLATE-cross-repo.md",
    ".agents/plans/TEMPLATE-register-repo.md",
    "contracts/INDEX.md",
    "docs/harness/inventory.md",
    "docs/harness/verification.md",
    "docs/harness/PARTICIPANT_AGENTS_TEMPLATE.md",
    "scripts/check_harness.py",
    "scripts/harness_lib.py",
)

PLAN_HEADINGS = (
    "## Goal",
    "## Included / Excluded",
    "## Repository Write Scope",
    "## Contract Freeze",
    "## Concrete Steps",
    "## Validation Matrix",
    "## Rollback Unit / Stop Conditions",
    "## Progress",
    "## Decision Log",
    "## Surprises & Discoveries",
    "## Review / Writeback / Outcomes",
    "## Recovery Point / Next Action",
)


def _load_repos(root: Path) -> dict[str, Any]:
    path = root / "repos.yaml"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise HarnessError("repos.yaml is missing") from exc
    except json.JSONDecodeError as exc:
        raise HarnessError(
            "repos.yaml must use the documented JSON-compatible YAML subset: "
            f"{exc}"
        ) from exc
    if not isinstance(data, dict) or data.get("version") != 1:
        raise HarnessError("repos.yaml version must be 1")
    repositories = data.get("repositories")
    if not isinstance(repositories, dict) or len(repositories) < 2:
        raise HarnessError("repos.yaml must register control and at least one participant")
    return data


def validate(root: Path, *, verify_paths: bool = False) -> list[str]:
    root = root.resolve()
    findings: list[str] = []
    for relative in REQUIRED_FILES:
        if not (root / relative).is_file():
            findings.append(f"missing required file: {relative}")

    try:
        data = _load_repos(root)
    except HarnessError as exc:
        findings.append(str(exc))
        return findings

    repositories = data["repositories"]
    controls: list[str] = []
    seen_paths: set[str] = set()
    for repo_id, item in repositories.items():
        if not isinstance(repo_id, str) or not ID_PATTERN.fullmatch(repo_id):
            findings.append(f"invalid repository id: {repo_id!r}")
            continue
        if not isinstance(item, dict):
            findings.append(f"repository {repo_id} must be an object")
            continue
        path = item.get("path")
        role = item.get("role")
        if not isinstance(path, str) or not path:
            findings.append(f"repository {repo_id} has no path")
            continue
        normalised = PurePosixPath(path.replace("\\", "/")).as_posix()
        normalised_path = PurePosixPath(normalised)
        if normalised_path.is_absolute() or (
            normalised != "." and not normalised.startswith("../")
        ):
            findings.append(f"repository {repo_id} path is outside sibling policy: {path}")
        elif normalised != "." and (
            not normalised_path.parts
            or normalised_path.parts[0] != ".."
            or ".." in normalised_path.parts[1:]
        ):
            findings.append(
                f"repository {repo_id} path traverses beyond the direct parent: {path}"
            )
        if normalised in seen_paths:
            findings.append(f"duplicate repository path: {normalised}")
        seen_paths.add(normalised)
        if role not in ALLOWED_ROLES:
            findings.append(f"repository {repo_id} has invalid role: {role}")
        if role == "control":
            controls.append(repo_id)
            if normalised != ".":
                findings.append(f"control repository {repo_id} path must be '.'")
        elif normalised == ".":
            findings.append(f"non-control repository {repo_id} cannot use path '.'")
        if not isinstance(item.get("duty"), str) or not item["duty"].strip():
            findings.append(f"repository {repo_id} has no duty")
        if not isinstance(item.get("verify"), str) or not item["verify"].strip():
            findings.append(f"repository {repo_id} has no verification command")

        if verify_paths and normalised != ".":
            resolved = (root / normalised).resolve()
            if not resolved.is_dir():
                findings.append(f"registered sibling does not exist: {repo_id} -> {resolved}")

    if len(controls) != 1:
        findings.append("exactly one control repository is required")

    inventory = _safe_read(root / "docs/harness/inventory.md")
    agents = _safe_read(root / "AGENTS.md")
    for repo_id, item in repositories.items():
        path = item.get("path") if isinstance(item, dict) else None
        if repo_id not in inventory:
            findings.append(f"inventory does not mention repository id: {repo_id}")
        if repo_id not in agents:
            findings.append(f"AGENTS.md does not mention repository id: {repo_id}")
        if isinstance(path, str) and f"`{path}`" not in inventory:
            findings.append(f"inventory does not mention path for {repo_id}: {path}")

    plan_template = _safe_read(root / ".agents/plans/TEMPLATE-cross-repo.md")
    for heading in PLAN_HEADINGS:
        if heading not in plan_template:
            findings.append(f"plan template missing heading: {heading}")
    if "none" not in plan_template.lower():
        findings.append("plan template must require 'none' for repositories without writes")

    workspace_files = sorted(root.glob("*.code-workspace"))
    if len(workspace_files) != 1:
        findings.append("exactly one *.code-workspace file is required")
    else:
        try:
            workspace = json.loads(workspace_files[0].read_text(encoding="utf-8"))
            folders = workspace.get("folders", [])
            workspace_pairs = {
                (folder.get("name"), folder.get("path"))
                for folder in folders
                if isinstance(folder, dict)
            }
            expected_pairs = {
                (repo_id, item.get("path"))
                for repo_id, item in repositories.items()
                if isinstance(item, dict)
            }
            if workspace_pairs != expected_pairs:
                findings.append("workspace folders do not match repos.yaml")
        except (json.JSONDecodeError, OSError) as exc:
            findings.append(f"invalid workspace file: {exc}")

    return findings


def _safe_read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--verify-paths",
        action="store_true",
        help="also require every registered sibling directory to exist",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    findings = validate(args.root, verify_paths=args.verify_paths)
    if findings:
        print("Harness validation failed:")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print("Harness validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
