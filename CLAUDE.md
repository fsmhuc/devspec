# OpenSpec Framework - Claude Code Configuration

This file provides instructions for Claude Code when working with this project.

## Project Overview

OpenSpec is an AI-native specification framework for building software with AI agents.

## Spec Entry Point

Always read `spec/index.md` first to understand the project structure.

## Available Tools

### CLI Tools (Direct Execution)

```bash
# Validate specifications
python3 mcp/cli.py validate spec

# Generate code from specs
python3 mcp/cli.py compile spec generated

# Visualize spec hierarchy
python3 mcp/cli.py graph spec tree

# List features and status
python3 mcp/cli.py list spec

# Create new feature
python3 mcp/cli.py create-feature my-feature --goals "goal1, goal2"

# Create new ADR
python3 mcp/cli.py create-adr "decision-title" --context "context" --decision "decision"

# Read a spec file
python3 mcp/cli.py read core/vision.md

# === Patch Workflow (for bug fixes) ===

# Create a patch for bug fix
python3 mcp/cli.py create-patch ipv6-parse --problem "IPv6 parsing fails" --fix "Updated regex"

# List all patches
python3 mcp/cli.py list-patches

# Mark patch as complete
python3 mcp/cli.py complete-patch ipv6-parse
```

### Python Tools

```bash
# Validation
python3 tools/spec-linter.py spec

# Code generation
python3 tools/spec-compiler.py spec generated

# Visualization
python3 tools/spec-graph.py spec tree
python3 tools/spec-graph.py spec mermaid
python3 tools/spec-graph.py spec json

# Full dev loop
python3 tools/ai-dev-loop.py spec
```

## AI Agent Rules

When working with this framework, follow these rules:

1. **Read index first** - Always start with `spec/index.md`
2. **Never overwrite specs** - Create new versions instead
3. **Architecture changes require ADR** - Document decisions in `spec/decisions/`
4. **Features must not conflict with architecture**
5. **Deprecated specs go to archive** - Move to `spec/archive/`
6. **Tasks must reference specs**
7. **Use patches for bug fixes** - Small fixes use `changes/patches/`, not full proposals

## When to Use What

| Change Type | Use | Path |
|-------------|-----|------|
| Bug fix | Patch | `changes/patches/fix-*.md` |
| New feature | Feature Spec | `spec/features/*/spec.md` |
| Architecture change | ADR | `spec/decisions/ADR-*.md` |
| Large change | Proposal | `changes/proposals/prop-*.md` |

## Workflow

```
1. Read spec/index.md
2. Understand vision and architecture
3. Check existing features
4. Modify or create specs
5. Validate changes
6. Generate code if needed
```

## Directory Structure

```
spec/
├── index.md          # AI entry point
├── core/             # Vision, Architecture, Glossary
├── features/         # Feature specs with tasks
├── decisions/        # ADR documents
├── workflow/         # Process rules
└── archive/          # Deprecated specs

changes/
├── patches/          # Bug fixes (lightweight)
│   ├── patch-template.md
│   └── fix-*.md
└── proposals/        # Larger changes (full review)
    ├── proposal-template.md
    └── prop-*.md
```

## MCP Integration

For Claude Desktop or other MCP-compatible tools, use:

```json
{
    "mcpServers": {
        "openspec": {
            "command": "python3",
            "args": ["/path/to/openspec-framework/mcp/server.py"]
        }
    }
}
```

## Quick Actions

When asked to:
- **Validate specs**: Run `python3 mcp/cli.py validate`
- **Create feature**: Run `python3 mcp/cli.py create-feature <name>`
- **Generate code**: Run `python3 mcp/cli.py compile`
- **Show structure**: Run `python3 mcp/cli.py graph`
