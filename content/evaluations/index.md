---
title: Evaluations
type: page
summary: Public evaluation plan for testing AFP against simpler baselines.
---

## Evaluation question

The central question is simple: **does AFP improve reliability enough to justify the extra structure?**

That claim should be tested rather than assumed.

## Baseline design

The evaluation compares four conditions while holding the model, task, tools, evidence set, and evaluation date constant whenever possible:

1. **Model only** — no additional governance structure.
2. **General instructions** — normal custom instructions or task guidance.
3. **AFP** — the AFP workflow applied to the same task.
4. **AFP + governance controls** — AFP with explicit evidence gates, review conditions, and regression checks where relevant.

## Validity Gate before Quality Gate

Every result must first be checked for a valid task contract, evidence set, rubric, model-visible premises, and fair comparison. An invalid test, provider block, or grader dispute must not be silently counted as an AFP or baseline failure.

Public results use at least these states:

- `MODEL_PASS`
- `MODEL_FAIL`
- `PROVIDER_BLOCK`
- `INFRA_ERROR`
- `INVALID_TEST`
- `GRADER_DISPUTE`

Model-quality pass rate is calculated only as:

**MODEL_PASS ÷ (MODEL_PASS + MODEL_FAIL)**

All other states remain visible and are reported separately.

## Metrics

The minimum comparison should record:

- task accuracy or rubric score;
- worst-case or fatal failures;
- variance across repeated runs;
- unsupported high-confidence claims;
- missed counter-evidence;
- tool-call count;
- token usage;
- completion time.

For high-risk workflows, average score alone is insufficient. A system that performs well on average but still produces severe unblocked failures may remain unsuitable.

## Experimental controls

A valid comparison should keep the following fixed whenever possible:

**same model · same task · same tools · same evidence · same evaluation date**

Any unavoidable difference must be documented. Shared A/B scoring uses the same user-visible outcome standard; AFP-specific terminology, section names, or exact wording are not requirements for baseline systems.

## Public Pilot Protocol v0.1

The first public protocol is deliberately a **text-only pilot**. It is designed to validate the comparison method, failure-state classification, and scoring workflow before testing live search, file operations, or external agent actions. It must not be cited as evidence of full agent capability.

[Read AFP Benchmark Protocol v0.1 →](/evaluations/protocol/)

## Reporting rule

AFP should not be described as empirically superior until reproducible comparisons support that claim. Negative results, mixed results, raw outputs, grader reasons, and excluded cases should be published alongside positive findings.

## Current status

**Evaluation status: Pilot Protocol v0.1 published; benchmark scores not yet published.**
