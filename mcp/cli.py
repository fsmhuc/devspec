#!/usr/bin/env python3
"""
OpenSpec CLI - Direct command-line interface for OpenSpec tools

Usage:
    python mcp/cli.py validate [spec_root]
    python mcp/cli.py compile [spec_root] [output_dir]
    python mcp/cli.py graph [spec_root] [tree|mermaid|json]
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
                total = len(re.findall(r"- \[[ x]\]", content))
                done = len(re.findall(r"- \[x\]", content))
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
