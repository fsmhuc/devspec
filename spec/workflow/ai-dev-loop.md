# AI 开发循环

> 自动化开发周期编排：验证 → 生成 → 测试 → 分析。

---

## 用途

将规格和实现通过自动化工作流连接起来，形成闭环。

---

## 循环阶段

```
┌─────────────────────────────────────────────────┐
│              AI 开发循环                          │
│                                                 │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│  │ 1. 验证   │ -> │ 2. 生成   │ -> │ 3. 测试  │  │
│  └──────────┘    └──────────┘    └──────────┘  │
│       │                               │         │
│       └─────────── <- ────────────────┘         │
│                    │                            │
│               ┌────▼────┐                       │
│               │ 4. 分析  │                       │
│               └─────────┘                       │
└─────────────────────────────────────────────────┘
```

---

## 阶段详解

### 阶段 1: 验证

运行规格验证器检查一致性。

- **通过** → 进入阶段 2
- **失败** → 停止循环，先修复规格问题

### 阶段 2: 生成

运行规格编译器生成代码制品。

- **通过** → 进入阶段 3
- **失败** → 检查编译器日志

### 阶段 3: 测试

在生成的代码上运行项目测试。

- **通过** → 进入阶段 4
- **跳过** → 如果没有配置测试运行器
- **失败** → 记录失败，进入阶段 4 分析

### 阶段 4: 分析

审查结果并生成建议。

输出:
- 失败阶段的修复建议
- 未完成任务清单
- 规格改进建议

---

## 使用方法

```bash
# 完整循环
python3 tools/ai-dev-loop.py spec

# 跳过测试
python3 tools/ai-dev-loop.py spec --skip-tests

# Shell 包装器
./tools/run-loop.sh spec
```

---

## CI/CD 集成

添加到 `.github/workflows/spec-validation.yml`:

```yaml
name: Spec Validation

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: python3 tools/spec-linter.py spec
      - run: python3 tools/spec-compiler.py spec generated
```
