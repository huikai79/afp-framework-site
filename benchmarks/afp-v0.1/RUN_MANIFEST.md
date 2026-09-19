# AFP Benchmark Run Manifest

The run manifest turns one live benchmark execution into a verifiable artifact bundle.

A bundle contains:

```text
raw-<timestamp>-<model>-r<repeats>-<execution>.jsonl
raw-<timestamp>-<model>-r<repeats>-<execution>.manifest.json
```

## What the manifest proves

The manifest records and binds:

- one execution ID shared by all rows;
- benchmark protocol version and scope;
- benchmark pack SHA-256;
- runner SHA-256;
- pinned live dependency file SHA-256;
- requested model and reasoning effort;
- expected and actual record counts;
- fixture/treatment IDs;
- raw JSONL filename, size, and SHA-256;
- Python/platform/OpenAI SDK metadata;
- the runtime-input vs evaluation-only leakage boundary;
- scoring status.

`verify-run` checks artifact integrity:

```bash
python benchmarks/afp-v0.1/runner.py verify-run \
  benchmarks/afp-v0.1/results/<run>.manifest.json
```

A successful verification means the raw file matches the manifest and the rows belong to the recorded execution/pack lineage.

## What the manifest does NOT prove

### Integrity is not exact reproducibility

A matching SHA-256 proves which artifact was recorded. It does not guarantee a model provider will emit the same response again.

Model serving, provider-side configuration, nondeterminism, model aliases, and unavailable historical infrastructure can prevent exact replay.

The manifest therefore records controllable and observable variables instead of claiming deterministic reproduction of external model behavior.

### Integrity is not benchmark validity

A valid bundle does not prove:

- the fixture set is representative;
- the rubric measures every relevant quality;
- the comparison is uncontaminated by prior tuning;
- the benchmark generalizes beyond the tested model/tasks.

Those are evaluation-design questions.

### Integrity is not a performance claim

Fresh live outputs are recorded as `UNSCORED`.

The manifest deliberately keeps:

- `expected_core`;
- `fatal_criterion`;
- `shared_rubric`

outside the model runtime input. They remain evaluation-only material.

No AFP superiority claim should be derived merely from a successful run or a valid manifest.

## Row-level lineage

Each raw row records:

- `execution_id`;
- `run_id`;
- pack and runner hashes;
- fixture ID and risk class;
- input SHA-256;
- effective instruction SHA-256;
- treatment instruction SHA-256;
- requested/returned model;
- provider response ID when available;
- token/latency metadata;
- raw output or infrastructure error.

The hashes permit later review of exactly which input/instruction bytes a row represents without copying hidden evaluation fields into the prompt.

## Current-code warnings

`verify-run` distinguishes artifact corruption from repository evolution.

If the current repository pack or runner differs from the hashes recorded in an old manifest, verification emits a warning. That does not invalidate the historical artifact; it means the current checkout is not the code/data version that produced it.

## Recommended publication flow

```text
validate pack
  -> live generation
  -> verify run bundle
  -> preserve raw bundle
  -> independent/defined grading
  -> inspect fatal failures
  -> aggregate with dependency awareness
  -> calibrate claims to tested scope
```

Do not skip from “bundle verified” directly to “framework works better.”
