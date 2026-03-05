# OpenSpec Framework

AI 原生的规格驱动开发框架。

---

## 快速链接

- [快速开始](docs/QUICKSTART.md)
- [架构说明](docs/ARCHITECTURE.md)
- [AI Agent 行为规范](spec/workflow/ai-agent-rules.md)
- [OpenSpec Pro](spec/workflow/openspec-pro.md)

---

## 项目结构

```
openspec-framework/
├── README.md              # 项目说明
├── CLAUDE.md              # AI Agent 配置
├── spec/                  # 规格文档
│   ├── index.md          # AI Agent 入口
│   ├── core/             # 愿景、架构、术语
│   ├── features/         # 功能规格模板
│   ├── decisions/        # ADR 模板
│   └── workflow/         # 工作流规则
├── tools/                 # 自动化工具
├── mcp/                   # MCP Server & CLI
├── examples/              # 示例（展示如何使用框架）
├── docs/                  # 用户文档
└── .github/               # CI/CD & AI 指令
```

---

## 使用方式

### 1. 复制到你的项目

```bash
cp -r spec/ tools/ mcp/ .github/ /your/project/
```

### 2. 定义规格

- 编辑 `spec/core/vision.md`
- 编辑 `spec/core/architecture.md`
- 用 `python3 mcp/cli.py create-feature <name>` 添加功能

### 3. 验证

```bash
python3 mcp/cli.py validate
```

### 4. 生成

```bash
python3 mcp/cli.py compile spec generated
```

### 5. 可视化

```bash
python3 mcp/cli.py graph spec tree
```

### 6. 完整开发循环

```bash
python3 tools/ai-dev-loop.py spec
```

---

## AI Agent 入口

AI Agent 从以下文件开始:

```
spec/index.md
```

---

## 核心原则

1. **Spec First** — 所有实现从规格开始
2. **Git 版本控制** — 通过 git 追踪变更
3. **决策记录** — 架构决策写 ADR
4. **永不覆盖** — 通过 git 管理版本
5. **废弃归档** — 不用的规格移至 archive

---

## 工具链

| 工具     | 命令                                 | 说明       |
| -------- | ------------------------------------ | ---------- |
| 验证     | `python3 mcp/cli.py validate`        | 检查一致性 |
| 编译     | `python3 mcp/cli.py compile`         | 生成代码   |
| 可视化   | `python3 mcp/cli.py graph spec tree` | 查看结构   |
| 开发循环 | `python3 tools/ai-dev-loop.py spec`  | 自动化流程 |
