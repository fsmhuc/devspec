# Spec Graph

Visualize specification hierarchy and dependencies.

---

## Purpose

Provide visual overview of spec structure.

---

## Output Formats

### ASCII Tree

```bash
python3 tools/spec-graph.py spec tree
```

Example output:

```
OpenSpec Hierarchy

└── 📁 OpenSpec
    ├── 🎯 Vision
    ├── 🏗️ Architecture
    ├── 📚 Features
    │   ├── 📦 example-feature
    │   │   └── ✅ Tasks
    └── 📋 Decisions
        └── 📝 ADR-0001-spec-versioning
```

### Mermaid Diagram

```bash
python3 tools/spec-graph.py spec mermaid
```

Generates Mermaid flowchart for documentation.

### JSON Graph

```bash
python3 tools/spec-graph.py spec json
```

Machine-readable graph structure.

---

## Integration

Use JSON output for:

- CI/CD visualization
- IDE plugins
- Custom tooling
