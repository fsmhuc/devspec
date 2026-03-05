# Quick Start Guide

Get started with OpenSpec Framework in 5 minutes.

---

## 1. Copy to Your Project

```bash
cp -r spec/ /path/to/your/project/
cp -r tools/ /path/to/your/project/
cp -r .github/ /path/to/your/project/
```

---

## 2. Define Your Vision

Edit `spec/core/vision.md`:

```markdown
# System Vision

My project aims to [goal].

Key goals:

- Goal 1
- Goal 2
- Goal 3
```

---

## 3. Define Architecture

Edit `spec/core/architecture.md`:

```markdown
# System Architecture

System layers:

1. Frontend
2. API
3. Database

Architecture rules:

- Frontend calls API only
- API handles business logic
- Database stores state
```

---

## 4. Add a Feature

Create `spec/features/my-feature/spec.md`:

```markdown
# My Feature

## Goals

- Solve problem X

## Design

Component A talks to Component B.

## Interfaces

- GET /api/my-feature
- POST /api/my-feature
```

Create `spec/features/my-feature/tasks.md`:

```markdown
# Tasks

- [ ] Design API schema
- [ ] Implement endpoint
- [ ] Add tests
```

---

## 5. Validate

```bash
python3 tools/spec-linter.py spec
```

---

## 6. Generate Code

```bash
python3 tools/spec-compiler.py spec generated
```

---

## 7. Visualize

```bash
python3 tools/spec-graph.py spec tree
```

---

## 8. Run Full Loop

```bash
./tools/run-loop.sh
```

---

## Next Steps

- Read `spec/workflow/ai-agent-rules.md`
- Set up CI/CD with `.github/workflows/spec-validation.yml`
- Customize tools for your stack
