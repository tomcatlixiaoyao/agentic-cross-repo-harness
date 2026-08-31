# AI 编程工具兼容说明

[English](agent-tool-compatibility.md) | 简体中文

Harness 围绕一份可移植的工程协议设计，而不是绑定某个 AI 产品。生成后的根目录
`AGENTS.md` 是唯一权威规则，其他文件只是将不同工具引导到这份规则的轻量适配层，
避免安全边界和工作流程长期漂移。

## 已支持的工具

| 工具 | 生成的入口 | 行为 |
| --- | --- | --- |
| Codex | `AGENTS.md` | 直接读取权威规则。 |
| Cursor | `.cursor/rules/harness-control.mdc` | 始终指向 `AGENTS.md`；Cursor 也能读取根目录 `AGENTS.md`。 |
| Claude Code | `CLAUDE.md` | 使用 `@AGENTS.md` 导入权威规则。 |
| GitHub Copilot | `.github/copilot-instructions.md` | 在支持的 Copilot 场景中引导工具读取权威规则。 |

可以在 manifest 中选择工具：

```json
{
  "agent_tools": ["codex", "cursor", "claude", "copilot"]
}
```

也可以在生成时覆盖：

```bash
harness init --manifest manifest.json --target ../product-harness --tools cursor,claude
```

`--tools auto` 会识别已有目标目录中的适配约定；新目录默认生成全部适配器。
初始化器仍然不会修改任何参与仓库。
出于安全考虑，改变工具选择不会自动删除已有适配文件；Doctor 会提示这类文件，由开发者确认后移除。

## 不限制项目语言

每个仓库的 `verify` 都是不透明命令。Harness 只记录和展示，不判断语言，也不会在结构
检查期间执行它：

```json
{"verify": "./mvnw test"}
{"verify": "npm test && npm run build"}
{"verify": "go test ./..."}
{"verify": "cargo test"}
```

建议优先使用 Maven Wrapper、Gradle Wrapper 等仓库自带入口，使控制面同时独立于项目语言
和开发者机器上的全局工具。

## 诊断接入状态

```bash
harness doctor --root ../product-harness
```

Doctor 会检查控制仓结构、适配文件和可选的本地 CLI。Cursor 或 Copilot 可能只在 IDE 中使用，
所以未发现 CLI 只是提示，不是失败。Doctor 永远不会执行参与仓库的验证命令。

## 扩展其他 AI 工具

新适配器只应包含加载或引用 `AGENTS.md` 所需的最少内容。增加工具标识、适配路径、控制仓模板
和相应测试即可，不要复制整份工程规则。
