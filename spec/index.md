# OpenSpec 规格索引

> 这是所有 AI Agent 的入口文件。每次会话开始时，Agent 必须首先阅读此文件。

---

## 阅读顺序

Agent 必须按以下顺序阅读文档：

| 优先级 | 文档       | 路径                        | 说明                                     |
| ------ | ---------- | --------------------------- | ---------------------------------------- |
| 1      | 愿景       | `spec/core/vision.md`       | 系统目标与长期方向                       |
| 2      | 架构       | `spec/core/architecture.md` | 系统分层与组件关系                       |
| 3      | 术语表     | `spec/core/glossary.md`     | 关键术语定义，确保 Agent 与人类用语一致  |
| 4      | 架构决策   | `spec/decisions/ADR-*.md`   | 已有的架构决策记录                       |
| 5      | 功能规格   | `spec/features/*/spec.md`   | 功能级别的设计规格                       |
| 6      | 任务列表   | `spec/features/*/tasks.md`  | 每个功能的实现任务                       |
| 7      | 测试策略   | `spec/workflow/testing-strategy.md` | TDD 工作流与测试分层要求                 |
| 7.5    | 波及分析   | `spec/workflow/impact-analysis.md`  | 变更影响分析与定向测试策略               |
| 8      | 工作流规则 | `spec/workflow/`            | Agent 协作规则（修改任何规格前必须阅读） |

---

## 上下文加载策略

根据任务类型，Agent 应加载不同的文件集合以优化上下文窗口：

### 新功能开发
```
必读: vision.md → architecture.md → glossary.md
然后: 相关 features/*/spec.md → 相关 ADR-*.md
最后: spec/workflow/ai-agent-rules.md
```

### Bug 修复
```
必读: 相关 features/*/spec.md → 相关 tasks.md
然后: spec/workflow/patch-workflow.md
跳过: vision.md, architecture.md（除非 bug 涉及架构）
```

### 架构变更
```
必读: vision.md → architecture.md → 所有 ADR-*.md
然后: spec/workflow/ai-agent-rules.md
最后: 受影响的 features/*/spec.md
```

### 代码审查 / 理解系统
```
必读: vision.md → architecture.md → glossary.md
然后: 按需加载 features/
```

---

## 变更分类

| 变更类型 | 使用方式     | 路径                          | 需要审查 |
| -------- | ------------ | ----------------------------- | -------- |
| Bug 修复 | Patch        | `changes/patches/fix-*.md`    | 可选     |
| 新功能   | Feature Spec | `spec/features/*/spec.md`     | 必须     |
| 架构变更 | ADR          | `spec/decisions/ADR-*.md`     | 必须     |
| 大型变更 | Proposal     | `changes/proposals/prop-*.md` | 必须     |

---

## 目录结构

```
spec/
├── index.md              # AI Agent 入口（本文件）
├── core/                  # 核心文档
│   ├── vision.md          # 愿景与目标
│   ├── architecture.md    # 系统架构
│   └── glossary.md        # 术语表
├── features/              # 功能规格（使用时创建）
│   ├── template.md        # 功能模板
│   ├── tasks-template.md  # 任务模板
│   └── <feature>/         # 具体功能目录
│       ├── spec.md
│       ├── tasks.md
│       └── decisions.md
├── decisions/             # 架构决策记录（ADR）
│   ├── ADR-template.md    # ADR 模板
│   └── ADR-*.md
├── workflow/              # 工作流与规则
│   ├── ai-agent-rules.md  # AI Agent 行为规范
│   ├── spec-workflow.md   # 规格编写流程
│   ├── context-loading.md # 上下文加载指南
│   ├── versioning.md      # 版本控制策略
│   ├── patch-workflow.md  # 补丁工作流
│   ├── testing-strategy.md # TDD 与测试策略
│   └── impact-analysis.md # 波及分析（变更影响与定向测试）
└── archive/               # 已废弃的规格

changes/
├── patches/               # 轻量修复（模板 + 实际补丁）
└── proposals/             # 大型变更提案

examples/                   # 示例（展示如何使用框架，不属于框架本体）
├── user-auth/             # 示例功能: 用户认证
├── example-feature/       # 示例功能: 基础示例
├── decisions/             # 示例 ADR
└── patches/               # 示例补丁
```

---

## 核心原则

1. **Spec First** — 所有实现必须从规格开始
2. **版本追溯** — 使用 git 管理版本，永不覆盖
3. **决策记录** — 架构决策必须写 ADR
4. **任务可追溯** — 每个任务必须关联到规格
5. **渐进式加载** — Agent 按需加载上下文，不浪费 token
6. **框架与内容分离** — 模板和规则是框架，具体功能是使用者的内容
7. **测试先行** — 先写测试，再写实现（TDD: Red → Green → Refactor）
