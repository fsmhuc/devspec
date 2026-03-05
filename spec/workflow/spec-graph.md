# 规格图

> 可视化规格层级结构和依赖关系。

---

## 用途

提供规格结构的可视化概览，帮助理解系统全貌。

---

## 输出格式

### ASCII 树

```bash
python3 mcp/cli.py graph spec tree
```

示例输出:

```
OpenSpec Hierarchy

└── 📁 OpenSpec
    ├── 🎯 愿景
    ├── 🏗️ 架构
    ├── 📚 功能
    │   ├── 📦 my-feature
    │   │   └── ✅ 任务 [2/4]
    └── 📋 决策
        └── 📝 ADR-0001-xxx
```

### Mermaid 图

```bash
python3 mcp/cli.py graph spec mermaid
```

生成 Mermaid 流程图，可嵌入文档。

### JSON 结构

```bash
python3 mcp/cli.py graph spec json
```

机器可读的图结构数据。

---

## 集成方式

| 用途         | 格式      |
| ------------ | --------- |
| 终端浏览     | `tree`    |
| 文档嵌入     | `mermaid` |
| CI/CD 流水线 | `json`    |
| IDE 插件     | `json`    |
