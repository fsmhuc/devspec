# AI Agent 指令

> 本仓库使用 DevSpec 框架管理规格和开发流程。所有 AI Agent 必须遵守以下规则。

## 入口

每次会话开始时，先阅读:

```
spec/index.md
```

## 核心规则

1. **先读后写** — 理解系统后再修改
2. **规格驱动** — 实现必须有对应规格
3. **永不覆盖** — 通过 git 追踪，不直接覆盖
4. **架构变更 = ADR** — 影响架构的变更必须先写 ADR
5. **功能符合架构** — 新功能设计不得与架构冲突
6. **废弃归档** — 不用的规格移至 `spec/archive/`
7. **任务关联规格** — 每个任务必须追溯到规格
8. **测试先行（TDD）** — 先写测试，再写实现；测试失败是阻断性事件。详见 `spec/workflow/testing-strategy.md`

## 工作流

```
spec/workflow/spec-workflow.md
```

## 上下文加载

按任务类型加载文件，不要浪费上下文窗口:

```
spec/workflow/context-loading.md
```

## 审查门控

- 读取分析 / 运行工具 / 创建补丁 → 可自主执行
- 修改规格 / 创建 ADR / 删除文件 → 需要人类确认

## 工具

```bash
python3 mcp/cli.py validate spec     # 验证规格
python3 mcp/cli.py compile spec generated  # 生成代码
python3 mcp/cli.py graph spec tree   # 查看结构
python3 mcp/cli.py list spec         # 列出功能
python3 tools/ai-dev-loop.py spec    # 完整开发循环（含测试阻断）
python3 tools/impact-analyzer.py      # 波及分析（变更影响范围测试）
```
