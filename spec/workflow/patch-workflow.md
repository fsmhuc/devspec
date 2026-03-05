# 补丁工作流

> 用于不涉及规格变更的轻量 Bug 修复。

---

## 什么时候用 Patch

| 场景              | 用 Patch?              |
| ----------------- | ---------------------- |
| Bug 修复          | ✅ 是                   |
| 拼写错误 / 小修正 | ✅ 是                   |
| 小重构            | ✅ 是                   |
| 配置修改          | ✅ 是                   |
| 新功能            | ❌ 否 — 用 Feature Spec |
| 架构变更          | ❌ 否 — 用 ADR          |
| 破坏性变更        | ❌ 否 — 用 Proposal     |

---

## Patch vs Proposal 决策树

```
这个变更:
├── 会影响规格文档？
│   ├── 否 → Patch ✅
│   └── 是 → 会影响架构？
│       ├── 否 → Proposal（小型）
│       └── 是 → ADR + Proposal
```

---

## 工作流程

### 1. 创建 Patch 文件

```bash
# 通过 CLI
python3 mcp/cli.py create-patch <name> --problem "问题描述" --fix "修复方案"

# 或手动创建
changes/patches/fix-<描述>.md
```

### 2. 记录问题和修复方案

在 patch 文件中填写：
- 问题的根因
- 修复的具体方案
- 影响范围

### 3. 实施修复

- 按 patch 文件中的方案修改代码
- 修复应该尽可能小且聚焦

### 4. 验证

- [ ] 运行相关测试
- [ ] 运行 `python3 mcp/cli.py validate`
- [ ] 确认没有引入新问题

### 5. 提交

```bash
git commit -m "[patch] <简短描述>"
```

### 6. 标记完成

```bash
python3 mcp/cli.py complete-patch <name>
```

---

## 命名规范

```
changes/patches/fix-<简短描述>.md

示例:
- fix-ipv6-parse.md
- fix-login-timeout.md
- fix-memory-leak-worker.md
```

---

## 目录结构

```
changes/
├── patches/               # Bug 修复（轻量）
│   ├── patch-template.md  # 补丁模板
│   └── fix-*.md           # 具体补丁
└── proposals/             # 大型变更（需审查）
    ├── proposal-template.md
    └── prop-*.md
```
