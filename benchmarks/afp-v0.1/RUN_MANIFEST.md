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

A successful verification means the raw file and manifest are internally consistent and the rows match the recorded execution/pack/runner lineage.

## What the manifest does NOT prove

### Internal consistency is not authenticity

The manifest is a sidecar file, not a cryptographic signature or trusted timestamp. If someone can rewrite both the raw JSONL and the manifest, they can recompute the hashes. Verification therefore detects accidental corruption, raw-only modification, incomplete/cross-run bundles, and lineage inconsistency; it does not prove that a bundle came from a trusted actor or has never been jointly rewritten.

For stronger provenance, preserve the bundle in an access-controlled artifact store and record the CI run / source revision that produced it. A future signed-attestation layer can strengthen this further.

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

If the current repository pack, runner, source revision, or pinned live dependency file differs from the values recorded in an old manifest, verification emits a warning. That does not invalidate the historical artifact; it means the current checkout/environment is not the same version that produced it.

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


## Pre-merge live smoke gate

The existing **AFP Benchmark v0.1** workflow supports a manual live smoke run on the v3 branch.

Recommended first external check:

```text
mode = live
confirm_external_costs = true
scope = smoke
fixture_id = P01
treatment = A
repeats = 1
reasoning = none
model = <explicit OpenAI model ID>
```

With `scope=smoke`, the runner issues exactly one fixture/treatment/repeat request and the workflow requires the generated manifest to report:

- `expected_record_count == 1`
- `actual_record_count == 1`
- `scoring.status == UNSCORED`

The live job is manual and requires the `OPENAI_API_KEY` repository secret. Pull-request and push validation do not call the model API.

Only after the one-case smoke succeeds should `scope=full` be considered. Full scope executes the complete fixture × treatment matrix and may create materially more billable model usage.

A successful live smoke proves provider/API/runner/bundle integration for the selected single case. It does not establish benchmark quality, comparative superiority, grading validity, or statistical significance.
