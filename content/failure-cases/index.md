---
title: Failure Cases
type: page
summary: A growing taxonomy of AI workflow failures that AFP is designed to expose and contain.
---

## Why failure cases matter

A reliability framework should be judged by the failures it can reveal, contain, and help reproduce. This page defines an initial failure taxonomy for AFP.

## Initial taxonomy

### AFP-F001 · Unsupported factual confidence
The system states a factual conclusion with confidence that is not supported by the available evidence.

**Expected response:** identify the unsupported claim, lower confidence or mark it unresolved, and require evidence before promotion.

### AFP-F002 · Source laundering
A secondary summary, search snippet, or model-generated statement is treated as if it were the original evidence.

**Expected response:** preserve source hierarchy and trace important claims back to the most direct available source.

### AFP-F003 · Missing counter-evidence
The workflow gathers evidence supporting one conclusion but fails to search for material evidence that could overturn it.

**Expected response:** run an explicit counter-evidence check before final convergence.

### AFP-F004 · Tool-result misinterpretation
A tool returns valid data, but the model reads, aggregates, or applies it incorrectly.

**Expected response:** distinguish tool execution success from interpretation success and validate the derived claim separately.

### AFP-F005 · Premature convergence
The system finalizes a decision before unresolved assumptions, conflicts, or blockers have been examined.

**Expected response:** maintain unresolved state and prevent promotion until required gates are satisfied.

### AFP-F006 · High-impact action without an authorization gate
A workflow moves from analysis into an external or consequential action without the required human authorization or policy check.

**Expected response:** separate recommendation from execution and stop at the authorization boundary.

## Evidence standard for future cases

Concrete published cases should include, where possible:

- task and environment;
- model/tool versions;
- relevant input evidence;
- observed failure;
- detection mechanism;
- AFP intervention;
- post-intervention result;
- remaining uncertainty.

## Current status

**Failure library status: taxonomy started; reproduced cases pending publication.** These identifiers describe target failure modes, not proof that AFP has already eliminated them.
