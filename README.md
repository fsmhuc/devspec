# DevSpec

AI 原生的规格驱动开发框架 — 让 AI Agent 与人类高效协作开发软件。

---

## 什么是 DevSpec？

DevSpec 提供一套可复用的规格工作流，解决 AI 协作开发中的核心问题：

| 问题            | DevSpec 方案            |
| --------------- | ------------------------ |
| 规格漂移        | 自动化验证保持一致性     |
| AI 不知从何入手 | 结构化入口和行为规范     |
| 决策无记录      | ADR 记录所有架构决策     |
| 任务无追溯      | 任务 → 规格 → 愿景全链路 |
| 代码和设计脱节  | 规格编译器自动生成代码桩 |

---

## 快速开始

### 1. 复制到你的项目

```bash
cp -r spec/ tools/ mcp/ .github/ /path/to/your/project/
```

### 2. 定义愿景

编辑 `spec/core/vision.md`:

```markdown
# 系统愿景

## 使命
为 AI Agent 和人类团队提供结构化的协作开发框架

## 核心目标
1. 防止规格漂移
2. 支持 AI 驱动开发
3. 决策可追溯
```

### 3. 定义架构

编辑 `spec/core/architecture.md`:

```markdown
# 系统架构

## 架构概览
分层架构: 规格层 → 实现层 → 运行时层

## 架构约束
1. 功能不得与架构冲突
2. 架构变更需要 ADR
```

### 4. 添加功能

```bash
python3 mcp/cli.py create-feature my-feature --goals "目标1, 目标2"
```

### 5. 验证 & 生成

```bash
# 验证规格
python3 mcp/cli.py validate

# 生成代码桩
python3 mcp/cli.py compile spec generated

# 查看规格结构
python3 mcp/cli.py graph spec tree

# 完整开发循环
python3 tools/ai-dev-loop.py spec
```

### 6. 初始化混合模式（Claude CLI / OpenCode）

```bash
# 生成 .claude/ 与 .opencode/ 的 commands 和 skills 模板
python3 mcp/cli.py init

# 查看推荐工作流（对话优先 + 命令检查点）
python3 mcp/cli.py workflow
```

---

## 规格分层

```
愿景层 (Why)        — 为什么做这个系统
    │
    ▼
架构层 (What)       — 系统由什么组成
    │
    ▼
功能层 (How)        — 每个功能怎么设计
    │
    ▼
任务层 (Do)         — 具体做什么事
    │
    ▼
实现层 (Code)       — 代码和制品
```

---

## AI Agent 入口

AI Agent 应从以下文件开始:

```
spec/index.md
```

这个索引会引导 Agent 按正确顺序加载上下文。

---

## 项目结构

```
devspec/
├── spec/                       # 规格文档（框架核心）
│   ├── index.md               # AI Agent 入口
│   ├── core/                  # 核心: 愿景 & 架构
│   │   ├── vision.md          # 系统愿景与目标
│   │   ├── architecture.md    # 系统架构与约束
│   │   └── glossary.md        # 术语表
│   ├── features/              # 功能规格（使用时创建）
│   │   ├── template.md        # 功能模板（含验收标准、非目标等）
│   │   └── tasks-template.md  # 任务模板（含优先级、依赖）
│   ├── decisions/             # 架构决策记录（ADR）
│   │   └── ADR-template.md    # ADR 模板
│   ├── workflow/              # 工作流规则
│   │   ├── ai-agent-rules.md  # AI Agent 行为规范
│   │   ├── spec-workflow.md   # 规格编写流程
│   │   ├── context-loading.md # 上下文加载指南
│   │   ├── versioning.md      # 版本控制策略
│   │   ├── patch-workflow.md  # 补丁工作流
│   │   ├── testing-strategy.md # TDD 与测试策略
│   │   ├── impact-analysis.md # 波及分析与影响范围测试
│   │   ├── verify.md          # 三维验证（ds:verify）
│   │   ├── progressive-rigor.md # 渐进式严格度（Lite/Full）
│   │   ├── delta-specs.md     # Delta Specs 增量变更工作流
│   │   └── archive-workflow.md # 归档工作流
│   └── archive/               # 已废弃的规格
├── tools/                      # 自动化工具
│   ├── spec-linter.py         # 规格验证
│   ├── spec-compiler.py       # 代码生成
│   ├── spec-graph.py          # 结构可视化
│   ├── ai-dev-loop.py         # 开发循环编排
│   ├── run-loop.sh            # 循环运行脚本
│   └── impact-analyzer.py     # 波及分析引擎
├── mcp/                        # MCP Server & CLI
│   ├── cli.py                 # CLI 工具
│   └── server.py              # MCP Server
├── examples/                   # 示例（展示框架用法，不属于框架本体）
│   ├── user-auth/             # 示例: 用户认证功能
│   ├── example-feature/       # 示例: 基础功能
│   ├── decisions/             # 示例: ADR
│   └── patches/               # 示例: 补丁
├── changes/                    # 变更管理
│   ├── patches/               # Bug 修复（轻量）
│   ├── proposals/             # 大型变更提案 + Delta Specs
│   │   └── delta-template.md  # Delta 模板
│   └── archive/               # 已完成变更的归档
└── .github/
    ├── copilot-instructions.md # AI 指令
    └── workflows/
        └── spec-validation.yml
```

---

## 工具链

| 工具         | 命令                                       | 说明                   |
| ------------ | ------------------------------------------ | ---------------------- |
| **验证器**   | `python3 mcp/cli.py validate`              | 检查规格一致性和完整性 |
| **三维验证** | `python3 mcp/cli.py verify <feature>`      | 完整性/正确性/一致性语义验证 |
| **编译器**   | `python3 mcp/cli.py compile`               | 从规格生成代码桩       |
| **可视化**   | `python3 mcp/cli.py graph spec tree`       | 查看规格层级结构       |
| **开发循环** | `python3 tools/ai-dev-loop.py spec`        | 验证→生成→波及分析→测试→分析    |
| **功能创建** | `python3 mcp/cli.py create-feature <name>` | 创建功能规格骨架（支持 --rigor） |
| **ADR 创建** | `python3 mcp/cli.py create-adr <title>`    | 创建架构决策记录       |
| **Delta 创建** | `python3 mcp/cli.py create-delta <name>`   | 创建增量规格变更       |
| **归档**     | `python3 mcp/cli.py archive <name>`        | 归档已完成的变更       |
| **归档列表** | `python3 mcp/cli.py list-archive`          | 查看已归档变更         |
| **混合初始化** | `python3 mcp/cli.py init`                 | 生成 Claude CLI / OpenCode 命令与技能模板 |
| **工作流提示** | `python3 mcp/cli.py workflow`             | 查看混合模式推荐流程 |
| **波及分析** | `python3 tools/impact-analyzer.py`         | 分析代码变更的测试影响范围 |

---

## 混合模式（推荐）

默认采用"对话驱动为主，命令驱动为辅"：

- 对话驱动：让 AI 读取 `spec/index.md` 并按任务上下文推进设计与实现
- 命令检查点：在关键节点执行 `validate / compile / graph / loop`
- Slash 别名：可直接运行 `python3 mcp/cli.py ds:validate` 等别名命令
- 同时支持 **Claude CLI**（`.claude/commands/`）和 **OpenCode**（`.opencode/commands/`）

可用别名：

- `ds:validate`
- `ds:verify`
- `ds:compile`
- `ds:graph`
- `ds:loop`
- `ds:workflow`
- `ds:impact`
- `ds:archive`
- `ds:list-archive`
- `ds:create-delta`
---

## 核心原则

1. **Spec First** — 所有实现从规格开始
2. **Git 版本控制** — 通过 git 追踪变更，不用文件复制
3. **决策记录** — 架构决策写 ADR，功能决策写 decisions.md
4. **永不覆盖** — 不直接覆盖规格，通过 git 追踪变更
5. **废弃归档** — 不用的规格移至 archive
6. **按需加载** — Agent 根据任务类型加载最少必要的上下文
7. **测试先行** — 先写测试，再写实现（TDD: Red → Green → Refactor）
---

## AI Agent 规则

AI Agent 必须遵守:

1. 先读后写 — 理解系统后再修改
2. 规格驱动 — 所有实现有对应规格
3. 最小变更 — 每次变更尽可能小且聚焦
4. 永不覆盖 — 通过 git 追踪
5. 架构变更需 ADR — 影响架构的变更先写决策
6. 不确定就问 — 不猜测
7. 测试先行 — 先写测试，再写实现（TDD）

详见 `spec/workflow/ai-agent-rules.md`

---

## 变更分类

| 变更类型 | 方式         | 路径                          | 需审查 |
| -------- | ------------ | ----------------------------- | ------ |
| Bug 修复 | Patch        | `changes/patches/fix-*.md`    | 可选   |
| 新功能   | Feature Spec | `spec/features/*/spec.md`     | 必须   |
| 架构变更 | ADR          | `spec/decisions/ADR-*.md`     | 必须   |
| 大型变更 | Proposal     | `changes/proposals/prop-*.md` | 必须   |

---

## CI/CD 集成

```yaml
# .github/workflows/spec-validation.yml
name: Spec Validation
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: python3 tools/spec-linter.py spec
      - run: python3 tools/spec-compiler.py spec generated
```

---

## MCP Server 集成

```json
{
    "mcpServers": {
        "devspec": {
            "command": "python3",
            "args": ["/path/to/devspec/mcp/server.py"]
        }
    }
}
```

---

## 文档

- [快速开始](docs/QUICKSTART.md)
- [架构说明](docs/ARCHITECTURE.md)
- [Architecture Overview](docs/ARCHITECTURE.md)
- [DevSpec Pro](spec/workflow/devspec-pro.md)
- [AI Agent Rules](spec/workflow/ai-agent-rules.md)

---

## Why DevSpec?

| Problem | Solution |
|---------|----------|
| AI randomly modifies specs | Workflow rules prevent overwrites |
| Specs get overwritten | Versioning preserves history |
| Design drift | ADRs track decisions |
| AI doesn't know where to start | `spec/index.md` entry point |
| Features become disorganized | Structured `features/` directory |

---

## License

MIT License
