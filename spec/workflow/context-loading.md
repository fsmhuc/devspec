# 上下文加载指南

> 指导 AI Agent 根据任务类型高效加载文件，避免浪费上下文窗口。

---

## 为什么需要这个指南

AI Agent 的上下文窗口是有限的。加载不必要的文件会：
- 浪费 token
- 稀释关键信息
- 降低回答质量

**原则: 按需加载，最小必要。**

---

## 按任务类型的加载策略

### 🆕 新功能开发

```
第一步（必读）:
  spec/core/vision.md          # 确认功能符合愿景
  spec/core/architecture.md    # 确认不违反架构

第二步（相关上下文）:
  spec/features/*/spec.md      # 只加载相关功能的规格
  spec/decisions/ADR-*.md      # 只加载相关的 ADR

第三步（规则）:
  spec/workflow/ai-agent-rules.md
  spec/workflow/spec-workflow.md

跳过:
  - 无关功能的 spec.md 和 tasks.md
  - archive/ 目录
  - generated/ 目录
```

### 🐛 Bug 修复

```
第一步（必读）:
  spec/features/<相关功能>/spec.md   # 理解功能设计
  spec/features/<相关功能>/tasks.md  # 查看任务状态

第二步（规则）:
  spec/workflow/patch-workflow.md    # 了解补丁流程

跳过:
  - vision.md（除非 bug 影响系统方向）
  - architecture.md（除非 bug 涉及架构）
  - 无关功能的文件
```

### 🏗️ 架构变更

```
第一步（必读）:
  spec/core/vision.md               # 变更是否符合愿景
  spec/core/architecture.md         # 当前架构是什么
  spec/decisions/ADR-*.md           # 所有已有决策

第二步（影响分析）:
  spec/features/*/spec.md           # 哪些功能会受影响

第三步（规则）:
  spec/workflow/ai-agent-rules.md   # 审查门控规则
```

### 📖 理解系统 / 代码审查

```
第一步:
  spec/index.md                     # 概览
  spec/core/vision.md               # 为什么
  spec/core/architecture.md         # 是什么

第二步:
  spec/core/glossary.md             # 术语统一
  spec/features/（按需浏览）

第三步:
  spec/decisions/（按需浏览）
```

### ✅ 更新任务状态

```
只需加载:
  spec/features/<功能>/tasks.md     # 直接更新

跳过: 其他所有文件
```

---

## 加载优先级矩阵

| 文件 | 新功能 | Bug修复 | 架构变更 | 理解系统 |
|------|--------|---------|----------|----------|
| vision.md | ⭐必读 | ⬜跳过 | ⭐必读 | ⭐必读 |
| architecture.md | ⭐必读 | ⬜跳过 | ⭐必读 | ⭐必读 |
| glossary.md | 🔵推荐 | ⬜跳过 | 🔵推荐 | ⭐必读 |
| 相关 ADR | 🔵推荐 | ⬜跳过 | ⭐必读 | 🔵推荐 |
| 相关 spec.md | ⭐必读 | ⭐必读 | ⭐必读 | 🔵推荐 |
| 相关 tasks.md | 🔵推荐 | ⭐必读 | ⬜跳过 | ⬜跳过 |
| ai-agent-rules.md | ⭐必读 | ⬜跳过 | ⭐必读 | ⬜跳过 |

图例: ⭐必读 | 🔵推荐 | ⬜跳过

---

## 大型项目的分批加载

当功能数量超过 10 个时：

1. 先加载 `spec/index.md` 获取功能列表
2. 只加载与当前任务直接相关的 2-3 个功能
3. 如果发现需要更多上下文，再按需加载
4. 永远不要一次性加载所有功能规格
