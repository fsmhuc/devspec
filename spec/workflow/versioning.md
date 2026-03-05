# 版本控制策略

> 所有规格的版本通过 Git 管理，而非文件复制。

---

## 核心原则

**使用 Git，不用文件复制。**

~~错误做法~~：`auth-v1.md`, `auth-v2.md`, `auth-v3.md` → 文件爆炸，难以追踪

**正确做法**：一个文件 `spec.md`，通过 git 历史追踪演变

---

## Git 使用规范

### Commit Message 格式

```
[类型] 简短描述

详细说明（可选）

关联: spec/features/xxx, ADR-XXXX
```

类型前缀：

| 前缀      | 说明         | 示例                                 |
| --------- | ------------ | ------------------------------------ |
| `[spec]`  | 规格变更     | `[spec] my-feature: 添加 OAuth2 支持` |
| `[adr]`   | 架构决策     | `[adr] ADR-0003: 采用 PostgreSQL`     |
| `[task]`  | 任务状态更新 | `[task] my-feature: 完成 API 设计`    |
| `[patch]` | Bug 修复     | `[patch] 修复 IPv6 解析错误`         |
| `[arch]`  | 架构变更     | `[arch] 增加缓存层`                  |
| `[doc]`   | 纯文档更新   | `[doc] 更新 README`                  |

### 分支策略

```
main                    # 稳定版规格
├── feature/xxx         # 新功能的规格+实现
├── adr/xxx             # 架构决策讨论
└── fix/xxx             # Bug 修复
```

---

## 查看规格历史

```bash
# 查看某个规格的变更历史
git log --oneline spec/features/my-feature/spec.md

# 查看两个版本的差异
git diff HEAD~3 HEAD -- spec/features/my-feature/spec.md

# 查看某个时间点的规格
git show HEAD~5:spec/features/my-feature/spec.md
```

---

## 废弃规格

当功能不再需要时：

1. 将规格移至 `spec/archive/`
2. 更新 `spec/index.md` 中的引用
3. 提交: `[spec] archive: 废弃 <feature>，原因: ...`

---

## 规格冲突处理

当多人/多 Agent 同时修改同一规格：

1. 拉取最新版本: `git pull`
2. 如有冲突，保留更完整的版本
3. 冲突解决后记录在 commit message 中
