# OpenSpec Pro

Advanced AI-native specification system.

---

## Components

### 1. Spec Validator

Validates specification consistency and completeness.

See: `spec/workflow/spec-validator.md`

### 2. Spec Compiler

Transforms specs into code artifacts.

See: `spec/workflow/spec-compiler.md`

### 3. Spec Graph

Visualizes spec hierarchy.

See: `spec/workflow/spec-graph.md`

### 4. AI Dev Loop

Orchestrates automated development cycle.

See: `spec/workflow/ai-dev-loop.md`

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    OpenSpec Pro                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│   spec/                                                  │
│   ├── index.md ──────> [Validator] ────┐               │
│   ├── core/                             │               │
│   ├── features/                         ▼               │
│   └── decisions/ ────> [Compiler] ───> generated/       │
│                              │                          │
│                              ▼                          │
│                         [Graph] ───> Visualization      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Benefits

| Problem | Solution |
|---------|----------|
| Spec drift | Automated validation |
| Manual coding | Code generation |
| Unclear structure | Visual graphs |
| Broken workflow | AI Dev Loop |

---

## Getting Started

1. Define specs in `spec/` directory
2. Run validation: `./tools/validate-spec.sh`
3. Generate code: `python3 tools/spec-compiler.py spec`
4. Visualize: `python3 tools/spec-graph.py spec tree`
5. Full loop: `./tools/run-loop.sh`
