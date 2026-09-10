[繁體中文](README.zh.md)

# Antifragile Prompting (AFP) Framework · SafeLoop

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

AFP / SafeLoop is an open working framework for making consequential or reusable AI workflows easier to inspect, challenge, validate, revise, and re-test.

## Current public contract

**Assumptions → Evidence → Counter-evidence → Decision → Validation → Revision**

SafeLoop is the feedback cycle around that workflow: **Produce → Inspect → Challenge → Validate → Revise → Re-test**.

AFP does not by itself guarantee factual correctness, safety, compliance, or superior model performance. Domain controls and qualified human review remain necessary where applicable.

## Evidence status

- Public specification: working specification.
- Failure library: initial taxonomy published; reproduced cases are still being developed.
- Evaluation: Pilot Protocol v0.1 published.
- Benchmark scores: not yet published.

The project should not be described as empirically superior until reproducible comparisons support that claim.

## Repository map

- `content/specification/` — current public specification.
- `content/evaluations/` — evaluation design, protocol, and pilot status.
- `content/failure-cases/` — failure taxonomy and future reproduced cases.
- `benchmarks/afp-v0.1/` — frozen pilot pack and raw-output runner.
- `system-prompts/` and the 2025 prompt page — historical prompt-governance artifacts; not the complete current specification.
- `static/uploads/` — archived whitepaper PDFs. The 2025 PDFs are historical concept editions.

## Reproducibility

The benchmark validation mode makes no model API calls. Live mode is manual, requires an explicit model ID and repository secret, and writes raw outputs for later grading. Raw generation alone does not establish a benchmark result.

## Contributing

Review the public protocol, reproduce the benchmark pack, propose reproducible failure cases, or submit documentation/implementation improvements through GitHub Issues and Pull Requests. Do not post secrets or sensitive personal information in public discussions.

## License

AFP-owned text and documentation are released under Creative Commons Attribution 4.0 International (CC BY 4.0). Third-party software and template components retain their own licenses.
