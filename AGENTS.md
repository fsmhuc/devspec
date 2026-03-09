# DevSpec - AI Agent 配置指南

## 项目概述

DevSpec 是一个规格驱动的开发框架，强调：规格优先、TDD、版本控制的规格以及可追溯的决定。所有工作都必须遵循存储在 `spec/` 下的结构化规格。

## 构建/开发命令

### 验证和检查
```bash
# 验证所有规格的一致性
python3 mcp/cli.py validate [spec_root]

# 综合三维验证（完整性/正确性/一致性）
python3 mcp/cli.py verify <feature_name>      # 验证特定功能
python3 mcp/cli.py verify --all               # 验证所有功能

# 从规格编译为制品
python3 mcp/cli.py compile [spec_root] [output_dir]

# 可视化规格结构
python3 mcp/cli.py graph [spec_root] [tree|mermaid|json]
```

### 规格生成和管理
```bash
# 功能创建
python3 mcp/cli.py create-feature <name> --goals "目标1, 目标2" --rigor lite|full

# ADR（架构决定记录）创建
python3 mcp/cli.py create-adr <title> --context "问题描述" --decision "选择的解决方案"

# 为缺陷修复创建补丁
python3 mcp/cli.py create-patch <name> --problem "问题描述" --fix "解决方案"

# Delta 规格（增量更改）
python3 mcp/cli.py create-delta <name> --target <spec-path>

# 开发循环（验证 → 编译 → 影响分析 → 测试 → 分析）
python3 tools/ai-dev-loop.py spec             # 完整循环
python3 tools/ai-dev-loop.py spec --skip-tests # 跳过测试（纯规格更改）
```

### 运行测试
```bash
# 运行包含定向测试的完整开发循环
python3 tools/ai-dev-loop.py spec

# 手动通过影响分析指定测试目标
python3 tools/impact-analyzer.py              # 根据 git diff 查找受影响的测试
python3 tools/impact-analyzer.py --format json # 以 JSON 格式显示

# 特定测试运行器会被自动检测和使用：
# - pytest: 用于 Python 项目
# - jest: 用于 TypeScript/JavaScript 项目
# - go test: 用于 Go 项目
```

### 归档和清理
```bash
# 归档已完成的补丁或功能
python3 mcp/cli.py archive <name>

# 列出归档和补丁
python3 mcp/cli.py list-archive
python3 mcp/cli.py list-patches
```

## 代码风格指南

### 常用命令/别名
以下常用操作的快捷方式：
- `ds:validate` → `python3 mcp/cli.py validate`
- `ds:verify` → `python3 mcp/cli.py verify <feature>`
- `ds:compile` → `python3 mcp/cli.py compile`
- `ds:graph` → `python3 mcp/cli.py graph`
- `ds:loop` → `python3 tools/ai-dev-loop.py spec`
- `ds:workflow` → `python3 mcp/cli.py workflow`
- `ds:impact` → `python3 tools/impact-analyzer.py`
- `ds:archive` → `python3 mcp/cli.py archive`

### 导入和格式化
- Python 代码使用遵循 PEP 8 的标准导入（按标准库、第三方、本地库分组）
- 鼓励在有帮助的地方使用类型提示
- 使用统一的 4 空格缩进
- 行长度应在 80-120 字符之间

### 命名约定
- 变量/函数: snake_case (Python), camelCase (TS/JS)
- 类: PascalCase
- 常量: UPPER_CASE
- 文件和目录: kebab-case
- 规格功能名: kebab-case (用于目录名)

### 错误处理
- 使用 Python 的异常处理 (`try/except/finally`)
- 处理前先验证输入
- 包含有意义的错误消息
- 在 linter 输出中区分错误和警告

### 测试模式
- **TDD 优先哲学**: 在实现之前先编写表达规格的测试
- **三步骤流程**: 红色（编写失败的测试） → 绿色（最小代码使其通过） → 重构
- **命名约定**: `test_<行为>_<场景>_<期望结果>()`
  - 示例:
    - `test_login_with_valid_credentials_returns_token()`
    - `test_create_with_duplicate_name_raises_error()`
- 测试类型: 单元测试（函数/类级别）、集成测试（多层次）、E2E（用户流程）

## AI Agent 行为规则

### 入口点
每次会话开始时读取: `spec/index.md` - 这作为主要 AI 入口点，包含阅读顺序指南。

### 必需的工作流程
1. **先读，后写**: 在修改之前先了解系统
2. **规格驱动开发**: 所有实现都需要相应的规格
3. **最小化变更**: 每次提交/拉取请求都专注于单个问题
4. **TDD 强化**: 为所有实现遵循红-绿-重构循环

### 规格工作流程
1. 确定要修改的相关规格文件
2. 如果直接修改规格，使用 Delta 规格:
   `python3 mcp/cli.py create-delta <name> --target <spec-path>`
3. 运行验证: `python3 mcp/cli.py validate`
4. 运行编译: `python3 mcp/cli.py compile`
5. 在开发循环中执行测试

### 审查网关（需要人工批准的内容）
- ✅ 自主操作: 读取文件、运行验证/测试、创建补丁
- ❌ 需要人工: 创建/修改功能规格、ADR、架构更改、归档/删除操作

### 影响分析（用于代码修改）
修改代码时：
1. 运行 `python3 tools/impact-analyzer.py` 来识别受影响的测试
2. 执行由分析器确定的定向测试
3. 如果分析器指示跨模块更改，则执行额外的手动分析

### 故障排除协议
1. 规格不完整 → 询问用户，不要猜测
2. 多个区域存在冲突 → 报告所有冲突以供解决
3. 实现不确定 → 提供 2-3 个备选项供人工选择
4. 工具故障 → 报告错误并建议解决方案