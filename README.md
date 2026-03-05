# OpenSpec Framework

AI-native specification framework for building software with AI agents.

[![Spec Validation](https://github.com/your-org/openspec-framework/actions/workflows/spec-validation.yml/badge.svg)](https://github.com/your-org/openspec-framework/actions/workflows/spec-validation.yml)

---

## What is OpenSpec?

OpenSpec provides a reusable specification workflow that enables:

- **Prevent spec drift** - Automated validation keeps specs consistent
- **AI collaboration** - Clear entry points and rules for AI agents
- **Versioned architecture** - Track changes with ADR documents
- **Traceable decisions** - All design decisions are recorded
- **Code generation** - Transform specs into implementation artifacts

---

## Quick Start

### 1. Copy to Your Project

```bash
cp -r spec/ tools/ .github/ /path/to/your/project/
```

### 2. Define Your Vision

Edit `spec/core/vision.md`:

```markdown
# System Vision

My project aims to [goal].

Key goals:
- Goal 1
- Goal 2
```

### 3. Define Architecture

Edit `spec/core/architecture.md`:

```markdown
# System Architecture

System layers:
1. Frontend
2. API
3. Database
```

### 4. Add Features

Create `spec/features/my-feature/spec.md` and `tasks.md`.

### 5. Validate & Generate

```bash
# Validate specs
python3 tools/spec-linter.py spec

# Generate code
python3 tools/spec-compiler.py spec generated

# Visualize structure
python3 tools/spec-graph.py spec tree
```

---

## Spec Layers

```
Vision (Why)
    │
    ▼
Architecture (What)
    │
    ▼
Features (How)
    │
    ▼
Tasks (Do)
```

---

## AI Agent Entry Point

AI agents should start by reading:

```
spec/index.md
```

This index guides agents through the specification hierarchy in the correct order.

---

## Project Structure

```
openspec-framework/
├── spec/                    # Specifications
│   ├── index.md            # AI entry point
│   ├── core/               # Vision & Architecture
│   │   ├── vision.md
│   │   ├── architecture.md
│   │   └── glossary.md
│   ├── features/           # Feature specs
│   │   ├── template.md
│   │   └── <feature>/
│   │       ├── spec.md
│   │       ├── tasks.md
│   │       └── decisions.md
│   ├── decisions/          # Architecture Decision Records
│   │   └── ADR-*.md
│   ├── workflow/           # Process rules
│   │   ├── spec-workflow.md
│   │   ├── ai-agent-rules.md
│   │   └── versioning.md
│   └── archive/            # Deprecated specs
├── tools/                   # Automation tools
│   ├── spec-linter.py      # Validation
│   ├── spec-compiler.py    # Code generation
│   ├── spec-graph.py       # Visualization
│   ├── ai-dev-loop.py      # Workflow orchestration
│   ├── validate-spec.sh    # Quick validation
│   └── run-loop.sh         # Run full loop
├── docs/                    # Documentation
│   ├── QUICKSTART.md
│   └── ARCHITECTURE.md
└── .github/                 # GitHub integration
    ├── copilot-instructions.md
    └── workflows/
        └── spec-validation.yml
```

---

## OpenSpec Pro Features

| Feature | Tool | Description |
|---------|------|-------------|
| **Validation** | `spec-linter.py` | Check spec consistency |
| **Compilation** | `spec-compiler.py` | Generate code from specs |
| **Visualization** | `spec-graph.py` | View spec hierarchy |
| **Dev Loop** | `ai-dev-loop.py` | Automate development cycle |

---

## Framework Principles

1. **Spec First** - All implementation starts with specification
2. **Version Everything** - Changes create new versions, never overwrite
3. **Record Decisions** - Architecture decisions documented in ADRs
4. **Prevent Overwrite** - Never modify specs without versioning
5. **Archive Deprecated** - Move old specs to archive directory

---

## AI Agent Rules

AI agents working with this framework MUST follow:

1. Never overwrite existing spec without versioning
2. Architecture changes require ADR
3. Feature specs must not conflict with architecture
4. Deprecated specs must move to `spec/archive`
5. Tasks must reference a spec

See `spec/workflow/ai-agent-rules.md` for details.

---

## CI/CD Integration

The framework includes GitHub Actions workflow:

```yaml
# .github/workflows/spec-validation.yml
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: python3 tools/spec-linter.py spec
      - run: python3 tools/spec-compiler.py spec generated
```

---

## Documentation

- [Quick Start Guide](docs/QUICKSTART.md)
- [Architecture Overview](docs/ARCHITECTURE.md)
- [OpenSpec Pro](spec/workflow/openspec-pro.md)
- [AI Agent Rules](spec/workflow/ai-agent-rules.md)

---

## Why OpenSpec?

| Problem | Solution |
|---------|----------|
| AI randomly modifies specs | Workflow rules prevent overwrites |
| Specs get overwritten | Versioning preserves history |
| Design drift | ADRs track decisions |
| AI doesn't know where to start | `spec/index.md` entry point |
| Features become disorganized | Structured `features/` directory |

---

## License

MIT License
