# OpenSpec Framework 架构

---

## 概述

OpenSpec 是一个 AI 原生的规格框架，专为人类与 AI Agent 协作开发而设计。

---

## 设计原则

1. **Spec First** — 所有实现从规格开始
2. **Git 版本控制** — 通过 git 追踪变更，不用文件复制
3. **决策记录** — 架构决策写 ADR
4. **持续验证** — 自动化工具确保一致性
5. **从规格生成** — 代码从规格派生

---

## 目录结构

```
openspec-framework/
├── spec/                    # 规格文档（框架核心）
│   ├── index.md            # AI Agent 入口
│   ├── core/               # 愿景、架构、术语
│   ├── features/           # 功能规格模板（空目录，使用时填充）
│   ├── decisions/          # ADR 模板
│   ├── workflow/           # 工作流规则
│   └── archive/            # 废弃规格
├── tools/                   # 自动化工具
│   ├── spec-linter.py      # 验证
│   ├── spec-compiler.py    # 代码生成
│   ├── spec-graph.py       # 可视化
│   └── ai-dev-loop.py      # 开发循环
├── mcp/                     # MCP Server & CLI
├── examples/                # 示例（不属于框架本体）
├── docs/                    # 用户文档
└── .github/                 # CI/CD & AI 指令
```

---

## 规格分层

```
愿景层 (Why)        — spec/core/vision.md
    │
    ▼
架构层 (What)       — spec/core/architecture.md
    │
    ▼
功能层 (How)        — spec/features/*/spec.md
    │
    ▼
任务层 (Do)         — spec/features/*/tasks.md
```

---

## 工具流水线

```
spec/
  │
  ├── spec-linter.py ───> 验证报告
  │
  ├── spec-compiler.py ─> generated/
  │                         ├── stubs/    代码桩
  │                         ├── schemas/  API Schema
  │                         ├── docs/     文档
  │                         └── tests/    测试模板
  │
  └── spec-graph.py ────> 可视化（tree / mermaid / json）
```

---

## AI 集成

### 入口

AI Agent 从 `spec/index.md` 开始阅读。

### 行为规范

AI Agent 遵循 `spec/workflow/ai-agent-rules.md`。

### 上下文加载

AI Agent 按 `spec/workflow/context-loading.md` 的策略按需加载文件。

### GitHub Copilot

`.github/copilot-instructions.md` 提供仓库级别的 AI 指令。

---

## 扩展点

1. **自定义验证器** — 继承 `SpecLinter` 类
2. **代码生成器** — 继承 `SpecCompiler` 类，添加更多语言支持
3. **输出格式** — 继承 `SpecGraph` 类，增加输出格式
4. **循环阶段** — 修改 `AIDevLoop` 类，添加自定义阶段
