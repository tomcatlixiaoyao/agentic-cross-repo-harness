# Agentic Cross-Repository Harness

[English](README.md) | 简体中文

让不同 AI 编程工具安全地跨多个 Git 仓库协作，同时不限制参与项目的开发语言。

本项目用于生成一个轻量级的**控制仓库（Control Repository）**，把跨仓任务中的关键边界写清楚：智能体可以修改哪些仓库、谁拥有契约真相、每个仓库如何独立验证，以及任务中断后从哪里安全恢复。

它不绑定特定 AI 工具，可为 Codex、Cursor、Claude Code 和 GitHub Copilot 生成适配文件；
从源码运行时只依赖 Python 标准库，并且初始化时绝不会修改参与项目的仓库。

## 它解决什么问题

当一个 AI 任务同时涉及 API、前端、生成客户端、基础设施或文档仓库时，常见风险包括：

- 智能体修改了错误的仓库或未登记的目录；
- 消费方保存的快照反过来覆盖了提供方的契约真相；
- 多个仓库混在一个回滚单元中；
- 只运行一个仓库的测试，却宣称集成验证成功；
- 会话中断后，范围、决策、恢复点和下一步丢失。

Harness 将这些约束落成可审查的仓库文件和确定性检查。

## 你会得到什么

- 明确记录仓库职责的注册表；
- 作为单次任务写入边界的 ExecPlan 模板；
- 防止契约出现多份真相的 Provider/Consumer 规则；
- 每个仓库独立的验证和回滚单元；
- 不执行任何业务命令的只读结构校验器；
- 由同一份 `AGENTS.md` 驱动的轻量 AI 工具适配层；
- 用于说明适配状态和验证配置的 doctor 命令；
- 从相邻 Git 仓库生成 manifest 草稿的只读工作区发现命令；
- 面向公开发布的常见敏感信息扫描器。

各仓库的验证命令会被视为不透明字符串，因此参与项目可以使用 Maven、Gradle、npm、Go、Cargo
或任意仓库自带的工具链。

## 适合谁

当一次 AI 辅助变更可能跨越多个独立仓库时，建议使用本 Harness，例如：

- 需要协调多个仓库的平台或架构团队；
- 正在引入 Codex、Claude Code、Cursor 等编码智能体的团队；
- 需要明确 API 或数据契约归属的 Provider/Consumer 系统；
- 需要持续记录决策、恢复点和下一步的长任务。

如果任务始终只发生在一个小型仓库内，通常不需要引入它。

## 工作方式

```mermaid
flowchart LR
    I[需求或 Issue] --> C[控制仓库]
    C --> P[Provider 仓库]
    C --> W[Consumer 仓库]
    C --> O[其他参与仓库]
    P --> V[各仓独立验证]
    W --> V
    O --> V
    V --> R[评审与结果回写]
```

标准流程为：

```text
收集 → 准入判断 → 冻结契约 → 拆分任务 → 实现
     → 各仓验证 → 集成验证 → 评审 → 回写 → 通知
```

控制仓库只负责协调，不复制业务实现，也不成为契约的另一份真相。

## 三分钟体验

从源码运行的前置条件：Git、Python 3.10 或更高版本，不需要安装第三方 Python 依赖。
正式版本会生成 Windows、Linux 和 macOS 独立可执行程序。你可以从
[最新版本](https://github.com/tomcatlixiaoyao/agentic-cross-repo-harness/releases/latest)
下载对应平台的文件，放入 `PATH` 后先验证：

```text
harness --version
harness --help
```

Release 同时提供 `SHA256SUMS.txt`，运行前应核对下载文件的 SHA-256。Linux 和 macOS
用户可能还需要先执行 `chmod +x harness-*`。

如果希望直接从源码运行：

```bash
git clone https://github.com/tomcatlixiaoyao/agentic-cross-repo-harness.git
cd agentic-cross-repo-harness

python scripts/harness_cli.py discover \
  --root .. \
  --product sample-product \
  --exclude agentic-cross-repo-harness \
  --output ../sample-manifest.json

python scripts/harness_cli.py init \
  --manifest ../sample-manifest.json \
  --target ../sample-product-harness \
  --tools auto \
  --dry-run

python scripts/harness_cli.py init \
  --manifest ../sample-manifest.json \
  --target ../sample-product-harness \
  --tools auto

python scripts/harness_cli.py check --root ../sample-product-harness
python scripts/harness_cli.py doctor --root ../sample-product-harness
```

校验成功时会看到：

```text
Harness validation passed
```

随后 doctor 会列出各适配器状态，并给出结构检查结果。

`discover` 只扫描工作区根目录下的直接子 Git 仓库，不会执行推测出的验证命令；只有显式提供
`--output` 时才会写入一个 manifest 文件。它无法判断真实架构归属，初始化前必须人工确认草稿中的
角色、职责、契约和验证命令。

生成结果如下：

```text
sample-product-harness/
├── AGENTS.md
├── CLAUDE.md
├── README.md
├── repos.yaml
├── sample-product.code-workspace
├── .agents/
│   ├── PLANS.md
│   └── plans/
│       ├── TEMPLATE-cross-repo.md
│       └── TEMPLATE-register-repo.md
├── .cursor/rules/harness-control.mdc
├── .github/copilot-instructions.md
├── scripts/
│   ├── check_harness.py
│   ├── doctor_harness.py
│   └── harness_lib.py
├── contracts/INDEX.md
└── docs/harness/
    ├── inventory.md
    ├── verification.md
    └── PARTICIPANT_AGENTS_TEMPLATE.md
```

初始化器只会写入 `--target`，不会修改 `../sample-api`、`../sample-web` 或其他兄弟仓库。

`AGENTS.md` 是唯一权威的智能体规则。Claude Code 导入它，Cursor 和 Copilot 的适配文件只负责
将工具引导回该文件，详见[AI 编程工具兼容说明](docs/agent-tool-compatibility.zh-CN.md)。

Windows PowerShell 命令和 manifest 字段说明请查看[完整快速开始](docs/quick-start.md)。

如需查看 Java API Provider 与 Web Consumer 之间一次完整的契约变更，请使用
[端到端示例](examples/java-api-web/README.md)。示例包含填写好的执行前 ExecPlan、预期生成结果、
独立的 Maven/npm 验证和回滚边界。

已经使用本地代码图谱的团队还可以参考[Codebase Memory 可选集成](docs/codebase-memory-integration.zh-CN.md)。
结构分析可以建议影响范围，但不能授予 Harness 写入权限。

## 写入边界示例

每次跨仓任务都要复制生成的 ExecPlan 模板，并列出所有已注册仓库：

```markdown
| Repository | Allowed paths | Excluded paths |
| --- | --- | --- |
| harness | .agents/plans/2026-08-31/example.md | all other paths |
| api | src/contracts/openapi.yaml | all other paths |
| web | none | all |
```

`none` 表示没有写入权限。未出现在允许列中的仓库或路径，智能体不得修改。

## 重要安全保证

- 只能有一个角色为 `control`、路径为 `.` 的仓库；
- 参与仓库必须使用父目录下的显式相对路径，绝对路径和越级目录穿越会被拒绝；
- 校验器只读，不会执行参与仓库的验证命令；
- Provider 仓库拥有契约真相，Consumer 快照不能替代它；
- 提交、验证和回滚都保持仓库级独立；
- 发布、部署、权限变更、删除及其他外部副作用仍需独立确认。

设计原因请查看[核心概念](docs/concepts.md)和[安全模型](docs/security-model.md)。

## 项目状态

`0.3.0` 在多 AI 工具适配、统一命令入口、doctor 诊断和独立程序的基础上，增加了只读的相邻仓库
发现与保守验证命令建议。它仍不会自动执行部署、合并 PR、操作 Issue 系统或跨仓运行任意命令。

- [路线图](ROADMAP.md)
- [版本记录](CHANGELOG.md)
- [参与贡献](CONTRIBUTING.md)
- [安全策略](SECURITY.md)
- [最新版本](https://github.com/tomcatlixiaoyao/agentic-cross-repo-harness/releases/latest)

## 本地开发验证

```bash
python -m unittest discover -s tests -p "test_*.py"
python scripts/scan_public.py --root .
```

## 开源协议

MIT，详见 [LICENSE](LICENSE)。
