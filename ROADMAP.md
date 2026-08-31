# Roadmap

The roadmap favors safer adoption and clearer evidence over broad orchestration.

## 0.2 - Portable adoption

- Provide a unified command for initialization, validation, and diagnostics. (implemented)
- Generate thin Codex, Cursor, Claude Code, and GitHub Copilot adapters from one canonical policy. (implemented)
- Build standalone Windows, Linux, and macOS release assets. (automation implemented; first tagged release pending)
- Add a complete provider/consumer example with expected generated output. (implemented)
- Add continuous integration for tests and public-content scanning.
- Validate the manifest against the published JSON Schema.
- Improve diagnostics with stable error codes and remediation hints.

## 0.3 - Ecosystem integration

- Add adapters for Gemini CLI and other tools with stable repository instruction formats.
- Add optional issue and pull-request writeback adapters behind explicit confirmation.
- Add contract hash and snapshot-drift reporting without duplicating provider truth.
- Add migration guidance for existing multi-repository workspaces.
- Add optional, provider-neutral code-intelligence evidence adapters without granting write authority.

## Non-goals

- executing arbitrary commands across every registered repository;
- deploying or merging without explicit human authorization;
- replacing repository-local tests, ownership, or review;
- storing credentials or private operational data in the control repository.

Suggestions and focused pull requests are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).
