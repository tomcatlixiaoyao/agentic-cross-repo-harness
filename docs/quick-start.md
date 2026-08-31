# Quick Start

This guide starts with a fresh clone and ends with a generated, validated control repository.

## 1. Clone the generator

```bash
git clone https://github.com/tomcatlixiaoyao/agentic-cross-repo-harness.git
cd agentic-cross-repo-harness
```

Requirements: Python 3.10 or newer. The generator uses no third-party Python packages.

On Windows, use `python` or `py -3`. On Linux and macOS, use `python3` if `python` is not available.

## 2. Arrange repositories as siblings

The generated control repository and its participants should share one direct parent:

```text
workspace-parent/
├── agentic-cross-repo-harness/   # generator source
├── sample-api/                    # provider
└── sample-web/                    # consumer
```

The manifest uses `.` for the future control repository and explicit `../<name>` paths for participants. Absolute paths and traversal beyond the direct parent are rejected.

## 3. Create a manifest

Copy `examples/manifest.json` and adjust it for your repositories. Every entry requires:

- `id`: lowercase kebab-case identifier;
- `path`: `.` or a participant path beginning with `../`;
- `role`: `control`, `provider`, `consumer`, `participant`, or `shared`;
- `duty`: one-line responsibility;
- `contracts`: owned or consumed contract identifiers;
- `verify`: a real verification command, or the literal value `none`.

Exactly one entry must use role `control` and path `.`.

## 4. Preview before writing

Linux/macOS:

```bash
python3 scripts/init_harness.py \
  --manifest examples/manifest.json \
  --target ../sample-product-harness \
  --dry-run
```

Windows PowerShell:

```powershell
python scripts/init_harness.py `
  --manifest examples/manifest.json `
  --target ../sample-product-harness `
  --dry-run
```

The preview lists every managed file without creating the target directory.

## 5. Generate the control repository

Linux/macOS:

```bash
python3 scripts/init_harness.py \
  --manifest examples/manifest.json \
  --target ../sample-product-harness
```

Windows PowerShell:

```powershell
python scripts/init_harness.py `
  --manifest examples/manifest.json `
  --target ../sample-product-harness
```

The initializer refuses to overwrite managed files unless `--force` is supplied. `--force` replaces only its managed output set; it does not delete unrelated files.

## 6. Validate the generated repository

The generated repository includes its own checker:

```bash
python ../sample-product-harness/scripts/check_harness.py \
  --root ../sample-product-harness
```

Expected result:

```text
Harness validation passed
```

Add `--verify-paths` only when every registered participant should already exist locally. The checker verifies paths but never runs participant commands.

## 7. Inspect before committing

Review these files first:

- `repos.yaml`: machine-readable registry;
- `AGENTS.md`: cross-repository operating rules;
- `docs/harness/inventory.md`: review-friendly responsibility map;
- `.agents/PLANS.md`: plan requirements;
- `.agents/plans/TEMPLATE-cross-repo.md`: per-task write boundary.

## 8. Register participant guidance

The initializer deliberately leaves participant repositories untouched. For each participant:

1. create a registration ExecPlan from `.agents/plans/TEMPLATE-register-repo.md`;
2. confirm id, path, role, duty, contracts, and verification command;
3. adapt `docs/harness/PARTICIPANT_AGENTS_TEMPLATE.md` inside the participant repository;
4. verify and commit the control and participant repositories independently.

## 9. Start a cross-repository task

Copy `.agents/plans/TEMPLATE-cross-repo.md` into a dated plan. Fill one row per registered repository. Use `none` for repositories without write authority, then freeze contract truth, validation, rollback units, and stop conditions before implementation.
