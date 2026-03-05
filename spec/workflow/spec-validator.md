# Spec Validator

Automated specification validation system.

---

## Purpose

Ensure specifications are consistent and follow framework rules.

---

## Validation Rules

### 1. Completeness

- Vision must define goals
- Architecture must define layers/components
- Features must have spec.md
- ADRs must have required sections

### 2. Consistency

- Features must not conflict with architecture
- Tasks must reference existing specs
- Dependencies must be valid

### 3. Traceability

- All specs must be linked in index.md
- ADRs must reference affected specs
- Changes must be versioned

---

## Usage

```bash
python3 tools/spec-linter.py spec
```

---

## Exit Codes

- 0: All validations passed
- 1: Validation errors found
