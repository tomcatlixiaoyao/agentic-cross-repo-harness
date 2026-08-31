# Cross-Repository Planning Protocol

Any task that writes to a non-control repository requires an ExecPlan before implementation. A documentation-only change confined to the control repository may omit a plan when it is small and reversible.

Repository registration, removal, path changes, or role changes must use `TEMPLATE-register-repo.md` and require explicit developer confirmation before registry files are updated.

Every cross-repository plan must contain:

- the goal and included/excluded scope;
- one write-scope row for every repository in `repos.yaml`;
- provider truth and consumer snapshot references;
- concrete implementation steps;
- per-repository and integration validation;
- independent rollback units and stop conditions;
- progress, decisions, discoveries, outcomes, recovery point, and next action.

Store plan instances at `.agents/plans/YYYY-MM-DD/<slug>.md`. Update the plan while executing; do not use it only as a pre-work document.
