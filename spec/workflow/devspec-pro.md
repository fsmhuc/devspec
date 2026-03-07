# DevSpec Pro

> 高级 AI 原生规格系统的工具链。

---

## 工具组件

### 1. 规格验证器（Spec Validator）

验证规格的一致性和完整性。

```bash
python3 mcp/cli.py validate spec
python3 tools/spec-linter.py spec
```

检查项：
- 必要文件是否存在
- 必要章节是否完整
- 功能是否与架构冲突
- 任务是否关联到规格
- 是否有孤立规格

详见: `spec/workflow/spec-validator.md`

### 2. 规格编译器（Spec Compiler）

从规格生成代码桩、API Schema、文档和测试模板。

```bash
python3 mcp/cli.py compile spec generated
python3 tools/spec-compiler.py spec generated
```

详见: `spec/workflow/spec-compiler.md`

### 3. 规格图（Spec Graph）

可视化规格层级和依赖关系。

```bash
python3 mcp/cli.py graph spec tree     # ASCII 树
python3 mcp/cli.py graph spec mermaid  # Mermaid 图
python3 mcp/cli.py graph spec json     # JSON 结构
```

详见: `spec/workflow/spec-graph.md`

### 4. AI 开发循环（AI Dev Loop）

自动化开发周期：验证 → 生成 → 测试 → 分析。

```bash
python3 tools/ai-dev-loop.py spec
python3 tools/ai-dev-loop.py spec --skip-tests
```

详见: `spec/workflow/ai-dev-loop.md`

---

## 架构

```
┌─────────────────────────────────────────────────────────┐
│                    DevSpec Pro                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│   spec/                                                 │
│   ├── index.md ──────> [验证器] ────┐                   │
│   ├── core/                          │                   │
│   ├── features/                      ▼                   │
│   └── decisions/ ────> [编译器] ───> generated/          │
│                              │                          │
│                              ▼                          │
│                         [规格图] ───> 可视化              │
│                                                         │
│   [AI Dev Loop] 串联上述工具，自动化执行                   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 快速开始

```bash
# 1. 定义规格
#    编辑 spec/ 目录下的文件

# 2. 验证规格
python3 mcp/cli.py validate

# 3. 生成代码
python3 mcp/cli.py compile

# 4. 查看结构
python3 mcp/cli.py graph spec tree

# 5. 完整循环
python3 tools/ai-dev-loop.py spec
```
