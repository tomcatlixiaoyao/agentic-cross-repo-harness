# Changelog

All notable project changes are recorded here.

## Unreleased

- Upgraded GitHub Actions dependencies to their Node.js 24 runtime versions.
- Added direct release-download guidance and checksum verification instructions.
- Added GitHub issue and pull-request templates for public-safe contributions.
- Added manifest-schema contract tests and standalone executable smoke tests.
- Updated roadmap status to match the published v0.2.0 release and CI implementation.

## 0.2.0 - 2026-08-31

- Added one canonical `AGENTS.md` policy with generated Cursor, Claude Code, and GitHub Copilot adapters.
- Added manifest and CLI selection for `codex`, `cursor`, `claude`, and `copilot`, including automatic detection.
- Added a unified `harness` command surface with `init`, `check`, and read-only `doctor` commands.
- Added PyInstaller and GitHub Actions configuration for standalone Windows, Linux, and macOS release assets.
- Documented language-neutral verification and coding-agent compatibility.
- Clarified the project outcome and intended audience in the README.
- Added a complete three-minute example and generated-tree preview.
- Added Simplified Chinese documentation entry points.
- Expanded the quick start for fresh clones and Windows PowerShell.
- Added a public roadmap.
- Added a tested Java API provider and web consumer walkthrough with an illustrative ExecPlan and expected generated output.
- Added provider-neutral guidance for using Codebase Memory as an optional local analysis layer without expanding Harness authority.

## 0.1.0 - 2026-08-31

- Added deterministic control-repository generation from a JSON-compatible YAML manifest.
- Added structural validation and optional sibling-path checks.
- Added ExecPlan, repository-registration, contract-index, and participant-guidance templates.
- Added public-content scanning for common private-data indicators.
- Added tests for manifest rules, safe initialization, path boundaries, registry drift, and content scanning.
