# Security Model

## Protected assets

- source code and history in every registered repository;
- provider-owned API schemas and other contract truth;
- credentials, tokens, cookies, connection strings, and private endpoints;
- user, customer, employee, and production data;
- release, deployment, permission, and destructive-operation authority.

## Trust boundaries

The control repository coordinates work but does not own participant implementation. A registry entry describes a repository; it is not permission to modify every path in that repository.

An ExecPlan narrows write authority to a specific task, repository, and path set. It does not authorise publishing, deployment, permissions changes, deletion, purchases, messages, or external data mutation.

## Initializer guarantees

- writes only under the resolved `--target` directory;
- rejects filesystem roots and the current user's home directory as targets;
- rejects absolute participant paths;
- refuses existing managed files unless `--force` is explicit;
- uses temporary files and atomic replacement for managed outputs;
- never opens, edits, or executes sibling repositories.

## Checker guarantees

- reads control-plane files only;
- does not execute verification commands from `repos.yaml`;
- path verification checks existence only;
- reports structural inconsistencies without repairing them.

## Known limitations

- The checker does not prove that a duty statement is correct.
- The checker does not validate arbitrary YAML; `repos.yaml` uses a documented JSON-compatible subset.
- The public-content scanner is defence in depth, not a replacement for dedicated secret scanning or human review.
- An AI agent can still violate instructions; use repository permissions, protected branches, reviews, CI, and least-privilege credentials as independent controls.
