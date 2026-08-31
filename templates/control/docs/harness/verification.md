# Cross-Repository Verification

Verification has three layers:

1. **Control:** registry consistency, plan completeness, contract references, and Harness checks.
2. **Repository:** each modified repository runs the commands declared in its nearest `AGENTS.md` and `repos.yaml` entry.
3. **Integration:** contract compatibility and the real path crossing repository boundaries.

Record the exact command, repository commit, contract version or hash, result, and any degraded or blocked condition. Never report a layer as passed when its environment or dependency was unavailable.

The public Harness checker validates the control plane only. It deliberately does not execute sibling repository commands, publish artifacts, deploy services, change permissions, or mutate external data.

## Verification Record Template

| Layer | Repository/commit | Command | Contract/version | Result |
| --- | --- | --- | --- | --- |
| control |  |  | none | pending |
| repository |  |  |  | pending |
| integration | multiple |  |  | pending |

## Closeout

- Provider truth:
- Consumer snapshots:
- Commits by repository:
- Residual risks:
- Recovery point:
- Next action:
