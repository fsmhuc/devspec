# DevSpec — AI Agent 配置

> 本文件为 AI 编码 Agent 提供项目级指令。适用于 Claude Code、Cursor、Windsurf 等工具。

---

## 项目概述

DevSpec 是一个 AI 原生的规格框架，用于 AI Agent 与人类协作开发软件。
它通过结构化的规格文档驱动开发，确保设计一致性和决策可追溯性。

---

## 入口文件

**每次会话开始时，必须先阅读 `spec/index.md`**，它会指导你按正确顺序加载上下文。

---

## 上下文加载策略

根据任务类型，加载不同文件以优化上下文窗口：

| 任务类型 | 必读文件                                                     | 可选文件                              |
| -------- | ------------------------------------------------------------ | ------------------------------------- |
| 新功能   | `index.md` → `vision.md` → `architecture.md`                 | 相关 `features/*/spec.md`, `ADR-*.md` |
| Bug 修复 | 相关 `features/*/spec.md` + `tasks.md`                       | `patch-workflow.md`                   |
| 架构变更 | `vision.md` → `architecture.md` → 所有 `ADR-*.md`            | 受影响的 `features/`                  |
| 理解系统 | `index.md` → `vision.md` → `architecture.md` → `glossary.md` | 按需浏览 `features/`                  |

完整指南: `spec/workflow/context-loading.md`

---

## 可用工具

### CLI 工具

```bash
# === 规格管理 ===
python3 mcp/cli.py validate spec           # 验证规格一致性
python3 mcp/cli.py compile spec generated   # 从规格生成代码
python3 mcp/cli.py graph spec tree          # 可视化规格层级
python3 mcp/cli.py list spec                # 列出功能和状态
python3 mcp/cli.py read core/vision.md      # 读取规格文件

# === 创建 ===
python3 mcp/cli.py create-feature my-feature --goals "目标1, 目标2"  # 支持 --rigor lite|full
python3 mcp/cli.py create-adr "决策标题" --context "上下文" --decision "决策"
python3 mcp/cli.py create-delta <name> --target <feature>  # 创建增量规格变更

# === 补丁工作流 ===
python3 mcp/cli.py create-patch <name> --problem "问题" --fix "修复"
python3 mcp/cli.py list-patches
python3 mcp/cli.py complete-patch <name>

# === 验证与归档 ===
python3 mcp/cli.py verify <feature>         # 三维验证（完整性/正确性/一致性）
python3 mcp/cli.py verify --all             # 验证所有功能
python3 mcp/cli.py archive <name>           # 归档已完成的变更
python3 mcp/cli.py list-archive             # 查看已归档变更

# === 开发循环 ===
python3 tools/ai-dev-loop.py spec           # 完整循环
python3 tools/ai-dev-loop.py spec --skip-tests
```

---

## AI Agent 行为规则

### 必须做的
1. **先读 index** — 每次会话从 `spec/index.md` 开始
2. **按需加载** — 不要一次加载所有文件，根据任务类型选择
3. **规格驱动** — 所有实现必须有对应规格
4. **记录决策** — 架构变更写 ADR，功能决策写 `decisions.md`
5. **任务追溯** — 每个任务必须关联到规格
6. **最小变更** — 每次变更尽可能小且聚焦

### 不能做的
1. **不覆盖规格** — 通过 git 追踪变更，不要无记录重写
2. **不猜测** — 不确定时向人类提问
3. **不跳过验证** — 变更后运行 `validate` 确认无错误
4. **不绕过审查门控** — 架构变更和新功能需要人类确认

### 审查门控

| 操作              | 需要人类确认? |
| ----------------- | ------------- |
| 读取/分析文件     | ❌ 否          |
| 运行验证和测试    | ❌ 否          |
| 创建 Patch        | ❌ 否          |
| 更新任务状态      | ❌ 否          |
| 创建/修改功能规格 | ✅ 是          |
| 创建 ADR          | ✅ 是          |
| 修改架构文档      | ✅ 是          |
| 删除/归档文件     | ✅ 是          |

---

## 变更分类

| 变更类型   | 使用方式     | 路径                                |
| ---------- | ------------ | ----------------------------------- |
| Bug 修复   | Patch        | `changes/patches/fix-*.md`          |
| 新功能     | Feature Spec | `spec/features/*/spec.md`           |
| 架构变更   | ADR          | `spec/decisions/ADR-*.md`           |
| 大型变更   | Proposal     | `changes/proposals/prop-*.md`       |
| 增量变更   | Delta Spec   | `changes/proposals/delta-*.md`      |

---

## 工作流

```
1. 阅读 spec/index.md
2. 根据任务类型加载上下文
3. 检查愿景和架构约束
4. 查看现有功能和决策
5. 修改或创建规格
6. 验证变更（python3 mcp/cli.py validate）
7. 按需生成代码
```

---

## 目录结构

```
spec/
├── index.md              # AI Agent 入口
├── core/                  # 核心: 愿景、架构、术语
├── features/              # 功能规格 + 任务
│   ├── template.md        # 功能模板（支持 lite/full 严格度）
│   ├── tasks-template.md  # 任务模板
│   └── <feature>/
├── decisions/             # ADR 文档
│   └── ADR-template.md    # ADR 模板
├── workflow/              # 工作流规则
│   ├── context-loading.md # 上下文加载指南
│   ├── verify.md          # 三维验证（ds:verify）
│   ├── progressive-rigor.md # 渐进式严格度
│   ├── delta-specs.md     # Delta Specs 增量变更
│   └── archive-workflow.md # 归档工作流
└── archive/               # 废弃规格

changes/
├── patches/               # 轻量修复
├── proposals/             # 大型变更提案 + Delta Specs
│   └── delta-template.md  # Delta 模板
└── archive/               # 已完成变更的归档
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

## 错误处理

遇到问题时：
- **规格不完整** → 向人类提问，不要猜测
- **规格冲突** → 列出冲突点，请人类决策
- **实现不确定** → 提出 2-3 个方案供选择
- **工具失败** → 记录错误，尝试替代方案
