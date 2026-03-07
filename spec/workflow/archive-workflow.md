# 归档工作流

> 已完成的变更（Patch / Proposal / Delta）移入归档目录，保持活动区干净，同时保留完整审计轨迹。

---

## 核心理念

`changes/patches/` 和 `changes/proposals/` 只保留**活动中**的变更。
完成后归档到 `changes/archive/`，确保：

1. **活动区干净** — 只看到正在进行的工作
2. **审计轨迹完整** — 归档保留原始文档和合并记录
3. **可回溯** — 任何历史变更都能在 archive 中找到

---

## 归档流程

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│ 1. 变更已完成     │ ──> │ 2. 运行归档命令   │ ──> │ 3. 验证归档结果   │
└──────────────────┘     └──────────────────┘     └──────────────────┘
```

### 1. 确认变更已完成

归档前确认：
- Patch: 所有检查清单已勾选，修复已验证
- Proposal: 规格变更已合并，实现已完成
- Delta: 已合并到目标规格，验证通过

### 2. 运行归档命令

```bash
# 归档单个变更
python3 mcp/cli.py archive <name>

# 列出可归档的变更
python3 mcp/cli.py list-archive
```

归档操作会：
1. 在 `changes/archive/` 下创建 `YYYY-MM-DD-<name>/` 目录
2. 将原始文件移入该目录
3. 生成 `summary.md` 记录归档元信息

### 3. 验证归档结果

```bash
python3 mcp/cli.py validate
```

确认归档后：
- 原文件已从活动区移除
- 归档目录结构正确
- 无引用断裂

---

## 归档目录结构

```
changes/
├── patches/                    # 活动中的补丁
│   └── patch-template.md
├── proposals/                  # 活动中的提案和 Delta
│   ├── proposal-template.md
│   └── delta-template.md
└── archive/                    # 已完成的变更归档
    ├── 2025-03-07-fix-login-timeout/
    │   ├── fix-login-timeout.md   # 原始补丁文件
    │   └── summary.md             # 归档摘要
    ├── 2025-03-07-delta-add-export/
    │   ├── delta-add-export.md    # 原始 Delta 文件
    │   └── summary.md             # 归档摘要
    └── ...
```

### summary.md 格式

```markdown
# 归档摘要

| 字段       | 值                            |
| ---------- | ----------------------------- |
| 变更类型   | patch / proposal / delta      |
| 原始路径   | changes/patches/fix-xxx.md    |
| 归档日期   | YYYY-MM-DD                    |
| 归档原因   | 变更已完成并验证               |

## 变更概述

一句话描述完成了什么。

## 关联

- Commit: <git commit hash>
- 目标规格: <spec path>（如适用）
```

---

## 归档触发条件

| 变更类型 | 何时归档                           |
| -------- | ---------------------------------- |
| Patch    | 修复已提交且测试通过               |
| Proposal | 所有规格变更已合并、实现已完成     |
| Delta    | Delta 已合并到目标规格、验证通过   |

---

## 命名规范

```
changes/archive/YYYY-MM-DD-<原始文件名无扩展名>/

示例:
- 2025-03-07-fix-login-timeout/
- 2025-03-07-delta-add-batch-export/
- 2025-03-07-prop-new-auth-flow/
```

---

## 注意事项

- 归档是**移动**操作，不是复制。原始文件从活动区移除
- 归档后的文件**只读**，不应再修改
- 如果归档的变更需要回滚，创建新的 Patch 或 Delta，不要修改归档
- Git 会追踪文件移动，所以 `git log --follow` 仍可查看完整历史
