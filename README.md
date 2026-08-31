# Agentic Cross-Repository Harness

A provider-neutral control plane for AI-assisted work across multiple Git repositories.

The Harness gives agents and developers one place to define repository responsibilities, freeze cross-repository write scope, reference contract truth, validate each repository independently, and record integration outcomes. It does **not** copy business implementation into a coordination repository and it never treats automation as implicit permission to write everywhere.

## Why this exists

AI coding tools are effective inside one repository but become risky when a change spans an API provider, generated client, frontend, infrastructure, documentation, or another consumer. Common failure modes include:

- modifying the wrong repository or an unregistered sibling;
- allowing a consumer snapshot to redefine provider contract truth;
- mixing multiple repositories into one rollback unit;
- reporting integration success after running only one repository's tests;
- losing the exact scope, decisions, recovery point, and next action between sessions.

This project turns those boundaries into explicit repository files and deterministic checks.

## Core model

```text
Issue tracker        collaboration state, blockers, recovery, next action
       │
       ▼
Control repository   inventory, ExecPlans, contract references, outcomes
       │
       ├── Provider repository   contract truth + implementation + tests
       ├── Consumer repository   snapshots + consumption rules + tests
       └── Other participants    independently owned implementation
```

The workflow is:

```text
collect → gate → freeze → slice → implement
        → verify-<repo-id> → verify-integration
        → review → writeback → notify
```

## Quick start

Requirements: Python 3.10 or newer; no third-party Python packages.

1. Copy [examples/manifest.json](examples/manifest.json) and describe your repositories.
2. Preview generated files:

   ```bash
   python scripts/init_harness.py \
     --manifest examples/manifest.json \
     --target ../sample-product-harness \
     --dry-run
   ```

3. Initialise the control repository:

   ```bash
   python scripts/init_harness.py \
     --manifest examples/manifest.json \
     --target ../sample-product-harness
   ```

4. Validate it:

   ```bash
   python scripts/check_harness.py --root ../sample-product-harness
   ```

5. After cloning all registered siblings, optionally verify that their paths exist:

   ```bash
   python scripts/check_harness.py \
     --root ../sample-product-harness \
     --verify-paths
   ```

The initializer writes only inside `--target`. It does not edit sibling repositories. Participant `AGENTS.md` files are installed manually only after a registration ExecPlan and explicit developer confirmation.

## Generated control repository

```text
<product>-harness/
├── AGENTS.md
├── README.md
├── repos.yaml
├── <product>.code-workspace
├── .agents/
│   ├── PLANS.md
│   └── plans/
│       ├── TEMPLATE-cross-repo.md
│       └── TEMPLATE-register-repo.md
├── .cursor/rules/harness-control.mdc
├── scripts/
│   ├── check_harness.py
│   └── harness_lib.py
├── contracts/INDEX.md
└── docs/harness/
    ├── inventory.md
    ├── verification.md
    └── PARTICIPANT_AGENTS_TEMPLATE.md
```

`repos.yaml` intentionally uses the JSON-compatible subset of YAML 1.2. This keeps it readable by YAML tools while allowing deterministic validation with the Python standard library.

## Safety properties

- Exactly one registered repository has the `control` role and path `.`.
- Other repositories must use explicit relative sibling paths beginning with `../`.
- Cross-repository changes require an ExecPlan with a row for every registered repository.
- Repositories without write permission are recorded as `none`.
- Provider contract truth is referenced, not copied into the control repository.
- Repository verification and rollback units remain independent.
- The checker is read-only and never executes sibling commands.
- Publishing, deployment, permission changes, deletion, and external data mutation remain separate confirmed actions.

See [docs/concepts.md](docs/concepts.md), [docs/quick-start.md](docs/quick-start.md), and [docs/security-model.md](docs/security-model.md).

## Development

```bash
python -m unittest discover -s tests -p "test_*.py"
python scripts/scan_public.py --root .
```

## Status

The current release is an initial public foundation. It provides deterministic scaffolding and structural validation. It deliberately does not orchestrate deployments, issue trackers, pull-request merges, or arbitrary commands across sibling repositories.

## License

MIT. See [LICENSE](LICENSE).

