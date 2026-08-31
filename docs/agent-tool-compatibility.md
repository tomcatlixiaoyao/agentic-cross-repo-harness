# Coding-Agent Compatibility

[English](agent-tool-compatibility.md) | [简体中文](agent-tool-compatibility.zh-CN.md)

The Harness is built around one portable contract rather than one AI product. The generated
root `AGENTS.md` is the canonical instruction source. Tool-specific files are deliberately thin
adapters that point back to it, so safety and workflow rules do not drift.

## Supported adapters

| Tool | Generated entry point | Behavior |
| --- | --- | --- |
| Codex | `AGENTS.md` | Reads the canonical instructions directly. |
| Cursor | `.cursor/rules/harness-control.mdc` | Always points Cursor back to `AGENTS.md`; Cursor can also read root `AGENTS.md`. |
| Claude Code | `CLAUDE.md` | Imports the canonical file with `@AGENTS.md`. |
| GitHub Copilot | `.github/copilot-instructions.md` | Directs supported Copilot surfaces to the canonical file. |

Select adapters in the manifest:

```json
{
  "agent_tools": ["codex", "cursor", "claude", "copilot"]
}
```

Or override them during generation:

```bash
harness init --manifest manifest.json --target ../product-harness --tools cursor,claude
```

`--tools auto` preserves recognized adapter conventions in an existing target. For a new target,
it generates all supported adapters as the portable default. It never edits participant repositories.
For safety, changing the selection does not delete a pre-existing adapter; Doctor reports stale adapters
so a developer can review and remove them explicitly.

## Language neutrality

Each repository's `verify` value is an opaque command. The Harness records and reports it but does
not infer a programming language and does not execute it during structural checks. Examples:

```json
{"verify": "./mvnw test"}
{"verify": "npm test && npm run build"}
{"verify": "go test ./..."}
{"verify": "cargo test"}
```

Use repository-owned wrappers such as Maven Wrapper or Gradle Wrapper where possible. That keeps
the control plane independent from both the implementation language and globally installed build tools.

## Diagnose an installation

```bash
harness doctor --root ../product-harness
```

Doctor validates the control structure, reports configured adapter files, and shows optional local CLI
detection. A missing CLI is informational because Cursor and Copilot may be used entirely through an IDE.
Doctor never runs participant verification commands.

## Adding another coding agent

A new adapter should contain only the minimum file needed to load or reference `AGENTS.md`. Add its
identifier and path to `SUPPORTED_AGENT_TOOLS` and `AGENT_TOOL_CONFIG_PATHS`, add a control template,
and extend the generation and drift tests. Do not copy the complete operating policy into the adapter.
