# Concepts

## Control, provider, consumer, participant, shared

- **control** owns coordination artifacts: inventory, plans, contract references, verification summaries, and recovery information.
- **provider** owns a contract and the implementation that serves it.
- **consumer** consumes provider truth and may own generated snapshots, mocks, caches, or golden files.
- **participant** is involved in a cross-repository workflow without a provider/consumer relationship.
- **shared** owns explicitly shared assets that do not belong to one provider.

Roles describe truth ownership, not organisational seniority.

## Truth split

The control repository references facts but avoids becoming an extra copy of them.

| Surface | Owns |
| --- | --- |
| Issue tracker | collaboration status, blockers, follow-ups, recovery point, next action |
| Provider repository | contract truth, implementation, repository tests, runbook |
| Consumer repository | consumption rules, generated snapshots, consumer tests |
| Control repository | write authorisation, references, validation matrix, integration outcome |
| Pull request | diff narrative, review discussion, merge status |

If a consumer detects drift, return to provider truth before updating either side.

## ExecPlan as capability boundary

An ExecPlan is more than a task list. Its repository write-scope table is the capability boundary for that execution slice. A repository or path not present in the allowed column is not authorised for modification.

The plan must also freeze:

- provider truth path and version/hash;
- consumer snapshot path and version;
- validation commands and expected results;
- independent rollback units;
- stop conditions for missing decisions, credentials, environments, or repositories.

## Independent commits and rollback

Each repository is validated and committed independently. The control repository records the resulting commit identifiers and integration evidence. This preserves repository ownership and prevents a failed consumer change from requiring an opaque cross-repository rollback.

## Degraded and blocked results

The Harness does not convert missing infrastructure into success. If a validation layer cannot run, record it as `blocked` or `degraded`, explain the missing condition, and leave a concrete recovery point and next action.

## Canonical instructions and adapters

The root `AGENTS.md` is the canonical coding-agent contract. Files for Claude Code, Cursor, and
GitHub Copilot are transport adapters, not independent policy documents. Keeping them thin prevents
different tools from applying different repository boundaries or safety rules.

The Harness treats every repository verification command as opaque text. Language-specific ownership
stays inside the participant repository; the control plane coordinates evidence without interpreting or
executing the command during structural validation.
