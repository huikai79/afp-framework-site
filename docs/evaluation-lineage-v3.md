# AFP Evaluation Lineage v3

AFP benchmark output is treated as a **run bundle**, not an isolated JSONL file.

## Run bundle

A live execution produces:

```text
raw-<timestamp>-<model>-r<n>-<execution>.jsonl
raw-<timestamp>-<model>-r<n>-<execution>.manifest.json
```

The manifest binds the run to:

- execution ID;
- protocol/scope;
- benchmark pack SHA-256;
- runner SHA-256;
- live dependency-file SHA-256;
- requested model and reasoning effort;
- expected and actual record counts;
- fixture/treatment IDs;
- raw-result filename, size and SHA-256;
- Python/platform/OpenAI SDK environment;
- runtime/evaluation leakage boundary;
- scoring state.

Each raw row also records the execution ID, pack/runner hashes, fixture risk, effective instruction hash and input hash.

## Verification

`runner.py verify-run <manifest>` checks:

1. manifest schema;
2. raw artifact existence and SHA-256;
3. JSONL parseability;
4. declared vs actual row count;
5. expected benchmark shape vs actual row count;
6. one shared execution ID;
7. row pack hash vs manifest lineage.

Current repository pack/runner mismatches are warnings rather than integrity failures because historical runs must remain verifiable after the repository evolves.

## Evidence boundary

A valid run bundle proves lineage/integrity properties of the captured execution. It does **not** prove model quality, AFP superiority, valid grading, statistical significance, or absence of evaluation contamination outside the recorded boundary.

Outputs remain `UNSCORED` until a separate grading step is performed.
