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

## 4. Required report sections

Every substantive report should include:

1. Incident ID, date, status, severity, reporter/runtime provenance.
2. Short description of the failure.
3. User intent / expected behavior.
4. Observed behavior, preferably with exact excerpts.
5. Relevant provenance and prior corrections.
6. Failure chain — the sequence of control failures, not just the final bad output.
7. Root-cause analysis separated into verified findings and hypotheses.
8. Impact.
9. Corrective controls.
10. Regression tests / acceptance criteria.
11. Effect boundary — what was and was not changed by writing the report.

## 5. Behavioral failure rules

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

## 6. Closure criteria

An issue may close only when:

- the failure mechanism is bounded well enough to test;
- corrective controls are specified or implemented;
- regression cases exist that would fail on the old behavior and pass on the corrected behavior;
- any claimed implementation/persistence/effect has been read back or otherwise verified;
- unresolved hypotheses are explicitly left unresolved.

Closing one issue does not establish global behavioral correctness.
