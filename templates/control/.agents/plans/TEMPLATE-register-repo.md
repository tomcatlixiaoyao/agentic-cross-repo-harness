# ExecPlan: register-repository-<id>

Register, remove, or change a repository only after the developer confirms the identity, path, role, responsibility, contracts, and verification command.

## Goal

## Developer Confirmation

- [ ] repository id
- [ ] relative sibling path
- [ ] role (`control`, `provider`, `consumer`, `participant`, or `shared`)
- [ ] one-sentence responsibility and explicit non-responsibilities
- [ ] owned or consumed contracts (`none` if not applicable)
- [ ] verification command (`none` if unavailable)
- [ ] developer explicitly approved the registry change

## Included / Excluded

Included: control-repository registry, inventory, workspace, boundary table, and the participant repository's root guidance after approval.

Excluded: business implementation, credentials, complete provider schemas, deployment, and unrelated repositories.

## Repository Write Scope

| Repository | Allowed paths | Excluded paths |
| --- | --- | --- |
| `<control-id>` | `repos.yaml`, `docs/harness/inventory.md`, `AGENTS.md`, `*.code-workspace` | implementation |
| `<new-id>` | `AGENTS.md` and confirmed thin tool adapters | all other paths |
| every other registered repository | none | all |

## Contract Freeze

## Concrete Steps

1. Obtain developer confirmation.
2. Update `repos.yaml`.
3. Update `docs/harness/inventory.md` and its change log.
4. Update the repository boundary table in `AGENTS.md`.
5. Update the workspace folders.
6. Add or update the participant repository's root `AGENTS.md` from the provided template.
7. Add only the confirmed thin adapters for coding agents used by that repository.
8. Run the Harness checker and repository-specific verification.

## Validation Matrix

| Layer | Command | Expected result | Actual result |
| --- | --- | --- | --- |
| control | `python scripts/check_harness.py --root <control-repo>` | registry surfaces agree | pending |
| `<new-id>` | read its root `AGENTS.md` | points to control and states real verification | pending |
| integration | open workspace | every registered repository appears once | pending |

## Rollback Unit / Stop Conditions

Rollback all registry-surface changes together. Stop before any change if developer confirmation is incomplete.

## Progress

## Decision Log

## Surprises & Discoveries

## Review / Writeback / Outcomes

## Recovery Point / Next Action
