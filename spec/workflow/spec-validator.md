# 规格验证器

> 自动检查规格的一致性、完整性和可追溯性。

---

## 用途

确保所有规格文档符合框架要求，在 CI/CD 中自动运行。

---

## 验证规则

### 1. 完整性检查

- `vision.md` 必须定义目标（goals）
- `architecture.md` 必须定义分层或组件
- 每个功能必须有 `spec.md`
- 每个 ADR 必须有 status、context、decision、consequences 章节
- Feature spec 必须有目标、设计、接口、验收标准

### 2. 一致性检查

- 功能设计不得与架构约束冲突
- 任务必须引用存在的规格
- 依赖的功能必须存在

### 3. 可追溯性检查

- 核心规格必须在 `index.md` 中引用
- ADR 必须列出受影响的规格
- 废弃规格必须在 `archive/` 中

---

## 使用方法

```bash
# 通过 CLI
python3 mcp/cli.py validate spec

# 直接运行
python3 tools/spec-linter.py spec
```

---

## 退出码

- `0`: 所有检查通过
- `1`: 存在验证错误

---

## CI/CD 集成

```yaml
# .github/workflows/spec-validation.yml
name: Spec Validation
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: python3 tools/spec-linter.py spec
```
