#!/usr/bin/env python3
"""Shared validation and rendering helpers for the cross-repo harness."""

from __future__ import annotations

import json
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any


ALLOWED_ROLES = {"control", "provider", "consumer", "participant", "shared"}
HARNESS_VERSION = "0.2.0"
SUPPORTED_AGENT_TOOLS = ("codex", "cursor", "claude", "copilot")
LEGACY_AGENT_TOOLS = ("codex", "cursor")
AGENT_TOOL_CONFIG_PATHS = {
    "cursor": Path(".cursor/rules/harness-control.mdc"),
    "claude": Path("CLAUDE.md"),
    "copilot": Path(".github/copilot-instructions.md"),
}
ID_PATTERN = re.compile(r"^[a-z][a-z0-9-]{0,62}$")
PRODUCT_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._ -]{0,79}$")


class HarnessError(ValueError):
    """Raised when a manifest or generated harness violates the contract."""


@dataclass(frozen=True)
class Repository:
    repo_id: str
    path: str
    role: str
    duty: str
    contracts: tuple[str, ...]
    verify: str


@dataclass(frozen=True)
class Manifest:
    version: int
    product: str
    repositories: tuple[Repository, ...]
    agent_tools: tuple[str, ...]

    @property
    def control(self) -> Repository:
        return next(repo for repo in self.repositories if repo.role == "control")


def _require_scalar(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise HarnessError(f"{field} must be a non-empty string")
    text = value.strip()
    if "\n" in text or "\r" in text:
        raise HarnessError(f"{field} must be a single line")
    return text


def _normalise_repo_path(value: Any, field: str) -> str:
    raw = _require_scalar(value, field).replace("\\", "/")
    path = PurePosixPath(raw)
    if path.is_absolute() or re.match(r"^[A-Za-z]:", raw):
        raise HarnessError(f"{field} must be relative to the control repository")
    if raw != "." and not raw.startswith("../"):
        raise HarnessError(
            f"{field} must be '.' or a sibling path beginning with '../'"
        )
    normalised = path.as_posix()
    if normalised in {"..", "../"}:
        raise HarnessError(f"{field} must name a repository, not only its parent")
    if raw != "." and (not path.parts or path.parts[0] != ".." or ".." in path.parts[1:]):
        raise HarnessError(f"{field} may traverse only to the direct parent directory")
    return normalised


def load_manifest(path: Path) -> Manifest:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise HarnessError(f"manifest not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise HarnessError(f"manifest must be valid JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise HarnessError("manifest root must be an object")
    if data.get("version") != 1:
        raise HarnessError("manifest version must be 1")

    product = _require_scalar(data.get("product"), "product")
    if not PRODUCT_PATTERN.fullmatch(product):
        raise HarnessError("product contains unsupported characters or is too long")

    agent_tools = normalise_agent_tools(
        data.get("agent_tools", list(SUPPORTED_AGENT_TOOLS)), field="agent_tools"
    )

    raw_repositories = data.get("repositories")
    if not isinstance(raw_repositories, list) or len(raw_repositories) < 2:
        raise HarnessError("repositories must contain control and at least one participant")

    repositories: list[Repository] = []
    seen_ids: set[str] = set()
    seen_paths: set[str] = set()
    for index, item in enumerate(raw_repositories):
        prefix = f"repositories[{index}]"
        if not isinstance(item, dict):
            raise HarnessError(f"{prefix} must be an object")
        repo_id = _require_scalar(item.get("id"), f"{prefix}.id")
        if not ID_PATTERN.fullmatch(repo_id):
            raise HarnessError(f"{prefix}.id must use lowercase kebab-case")
        if repo_id in seen_ids:
            raise HarnessError(f"duplicate repository id: {repo_id}")

        path_value = _normalise_repo_path(item.get("path"), f"{prefix}.path")
        if path_value in seen_paths:
            raise HarnessError(f"duplicate repository path: {path_value}")

        role = _require_scalar(item.get("role"), f"{prefix}.role")
        if role not in ALLOWED_ROLES:
            raise HarnessError(
                f"{prefix}.role must be one of {', '.join(sorted(ALLOWED_ROLES))}"
            )
        duty = _require_scalar(item.get("duty"), f"{prefix}.duty")
        verify = _require_scalar(item.get("verify", "none"), f"{prefix}.verify")

        raw_contracts = item.get("contracts", [])
        if not isinstance(raw_contracts, list) or not all(
            isinstance(contract, str) and contract.strip() for contract in raw_contracts
        ):
            raise HarnessError(f"{prefix}.contracts must be an array of strings")
        contracts = tuple(contract.strip() for contract in raw_contracts)

        repositories.append(
            Repository(repo_id, path_value, role, duty, contracts, verify)
        )
        seen_ids.add(repo_id)
        seen_paths.add(path_value)

    controls = [repo for repo in repositories if repo.role == "control"]
    if len(controls) != 1:
        raise HarnessError("exactly one repository must have role 'control'")
    if controls[0].path != ".":
        raise HarnessError("the control repository path must be '.'")
    if any(repo.path == "." and repo.role != "control" for repo in repositories):
        raise HarnessError("only the control repository may use path '.'")

    return Manifest(1, product, tuple(repositories), agent_tools)


def normalise_agent_tools(value: Any, *, field: str = "agent_tools") -> tuple[str, ...]:
    if isinstance(value, str):
        raw_tools = [item.strip() for item in value.split(",") if item.strip()]
    elif isinstance(value, list) and all(isinstance(item, str) for item in value):
        raw_tools = [item.strip() for item in value if item.strip()]
    else:
        raise HarnessError(f"{field} must be a comma-separated string or array of strings")

    if len(raw_tools) != len(set(raw_tools)):
        raise HarnessError(f"{field} must not contain duplicate tools")
    unknown = sorted(set(raw_tools) - set(SUPPORTED_AGENT_TOOLS))
    if unknown:
        raise HarnessError(
            f"{field} contains unsupported tools: {', '.join(unknown)}; "
            f"supported: {', '.join(SUPPORTED_AGENT_TOOLS)}"
        )
    if not raw_tools:
        raise HarnessError(f"{field} must select at least one agent tool")
    selected = set(raw_tools)
    return tuple(tool for tool in SUPPORTED_AGENT_TOOLS if tool in selected)


def detect_agent_tools(target: Path) -> tuple[str, ...]:
    """Detect existing project conventions, defaulting to the portable full set."""
    target = target.resolve()
    detected: set[str] = set()
    if (target / ".codex").exists() or (target / "AGENTS.md").is_file():
        detected.add("codex")
    if (target / ".cursor").exists():
        detected.add("cursor")
    if (target / "CLAUDE.md").is_file() or (target / ".claude").exists():
        detected.add("claude")
    if (target / ".github/copilot-instructions.md").is_file():
        detected.add("copilot")
    if not detected:
        return SUPPORTED_AGENT_TOOLS
    return tuple(tool for tool in SUPPORTED_AGENT_TOOLS if tool in detected)


def installed_agent_commands() -> dict[str, str | None]:
    """Return optional local CLI evidence; IDE-only tools may legitimately be absent."""
    candidates = {
        "codex": ("codex",),
        "cursor": ("cursor-agent", "cursor"),
        "claude": ("claude",),
        "copilot": ("copilot",),
    }
    return {
        tool: next((path for command in commands if (path := shutil.which(command))), None)
        for tool, commands in candidates.items()
    }


def manifest_payload(manifest: Manifest) -> dict[str, Any]:
    return {
        "version": manifest.version,
        "product": manifest.product,
        "agent_tools": list(manifest.agent_tools),
        "repositories": {
            repo.repo_id: {
                "path": repo.path,
                "role": repo.role,
                "duty": repo.duty,
                "contracts": list(repo.contracts),
                "verify": repo.verify,
            }
            for repo in manifest.repositories
        },
    }


def _md_cell(value: str) -> str:
    return value.replace("|", "\\|")


def render_inventory(manifest: Manifest) -> str:
    rows = []
    for repo in manifest.repositories:
        contracts = ", ".join(repo.contracts) if repo.contracts else "none"
        rows.append(
            "| {id} | `{path}` | {role} | {duty} | {contracts} | `{verify}` | active |".format(
                id=_md_cell(repo.repo_id),
                path=_md_cell(repo.path),
                role=_md_cell(repo.role),
                duty=_md_cell(repo.duty),
                contracts=_md_cell(contracts),
                verify=_md_cell(repo.verify),
            )
        )
    return f"""# Repository Inventory

This file is the human-readable repository responsibility map for **{manifest.product}**.
Repositories not listed here are outside the Harness write boundary.

| id | path | role | duty | contracts | verification | status |
| --- | --- | --- | --- | --- | --- | --- |
{chr(10).join(rows)}

## Change Log

| date | action | repository | reason | ExecPlan |
| --- | --- | --- | --- | --- |
| YYYY-MM-DD | init | all | Initial confirmed registration | `.agents/plans/YYYY-MM-DD/register-initial.md` |
"""


def render_agents(manifest: Manifest) -> str:
    boundary_rows = "\n".join(
        f"| {repo.repo_id} | `{repo.path}` | {repo.role} | {_md_cell(repo.duty)} |"
        for repo in manifest.repositories
    )
    ids = ", ".join(f"`{repo.repo_id}`" for repo in manifest.repositories)
    return f"""# {manifest.product} Cross-Repository Harness

## Purpose

This repository is the control plane for coordinated work across multiple repositories.
It owns plans, explicit write authorisation, contract references, joint verification, and result writeback. It must not become a third copy of business code or provider contracts.

## Repository Boundary

| id | path | role | responsibility |
| --- | --- | --- | --- |
{boundary_rows}

The registered repository ids are: {ids}. The machine-readable inventory is `repos.yaml`; the review-friendly inventory is `docs/harness/inventory.md`.

## Mandatory Workflow

`collect -> gate -> freeze -> slice -> implement -> verify-<repo-id> -> verify-integration -> review -> writeback -> notify`

1. Read `repos.yaml`, `docs/harness/inventory.md`, `.agents/PLANS.md`, and the nearest `AGENTS.md` in every repository being inspected.
2. Default to modifying only this control repository.
3. Before modifying any non-control repository, create an ExecPlan from `.agents/plans/TEMPLATE-cross-repo.md`.
4. List every registered repository in the plan. Use `none` for repositories that are not authorised for writes.
5. Freeze provider truth, consumer snapshots, validation commands, rollback units, and stop conditions before implementation.
6. Modify only paths explicitly authorised by the current plan.
7. Verify and commit each repository independently. Never mix repositories in one rollback unit.
8. Record commit ids, contract versions or hashes, verification results, residual risks, recovery point, and next action.

## Truth Ownership

- Issue tracker: collaboration status, blockers, follow-ups, recovery point, and next action.
- Each implementation repository: executable code, local rules, tests, and owned contracts.
- Pull request: code-change narrative and review discussion.
- This control repository: references and outcomes, not copied contract truth.

Provider repositories own contract truth. Consumer repositories may store generated snapshots, mocks, caches, and golden files, but may not redefine provider truth.

## Safety

- Never commit credentials, cookies, connection strings, private user data, internal-only endpoints, or raw operational logs.
- Never write to an unregistered sibling repository.
- Never treat Harness checks as a substitute for repository tests, contract tests, integration tests, or review.
- Publishing, deployment, permission changes, destructive operations, and other external side effects require separate user confirmation.
"""


def render_workspace(manifest: Manifest) -> str:
    folders = [
        {"path": repo.path, "name": repo.repo_id} for repo in manifest.repositories
    ]
    return json.dumps(
        {
            "folders": folders,
            "settings": {
                "git.autoRepositoryDetection": False,
                "scm.alwaysShowRepositories": True,
            },
        },
        indent=2,
        ensure_ascii=False,
    ) + "\n"


def render_control_readme(manifest: Manifest) -> str:
    participants = "\n".join(
        f"- `{repo.path}` (`{repo.repo_id}`, {repo.role}): {repo.duty}"
        for repo in manifest.repositories
        if repo.role != "control"
    )
    workspace_name = f"{slugify(manifest.product)}.code-workspace"
    tools = ", ".join(manifest.agent_tools)
    return f"""# {manifest.product} Cross-Repository Harness

This control repository coordinates registered sibling repositories without duplicating their implementation or contract truth.

Configured coding-agent adapters: **{tools}**. `AGENTS.md` is the canonical instruction source; tool-specific files only point agents back to it.

## Registered repositories

{participants}

## Start here

1. Open `{workspace_name}` in your coding agent, or open this control repository as the project root.
2. Read `AGENTS.md`, `repos.yaml`, `docs/harness/inventory.md`, and `.agents/PLANS.md`.
3. For a cross-repository change, create an ExecPlan from `.agents/plans/TEMPLATE-cross-repo.md`.
4. Run `python scripts/check_harness.py --root .` and `python scripts/doctor_harness.py --root .` from this generated control repository.

The Harness never grants itself permission to publish, deploy, change access, delete data, or write outside an approved ExecPlan.
"""


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "cross-repo-harness"


def template_files(template_root: Path) -> dict[Path, str]:
    files: dict[Path, str] = {}
    for source in sorted(template_root.rglob("*")):
        if source.is_file():
            files[source.relative_to(template_root)] = source.read_text(encoding="utf-8")
    return files


def generated_files(manifest: Manifest, template_root: Path) -> dict[Path, str]:
    files = template_files(template_root)
    for tool, relative in AGENT_TOOL_CONFIG_PATHS.items():
        if tool not in manifest.agent_tools:
            files.pop(relative, None)
    project_root = resource_root()
    for script_name in ("check_harness.py", "doctor_harness.py", "harness_lib.py"):
        source = project_root / "scripts" / script_name
        files[Path("scripts") / script_name] = source.read_text(encoding="utf-8")
    files[Path("repos.yaml")] = json.dumps(
        manifest_payload(manifest), indent=2, ensure_ascii=False
    ) + "\n"
    files[Path("AGENTS.md")] = render_agents(manifest)
    files[Path("README.md")] = render_control_readme(manifest)
    files[Path("docs/harness/inventory.md")] = render_inventory(manifest)
    files[Path(f"{slugify(manifest.product)}.code-workspace")] = render_workspace(manifest)
    return files


def resource_root() -> Path:
    """Locate bundled templates in source checkouts and frozen executables."""
    frozen_root = getattr(sys, "_MEIPASS", None)
    if frozen_root:
        return Path(frozen_root)
    return Path(__file__).resolve().parent.parent


def is_dangerous_target(path: Path) -> bool:
    resolved = path.resolve()
    if resolved == Path(resolved.anchor):
        return True
    try:
        if resolved == Path.home().resolve():
            return True
    except RuntimeError:
        pass
    return False
