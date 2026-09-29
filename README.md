# Saffron Quality Gate (SQG)

**An executable quality gate for code, content and configuration.**

SQG is a production-grade quality enforcement engine that scans code, content, config, and design against 36 prohibited anti-slop patterns (A-001 through A-036) and scores deliverables across 14 quality dimensions — correctness, security, resilience, maintainability, usability, and more.

Built by [Saffron](https://saffronsystems.io), an applied-intelligence and software engineering company in Minneapolis. SQG flags known failure patterns; it cannot prove that a codebase is correct, and it is not a substitute for tests or review.

## Quick Start

```bash
pip install saffron-quality-gate

# Scan your project
sqg scan --path .

# One-line summary
sqg scan --path . --format summary

# Full quality report
sqg audit --path . --format table
```

## The 36 Anti-Slop Patterns

| ID | Pattern | Severity |
|----|---------|----------|
| A-001 | Happy-path-only implementation | 🔴 Blocker |
| A-002 | Placeholder logic (TODO/FIXME/HACK) | 🔴 Blocker |
| A-003 | Generic boilerplate | 🟡 Warning |
| A-004 | Unverified claims | ⚪ Info |
| A-005 | Cargo-cult architecture | ⚪ Skip |
| A-006 | Feature checklists without depth | ⚪ Info |
| A-007 | Verbose output / low info-density | ⚪ Info |
| A-008 | Inconsistent naming/styling | 🟡 Warning |
| A-009 | Tests-for-coverage (empty asserts) | 🔴 Blocker |
| A-010 | Polished surface, weak foundation | 🟡 Warning |
| A-011 | Excessive abstraction | ⚪ Info |
| A-012 | Dependency bloat | 🟡 Warning |
| A-013 | Default config shipped unchanged | 🔴 Blocker |
| A-014 | **Silent failure (except: pass)** | 🚨 Highest Priority |
| A-015 | Hardcoded values | 🔴 Blocker |
| A-016 | Inconsistent error handling | 🟡 Warning |
| A-017 | One-size-fits-all / copy-paste | 🟡 Warning |
| A-018 | Premature optimization | ⚪ Info |
| A-019 | Symmetry obsession | ⚪ Skip |
| A-020 | Semantic overload | ⚪ Info |
| A-021 | Performance theatre | ⚪ Info |
| A-022 | Negative code (workarounds) | 🟡 Warning |
| A-023 | Comment rot | ⚪ Info |
| A-024 | Framework lock-in | 🟡 Warning |
| A-025 | Premature generalization | ⚪ Info |
| A-026 | Implicit contracts | 🟡 Warning |
| A-027 | False laziness | 🔴 Blocker |
| A-028 | Code golf | ⚪ Info |
| A-029 | Copy-paste reuse (duplicates) | 🟡 Warning |
| A-030 | Error string parsing | 🔴 Blocker |
| A-031 | Numeric type abuse | 🟡 Warning |
| A-032 | Implicit null handling | ⚪ Skip |
| A-033 | **Timezone neglect** | 🔴 Blocker |
| A-034 | **Side-effect mismatch** | 🔴 Blocker |
| A-035 | Silent data loss | 🟡 Warning |
| A-036 | Callback pyramid / nested chains | 🟡 Warning |

## Commands

```bash
sqg --help              # Full help
sqg scan --path .       # Anti-slop scan (A-001 to A-036)
sqg audit --path .      # Full 14-dimension quality audit
sqg gate --path .       # Unified gate runner (all checks)
sqg version             # Version info
```

## Integration

```bash
# As a pre-commit hook
echo '#!/bin/sh\nsqg scan --path . --format summary || exit 1' > .git/hooks/pre-commit

# As a CI step
- name: Quality Gate
  run: sqg gate --path . --strict
```

## The 14 Quality Dimensions

1. **Correctness** (15%)
2. **Functional Excellence** (12%)
3. **Architecture** (10%)
4. **Resilience & Reliability** (10%)
5. **Security** (10%)
6. **Performance & Efficiency** (8%)
7. **Usability** (10%)
8. **Accessibility** (5%)
9. **Maintainability** (10%)
10. **Observability** (5%)
11. **Test Quality & Coverage** (5%)
12. **Aesthetic & Visual** (3%)
13. **Documentation** (4%)
14. **Strategic Value** (3%)

---

**[Saffron](https://saffronsystems.io)** · Minneapolis, Minnesota · Nothing can match the human touch.