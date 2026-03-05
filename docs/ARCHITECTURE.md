# OpenSpec Framework Architecture

---

## Overview

OpenSpec is an AI-native specification framework designed for human-AI collaboration.

---

## Design Principles

### 1. Spec First

All implementation starts with specification.

### 2. Version Everything

Changes create new versions, never overwrite.

### 3. Record Decisions

Architecture decisions are documented in ADRs.

### 4. Validate Continuously

Automated tools ensure consistency.

### 5. Generate from Specs

Code is derived from specifications.

---

## Directory Structure

```
openspec-framework/
├── spec/                    # Specifications
│   ├── index.md            # AI entry point
│   ├── core/               # Core specs
│   ├── features/           # Feature specs
│   ├── decisions/          # ADRs
│   ├── workflow/           # Process rules
│   └── archive/            # Deprecated specs
├── tools/                   # Automation tools
│   ├── spec-linter.py      # Validation
│   ├── spec-compiler.py    # Code generation
│   ├── spec-graph.py       # Visualization
│   └── ai-dev-loop.py      # Workflow orchestration
├── docs/                    # Documentation
└── .github/                 # GitHub integration
```

---

## Spec Layers

```
Vision          (Why)
    │
    ▼
Architecture    (What)
    │
    ▼
Features        (How)
    │
    ▼
Tasks           (Do)
```

---

## Tool Pipeline

```
spec/
  │
  ├── spec-linter.py ───> Validation Report
  │
  ├── spec-compiler.py ─> generated/
  │                         ├── stubs/
  │                         ├── schemas/
  │                         ├── docs/
  │                         └── tests/
  │
  └── spec-graph.py ────> Visualization
```

---

## AI Integration

### Entry Point

AI agents read `spec/index.md` first.

### Workflow Rules

AI agents follow `spec/workflow/ai-agent-rules.md`.

### GitHub Copilot

`.github/copilot-instructions.md` provides context.

---

## Extension Points

1. **Custom Validators**: Extend `spec-linter.py`
2. **Code Generators**: Extend `spec-compiler.py`
3. **Output Formats**: Extend `spec-graph.py`
4. **Loop Stages**: Extend `ai-dev-loop.py`
