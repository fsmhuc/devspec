# 快速开始

5 分钟上手 DevSpec。

---

## 1. 复制到你的项目

```bash
cp -r spec/ tools/ mcp/ .github/ /path/to/your/project/
```

---

## 2. 定义愿景

编辑 `spec/core/vision.md`（参考模板中的注释）：

```markdown
# 系统愿景

## 使命
[一句话描述系统目标]

## 核心目标
1. 目标 1
2. 目标 2

## 非目标
- 不做的事情
```

---

## 3. 定义架构

编辑 `spec/core/architecture.md`：

```markdown
# 系统架构

## 架构概览
[整体架构风格]

## 系统分层
1. 前端
2. API
3. 数据库

## 架构约束
- 功能不得与架构冲突
- 架构变更需要 ADR
```

---

## 4. 添加功能

```bash
python3 mcp/cli.py create-feature my-feature --goals "目标1, 目标2"
```

然后编辑生成的文件：
- `spec/features/my-feature/spec.md` — 功能规格
- `spec/features/my-feature/tasks.md` — 任务列表

---

## 5. 验证

```bash
python3 mcp/cli.py validate
```

---

## 6. 生成代码

```bash
python3 mcp/cli.py compile spec generated
```

---

## 7. 查看结构

```bash
python3 mcp/cli.py graph spec tree
```

---

## 8. 完整开发循环

```bash
python3 tools/ai-dev-loop.py spec
```

---

## 9. 混合模式（推荐）

“对话驱动为主，命令驱动为辅”：

```bash
# 初始化 Claude 命令/技能模板
python3 mcp/cli.py init

# 查看推荐工作流
python3 mcp/cli.py workflow

# 关键检查点（可在对话过程中随时执行）
python3 mcp/cli.py ds:validate
python3 mcp/cli.py ds:compile
python3 mcp/cli.py ds:graph
python3 mcp/cli.py ds:loop
```

---

## 下一步

- 阅读 `spec/workflow/ai-agent-rules.md` 了解 AI 行为规范
- 阅读 `spec/workflow/context-loading.md` 了解上下文加载策略
- 查看 `examples/` 目录中的示例
- 配置 CI/CD: `.github/workflows/spec-validation.yml`
