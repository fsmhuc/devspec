# 波及分析（Impact Analysis）

> 代码变更后，自动识别所有受影响的测试，确保不遗漏回归风险。宁可多跑，不可漏跑。

---

## 核心理念

代码变更的影响范围往往超出直觉判断。波及分析通过三层模型系统性地识别受影响的测试，
替代"只跑新写的测试"这种不充分的做法。

---

## 三层分析模型

```
┌──────────────────────────────────────────────────────┐
│                  波及分析三层模型                       │
│                                                      │
│  ┌─────────────────┐                                 │
│  │ Layer 1          │  git diff → 命名约定映射         │
│  │ 确定性 · 高置信度 │  src/auth.py → tests/test_auth.py │
│  └────────┬────────┘                                 │
│           ▼                                          │
│  ┌─────────────────┐                                 │
│  │ Layer 2          │  规格依赖图 → 功能关联测试        │
│  │ 确定性 · 中置信度 │  feature-A 依赖 feature-B        │
│  └────────┬────────┘                                 │
│           ▼                                          │
│  ┌─────────────────┐                                 │
│  │ Layer 3          │  AI Agent 读取 diff 内容         │
│  │ 概率性 · 需判断   │  识别跨模块副作用               │
│  └─────────────────┘                                 │
└──────────────────────────────────────────────────────┘
```

### Layer 1: 命名约定映射（确定性）

通过 git diff 获取变更文件列表，按命名约定映射到对应的测试文件。

**默认映射规则:**

| 源文件模式 | 测试文件模式 |
|-----------|-------------|
| `src/**/*.py` | `tests/**/test_{basename}.py` |
| `src/**/*.ts` | `tests/**/{basename}.test.ts` |
| `src/**/*.tsx` | `tests/**/{basename}.test.tsx` |
| `src/**/*.js` | `tests/**/{basename}.test.js` |
| `lib/**/*.go` | `lib/**/{basename}_test.go` |

**自定义映射:** 在 `.devspec/impact.yml` 中配置:

```yaml
mapping_rules:
  - pattern: "src/**/*.py"
    test_pattern: "tests/**/test_{basename}.py"
  - pattern: "src/**/*.ts"
    test_pattern: "tests/**/{basename}.test.ts"
```

### Layer 2: 规格依赖图映射（确定性）

从 `spec/features/*/spec.md` 中提取功能间的依赖关系，当一个功能的代码变更时，
所有依赖它的功能的测试也需要运行。

**映射路径:**

```
变更文件 → 所属功能（spec引用） → 依赖该功能的其他功能 → 相关测试
```

### Layer 3: AI Agent 补充分析（概率性）

当 Layer 1+2 检测到跨模块变更时，标记 `ai_suggestion_needed=true`，
提示 AI Agent 进行更深入的分析。

**触发 Layer 3 的跨模块变更模式:**

| 模式 | 含义 |
|------|------|
| `config/`, `settings.*` | 全局配置变更 |
| `interface/`, `schema/`, `types/` | 接口/类型定义变更 |
| `utils/`, `common/`, `shared/` | 共享工具模块变更 |
| `migrations/` | 数据库迁移变更 |
| `routes/`, `api/` | API 路由变更 |
| `middleware/` | 中间件变更 |

**Agent Layer 3 分析输出格式:**

```json
{
  "supplementary_tests": [
    {
      "path": "tests/test_billing.py",
      "reason": "auth.py 的接口签名变更影响 billing 模块的认证调用",
      "confidence": "medium"
    }
  ]
}
```

---

## 测试失败分类

波及分析识别的测试运行后，失败需要分类处理:

| 类型 | 原因 | 处理方式 | 所需证据 |
|------|------|----------|----------|
| `regression` | 代码变更的副作用 | **修复代码**（已有测试 = 行为契约） | 已有测试即为证据 |
| `spec_update` | 规格/需求变更，旧测试反映过时预期 | **更新测试**（必须关联规格变更） | 必须有 spec diff 或 ADR |

### 分类规则

1. **Layer 1 + Layer 2 默认标记为 `regression`** — 确定性分析无法判断意图
2. **Layer 3（AI Agent）可升级为 `spec_update`** — 但必须附带推理依据
3. **`spec_update` 需要更严格的审查** — 测试变更必须引用规格变更（feature spec diff 或 ADR）
4. **禁止静默修改测试** — 不允许"为了让 CI 通过而改测试"

### 失败处理流程

```
测试失败
  │
  ├── 对应的规格/需求是否变更？
  │   ├── 否 → 类型: regression → 修复代码
  │   └── 是 → 类型: spec_update → 更新测试
  │           └── 测试变更 commit 必须引用:
  │               - 对应的 spec.md 变更
  │               - 或对应的 ADR
  │
  └── 禁止: 直接删除/跳过失败测试
```

---

## 与开发循环集成

波及分析作为 AI 开发循环的第 3 阶段，位于"生成"和"测试"之间:

```
验证 → 生成 → 波及分析 → 测试 → 分析
              ▲ 新增
```

### 集成细节

- **输入**: git diff（base_ref 默认 `HEAD~1`，CI/PR 中为 `origin/main`）
- **输出**: 受影响的测试列表 + 是否需要 Agent Layer 3 分析
- **传递**: 测试列表传递给测试阶段，执行定向测试
- **回退**: 如果波及分析失败 → 回退到全量测试（宁可多跑，不可漏跑）

### base_ref 默认值

| 场景 | base_ref |
|------|----------|
| 本地开发 | `HEAD~1` |
| CI/PR | `origin/main` |
| 手动指定 | `--base <ref>` |

---

## 使用方式

### CLI

```bash
# 基本用法（对比 HEAD~1）
python3 tools/impact-analyzer.py

# 指定基准
python3 tools/impact-analyzer.py --base origin/main

# JSON 输出（供程序消费）
python3 tools/impact-analyzer.py --format json

# 通过 CLI 别名
python3 mcp/cli.py impact
python3 mcp/cli.py ds:impact
```

### 编程接口

```python
from tools.impact_analyzer import ImpactAnalyzer

analyzer = ImpactAnalyzer(spec_root="spec")
report = analyzer.analyze(base_ref="HEAD~1")

if report.fallback:
    # 分析失败，回退到全量测试
    run_all_tests()
else:
    # 定向测试
    for test in report.affected_tests:
        run_test(test.path)
    
    if report.ai_suggestion_needed:
        # 提示 Agent 进行 Layer 3 分析
        agent_analyze(report.cross_module_changes)
```

---

## ImpactReport 结构

```json
{
  "changed_files": ["src/auth.py", "src/user.py"],
  "affected_tests": [
    {
      "path": "tests/test_auth.py",
      "reason": "命名约定匹配: src/auth.py",
      "type": "regression",
      "layer": 1,
      "confidence": "high"
    },
    {
      "path": "tests/test_password.py",
      "reason": "规格依赖: 功能 'password-policy' 受影响",
      "type": "regression",
      "layer": 2,
      "confidence": "medium"
    }
  ],
  "ai_suggestion_needed": true,
  "cross_module_changes": [
    "src/utils/auth_helper.py — 共享工具模块变更"
  ],
  "base_ref": "HEAD~1",
  "fallback": false,
  "error": null
}
```

---

## 配置文件

可选的 `.devspec/impact.yml`:

```yaml
mapping_rules:
  - pattern: "src/**/*.py"
    test_pattern: "tests/**/test_{basename}.py"
  - pattern: "src/**/*.ts"
    test_pattern: "tests/**/{basename}.test.ts"
  - pattern: "lib/**/*.go"
    test_pattern: "lib/**/{basename}_test.go"
```

如果不存在配置文件，使用内置默认规则。
