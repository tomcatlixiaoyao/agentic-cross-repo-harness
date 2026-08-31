# Java API + Web Consumer Example

This example shows how to coordinate one deliberately small contract change across a Java API provider and a web consumer without making either repository subordinate to the control repository.

## Scenario

The storefront needs to display an optional delivery window returned by the catalog API:

```json
{
  "productId": "demo-123",
  "deliveryWindow": "2-3 business days"
}
```

The provider owns `catalog-api-v1` and its OpenAPI source. The consumer may regenerate a client or snapshot, but that generated copy never becomes contract truth.

The illustrative workspace is arranged as siblings:

```text
workspace-parent/
├── agentic-cross-repo-harness/
├── catalog-api/
├── storefront-web/
└── catalog-change-harness/       # generated control repository
```

## Generate the control repository

From the generator checkout on Linux or macOS:

```bash
python3 scripts/harness_cli.py init \
  --manifest examples/java-api-web/manifest.json \
  --target ../catalog-change-harness \
  --tools auto \
  --dry-run

python3 scripts/harness_cli.py init \
  --manifest examples/java-api-web/manifest.json \
  --target ../catalog-change-harness \
  --tools auto
```

From Windows PowerShell:

```powershell
python scripts/harness_cli.py init `
  --manifest examples/java-api-web/manifest.json `
  --target ../catalog-change-harness `
  --tools auto `
  --dry-run

python scripts/harness_cli.py init `
  --manifest examples/java-api-web/manifest.json `
  --target ../catalog-change-harness `
  --tools auto
```

The initializer writes only to `catalog-change-harness`. It does not create or modify `catalog-api` or `storefront-web`.

Validate the generated structure:

```bash
python ../catalog-change-harness/scripts/check_harness.py --root ../catalog-change-harness
python ../catalog-change-harness/scripts/doctor_harness.py --root ../catalog-change-harness
```

Add `--verify-paths` to the checker only after both participant repositories exist as registered siblings. The checker never executes Maven or npm commands.

## Start the first task

Copy [`plans/add-delivery-window.md`](plans/add-delivery-window.md) into the generated control repository under a dated filename such as:

```text
.agents/plans/2026-08-31-add-delivery-window.md
```

Before implementation, replace every `TBD` with reviewed repository evidence. The example plan demonstrates:

- path-level write authority for every registered repository;
- provider-owned contract truth and consumer snapshot rules;
- independent Maven, npm, and Harness validation;
- repository-level commits and rollback;
- explicit stop conditions and a recoverable next action.

The plan is intentionally not marked complete: it is a reusable walkthrough, not fabricated execution evidence.

## Expected generated result

See [`expected-output.md`](expected-output.md) for the files and boundaries that should be inspected before committing the generated control repository.
