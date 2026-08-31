# Optional Codebase Memory Integration

[Codebase Memory MCP](https://github.com/DeusData/codebase-memory-mcp) and this Harness solve different parts of an AI-assisted change:

- Codebase Memory builds a local structural model of source code and can suggest call paths, routes, dependencies, and likely impact.
- The Harness records human-reviewed repository authority, contract ownership, validation, rollback, and recovery state.

Code intelligence is evidence, not authorisation. Installing or querying a memory tool must never expand an ExecPlan write boundary.

## Recommended flow

```text
requirement
  -> Harness registry and draft ExecPlan
  -> local code graph and impact exploration
  -> human review of suggested repositories and paths
  -> frozen ExecPlan write scope
  -> implementation
  -> independent repository validation
  -> integration evidence and recovery state
```

## Safe setup

1. Review the upstream source, release checksums, installation behavior, and organisation policy before installing any binary or MCP server.
2. Keep processing local. Do not publish graph databases, source snippets, internal routes, or generated architecture summaries from private repositories.
3. Restrict indexing to the intended workspace. Codebase Memory documents `CBM_ALLOWED_ROOT` for confining requested repository paths.
4. Review changes to user-level agent configuration and hooks. Installation is not equivalent to granting permission to modify repositories.
5. Index only registered repositories needed for the task. Ignore generated output, credentials, local configuration, and other sensitive paths with the tool's supported ignore mechanism.

Follow the upstream installation instructions rather than copying an unpinned installer command into a shared plan.

## Evidence to collect

Before freezing an ExecPlan, use structural queries to answer questions such as:

- Which provider route or handler owns the requested behavior?
- Which callers and consumer repositories depend on the symbol or contract?
- Does the proposed change cross a package, service, or repository boundary?
- Which tests are structurally adjacent to the affected code?

Record only compact, reviewable evidence in the plan:

```markdown
| Evidence | Value |
| --- | --- |
| Repository revision | immutable commit id |
| Index freshness | indexed at that revision |
| Qualified symbols | provider-qualified symbol names |
| Suggested affected paths | reviewed path list |
| Human decision | accepted, narrowed, or rejected with reason |
```

Do not commit a local SQLite graph or bulk source-derived output to the control repository.

## Authority boundary

Memory results may suggest a broader or narrower impact set. They do not automatically change any of these Harness rules:

- unregistered repositories remain out of scope;
- every registered repository still needs an ExecPlan row;
- allowed paths require human confirmation;
- provider contract truth remains in the provider repository;
- validation commands remain repository-owned and are not executed by the Harness checker;
- publishing, deployment, permission changes, and destructive operations require separate confirmation.

When graph evidence conflicts with source, generated code, repository instructions, or runtime behavior, stop and resolve the discrepancy. Do not treat an inferred edge as authoritative.

## Failure and fallback

Codebase Memory is optional. If it is unavailable, stale, unsupported, or prohibited by policy:

1. continue with normal repository inspection and native language tooling;
2. mark structural analysis as unavailable or degraded;
3. do not mark repository or integration validation successful because indexing succeeded;
4. preserve a recovery point and the next concrete investigation step.

The Harness remains usable without MCP, a daemon, a graph database, or any particular coding agent.
