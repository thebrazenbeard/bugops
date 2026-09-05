# BugOps

Operational control repository for reporting, analyzing, tracking, and closing bugs, misses, regressions, and behavioral failures.

## Operating model

BugOps separates **incident evidence** from **lifecycle tracking**:

- `reports/` contains durable error reports/postmortems.
- GitHub Issues are the live queue for status, ownership, follow-up, and closure.
- `.github/ISSUE_TEMPLATE/behavioral-error-report.md` is the minimum intake format for behavioral failures.
- `REPORTING_STANDARD.md` defines severity, evidence classes, required analysis, regression criteria, and closure rules.

A report is not complete because the failure was acknowledged. It is complete only when the actual failed behavior is identified, relevant provenance is preserved, corrective controls are specified, and a regression test can distinguish the corrected behavior from the failure.

## Core rules

1. Preserve the user's actual proposition and referent. Do not silently strengthen, broaden, sanitize, or substitute it.
2. Distinguish `OBSERVED`, `USER_DIRECT`, `RETRIEVED_EVIDENCE`, `INFERENCE`, and `HYPOTHESIS`.
3. If a Project-specific term, symbol, correction key, or odd phrase may have provenance, retrieve before interpreting.
4. A present correction stops the obsolete route before apology or explanation.
5. Repeated failures must link prior incidents/corrections when known.
6. Never claim a fix, persistence, routing change, or closure without readback/evidence.
7. GitHub issue closure means the stated acceptance criteria have been met; it does not mean the underlying architecture is globally solved.

## Current incidents

See the repository Issues tab and `reports/`.
