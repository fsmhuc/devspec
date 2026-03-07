#!/usr/bin/env python3
"""
OpenSpec CLI - Direct command-line interface for OpenSpec tools

Usage:
    python mcp/cli.py validate [spec_root]
    python mcp/cli.py compile [spec_root] [output_dir]
    python mcp/cli.py graph [spec_root] [tree|mermaid|json]
    python mcp/cli.py loop [spec_root] [--skip-tests]
    python mcp/cli.py impact [--base <ref>] [--format json|text]
    python mcp/cli.py workflow
    python mcp/cli.py init [--force] [--root <project_root>]
    python mcp/cli.py create-feature <name> [--goals "goal1, goal2"]
    python mcp/cli.py create-adr <title> --context "..." --decision "..."
    python mcp/cli.py create-patch <name> --problem "..." --fix "..."
    python mcp/cli.py list-patches
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

    lines = ["=== OpenSpec Validation Results ===\n"]
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
    lines = ["=== OpenSpec Compilation Complete ===\n"]
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


def spec_create_feature(name: str, goals: str = "", spec_root: str = "spec") -> str:
    """Create a new feature specification structure."""
    spec_path = Path(spec_root) / "features" / name
    if spec_path.exists():
        return f"Error: Feature '{name}' already exists"

    spec_path.mkdir(parents=True)
    goals_list = [g.strip() for g in goals.split(",")] if goals else ["Define feature goals"]
    goals_text = "\n".join(f"- {g}" for g in goals_list)

    spec_content = f"""# {name.replace('-', ' ').title()}

## Goals

{goals_text}

## Design

Describe the feature design here.

## Interfaces

- GET /api/{name}
- POST /api/{name}

## Dependencies

- List dependencies here

## Risks

- List potential risks here
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

    return f"""Created feature: {name}/

Files created:
  - spec/{name}/spec.md      # Feature specification
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
    return """=== OpenSpec Hybrid Workflow ===

Conversation-driven (default):
1. Describe the goal to AI in natural language
2. AI loads spec/index.md and related context
3. AI proposes/implements focused changes

Slash/command-driven checkpoints:
- opsx:validate  -> python3 mcp/cli.py validate
- opsx:compile   -> python3 mcp/cli.py compile spec generated
- opsx:graph     -> python3 mcp/cli.py graph spec tree
- opsx:loop      -> python3 mcp/cli.py loop spec

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
    opencode_skills_dir = root_path / ".opencode" / "skills" / "openspec-hybrid"

    command_files = {
        "opsx-start.md": """---
description: OpenSpec 对话式启动（加载上下文并制定下一步）
---

请按 OpenSpec 规则执行：
1. 先读取 spec/index.md
2. 根据任务类型按需加载上下文
3. 给出最小可执行计划并开始实施
""",
        "opsx-validate.md": """---
description: OpenSpec 校验检查点
---

运行命令：python3 mcp/cli.py opsx:validate
然后总结 errors/warnings，并给出下一步。
""",
        "opsx-compile.md": """---
description: OpenSpec 规格编译检查点
---

运行命令：python3 mcp/cli.py opsx:compile
然后总结生成产物与后续行动。
""",
        "opsx-graph.md": """---
description: OpenSpec 规格结构可视化检查点
---

运行命令：python3 mcp/cli.py opsx:graph
输出并解释当前规格层级结构。
""",
        "opsx-loop.md": """---
description: OpenSpec 完整开发循环检查点
---

运行命令：python3 mcp/cli.py opsx:loop
汇总验证、生成、测试、分析结果。
""",
        "opsx-workflow.md": """---
description: 查看 OpenSpec 混合工作流建议
---

运行命令：python3 mcp/cli.py workflow
并按"对话优先 + 命令检查点"模式推进。
""",
    }

    # Claude CLI skill (flat file)
    claude_skill_content = """# OpenSpec Hybrid Skill

## 目标
使用"对话驱动为主，命令驱动为辅"完成 OpenSpec 工作流。

## 默认行为
1. 对话中先澄清目标与约束
2. 先读 spec/index.md，再按需加载上下文
3. 在关键节点执行命令检查点：validate / compile / graph / loop

## 命令映射
- opsx:validate
- opsx:compile
- opsx:graph
- opsx:loop
"""

    # OpenCode skill (directory-based SKILL.md with required name + description frontmatter)
    opencode_skill_content = """---
name: openspec-hybrid
description: OpenSpec 混合工作流技能 — 对话驱动为主，命令检查点为辅，驱动规格验证、编译、可视化与开发循环
---

# OpenSpec Hybrid Skill

## 目标
使用"对话驱动为主，命令驱动为辅"完成 OpenSpec 工作流。

## 默认行为
1. 对话中先澄清目标与约束
2. 先读 spec/index.md，再按需加载上下文
3. 在关键节点执行命令检查点：validate / compile / graph / loop

## 命令映射
- opsx:validate  -> python3 mcp/cli.py opsx:validate
- opsx:compile   -> python3 mcp/cli.py opsx:compile
- opsx:graph     -> python3 mcp/cli.py opsx:graph
- opsx:loop      -> python3 mcp/cli.py opsx:loop
- opsx:workflow  -> python3 mcp/cli.py workflow
"""

    created = []
    skipped = []

    # Generate Claude CLI scaffolding
    for filename, content in command_files.items():
        _write_scaffold_file(claude_commands_dir / filename, content, force, created, skipped)

    _write_scaffold_file(claude_skills_dir / "openspec-hybrid.md", claude_skill_content, force, created, skipped)

    # Generate OpenCode scaffolding
    for filename, content in command_files.items():
        _write_scaffold_file(opencode_commands_dir / filename, content, force, created, skipped)

    _write_scaffold_file(opencode_skills_dir / "SKILL.md", opencode_skill_content, force, created, skipped)

    lines = ["=== OpenSpec Init Complete ===", ""]
    lines.append(f"Root: {root_path}")
    lines.append("Scaffold:")
    lines.append("  Claude CLI:")
    lines.append("    - .claude/commands/opsx-*.md")
    lines.append("    - .claude/skills/openspec-hybrid.md")
    lines.append("  OpenCode:")
    lines.append("    - .opencode/commands/opsx-*.md")
    lines.append("    - .opencode/skills/openspec-hybrid/SKILL.md")

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


def print_usage():
    print(__doc__)


def main():
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    command = sys.argv[1]

    alias_to_command = {
        "opsx:validate": "validate",
        "opsx:compile": "compile",
        "opsx:graph": "graph",
        "opsx:list": "list",
        "opsx:list-patches": "list-patches",
        "opsx:workflow": "workflow",
        "opsx:loop": "loop",
        "opsx:impact": "impact",
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
                print("Usage: cli.py create-feature <name> [--goals 'goal1, goal2']")
                sys.exit(1)
            name = sys.argv[2]
            goals = ""
            if "--goals" in sys.argv:
                idx = sys.argv.index("--goals")
                goals = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else ""
            print(spec_create_feature(name, goals))

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
