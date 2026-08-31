# ExecPlan: <cross-repository task>

Copy this file to `.agents/plans/YYYY-MM-DD/<slug>.md`.
Copy every id from `repos.yaml` into the write-scope and validation tables. Write `none` for repositories that are not authorised for changes.

## Goal

## Included / Excluded

## Repository Write Scope

| Repository | Allowed paths | Excluded paths |
| --- | --- | --- |
| `<control-id>` |  |  |
| `<participant-id>` | none | all |

## Contract Freeze

Use `none` when this task does not change or consume a versioned contract.

| Contract | Provider repo | Truth path | Version/hash | Consumer repo | Snapshot path | Change policy |
| --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |

## Concrete Steps

## Validation Matrix

| Layer | Command | Expected result | Actual result |
| --- | --- | --- | --- |
| `<control-id>` |  |  | pending |
| `<participant-id>` | none | no write | pending |
| integration |  |  | pending |

## Rollback Unit / Stop Conditions

Keep rollback units repository-local. Stop if a required repository, contract, permission, credential, environment, or human decision is missing.

## Progress

## Decision Log

## Surprises & Discoveries

## Review / Writeback / Outcomes

## Recovery Point / Next Action
