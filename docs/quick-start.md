# Quick Start

## 1. Arrange repositories as siblings

```text
workspace-parent/
├── sample-product-harness/
├── sample-api/
└── sample-web/
```

The public initializer permits `.` for the control repository and explicit `../<name>` paths for sibling repositories. Absolute paths and implicit workspace discovery are rejected.

## 2. Create a manifest

Start from `examples/manifest.json`. Every repository requires:

- `id`: lowercase kebab-case identifier;
- `path`: `.` or a named sibling path beginning with `../`;
- `role`: `control`, `provider`, `consumer`, `participant`, or `shared`;
- `duty`: one-line responsibility;
- `contracts`: owned or consumed contract identifiers;
- `verify`: real verification command, or the literal value `none`.

Exactly one entry must use role `control` and path `.`.

## 3. Preview before writing

```bash
python scripts/init_harness.py \
  --manifest examples/manifest.json \
  --target ../sample-product-harness \
  --dry-run
```

The initializer refuses to overwrite managed files unless `--force` is supplied. `--force` replaces only the managed output set and does not delete unrelated files.

## 4. Initialise and inspect

```bash
python scripts/init_harness.py \
  --manifest examples/manifest.json \
  --target ../sample-product-harness
```

Review `repos.yaml`, `AGENTS.md`, and `docs/harness/inventory.md` before committing them.

## 5. Register participant guidance

The initializer deliberately leaves sibling repositories untouched. For each participant:

1. create a registration ExecPlan from `.agents/plans/TEMPLATE-register-repo.md`;
2. obtain developer confirmation for id, path, role, duty, contracts, and verification;
3. adapt `docs/harness/PARTICIPANT_AGENTS_TEMPLATE.md` into the participant repository;
4. verify and commit the control and participant repositories independently.

## 6. Run the checker

```bash
python scripts/check_harness.py --root ../sample-product-harness
```

Add `--verify-paths` only when all sibling repositories should already exist locally. The checker does not run their commands.

## 7. Start a cross-repository task

Copy `.agents/plans/TEMPLATE-cross-repo.md` into a dated plan. Fill one row per repository, marking non-written repositories as `none`. Freeze contract truth, validation, rollback, and stop conditions before modifying a participant.
