---
title: AFP Benchmark Protocol v0.1
type: page
url: /evaluations/protocol/
summary: Public text-layer pilot protocol for fair AFP baseline comparisons.
---

## Purpose

This pilot does not assume AFP is better. It defines a comparison contract that can be inspected and reproduced.

The question is: **under the same model and the same visible inputs, does AFP reduce observable reliability failures enough to justify its additional structure?**

## Test boundary

Protocol v0.1 is text-only. It does not test live web search, file operations, external agent actions, production traffic, or end-to-end safety. Results from this pilot must not be presented as proof of full agent capability.

## Four comparison conditions

1. **A · Model only** — no additional governance structure.
2. **B · General instructions** — ordinary task/custom instructions.
3. **C · AFP** — AFP workflow applied to the same task.
4. **D · AFP + governance controls** — AFP plus explicit evidence gates, review conditions, and regression checks where relevant.

Whenever possible, comparisons hold constant the **model, task, tools, evidence set, and evaluation date**.

## Validity before quality

Each run is first classified so infrastructure and test-design failures are not silently counted as model failures. Public states include `MODEL_PASS`, `MODEL_FAIL`, `PROVIDER_BLOCK`, `INFRA_ERROR`, `INVALID_TEST`, and `GRADER_DISPUTE`.

Model-quality pass rate is calculated only from `MODEL_PASS` and `MODEL_FAIL`; all other states remain visible separately.

## Minimum reporting

Reports should preserve task/rubric scores, severe or fatal failures, repeated-run variance, unsupported high-confidence claims, missed counter-evidence, tool calls, token usage, completion time, raw outputs, grader reasons, and excluded cases where applicable.

## Reproducibility

The frozen machine-readable pilot pack and runner live in `benchmarks/afp-v0.1/` in the public repository. Validation mode makes no model API calls. Live raw-output generation is manual and does not become a benchmark claim until grading and validity checks are complete.

[View the benchmark files on GitHub](https://github.com/huikai79/afp-framework-site/tree/main/benchmarks/afp-v0.1)

## Current status

**Protocol published; benchmark scores not yet published.** Negative, mixed, disputed, and excluded outcomes should remain visible alongside positive results.
