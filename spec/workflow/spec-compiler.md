# 规格编译器

> 将规格文档转换为可实现的代码制品。

---

## 用途

从规格自动生成代码桩、API Schema、文档和测试模板，减少重复工作。

---

## 生成的制品

| 制品类型   | 输出路径                            | 来源               | 说明                        |
| ---------- | ----------------------------------- | ------------------ | --------------------------- |
| 代码桩     | `generated/stubs/<feature>.ts`      | spec.md            | TypeScript 类桩 + TODO 标记 |
| API Schema | `generated/schemas/openapi.json`    | spec.md 的接口章节 | OpenAPI 3.0 规范            |
| 文档       | `generated/docs/<feature>.md`       | spec.md            | 功能文档                    |
| 测试模板   | `generated/tests/<feature>.test.ts` | tasks.md           | 测试桩                      |

---

## 使用方法

```bash
# 通过 CLI
python3 mcp/cli.py compile spec generated

# 直接运行
python3 tools/spec-compiler.py spec generated
```

---

## 自定义扩展

继承 `SpecCompiler` 类可以添加：

- 自定义代码生成器（如 Python、Go、Rust）
- 额外的输出格式
- 语言特定的模板
