# AFP Architecture

AFP should remain auditable as it evolves. The repository therefore separates specification, prompts, evaluation material, benchmark execution, and public claims instead of treating them as one document.

## Core flow

```text
Specification
    |
    v
Operational prompts / procedures
    |
    v
Evaluation cases + failure cases
    |
    v
Benchmark runner
    |
    v
Observed results
    |
    v
Calibrated claims / documentation
```

Each layer has a different role. A change in one layer must not silently redefine the others.

## Layer responsibilities

### Specification

Defines the intended concepts, boundaries, terminology, and required behavior.

It answers: **What is AFP supposed to do?**

### Operational prompts and procedures

Translate the specification into instructions that a model or workflow can execute.

They answer: **How is the specification operationalized?**

### Evaluation and failure cases

Provide concrete cases, expected properties, known limitations, and regression targets.

They answer: **What would count as success or failure on a case?**

### Benchmark runner

Executes the defined evaluation protocol. The runner should be deterministic wherever the surrounding model/API allows it and should record variables that cannot be controlled.

It answers: **How is the comparison performed?**

### Results and claims

Observed benchmark output does not automatically justify a broad claim. Public wording must stay within the tested model, task set, version, and protocol.

It answers: **What does the evidence actually support?**

## Non-negotiable separations

1. **Gold/evaluation answers are not runtime instructions.** Holdout material must not leak into the system being tested.
2. **Examples are not evidence of superiority.** Examples demonstrate use; comparative claims require controlled evaluation.
3. **Failure taxonomies are not scores.** A named failure mode helps diagnose behavior but does not by itself measure prevalence or effect size.
4. **More process is not automatically better.** A new AFP step should survive regression testing or be removed/reduced.
5. **Benchmark output is versioned evidence.** Results apply to the tested configuration, not to every model or future release.

## Change lifecycle

For a material AFP change:

```text
propose
  -> identify affected assumptions
  -> add/update failure or evaluation case
  -> implement the change
  -> run paired/regression evaluation
  -> inspect regressions and unknowns
  -> update claims/documentation
```

If a change cannot be evaluated yet, mark it as experimental rather than presenting it as an established improvement.

## Benchmark record

A reproducible comparison should record at least:

- AFP/specification version;
- model and mode;
- prompt/procedure version;
- task set version;
- execution date;
- relevant tool availability;
- run count or paired-run structure;
- scoring/evaluation rule;
- known contamination or leakage risk;
- failures and unresolved cases.

## Architectural review questions

Before adding a new rule or module:

- Does it address a known failure mode?
- Can the expected improvement be observed or tested?
- Could the same result be achieved with a smaller mechanism?
- Does it change the evaluation target or only the implementation?
- Does it introduce leakage, hidden state, or an unverifiable dependency?
- What result would cause us to roll it back?

The goal of this architecture is not to maximize framework complexity. It is to keep the path from **claim -> procedure -> evidence -> revision** inspectable.
