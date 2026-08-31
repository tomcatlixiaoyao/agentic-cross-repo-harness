# Contribution Rules for Agents

## Scope

This repository contains a provider-neutral, public-safe Harness generator and checker. Keep implementation generic: do not add company-specific workflows, private hosts, credentials, personal machine paths, production data, or copied internal documents.

## Required checks

After changing Python, templates, schema, or generated-file behavior, run:

```bash
python -m unittest discover -s tests -p "test_*.py"
python scripts/scan_public.py --root .
```

When generated structure changes, update the checker, README tree, tests, and templates together.

## Safety invariants

- The initializer may write only below its explicit target directory.
- The checker is read-only and must not execute repository verification commands.
- A generated Harness must never modify participant repositories automatically.
- Exactly one repository is the control repository at `.`; participants use paths beneath the direct parent.
- Cross-repository writes require an explicit ExecPlan row for every registered repository; `none` means no write authority.
- Provider repositories own contract truth. Consumer snapshots never replace provider truth.
- Publishing, deployment, permission changes, merges, deletion, and external mutations require separate confirmation.

## Change discipline

Prefer standard-library Python and deterministic output. Add a focused regression test for every fixed bug or strengthened invariant. Do not weaken a safety check merely to make an example pass.
