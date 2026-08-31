# Roadmap

The roadmap favors safer adoption and clearer evidence over broad orchestration.

## 0.2 - Easier adoption

- Package a single command for initialization and validation.
- Add a complete provider/consumer example with expected generated output.
- Add continuous integration for tests and public-content scanning.
- Validate the manifest against the published JSON Schema.
- Improve diagnostics with stable error codes and remediation hints.

## 0.3 - Ecosystem integration

- Document integration patterns for multiple coding-agent products.
- Add optional issue and pull-request writeback adapters behind explicit confirmation.
- Add contract hash and snapshot-drift reporting without duplicating provider truth.
- Add migration guidance for existing multi-repository workspaces.

## Non-goals

- executing arbitrary commands across every registered repository;
- deploying or merging without explicit human authorization;
- replacing repository-local tests, ownership, or review;
- storing credentials or private operational data in the control repository.

Suggestions and focused pull requests are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).
