# Spec Index

This is the entry point for all AI agents.

Agents MUST read documents in the following order.

---

# 1 Vision

System goals and long-term direction.

```
spec/core/vision.md
```

---

# 2 Architecture

High level system architecture.

```
spec/core/architecture.md
```

---

# 3 Glossary

Key terms and definitions.

```
spec/core/glossary.md
```

---

# 4 Decisions

Architecture decisions.

```
spec/decisions
```

---

# 5 Features

Feature level specifications.

```
spec/features
```

---

# 6 Tasks

Implementation tasks for each feature.

```
spec/features/*/tasks.md
```

---

# 7 Workflow

AI agent collaboration rules.

```
spec/workflow
```

Agents MUST follow these rules before modifying any spec.

---

# 8 Changes

Track patches and proposals.

```
changes/
├── patches/     # Bug fixes (lightweight)
└── proposals/   # Larger changes (full review)
```

## Patch Workflow

For small bug fixes without spec changes:

```
changes/patches/fix-<description>.md
```

See: `spec/workflow/patch-workflow.md`

## Proposal Workflow

For larger changes affecting specs:

```
changes/proposals/prop-<description>.md
```
