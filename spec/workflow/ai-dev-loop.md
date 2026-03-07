# AI 开发循环

> 自动化开发周期编排：验证 → 生成 → 波及分析 → 测试 → 分析。

---

## 用途

将规格和实现通过自动化工作流连接起来，形成闭环。

---

## 循环阶段

```
┌───────────────────────────────────────────────────────────┐
│              AI 开发循环（5 阶段）                          │
│                                                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ 1. 验证   │->│ 2. 生成   │->│ 3.波及分析│->│ 4. 测试  │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
│       │                                        │         │
│       └──────────────── <- ────────────────────┘         │
│                         │                                │
│                    ┌────▼────┐                            │
│                    │ 5. 分析  │                            │
│                    └─────────┘                            │
└───────────────────────────────────────────────────────────┘
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

### 阶段 3: 波及分析（新增）

运行波及分析引擎，识别代码变更影响的所有测试。

- 三层分析模型:
  - **Layer 1**: git diff + 命名约定 → 直接关联的测试文件
  - **Layer 2**: 规格依赖图 → 间接受影响功能的测试
  - **Layer 3**: AI Agent 读取 diff 内容，识别跨模块副作用（由 Agent 执行）
- **输出** → 受影响的测试列表传递给测试阶段
- **失败回退** → 分析失败时回退到全量测试（宁可多跑，不可漏跑）

详见: `spec/workflow/impact-analysis.md`

### 阶段 4: 测试（阻断性）

在生成的代码上运行项目测试。**测试失败 = 循环失败。**

- 如果波及分析提供了测试列表 → 执行**定向测试**
- 如果未提供测试列表 → 执行**全量测试**
- **通过** → 进入阶段 5
- **失败** → **停止循环**，按失败分类处理:
  - `regression` — 修复代码
  - `spec_update` — 更新测试（必须关联规格变更）
- **未找到测试运行器** → 发出警告（不再静默跳过）

### 阶段 5: 分析

审查结果并生成建议。

输出:
- 失败阶段的修复建议
- 未完成任务清单
- 规格改进建议

---

## 使用方法

```bash
# 完整循环（含波及分析 + 定向测试）
python3 tools/ai-dev-loop.py spec

# 跳过测试和波及分析（仅限纯规格变更，无代码变更时使用）
python3 tools/ai-dev-loop.py spec --skip-tests

# 单独运行波及分析
python3 tools/impact-analyzer.py
python3 tools/impact-analyzer.py --base origin/main --format json

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

  test:
    runs-on: ubuntu-latest
    needs: validate
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # 波及分析需要 git 历史
      - uses: actions/setup-python@v5
      - name: Impact Analysis
        run: python3 tools/impact-analyzer.py --base origin/main --format json > impact-report.json || true
      - name: Run Tests
        run: python3 -m pytest --tb=short -q || echo 'No tests configured'
```
