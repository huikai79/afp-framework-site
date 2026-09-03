---
title: AFP Specification
type: page
summary: Current public specification for AFP / SafeLoop.
---

## Purpose

AFP defines a reliability-oriented workflow for AI systems that produce consequential or reusable outputs. The current public specification is intentionally small and testable.

## Core workflow

1. **Assumptions** — state material assumptions that could change the result.
2. **Evidence** — attach important claims to inspectable evidence where available.
3. **Counter-evidence** — actively check for evidence or conditions that could overturn the working conclusion.
4. **Decision** — distinguish facts, inference, assumptions, and unknowns before converging.
5. **Validation** — test the output against explicit acceptance criteria and known failure modes.
6. **Revision** — when validation fails or evidence changes, revise and run the relevant checks again.

## SafeLoop

SafeLoop is the feedback cycle around that workflow:

**Produce → Inspect → Challenge → Validate → Revise → Re-test**

The loop is complete only when the result either passes its stated checks or is explicitly marked as unresolved.

## Reliability requirements

A conforming AFP workflow should make it possible to answer:

- What evidence supports the important claims?
- Which assumptions materially affect the result?
- What could falsify or block the conclusion?
- Which checks were performed?
- What changed after a failed check or new evidence?
- Can the relevant test be run again?

## Scope boundary

AFP does not guarantee factual correctness, safety, or compliance by itself. It is a workflow structure for making those properties easier to test and audit. Domain-specific controls, qualified human review, and external rules remain necessary where applicable.

## Status

**Public specification status: working specification.** This page defines the current minimum structure. Formal schemas, machine-readable states, and conformance tests are planned but are not claimed as complete.
