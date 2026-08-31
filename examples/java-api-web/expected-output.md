# Expected Output

Generating this example creates a separate control repository with the following important files:

```text
catalog-change-harness/
├── AGENTS.md
├── CLAUDE.md
├── README.md
├── repos.yaml
├── catalog-delivery-window.code-workspace
├── .agents/
│   ├── PLANS.md
│   └── plans/
│       ├── TEMPLATE-cross-repo.md
│       └── TEMPLATE-register-repo.md
├── .cursor/rules/harness-control.mdc
├── .github/copilot-instructions.md
├── contracts/INDEX.md
├── docs/harness/
│   ├── inventory.md
│   ├── verification.md
│   └── PARTICIPANT_AGENTS_TEMPLATE.md
└── scripts/
    ├── check_harness.py
    ├── doctor_harness.py
    └── harness_lib.py
```

Review these invariants:

1. `repos.yaml` has one control repository at `.`.
2. `catalog-api` is the provider for `catalog-api-v1`.
3. `storefront-web` is a consumer of that contract, not its owner.
4. Maven and npm commands are stored as repository-owned validation instructions; the Harness checker does not execute them.
5. `AGENTS.md` is canonical. Tool-specific adapter files point back to it instead of creating separate policies.
6. The generated workspace opens all three sibling repositories, but opening a repository does not grant write authority.

The structure check should return:

```text
Harness validation passed
```

If either sibling is absent, `--verify-paths` must report it. Missing infrastructure is not converted into a successful integration result.
