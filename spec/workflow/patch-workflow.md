# Patch Workflow

Lightweight workflow for small bug fixes.

---

## When to Use Patch

Use patches for:

- Bug fixes
- Typos and minor corrections
- Small refactoring
- Configuration changes

Do NOT use patches for:

- New features (use feature spec)
- Architecture changes (use ADR)
- Breaking changes (use proposal)

---

## Patch vs Proposal

| Criteria | Patch | Proposal |
|----------|-------|----------|
| Spec changes | No | Yes |
| Breaking changes | No | Possibly |
| New functionality | No | Yes |
| Review required | Optional | Required |
| ADR required | No | If architectural |

---

## Workflow

```
1. Create patch file
   changes/patches/fix-<description>.md

2. Document problem and fix

3. Test the fix

4. Mark checklist complete

5. Commit with prefix: [patch] fix description
```

---

## Naming Convention

```
changes/patches/fix-<short-description>.md

Examples:
- fix-ipv6-parse.md
- fix-login-timeout.md
- fix-memory-leak-worker.md
```

---

## Directory Structure

```
changes/
├── patches/           # Bug fixes (lightweight)
│   ├── patch-template.md
│   └── fix-*.md
│
└── proposals/         # Larger changes (full review)
    ├── proposal-template.md
    └── prop-*.md
```
