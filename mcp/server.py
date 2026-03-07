#!/usr/bin/env python3
"""
DevSpec MCP Server

Provides DevSpec tools as MCP (Model Context Protocol) tools
that can be directly invoked by Claude and other AI assistants.

Usage:
    python mcp/server.py

Or add to Claude Desktop config:
    {
        "mcpServers": {
            "devspec": {
                "command": "python",
                "args": ["/path/to/devspec/mcp/server.py"]
            }
        }
    }
"""

import sys
import json
import os
from pathlib import Path
from typing import Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

# MCP SDK (minimal implementation)
class MCPServer:
    def __init__(self, name: str, version: str):
        self.name = name
        self.version = version
        self.tools = {}

    def tool(self, name: str, description: str, parameters: dict):
        def decorator(func):
            self.tools[name] = {
                "description": description,
                "parameters": parameters,
                "handler": func
            }
            return func
        return decorator

    def run(self):
        """Run the MCP server loop."""
        while True:
            try:
                line = input()
                if not line:
                    continue
                request = json.loads(line)
                response = self.handle_request(request)
                print(json.dumps(response), flush=True)
            except EOFError:
                break
            except Exception as e:
                print(json.dumps({"error": str(e)}), flush=True)

    def handle_request(self, request: dict) -> dict:
        method = request.get("method")
        params = request.get("params", {})

        if method == "initialize":
            return {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {
                    "name": self.name,
                    "version": self.version
                }
            }
        elif method == "tools/list":
            return {
                "tools": [
                    {
                        "name": name,
                        "description": tool["description"],
                        "inputSchema": {
                            "type": "object",
                            "properties": tool["parameters"],
                            "required": [k for k, v in tool["parameters"].items()
                                       if v.get("required", False)]
                        }
                    }
                    for name, tool in self.tools.items()
                ]
            }
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            if tool_name in self.tools:
                try:
                    result = self.tools[tool_name]["handler"](**arguments)
                    return {"content": [{"type": "text", "text": result}]}
                except Exception as e:
                    return {"content": [{"type": "text", "text": f"Error: {str(e)}"}], "isError": True}
            return {"error": f"Unknown tool: {tool_name}"}

        return {"error": f"Unknown method: {method}"}


# Create server
server = MCPServer("devspec", "1.0.0")


@server.tool(
    "spec_validate",
    "Validate DevSpec specifications for consistency and completeness",
    {
        "spec_root": {
            "type": "string",
            "description": "Path to the spec directory",
            "default": "spec"
        }
    }
)
def spec_validate(spec_root: str = "spec") -> str:
    """Validate all specifications."""
    from spec_linter import SpecLinter

    linter = SpecLinter(spec_root)

    # Run all checks
    linter.check_index()
    linter.check_vision()
    linter.check_architecture()
    linter.check_features()
    linter.check_adrs()
    linter.check_tasks()
    linter.check_orphans()

    # Format results
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


@server.tool(
    "spec_compile",
    "Generate code artifacts from DevSpec specifications",
    {
        "spec_root": {
            "type": "string",
            "description": "Path to the spec directory",
            "default": "spec"
        },
        "output_dir": {
            "type": "string",
            "description": "Path to output directory for generated artifacts",
            "default": "generated"
        }
    }
)
def spec_compile(spec_root: str = "spec", output_dir: str = "generated") -> str:
    """Compile specs to code artifacts."""
    from spec_compiler import SpecCompiler

    compiler = SpecCompiler(spec_root, output_dir)
    compiler.compile_all()

    lines = ["=== DevSpec Compilation Complete ===\n"]
    lines.append(f"Output directory: {output_dir}/")
    lines.append("\nGenerated artifacts:")
    lines.append("  - stubs/     TypeScript implementation stubs")
    lines.append("  - schemas/   OpenAPI schemas")
    lines.append("  - docs/      Feature documentation")
    lines.append("  - tests/     Test templates")

    return "\n".join(lines)


@server.tool(
    "spec_graph",
    "Generate visualization of DevSpec hierarchy",
    {
        "spec_root": {
            "type": "string",
            "description": "Path to the spec directory",
            "default": "spec"
        },
        "format": {
            "type": "string",
            "description": "Output format: tree, mermaid, or json",
            "enum": ["tree", "mermaid", "json"],
            "default": "tree"
        }
    }
)
def spec_graph(spec_root: str = "spec", format: str = "tree") -> str:
    """Generate spec hierarchy visualization."""
    from spec_graph import SpecGraph
    import io
    import contextlib

    graph = SpecGraph(spec_root)
    graph.build_graph()

    if format == "tree":
        # Capture ASCII tree output
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            graph.print_ascii_tree()
        return output.getvalue()
    elif format == "mermaid":
        return graph.generate_mermaid()
    elif format == "json":
        return json.dumps(graph.generate_json(), indent=2)

    return "Unknown format. Use: tree, mermaid, or json"


@server.tool(
    "spec_create_feature",
    "Create a new feature specification",
    {
        "name": {
            "type": "string",
            "description": "Feature name (kebab-case)"
        },
        "goals": {
            "type": "string",
            "description": "Feature goals (comma-separated)"
        },
        "spec_root": {
            "type": "string",
            "description": "Path to the spec directory",
            "default": "spec"
        }
    }
)
def spec_create_feature(name: str, goals: str = "", spec_root: str = "spec") -> str:
    """Create a new feature specification structure."""
    spec_path = Path(spec_root) / "features" / name

    if spec_path.exists():
        return f"Error: Feature '{name}' already exists"

    spec_path.mkdir(parents=True)

    # Create spec.md
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

    # Create tasks.md
    tasks_content = f"""# Tasks

- [ ] Design API schema
- [ ] Implement {name} logic
- [ ] Add unit tests
- [ ] Update documentation
"""

    (spec_path / "tasks.md").write_text(tasks_content)

    # Create decisions.md
    decisions_content = f"""# Feature Decisions

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


@server.tool(
    "spec_create_adr",
    "Create a new Architecture Decision Record",
    {
        "title": {
            "type": "string",
            "description": "ADR title"
        },
        "context": {
            "type": "string",
            "description": "The context and problem statement"
        },
        "decision": {
            "type": "string",
            "description": "The decision made"
        },
        "spec_root": {
            "type": "string",
            "description": "Path to the spec directory",
            "default": "spec"
        }
    }
)
def spec_create_adr(title: str, context: str, decision: str, spec_root: str = "spec") -> str:
    """Create a new ADR document."""
    decisions_path = Path(spec_root) / "decisions"

    # Find next ADR number
    existing = list(decisions_path.glob("ADR-*.md"))
    next_num = len(existing) + 1
    adr_name = f"ADR-{next_num:04d}-{title.lower().replace(' ', '-')}.md"
    adr_path = decisions_path / adr_name

    # Create ADR content
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


@server.tool(
    "spec_list_features",
    "List all features and their task status",
    {
        "spec_root": {
            "type": "string",
            "description": "Path to the spec directory",
            "default": "spec"
        }
    }
)
def spec_list_features(spec_root: str = "spec") -> str:
    """List all features with task completion status."""
    import re

    features_path = Path(spec_root) / "features"
    if not features_path.exists():
        return "No features directory found"

    lines = ["=== Feature Status ===\n"]

    for feature_dir in sorted(features_path.iterdir()):
        if feature_dir.is_dir() and feature_dir.name != "template.md":
            tasks_file = feature_dir / "tasks.md"

            total = 0
            done = 0

            if tasks_file.exists():
                content = tasks_file.read_text()
                total = len(re.findall(r"- \[[ x]\]", content))
                done = len(re.findall(r"- \[x\]", content))

            status = f"[{done}/{total}]" if total > 0 else "[no tasks]"
            lines.append(f"  {status} {feature_dir.name}")

    return "\n".join(lines)


@server.tool(
    "spec_read",
    "Read a specification file",
    {
        "path": {
            "type": "string",
            "description": "Path to the spec file (relative to spec root)"
        },
        "spec_root": {
            "type": "string",
            "description": "Path to the spec directory",
            "default": "spec"
        }
    }
)
def spec_read(path: str, spec_root: str = "spec") -> str:
    """Read a specification file."""
    file_path = Path(spec_root) / path

    if not file_path.exists():
        return f"Error: File not found: {path}"

    return file_path.read_text()


# Entry point
if __name__ == "__main__":
    # Check for direct tool invocation (for CLI use)
    if len(sys.argv) > 1:
        tool_name = sys.argv[1]
        if tool_name in server.tools:
            # Parse arguments
            import argparse
            parser = argparse.ArgumentParser(description=f"DevSpec {tool_name}")
            for param, schema in server.tools[tool_name]["parameters"].items():
                parser.add_argument(f"--{param}",
                                   default=schema.get("default"),
                                   help=schema.get("description", ""))
            args = parser.parse_args(sys.argv[2:])
            result = server.tools[tool_name]["handler"](**vars(args))
            print(result)
        else:
            print(f"Unknown tool: {tool_name}")
            print(f"Available tools: {', '.join(server.tools.keys())}")
    else:
        # Run as MCP server
        server.run()
