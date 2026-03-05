# AI Development Loop

Automated development cycle orchestration.

---

## Purpose

Connect specs to implementation through automated workflow.

---

## Loop Stages

```
┌─────────────────────────────────────────────────┐
│                                                 │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│  │ Validate │ -> │ Generate │ -> │   Test   │  │
│  └──────────┘    └──────────┘    └──────────┘  │
│       │                               │         │
│       └─────────── <- ────────────────┘         │
│                    │                            │
│               ┌────▼────┐                       │
│               │ Analyze │                       │
│               └─────────┘                       │
└─────────────────────────────────────────────────┘
```

---

## Stage 1: Validate

Run spec-linter to check consistency.

**Failure**: Stop and fix spec issues.

---

## Stage 2: Generate

Run spec-compiler to create artifacts.

**Failure**: Check compiler logs.

---

## Stage 3: Test

Run project tests on generated code.

**Skipped**: If no test runner found.

---

## Stage 4: Analyze

Review results and suggest updates.

Output:
- Failed stage actions
- Incomplete tasks list
- Spec improvement suggestions

---

## Usage

```bash
# Full loop
python3 tools/ai-dev-loop.py spec

# Skip tests
python3 tools/ai-dev-loop.py spec --skip-tests

# Shell wrapper
./tools/run-loop.sh spec
```

---

## CI/CD Integration

Add to `.github/workflows/spec-validation.yml`:

```yaml
name: Spec Validation

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: python3 tools/spec-linter.py spec
```
