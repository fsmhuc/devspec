# OpenSpec Framework

AI-native specification framework for building software with AI agents.

---

## Quick Links

- [Quick Start Guide](docs/QUICKSTART.md)
- [Architecture](docs/ARCHITECTURE.md)
- [AI Agent Rules](spec/workflow/ai-agent-rules.md)
- [OpenSpec Pro](spec/workflow/openspec-pro.md)

---

## Project Structure

```
openspec-framework
├── README.md              # This file
├── spec/                  # Specifications
│   ├── index.md          # AI entry point
│   ├── core/             # Vision & Architecture
│   ├── features/         # Feature specs
│   ├── decisions/        # ADRs
│   └── workflow/         # Process rules
├── tools/                 # Automation
│   ├── spec-linter.py    # Validation
│   ├── spec-compiler.py  # Code generation
│   ├── spec-graph.py     # Visualization
│   └── ai-dev-loop.py    # Dev loop
├── docs/                  # Documentation
└── .github/               # CI/CD & AI instructions
```

---

## Usage

### 1. Copy to Your Project

```bash
cp -r spec/ tools/ .github/ /your/project/
```

### 2. Define Specs

- Edit `spec/core/vision.md`
- Edit `spec/core/architecture.md`
- Add features in `spec/features/`

### 3. Validate

```bash
python3 tools/spec-linter.py spec
```

### 4. Generate

```bash
python3 tools/spec-compiler.py spec generated
```

### 5. Visualize

```bash
python3 tools/spec-graph.py spec tree
```

### 6. Run Full Loop

```bash
./tools/run-loop.sh
```

---

## AI Agent Entry Point

AI agents should start by reading:

```
spec/index.md
```

---

## Framework Principles

1. **Spec First** - All implementation starts with specification
2. **Version Everything** - Changes create new versions
3. **Record Decisions** - Architecture decisions in ADRs
4. **Prevent Overwrite** - Never modify specs without versioning
5. **Archive Deprecated** - Move old specs to archive

---

## OpenSpec Pro Features

| Feature | Tool | Purpose |
|---------|------|---------|
| Validation | spec-linter.py | Check consistency |
| Compilation | spec-compiler.py | Generate code |
| Visualization | spec-graph.py | View hierarchy |
| Dev Loop | ai-dev-loop.py | Automate workflow |

---

## License

MIT License
