# Participant Repository Guidance Template

Copy and adapt this content into a registered participant repository only after that repository has been confirmed and included in a registration ExecPlan.

```markdown
# <repository-id>

Cross-repository coordination rules live in sibling `<control-repository-path>/AGENTS.md`.
For work that affects another registered repository, open the control workspace and follow its ExecPlan protocol.

## Responsibility

- Owns: <implementation and truth owned by this repository>
- Does not own: <explicit boundaries>

## Verification

- `<real command or none>`

## Safety

- Do not modify unregistered siblings.
- Do not redefine provider-owned contracts.
- Do not commit credentials, private data, internal logs, or machine-specific paths.
```

Do not copy temporary task state, business secrets, or a complete provider schema into this file.

## Coding-agent adapters

Keep the participant `AGENTS.md` above as its canonical local guidance. Add only the adapters used by
the team:

- Claude Code: create a root `CLAUDE.md` containing only `@AGENTS.md`.
- Cursor: root `AGENTS.md` is sufficient; an always-applied `.cursor/rules/*.mdc` may point to it.
- GitHub Copilot: add `.github/copilot-instructions.md` that tells Copilot to read and follow root `AGENTS.md`.
- Codex: reads root and nested `AGENTS.md` directly.

These participant files must be added only through a confirmed registration ExecPlan. The initializer
does not write them automatically.
