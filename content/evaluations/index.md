---
title: Evaluations
type: page
summary: Public evaluation plan for testing AFP against simpler baselines.
---

## Evaluation question

The central question is simple: **does AFP improve reliability enough to justify the extra structure?**

That claim should be tested rather than assumed.

## Baseline design

The current evaluation plan compares four conditions while holding the model, task, tools, evidence set, and test date constant:

1. **Model only** — no additional governance structure.
2. **General instructions** — normal custom instructions or task guidance.
3. **AFP** — the AFP workflow applied to the same task.
4. **AFP + governance controls** — AFP with explicit evidence gates, review conditions, and regression checks where relevant.

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

Any unavoidable difference should be documented.

## Reporting rule

AFP should not be described as empirically superior until a reproducible comparison supports that claim. Negative or mixed results should be published alongside positive results.

## Current status

**Evaluation status: protocol defined; public benchmark results pending.** The website will publish datasets, prompts/instructions, scoring rubrics, and results when they are ready for reproducible review.
