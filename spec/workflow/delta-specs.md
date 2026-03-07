# Delta Specs 工作流

> 规格变更使用增量（Delta）格式描述，确保每次变更可追溯、可审查、可归档。

---

## 核心理念

传统方式直接编辑规格文件，变更历史只能依赖 git diff。
Delta Specs 要求**先描述变更意图，再合并到主规格**，实现：

1. **变更可审查** — 每次规格变更都有独立的 Delta 文档
2. **意图可追溯** — Delta 记录了"为什么改"和"改了什么"
3. **冲突可检测** — 多个 Delta 修改同一节时，归档阶段自动检测
4. **演进可回溯** — Archive 保留所有历史 Delta

---

## Delta 类型

| 标记         | 含义     | 说明                     |
| ------------ | -------- | ------------------------ |
| `[ADDED]`    | 新增     | 在目标规格中添加新内容   |
| `[MODIFIED]` | 修改     | 修改目标规格中的现有内容 |
| `[REMOVED]`  | 删除     | 从目标规格中移除内容     |

---

## 工作流程

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ 1. 创建 Delta │ ──> │ 2. 审查确认   │ ──> │ 3. 合并到规格 │
└──────────────┘     └──────────────┘     └──────────────┘
                                                │
                     ┌──────────────┐     ┌─────┴────────┐
                     │ 5. 归档 Delta │ <── │ 4. 验证一致性 │
                     └──────────────┘     └──────────────┘
```

### 1. 创建 Delta

```bash
# 通过 CLI
python3 mcp/cli.py create-delta <name> --target <spec-path>

# 或手动创建
changes/proposals/delta-<描述>.md
```

使用模板 `changes/proposals/delta-template.md`，填写：
- 目标规格路径
- [ADDED] / [MODIFIED] / [REMOVED] 各节内容
- 影响分析

### 2. 审查确认

规格变更属于**审查门控**操作（见 `ai-agent-rules.md`），需要人类确认。

审查要点：
- Delta 内容是否准确反映变更意图？
- 影响分析是否完整？
- 是否需要创建 ADR？

### 3. 合并到规格

审查通过后，将 Delta 内容合并到目标规格文件：
- `[ADDED]` → 添加到目标节
- `[MODIFIED]` → 替换目标节中的对应内容
- `[REMOVED]` → 从目标节中移除

```bash
# 合并后验证
python3 mcp/cli.py validate
```

### 4. 验证一致性

合并后运行验证，确保：
- 规格结构完整
- 引用关系正确
- 无冲突

### 5. 归档 Delta

合并完成后，Delta 文件移入归档：

```bash
python3 mcp/cli.py archive <delta-name>
```

归档路径：`changes/archive/YYYY-MM-DD-<name>/`

---

## 适用场景

| 场景           | 是否使用 Delta? |
| -------------- | --------------- |
| 新功能规格     | ✅ 是（首次创建用 Feature Spec，后续修改用 Delta） |
| 修改现有规格   | ✅ 是           |
| 架构变更       | ✅ 是（配合 ADR） |
| Bug 修复       | ❌ 否（用 Patch，不涉及规格变更） |
| 纯文档更新     | ❌ 否（直接修改） |

---

## 与现有工作流的关系

- **Patch 工作流** — 不变。Patch 用于代码修复，不涉及规格
- **Proposal 工作流** — 大型变更仍使用 Proposal，但 Proposal 中的规格变更部分使用 Delta 格式
- **Feature Spec** — 首次创建用完整模板，后续修改用 Delta
- **ADR** — 架构变更仍需 ADR，Delta 与 ADR 关联

---

## 命名规范

```
changes/proposals/delta-<简短描述>.md

示例:
- delta-add-batch-export.md
- delta-modify-auth-flow.md
- delta-remove-legacy-api.md
```
