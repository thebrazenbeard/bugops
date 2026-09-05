# BugOps Reporting Standard

## 1. Purpose

BugOps exists to make failures inspectable and actionable rather than merely memorable. Reports should capture what actually failed, why the failure mattered, what evidence supports the analysis, and what would count as a real correction.

## 2. Evidence classes

Use these labels inside reports:

- `USER_DIRECT` — explicit user statement/correction.
- `OBSERVED` — directly observed runtime/output behavior.
- `RETRIEVED_EVIDENCE` — read back from a governed or durable source.
- `INFERENCE` — reasoned conclusion from evidence; must name its premises.
- `HYPOTHESIS` — plausible mechanism not yet verified.

Do not promote inference or hypothesis into observed fact by repetition.

## 3. Severity

- `SEV-0` — safety/security/data-loss or protected-effect failure with immediate material risk.
- `SEV-1` — core control, identity, authority, provenance, correction, or behavioral-integrity failure; repeated regression after an existing correction also qualifies.
- `SEV-2` — material workflow or quality failure with bounded impact and no protected-effect breach.
- `SEV-3` — localized miss, presentation defect, or low-impact usability issue.

Severity describes impact, not emotional intensity.

## 4. Incident lifecycle and PR requirement

A substantive BugOps incident is not complete when an issue exists. The default control path is:

1. **Open the issue immediately** so the incident has a durable lifecycle tracker.
2. **Create an incident branch** from a fresh read of the current default-branch head. Use a stable name such as `bug/BUG-0001-short-slug`.
3. **Write or update the durable report on the incident branch.** Regression cases, corrective-control specifications, and BugOps process changes for that incident belong on the same branch when practical.
4. **Open a pull request against the default branch** and link the issue and durable report. The PR is the review/adjudication surface for the incident record and proposed control changes.
5. **Keep the issue open after the PR is merged** unless the closure criteria below are independently satisfied. A merged report or implementation PR is evidence of source integration, not proof that runtime behavior is fixed.
6. **Verify readback** of the branch, PR, report, and any claimed implementation/effect before stating that the step occurred.

For `SEV-0`, `SEV-1`, and `SEV-2`, **issue + incident branch + PR are required by default**. A `SEV-3` incident may remain issue-only when it is purely localized and requires no durable report or source change; if source changes are proposed, it also requires a PR.

If an incident was recorded directly on the default branch before this control existed, do not rewrite history merely to simulate a clean PR. Record the process defect, create the incident branch from the fresh current head, put the corrective BugOps/process changes on that branch, open a PR, and link the original issue/report. The PR then establishes the review layer prospectively without pretending the earlier direct commit did not happen.

## 5. Required report sections

Every substantive report should include:

1. Incident ID, date, status, severity, reporter/runtime provenance.
2. Issue and PR references.
3. Short description of the failure.
4. User intent / expected behavior.
5. Observed behavior, preferably with exact excerpts.
6. Relevant provenance and prior corrections.
7. Failure chain — the sequence of control failures, not just the final bad output.
8. Root-cause analysis separated into verified findings and hypotheses.
9. Impact.
10. Corrective controls.
11. Regression tests / acceptance criteria.
12. Effect boundary — what was and was not changed by writing the report.

## 6. Behavioral failure rules

### Proposition integrity

If the user states proposition `A`, the runtime must not silently replace it with stronger/broader/different proposition `B` and then answer or correct `B` as though the user stated it.

### Provenance-sensitive terms

Project-specific coined words, symbols, correction keys, unusual phrases, or explicitly provenance-bearing referents must trigger retrieval when their exact meaning materially affects the response. Local semantic plausibility is not enough.

### Correction interrupt

A present correction terminates the obsolete interpretation route. The runtime applies the correction before apology, justification, explanation, or stylistic repair.

### Uptake tracking

Negative or disappointed user uptake is evidence that the preceding interpretation may have failed. The runtime should reassess the local proposition/frame rather than automatically continuing the prior bit.

### Identity / role recovery

After material degradation, identity or role claims should not be self-certified by prose alone when the governing project provides a validation/recovery mechanism.

## 7. Closure criteria

An issue may close only when:

- the failure mechanism is bounded well enough to test;
- corrective controls are specified or implemented;
- regression cases exist that would fail on the old behavior and pass on the corrected behavior;
- the incident PR/review path required by Section 4 has been completed or an explicit exception is documented;
- any claimed implementation/persistence/effect has been read back or otherwise verified;
- unresolved hypotheses are explicitly left unresolved.

Closing one issue does not establish global behavioral correctness.
