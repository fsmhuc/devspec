#!/usr/bin/env python3
"""
DevSpec CLI - Direct command-line interface for DevSpec tools

Usage:
    python mcp/cli.py validate [spec_root]
    python mcp/cli.py compile [spec_root] [output_dir]
    python mcp/cli.py graph [spec_root] [tree|mermaid|json]
    python mcp/cli.py loop [spec_root] [--skip-tests]
    python mcp/cli.py impact [--base <ref>] [--format json|text]
    python mcp/cli.py verify [<feature>|--all] [--format text|json]
    python mcp/cli.py workflow
    python mcp/cli.py init [--force] [--root <project_root>]
    python mcp/cli.py create-feature <name> [--goals "goal1, goal2"] [--rigor lite|full]
    python mcp/cli.py create-adr <title> --context "..." --decision "..."
    python mcp/cli.py create-patch <name> --problem "..." --fix "..."
    python mcp/cli.py create-delta <name> --target <spec-path>
    python mcp/cli.py archive <name>
    python mcp/cli.py list-patches
    python mcp/cli.py list-archive
    python mcp/cli.py list [spec_root]
    python mcp/cli.py read <path>
"""

import sys
import os
import re
import json
import io
import subprocess
import contextlib
import importlib.util
from pathlib import Path
import shutil
from datetime import date

# Get the directory where this script is located
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent
tools_dir = project_root / "tools"


def load_module(name: str, path: Path):
    """Load a Python module from file path (handles hyphenated filenames)."""
    spec = importlib.util.spec_from_file_location(name, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Load tool modules
spec_linter = load_module("spec_linter", tools_dir / "spec-linter.py")
spec_compiler = load_module("spec_compiler", tools_dir / "spec-compiler.py")
spec_graph = load_module("spec_graph", tools_dir / "spec-graph.py")


def run_impact_analysis(spec_root: str = "spec", base_ref: str = "HEAD~1", fmt: str = "text") -> str:
    """Run impact analysis on code changes."""
    analyzer_path = tools_dir / "impact-analyzer.py"
    if not analyzer_path.exists():
        return "Error: impact-analyzer.py not found in tools/"

    cmd = [sys.executable, str(analyzer_path), "--spec-root", spec_root, "--base", base_ref, "--format", fmt]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        output = (result.stdout or "") + ("\n" + result.stderr if result.stderr else "")
        return output.strip() or "Impact analysis completed (no output)."
    except subprocess.TimeoutExpired:
        return "Error: Impact analysis timed out (60s)"
    except Exception as e:
        return f"Error: {e}"


def spec_validate(spec_root: str = "spec") -> str:
    """Validate all specifications."""
    linter = spec_linter.SpecLinter(spec_root)
    linter.check_index()
    linter.check_vision()
    linter.check_architecture()
    linter.check_features()
    linter.check_adrs()
    linter.check_tasks()
    linter.check_orphans()

    lines = ["=== DevSpec Validation Results ===\n"]
    if linter.errors:
        lines.append("ERRORS:")
        for error in linter.errors:
            lines.append(f"  [x] {error}")
        lines.append("")
    if linter.warnings:
        lines.append("WARNINGS:")
        for warning in linter.warnings:
            lines.append(f"  [!] {warning}")
        lines.append("")
    if not linter.errors and not linter.warnings:
        lines.append("All checks passed!")
    lines.append(f"\nSummary: {len(linter.errors)} errors, {len(linter.warnings)} warnings")
    return "\n".join(lines)


def spec_compile(spec_root: str = "spec", output_dir: str = "generated") -> str:
    """Compile specs to code artifacts."""
    compiler = spec_compiler.SpecCompiler(spec_root, output_dir)
    compiler.compile_all()
    lines = ["=== DevSpec Compilation Complete ===\n"]
    lines.append(f"Output directory: {output_dir}/")
    lines.append("\nGenerated artifacts:")
    lines.append("  - stubs/     TypeScript implementation stubs")
    lines.append("  - schemas/   OpenAPI schemas")
    lines.append("  - docs/      Feature documentation")
    lines.append("  - tests/     Test templates")
    return "\n".join(lines)


def spec_graph_output(spec_root: str = "spec", fmt: str = "tree") -> str:
    """Generate spec hierarchy visualization."""
    g = spec_graph.SpecGraph(spec_root)
    g.build_graph()

    if fmt == "tree":
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            g.print_ascii_tree()
        return output.getvalue()
    elif fmt == "mermaid":
        return g.generate_mermaid()
    elif fmt == "json":
        return json.dumps(g.generate_json(), indent=2)
    return "Unknown format. Use: tree, mermaid, or json"


def spec_list_features(spec_root: str = "spec") -> str:
    """List all features with task completion status."""
    features_path = Path(spec_root) / "features"
    if not features_path.exists():
        return "No features directory found"

    lines = ["=== Feature Status ===\n"]
    for feature_dir in sorted(features_path.iterdir()):
        if feature_dir.is_dir() and feature_dir.name != "template.md":
            tasks_file = feature_dir / "tasks.md"
            total, done = 0, 0
            if tasks_file.exists():
                content = tasks_file.read_text()
                # Count checkbox-style tasks: - [x] and - [ ]
                checkbox_total = len(re.findall(r"- \[[ x]\]", content))
                checkbox_done = len(re.findall(r"- \[x\]", content))
                # Count table-style tasks: | # | task | `status` |
                table_statuses = re.findall(r"\|\s*\d+\s*\|.*?\|\s*`(\w[\w-]*)`\s*\|", content)
                table_total = len(table_statuses)
                table_done = sum(1 for s in table_statuses if s == "done")
                # Use whichever format has more tasks
                if table_total > checkbox_total:
                    total, done = table_total, table_done
                else:
                    total, done = checkbox_total, checkbox_done
            status = f"[{done}/{total}]" if total > 0 else "[no tasks]"
            lines.append(f"  {status} {feature_dir.name}")
    return "\n".join(lines)


def spec_create_feature(name: str, goals: str = "", rigor: str = "lite", spec_root: str = "spec") -> str:
    """Create a new feature specification structure."""
    spec_path = Path(spec_root) / "features" / name
    if spec_path.exists():
        return f"Error: Feature '{name}' already exists"

    if rigor not in ("lite", "full"):
        rigor = "lite"

    spec_path.mkdir(parents=True)
    goals_list = [g.strip() for g in goals.split(",")] if goals else ["Define feature goals"]
    goals_text = "\n".join(f"- {g}" for g in goals_list)

    if rigor == "lite":
        spec_content = f"""# {name.replace('-', ' ').title()}

> 状态: `draft`
> 严格等级: `lite`

---

## 目标

{goals_text}

---

## 设计

描述功能的核心设计方案。

---

## 验收标准

- [ ] 标准 1: 描述可验证的行为
- [ ] 标准 2: 描述可验证的行为
"""
    else:
        spec_content = f"""# {name.replace('-', ' ').title()}

> 状态: `draft`
> 严格等级: `full`

---

## 目标

{goals_text}

---

## 非目标

- 不处理 XXX

---

## 设计

### 概述

用 2-3 句话概括功能的核心设计。

### 详细设计

描述实现方案，包括数据流、状态变化、核心逻辑等。

---

## 接口

| 方法 | 路径       | 描述     |
| ---- | ---------- | -------- |
| GET  | /api/{name} | 获取资源 |
| POST | /api/{name} | 创建资源 |

---

## 验收标准

- [ ] 标准 1: 描述可验证的行为
- [ ] 标准 2: 描述可验证的行为

---

## 约束条件

- 性能: 响应时间 < XXms
- 安全: 需要认证/授权

---

## 依赖

| 依赖项 | 类型     | 状态 |
| ------ | -------- | ---- |
| 功能-A | 功能依赖 | done |

---

## 风险

| 风险     | 可能性   | 影响     | 缓解方案 |
| -------- | -------- | -------- | -------- |
| 风险描述 | 高/中/低 | 高/中/低 | 应对方案 |

---

## 边界情况

- 当输入为空时...
- 当并发访问时...

---

## 测试策略

### 单元测试
- 测试用例 1

### 集成测试
- 场景 1

### 波及范围

| 受影响模块/功能 | 影响类型 | 需要测试 |
| -------------- | -------- | -------- |
| 功能-A         | 接口依赖 | 是       |
"""

    (spec_path / "spec.md").write_text(spec_content)

    tasks_content = f"""# Tasks

- [ ] Design API schema
- [ ] Implement {name} logic
- [ ] Add unit tests
- [ ] Update documentation
"""
    (spec_path / "tasks.md").write_text(tasks_content)

    decisions_content = """# Feature Decisions

Record feature-level decisions here.

## Decision Template

**Decision**: What was decided

**Reason**: Why it was decided

**Alternatives Considered**: What other options were evaluated
"""
    (spec_path / "decisions.md").write_text(decisions_content)

    return f"""Created feature: {name}/ (rigor: {rigor})

Files created:
  - spec/{name}/spec.md      # Feature specification ({rigor} mode)
  - spec/{name}/tasks.md     # Implementation tasks
  - spec/{name}/decisions.md # Decision log

Next steps:
1. Edit spec.md to define the feature
2. Update tasks.md with specific implementation tasks
3. Run spec_validate to check consistency
"""


def spec_create_adr(title: str, context: str, decision: str, spec_root: str = "spec") -> str:
    """Create a new ADR document."""
    decisions_path = Path(spec_root) / "decisions"
    existing = list(decisions_path.glob("ADR-*.md"))
    next_num = len(existing) + 1
    adr_name = f"ADR-{next_num:04d}-{title.lower().replace(' ', '-')}.md"
    adr_path = decisions_path / adr_name

    adr_content = f"""# {adr_name.replace('.md', '').replace('-', ' ').title()}

## Status

Proposed

---

## Context

{context}

---

## Decision

{decision}

---

## Consequences

Describe the consequences of this decision:

- Positive impacts
- Negative impacts
- Risks

---

## References

- Related specs: List any related specifications
"""
    adr_path.write_text(adr_content)

    return f"""Created ADR: {adr_name}

Path: spec/decisions/{adr_name}

Next steps:
1. Review and update the Status (Proposed -> Accepted)
2. Fill in the Consequences section
3. Add references to related specs
"""


def spec_read(path: str, spec_root: str = "spec") -> str:
    """Read a specification file."""
    file_path = Path(spec_root) / path
    if not file_path.exists():
        return f"Error: File not found: {path}"
    return file_path.read_text()


def spec_workflow_guide() -> str:
    """Show recommended hybrid workflow (conversation-first + command checkpoints)."""
    return """=== DevSpec Hybrid Workflow ===

Conversation-driven (default):
1. Describe the goal to AI in natural language
2. AI loads spec/index.md and related context
3. AI proposes/implements focused changes

Slash/command-driven checkpoints:
- ds:validate  -> python3 mcp/cli.py validate
- ds:compile   -> python3 mcp/cli.py compile spec generated
- ds:graph     -> python3 mcp/cli.py graph spec tree
- ds:loop      -> python3 mcp/cli.py loop spec

Recommended rhythm:
Talk to plan and implement, run commands at key checkpoints.
"""


def run_ai_dev_loop(spec_root: str = "spec", skip_tests: bool = False) -> str:
    """Run the full AI development loop script."""
    loop_script = project_root / "tools" / "ai-dev-loop.py"
    cmd = ["python3", str(loop_script), spec_root]
    if skip_tests:
        cmd.append("--skip-tests")

    completed = subprocess.run(cmd, capture_output=True, text=True)
    output = (completed.stdout or "") + ("\n" + completed.stderr if completed.stderr else "")
    output = output.strip()

    if completed.returncode != 0:
        return f"AI Dev Loop failed (exit={completed.returncode})\n\n{output}"

    return output if output else "AI Dev Loop completed successfully."


def _write_scaffold_file(path: Path, content: str, force: bool, created: list, skipped: list):
    if path.exists() and not force:
        skipped.append(path)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    created.append(path)


def spec_init(root: str = ".", force: bool = False) -> str:
    """Initialize Claude & OpenCode command/skill scaffolding for hybrid workflow."""
    root_path = Path(root).resolve()
    claude_commands_dir = root_path / ".claude" / "commands"
    claude_skills_dir = root_path / ".claude" / "skills"
    opencode_commands_dir = root_path / ".opencode" / "commands"
    opencode_skills_dir = root_path / ".opencode" / "skills" / "devspec-hybrid"

    command_files = {
        "ds-start.md": """---
description: DevSpec 对话式启动（加载上下文并制定下一步）
---

请按 DevSpec 规则执行：
1. 先读取 spec/index.md
2. 根据任务类型按需加载上下文
3. 给出最小可执行计划并开始实施
""",
        "ds-validate.md": """---
description: DevSpec 校验检查点
---

运行命令：python3 mcp/cli.py ds:validate
然后总结 errors/warnings，并给出下一步。
""",
        "ds-compile.md": """---
description: DevSpec 规格编译检查点
---

运行命令：python3 mcp/cli.py ds:compile
然后总结生成产物与后续行动。
""",
        "ds-graph.md": """---
description: DevSpec 规格结构可视化检查点
---

运行命令：python3 mcp/cli.py ds:graph
输出并解释当前规格层级结构。
""",
        "ds-loop.md": """---
description: DevSpec 完整开发循环检查点
---

运行命令：python3 mcp/cli.py ds:loop
汇总验证、生成、测试、分析结果。
""",
        "ds-workflow.md": """---
description: 查看 DevSpec 混合工作流建议
---

运行命令：python3 mcp/cli.py workflow
并按"对话优先 + 命令检查点"模式推进。
""",
    }

    # Claude CLI skill (flat file)
    claude_skill_content = """# DevSpec Hybrid Skill

## 目标
使用"对话驱动为主，命令驱动为辅"完成 DevSpec 工作流。

## 默认行为
1. 对话中先澄清目标与约束
2. 先读 spec/index.md，再按需加载上下文
3. 在关键节点执行命令检查点：validate / compile / graph / loop

## 命令映射
- ds:validate
- ds:compile
- ds:graph
- ds:loop
"""

    # OpenCode skill (directory-based SKILL.md with required name + description frontmatter)
    opencode_skill_content = """---
name: devspec-hybrid
description: DevSpec 混合工作流技能 — 对话驱动为主，命令检查点为辅，驱动规格验证、编译、可视化与开发循环
---

# DevSpec Hybrid Skill

## 目标
使用"对话驱动为主，命令驱动为辅"完成 DevSpec 工作流。

## 默认行为
1. 对话中先澄清目标与约束
2. 先读 spec/index.md，再按需加载上下文
3. 在关键节点执行命令检查点：validate / compile / graph / loop

## 命令映射
- ds:validate  -> python3 mcp/cli.py ds:validate
- ds:compile   -> python3 mcp/cli.py ds:compile
- ds:graph     -> python3 mcp/cli.py ds:graph
- ds:loop      -> python3 mcp/cli.py ds:loop
- ds:workflow  -> python3 mcp/cli.py workflow
"""

    created = []
    skipped = []

    # Generate Claude CLI scaffolding
    for filename, content in command_files.items():
        _write_scaffold_file(claude_commands_dir / filename, content, force, created, skipped)

    _write_scaffold_file(claude_skills_dir / "devspec-hybrid.md", claude_skill_content, force, created, skipped)

    # Generate OpenCode scaffolding
    for filename, content in command_files.items():
        _write_scaffold_file(opencode_commands_dir / filename, content, force, created, skipped)

    _write_scaffold_file(opencode_skills_dir / "SKILL.md", opencode_skill_content, force, created, skipped)

    lines = ["=== DevSpec Init Complete ===", ""]
    lines.append(f"Root: {root_path}")
    lines.append("Scaffold:")
    lines.append("  Claude CLI:")
    lines.append("    - .claude/commands/ds-*.md")
    lines.append("    - .claude/skills/devspec-hybrid.md")
    lines.append("  OpenCode:")
    lines.append("    - .opencode/commands/ds-*.md")
    lines.append("    - .opencode/skills/devspec-hybrid/SKILL.md")

    lines.append("")
    lines.append(f"Created: {len(created)}")
    for path in created:
        lines.append(f"  + {path.relative_to(root_path)}")

    if skipped:
        lines.append("")
        lines.append(f"Skipped (already exists): {len(skipped)}")
        for path in skipped:
            lines.append(f"  - {path.relative_to(root_path)}")
        lines.append("Use --force to overwrite scaffold files.")

    return "\n".join(lines)


def create_patch(name: str, problem: str = "", fix: str = "", impact: str = "") -> str:
    """Create a new patch file for bug fixes."""
    patches_dir = project_root / "changes" / "patches"
    patches_dir.mkdir(parents=True, exist_ok=True)

    patch_name = f"fix-{name.lower().replace(' ', '-')}.md"
    patch_path = patches_dir / patch_name

    if patch_path.exists():
        return f"Error: Patch '{patch_name}' already exists"

    patch_content = f"""# Patch: {name.replace('-', ' ').title()}

---

## Problem

{problem if problem else "Describe the bug or issue."}

---

## Fix

{fix if fix else "Explain the fix."}

---

## Impact

{impact if impact else "- Module 1"}

---

## Testing

- [ ] Unit test added/updated
- [ ] Manual testing performed
- [ ] No test needed (explain why)

---

## Checklist

- [ ] Fix is minimal and focused
- [ ] No spec changes required
- [ ] No breaking changes
- [ ] Reviewed by: ___________
"""

    patch_path.write_text(patch_content)

    return f"""Created patch: {patch_name}

Path: changes/patches/{patch_name}

Next steps:
1. Document the problem and fix
2. Test the fix
3. Complete the checklist
4. Commit with: git commit -m "[patch] {name}"
"""


def list_patches() -> str:
    """List all patches and their status."""
    patches_dir = project_root / "changes" / "patches"
    if not patches_dir.exists():
        return "No patches directory found"

    lines = ["=== Patch Status ===\n"]

    patches = sorted(patches_dir.glob("fix-*.md"))
    if not patches:
        lines.append("No patches found.")
        return "\n".join(lines)

    for patch_file in patches:
        content = patch_file.read_text()

        # Check checklist status
        total_checks = len(re.findall(r"- \[[ x]\]", content))
        done_checks = len(re.findall(r"- \[x\]", content))

        # Extract problem summary
        problem_match = re.search(r"## Problem\s*\n(.+?)(?=\n##|\Z)", content, re.DOTALL)
        problem_summary = ""
        if problem_match:
            problem_summary = problem_match.group(1).strip().split("\n")[0][:50]

        status = f"[{done_checks}/{total_checks}]" if total_checks > 0 else "[new]"
        lines.append(f"  {status} {patch_file.name}")
        if problem_summary:
            lines.append(f"       {problem_summary}...")

    return "\n".join(lines)


def complete_patch(name: str) -> str:
    """Mark a patch as complete."""
    patches_dir = project_root / "changes" / "patches"
    patch_path = patches_dir / f"fix-{name}.md" if not name.endswith(".md") else patches_dir / name

    if not patch_path.exists():
        # Try to find by partial match
        matches = list(patches_dir.glob(f"fix-*{name}*.md"))
        if matches:
            patch_path = matches[0]
        else:
            return f"Error: Patch not found: {name}"

    content = patch_path.read_text()

    # Mark all checkboxes as done
    updated = re.sub(r"- \[ \]", "- [x]", content)
    patch_path.write_text(updated)

    return f"""Patch completed: {patch_path.name}

The fix has been documented and tested.

Next step: Commit with prefix [patch]
"""




def create_delta(name: str, target: str = "", spec_root: str = "spec") -> str:
    """Create a new Delta Spec for incremental spec changes."""
    proposals_dir = project_root / "changes" / "proposals"
    proposals_dir.mkdir(parents=True, exist_ok=True)

    delta_name = f"delta-{name.lower().replace(' ', '-')}.md"
    delta_path = proposals_dir / delta_name

    if delta_path.exists():
        return f"Error: Delta '{delta_name}' already exists"

    today = date.today().isoformat()
    target_text = target if target else "<!-- 受影响的规格路径，如 spec/features/user-auth/spec.md -->"

    delta_content = f"""# Delta Spec: {name.replace('-', ' ').title()}

> 用于描述规格变更的增量格式。

---

## 元信息

| 字段       | 值                                         |
| ---------- | ------------------------------------------ |
| 变更名称   | {name.replace('-', ' ')}                   |
| 目标规格   | {target_text} |
| 状态       | `draft`                                    |
| 创建日期   | {today}                                    |

---

## Delta 变更

### [ADDED] 新增内容

```
目标节: ## <节名>
内容:
  - <描述新增内容>
```

### [MODIFIED] 修改内容

```
目标节: ## <节名>
原内容: <原始内容>
新内容: <新内容>
原因: <修改原因>
```

### [REMOVED] 删除内容

```
目标节: ## <节名>
删除内容: <要删除的内容>
原因: <删除原因>
```

---

## 影响分析

| 受影响规格/模块          | 影响类型     | 需要更新 |
| ----------------------- | ------------ | -------- |
| <!-- 规格或模块路径 -->  | 接口依赖     | 是/否    |

---

## 关联

- 关联 ADR: <!-- ADR-XXXX（如涉及架构变更） -->
- 关联任务: <!-- tasks.md 中的任务编号 -->

---

## 审查

- [ ] Delta 内容准确反映了变更意图
- [ ] 影响分析已完成
- [ ] 目标规格路径正确
- [ ] 需要人类确认（规格变更属于审查门控）
"""

    delta_path.write_text(delta_content)

    return f"""Created delta: {delta_name}

Path: changes/proposals/{delta_name}

Next steps:
1. Fill in the Delta changes ([ADDED], [MODIFIED], [REMOVED])
2. Complete impact analysis
3. Request human review (spec changes require review gate)
4. After approval, merge into target spec
5. Archive with: python3 mcp/cli.py archive {name}
"""


def archive_change(name: str) -> str:
    """Archive a completed change (patch/proposal/delta) to changes/archive/."""
    changes_dir = project_root / "changes"
    archive_dir = changes_dir / "archive"
    archive_dir.mkdir(parents=True, exist_ok=True)

    # Search for the file in patches/ and proposals/
    source_path = None
    change_type = None

    # Try patches
    for pattern in [f"fix-{name}.md", f"fix-{name}", f"{name}.md", name]:
        candidate = changes_dir / "patches" / pattern
        if candidate.exists():
            source_path = candidate
            change_type = "patch"
            break

    # Try proposals if not found in patches
    if not source_path:
        for pattern in [f"delta-{name}.md", f"prop-{name}.md", f"{name}.md", name]:
            candidate = changes_dir / "proposals" / pattern
            if candidate.exists():
                source_path = candidate
                change_type = "delta" if "delta" in candidate.name else "proposal"
                break

    if not source_path:
        return f"""Error: Change not found: {name}

Searched in:
  - changes/patches/fix-{name}.md
  - changes/proposals/delta-{name}.md
  - changes/proposals/prop-{name}.md
  - changes/proposals/{name}.md"""

    today = date.today().isoformat()
    stem = source_path.stem  # filename without .md
    archive_subdir = archive_dir / f"{today}-{stem}"

    if archive_subdir.exists():
        return f"Error: Archive directory already exists: {archive_subdir.relative_to(project_root)}"

    archive_subdir.mkdir(parents=True)

    # Move the file
    dest_path = archive_subdir / source_path.name
    shutil.move(str(source_path), str(dest_path))

    # Generate summary.md
    summary_content = f"""# 归档摘要

| 字段       | 值                            |
| ---------- | ----------------------------- |
| 变更类型   | {change_type}                 |
| 原始路径   | {source_path.relative_to(project_root)} |
| 归档日期   | {today}                       |
| 归档原因   | 变更已完成并验证               |

## 变更概述

<!-- 一句话描述完成了什么 -->

## 关联

- Commit: <!-- git commit hash -->
- 目标规格: <!-- spec path（如适用） -->
"""
    (archive_subdir / "summary.md").write_text(summary_content)

    return f"""Archived: {source_path.name} -> {archive_subdir.relative_to(project_root)}/

Files:
  - {archive_subdir.relative_to(project_root)}/{source_path.name}
  - {archive_subdir.relative_to(project_root)}/summary.md

The original file has been moved from the active area.
Run 'python3 mcp/cli.py validate' to verify no broken references.
"""


def list_archive() -> str:
    """List all archived changes."""
    archive_dir = project_root / "changes" / "archive"
    if not archive_dir.exists():
        return "No archive directory found."

    lines = ["=== Archived Changes ===", ""]

    entries = sorted(
        [d for d in archive_dir.iterdir() if d.is_dir()],
        key=lambda d: d.name,
        reverse=True,
    )

    if not entries:
        lines.append("No archived changes found.")
        return "\n".join(lines)

    for entry in entries:
        summary_path = entry / "summary.md"
        change_type = "unknown"
        archive_date = "unknown"

        if summary_path.exists():
            content = summary_path.read_text()
            # Parse type from summary table
            type_match = re.search(r"\|\s*变更类型\s*\|\s*(\S+)", content)
            if type_match:
                change_type = type_match.group(1)
            date_match = re.search(r"\|\s*归档日期\s*\|\s*(\S+)", content)
            if date_match:
                archive_date = date_match.group(1)

        # List files in the archive entry
        files = [f.name for f in entry.iterdir() if f.is_file() and f.name != "summary.md"]

        lines.append(f"  [{change_type}] {entry.name}")
        if files:
            lines.append(f"          files: {', '.join(files)}")

    lines.append(f"")
    lines.append(f"Total: {len(entries)} archived changes")
    return "\n".join(lines)


def spec_verify(feature: str = "", all_features: bool = False, fmt: str = "text", spec_root: str = "spec") -> str:
    """Three-dimension verification: Completeness, Correctness, Coherence."""
    features_path = Path(spec_root) / "features"
    if not features_path.exists():
        return "Error: No features directory found"

    # Collect features to verify
    targets = []
    if all_features:
        targets = [d for d in sorted(features_path.iterdir()) if d.is_dir() and d.name != "template.md"]
    elif feature:
        target = features_path / feature
        if not target.exists():
            return f"Error: Feature not found: {feature}"
        targets = [target]
    else:
        return "Usage: verify <feature-name> or verify --all"

    if not targets:
        return "No features found to verify."

    results = []
    for target_dir in targets:
        result = _verify_feature(target_dir, spec_root)
        results.append(result)

    if fmt == "json":
        return json.dumps([r for r in results], indent=2, ensure_ascii=False)

    # Text output
    lines = []
    for r in results:
        lines.append(f"=== DevSpec Verification: {r['name']} ===")
        lines.append("")

        # Completeness
        lines.append("[完整性] Completeness")
        for item in r["completeness"]:
            icon = "✅" if item["pass"] else ("⚠️" if item.get("warn") else "❌")
            lines.append(f"  {icon} {item['msg']}")
        lines.append("")

        # Correctness
        lines.append("[正确性] Correctness")
        for item in r["correctness"]:
            icon = "✅" if item["pass"] else "⚠️"
            lines.append(f"  {icon} {item['msg']}")
        lines.append("")

        # Coherence
        lines.append("[一致性] Coherence")
        for item in r["coherence"]:
            icon = "✅" if item["pass"] else "⚠️"
            lines.append(f"  {icon} {item['msg']}")
        lines.append("")

        passed = sum(1 for dim in ["completeness", "correctness", "coherence"] for i in r[dim] if i["pass"])
        warnings = sum(1 for dim in ["completeness", "correctness", "coherence"] for i in r[dim] if i.get("warn"))
        failed = sum(1 for dim in ["completeness", "correctness", "coherence"] for i in r[dim] if not i["pass"] and not i.get("warn"))
        lines.append(f"Summary: {passed} passed, {warnings} warnings, {failed} failed")
        lines.append("")

    return "\n".join(lines)


def _verify_feature(feature_dir: Path, spec_root: str) -> dict:
    """Verify a single feature across three dimensions."""
    name = feature_dir.name
    spec_file = feature_dir / "spec.md"
    tasks_file = feature_dir / "tasks.md"

    spec_content = spec_file.read_text() if spec_file.exists() else ""
    tasks_content = tasks_file.read_text() if tasks_file.exists() else ""

    # Detect rigor level
    rigor = "lite"
    rigor_match = re.search(r"严格等级:\s*`(\w+)`", spec_content)
    if rigor_match:
        rigor = rigor_match.group(1)

    result = {"name": name, "rigor": rigor, "completeness": [], "correctness": [], "coherence": []}

    # === Dimension 1: Completeness ===

    # Check tasks completion
    checkbox_total = len(re.findall(r"- \[[ x]\]", tasks_content))
    checkbox_done = len(re.findall(r"- \[x\]", tasks_content))
    table_statuses = re.findall(r"\|\s*\d+\s*\|.*?\|\s*`(\w[\w-]*)`\s*\|", tasks_content)
    table_total = len(table_statuses)
    table_done = sum(1 for s in table_statuses if s == "done")

    if table_total > checkbox_total:
        total, done = table_total, table_done
    else:
        total, done = checkbox_total, checkbox_done

    if total > 0:
        all_done = total == done
        result["completeness"].append({
            "pass": all_done,
            "warn": not all_done,
            "msg": f"tasks.md: {done}/{total} done"
        })
    else:
        result["completeness"].append({"pass": False, "warn": True, "msg": "tasks.md: no tasks found"})

    # Check acceptance criteria
    ac_section = re.search(r"## 验收标准(.*?)(?=\n## |\Z)", spec_content, re.DOTALL)
    if ac_section:
        ac_text = ac_section.group(1)
        ac_total = len(re.findall(r"- \[[ x]\]", ac_text))
        ac_done = len(re.findall(r"- \[x\]", ac_text))
        if ac_total > 0:
            result["completeness"].append({
                "pass": ac_total == ac_done,
                "warn": ac_total != ac_done,
                "msg": f"验收标准: {ac_done}/{ac_total} checked"
            })
        else:
            result["completeness"].append({"pass": False, "warn": True, "msg": "验收标准: no criteria found"})
    else:
        result["completeness"].append({"pass": False, "msg": "验收标准: section missing"})

    # Check required sections based on rigor
    lite_required = ["目标", "设计", "验收标准"]
    full_required = ["目标", "非目标", "设计", "接口", "验收标准", "约束条件", "依赖", "风险", "边界情况", "测试策略"]
    required = full_required if rigor == "full" else lite_required

    for section in required:
        found = re.search(rf"## {re.escape(section)}", spec_content)
        if found:
            # Check if section has content (not just the header)
            section_match = re.search(rf"## {re.escape(section)}(.*?)(?=\n## |\Z)", spec_content, re.DOTALL)
            has_content = bool(section_match and section_match.group(1).strip())
            if has_content:
                result["completeness"].append({"pass": True, "msg": f"spec.md 「{section}」节: present"})
            else:
                result["completeness"].append({"pass": False, "warn": True, "msg": f"spec.md 「{section}」节: empty"})
        else:
            if rigor == "lite" and section not in lite_required:
                result["completeness"].append({"pass": True, "warn": True, "msg": f"spec.md 缺少「{section}」节（lite 模式可跳过）"})
            else:
                result["completeness"].append({"pass": False, "msg": f"spec.md 缺少「{section}」节"})

    # === Dimension 2: Correctness (semi-auto checklist) ===

    # Check if API endpoints exist in spec
    has_api = bool(re.search(r"(GET|POST|PUT|DELETE|PATCH)\s+/", spec_content))
    if rigor == "full":
        if has_api:
            result["correctness"].append({"pass": True, "msg": "API 端点: defined in spec"})
        else:
            result["correctness"].append({"pass": False, "warn": True, "msg": "API 端点: not defined (需要人工确认是否需要)"})

    # Check acceptance criteria for verifiability
    if ac_section:
        ac_items = re.findall(r"- \[[ x]\]\s+(.+)", ac_section.group(1))
        if ac_items:
            result["correctness"].append({"pass": True, "msg": f"验收标准: {len(ac_items)} criteria defined"})
            for ac in ac_items:
                result["correctness"].append({"pass": True, "warn": True, "msg": f"  ↳ \"{ac}\" — 请确认实现是否匹配"})
        else:
            result["correctness"].append({"pass": False, "warn": True, "msg": "验收标准: no verifiable criteria"})

    # === Dimension 3: Coherence ===

    # Check architecture constraints
    arch_path = Path(spec_root) / "core" / "architecture.md"
    if arch_path.exists():
        result["coherence"].append({"pass": True, "msg": "架构约束: architecture.md exists (需要人工确认无冲突)"})
    else:
        result["coherence"].append({"pass": False, "warn": True, "msg": "架构约束: architecture.md not found"})

    # Check dependencies declared in spec
    dep_section = re.search(r"## 依赖(.*?)(?=\n## |\Z)", spec_content, re.DOTALL)
    if rigor == "full":
        if dep_section and dep_section.group(1).strip():
            result["coherence"].append({"pass": True, "msg": "依赖声明: present"})
        else:
            result["coherence"].append({"pass": False, "warn": True, "msg": "依赖声明: not found or empty"})

    # Check glossary consistency
    glossary_path = Path(spec_root) / "core" / "glossary.md"
    if rigor == "full":
        if glossary_path.exists():
            result["coherence"].append({"pass": True, "msg": "术语: glossary.md exists (需要人工确认一致性)"})
        else:
            result["coherence"].append({"pass": False, "warn": True, "msg": "术语: glossary.md not found"})

    return result

def print_usage():
    print(__doc__)


def main():
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    command = sys.argv[1]

    alias_to_command = {
        "ds:validate": "validate",
        "ds:compile": "compile",
        "ds:graph": "graph",
        "ds:list": "list",
        "ds:list-patches": "list-patches",
        "ds:workflow": "workflow",
        "ds:loop": "loop",
        "ds:impact": "impact",
        "ds:verify": "verify",
        "ds:archive": "archive",
        "ds:list-archive": "list-archive",
        "ds:create-delta": "create-delta",
    }
    if command in alias_to_command:
        command = alias_to_command[command]

    try:
        if command == "validate":
            spec_root = sys.argv[2] if len(sys.argv) > 2 else "spec"
            print(spec_validate(spec_root))

        elif command == "compile":
            spec_root = sys.argv[2] if len(sys.argv) > 2 else "spec"
            output_dir = sys.argv[3] if len(sys.argv) > 3 else "generated"
            print(spec_compile(spec_root, output_dir))

        elif command == "graph":
            spec_root = sys.argv[2] if len(sys.argv) > 2 else "spec"
            fmt = sys.argv[3] if len(sys.argv) > 3 else "tree"
            print(spec_graph_output(spec_root, fmt))

        elif command == "loop":
            spec_root = "spec"
            if len(sys.argv) > 2 and not sys.argv[2].startswith("--"):
                spec_root = sys.argv[2]
            skip_tests = "--skip-tests" in sys.argv
            print(run_ai_dev_loop(spec_root, skip_tests))

        elif command == "impact":
            spec_root = "spec"
            base_ref = "HEAD~1"
            fmt = "text"
            args = sys.argv[2:]
            i = 0
            while i < len(args):
                if args[i] == "--base" and i + 1 < len(args):
                    base_ref = args[i + 1]
                    i += 2
                elif args[i] == "--format" and i + 1 < len(args):
                    fmt = args[i + 1]
                    i += 2
                elif args[i] == "--spec-root" and i + 1 < len(args):
                    spec_root = args[i + 1]
                    i += 2
                else:
                    i += 1
            print(run_impact_analysis(spec_root, base_ref, fmt))
        elif command == "workflow":
            print(spec_workflow_guide())

        elif command == "init":
            force = "--force" in sys.argv
            root = "."
            if "--root" in sys.argv:
                idx = sys.argv.index("--root")
                root = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else "."
            print(spec_init(root=root, force=force))

        elif command == "create-feature":
            if len(sys.argv) < 3:
                print("Usage: cli.py create-feature <name> [--goals 'goal1, goal2'] [--rigor lite|full]")
                sys.exit(1)
            name = sys.argv[2]
            goals = ""
            rigor = "lite"
            if "--goals" in sys.argv:
                idx = sys.argv.index("--goals")
                goals = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else ""
            if "--rigor" in sys.argv:
                idx = sys.argv.index("--rigor")
                rigor = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else "lite"
            print(spec_create_feature(name, goals, rigor))

        elif command == "create-adr":
            if len(sys.argv) < 3:
                print("Usage: cli.py create-adr <title> --context '...' --decision '...'")
                sys.exit(1)
            title = sys.argv[2]
            context = ""
            decision = ""
            if "--context" in sys.argv:
                idx = sys.argv.index("--context")
                context = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else ""
            if "--decision" in sys.argv:
                idx = sys.argv.index("--decision")
                decision = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else ""
            print(spec_create_adr(title, context, decision))

        elif command == "list":
            spec_root = sys.argv[2] if len(sys.argv) > 2 else "spec"
            print(spec_list_features(spec_root))

        elif command == "read":
            if len(sys.argv) < 3:
                print("Usage: cli.py read <path>")
                sys.exit(1)
            print(spec_read(sys.argv[2]))

        elif command == "create-patch":
            if len(sys.argv) < 3:
                print("Usage: cli.py create-patch <name> --problem '...' --fix '...'")
                sys.exit(1)
            name = sys.argv[2]
            problem = ""
            fix = ""
            impact = ""
            if "--problem" in sys.argv:
                idx = sys.argv.index("--problem")
                problem = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else ""
            if "--fix" in sys.argv:
                idx = sys.argv.index("--fix")
                fix = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else ""
            if "--impact" in sys.argv:
                idx = sys.argv.index("--impact")
                impact = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else ""
            print(create_patch(name, problem, fix, impact))

        elif command == "list-patches":
            print(list_patches())

        elif command == "complete-patch":
            if len(sys.argv) < 3:
                print("Usage: cli.py complete-patch <name>")
                sys.exit(1)
            print(complete_patch(sys.argv[2]))

        elif command == "verify":
            feature = ""
            all_features = "--all" in sys.argv
            fmt = "text"
            if not all_features and len(sys.argv) > 2 and not sys.argv[2].startswith("--"):
                feature = sys.argv[2]
            if "--format" in sys.argv:
                idx = sys.argv.index("--format")
                fmt = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else "text"
            print(spec_verify(feature, all_features, fmt))

        elif command == "create-delta":
            if len(sys.argv) < 3:
                print("Usage: cli.py create-delta <name> [--target <spec-path>]")
                sys.exit(1)
            name = sys.argv[2]
            target = ""
            if "--target" in sys.argv:
                idx = sys.argv.index("--target")
                target = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else ""
            print(create_delta(name, target))

        elif command == "archive":
            if len(sys.argv) < 3:
                print("Usage: cli.py archive <name>")
                sys.exit(1)
            print(archive_change(sys.argv[2]))

        elif command == "list-archive":
            print(list_archive())

        elif command in ["help", "--help", "-h"]:
            print_usage()

        else:
            print(f"Unknown command: {command}")
            print_usage()
            sys.exit(1)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
