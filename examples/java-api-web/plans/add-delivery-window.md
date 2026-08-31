# ExecPlan: Add an optional delivery window

## Outcome

Expose an optional `deliveryWindow` field from the catalog API and render it in the storefront without changing the meaning of existing response fields.

This file is an illustrative, pre-execution plan. `TBD` values must be replaced with reviewed evidence before any participant repository is modified.

## Repository write scope

| Repository | Allowed paths | Excluded paths |
| --- | --- | --- |
| `harness` | `.agents/plans/YYYY-MM-DD-add-delivery-window.md`, `docs/harness/verification.md` | all other paths |
| `catalog-api` | `src/main/resources/openapi/catalog-api.yaml`, `src/main/java/example/catalog/api/`, `src/test/java/example/catalog/api/` | credentials, deployment configuration, database migrations, all other paths |
| `storefront-web` | `src/generated/catalog/`, `src/features/product/`, `src/features/product/__tests__/` | release configuration, environment files, all other paths |

`none` must be used instead of an empty or implied permission when a registered repository does not require writes.

## Frozen contract truth

| Item | Value |
| --- | --- |
| Provider | `catalog-api` |
| Contract id | `catalog-api-v1` |
| Provider truth path | `catalog-api/src/main/resources/openapi/catalog-api.yaml` |
| Pre-change revision | `TBD: immutable commit id` |
| Consumer snapshot path | `storefront-web/src/generated/catalog/` |
| Compatibility rule | `deliveryWindow` is optional; existing fields and response status remain unchanged |

The provider contract is authoritative. A generated consumer snapshot may demonstrate drift but may not redefine the field.

## Execution slices

1. Confirm the current provider revision, consumer generation command, and acceptance example.
2. Change and test the provider contract and Java implementation.
3. Record the provider commit id before regenerating the consumer.
4. Regenerate the consumer from the committed provider truth.
5. Add the storefront rendering and tests.
6. Run repository validations independently.
7. Run the agreed integration check and record evidence in the control repository.

## Validation matrix

| Layer | Command or evidence | Expected result | Status |
| --- | --- | --- | --- |
| Harness structure | `python scripts/check_harness.py --root . --verify-paths` | registered siblings and generated files are valid | not run |
| Java provider | `./mvnw test` | provider contract and implementation tests pass | not run |
| Web consumer | `npm test && npm run build` | generated client, UI tests, and production build pass | not run |
| Integration | `TBD: repository-owned contract or end-to-end command` | optional field is accepted and rendered; omission remains compatible | blocked until command is agreed |

Never mark a layer successful based on another layer's result.

## Independent commits and rollback

| Repository | Planned commit | Rollback unit |
| --- | --- | --- |
| `catalog-api` | contract, Java implementation, and provider tests | revert provider commit before consumer release |
| `storefront-web` | generated client, presentation, and consumer tests | revert consumer commit independently |
| `harness` | approved plan and final evidence only | revert coordination record without modifying participants |

## Stop conditions

Stop before participant writes when any of the following is true:

- the provider truth path or pre-change revision is unknown;
- adding the field is not backward compatible;
- the consumer generator is unavailable or its provenance is unclear;
- credentials, deployment, database migration, or publishing become necessary;
- required paths fall outside the authorised rows above;
- Codebase Memory or another analysis tool disagrees with inspected source and the discrepancy is unresolved.

## Recovery point and next action

Current recovery point: no participant repository has been modified.

Next action: record the immutable provider revision and agree on the integration validation command.
