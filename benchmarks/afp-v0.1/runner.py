#!/usr/bin/env python3
from __future__ import annotations

import argparse
import collections
import datetime as dt
import hashlib
import json
import os
import pathlib
import platform
import re
import sys
import subprocess
import time
import uuid


ROOT = pathlib.Path(__file__).resolve().parent
PACK_PATH = ROOT / "pack.json"
REQUIREMENTS_PATH = ROOT / "requirements-live.txt"
RESULT_DIR = ROOT / "results"
MANIFEST_SCHEMA_VERSION = 1


def load_pack() -> dict:
    with PACK_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def canonical_json_sha256(value: object) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def text_sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def file_sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def pack_sha256(pack: dict) -> str:
    return canonical_json_sha256(pack)


def source_revision() -> str | None:
    github_sha = os.getenv("GITHUB_SHA")
    if github_sha:
        return github_sha
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
        value = result.stdout.strip()
        return value or None
    except (OSError, subprocess.SubprocessError):
        return None


def validate_pack(pack: dict) -> list[str]:
    errors: list[str] = []
    if pack.get("protocol_version") != "0.1":
        errors.append("protocol_version must be 0.1")

    treatments = pack.get("treatments")
    if not isinstance(treatments, dict) or list(treatments.keys()) != ["A", "B", "C", "D"]:
        errors.append("treatments must contain A, B, C, D in order")

    fixtures = pack.get("fixtures")
    if not isinstance(fixtures, list) or len(fixtures) != 8:
        errors.append("fixtures must contain exactly 8 items")
        fixtures = []

    ids = [f.get("id") for f in fixtures]
    if ids != [f"P{i:02d}" for i in range(1, 9)]:
        errors.append("fixture IDs must be P01..P08")

    required_fixture_fields = {
        "id", "risk", "base_instruction", "evidence",
        "task", "expected_core", "fatal_criterion",
    }
    for fixture in fixtures:
        missing = required_fixture_fields - set(fixture)
        if missing:
            errors.append(f"{fixture.get('id','?')}: missing {sorted(missing)}")
        for field in required_fixture_fields:
            if field != "base_instruction" and not fixture.get(field):
                errors.append(f"{fixture.get('id','?')}: empty {field}")

    rubric = pack.get("shared_rubric", {})
    if rubric.get("total_range") != [0, 8]:
        errors.append("shared rubric total_range must be [0, 8]")
    if len(rubric.get("dimensions", [])) != 4:
        errors.append("shared rubric must contain 4 dimensions")

    return errors


def compose_instructions(fixture: dict, treatment: dict) -> str:
    parts = []
    if fixture.get("base_instruction"):
        parts.append(fixture["base_instruction"].strip())
    if treatment.get("instruction"):
        parts.append(treatment["instruction"].strip())
    return "\n\n".join(parts)


def compose_input(fixture: dict) -> str:
    return f"""Evidence:
{fixture['evidence']}

Task:
{fixture['task']}"""


def safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_") or "model"


def expected_record_count(pack: dict, repeats: int) -> int:
    return len(pack["fixtures"]) * len(pack["treatments"]) * repeats


def write_jsonl(
    records: list[dict],
    model: str,
    repeats: int,
    execution_id: str,
    result_dir: pathlib.Path = RESULT_DIR,
) -> pathlib.Path:
    result_dir.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = result_dir / (
        f"raw-{stamp}-{safe_name(model)}-r{repeats}-{execution_id[:8]}.jsonl"
    )
    with path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return path


def build_run_manifest(
    *,
    pack: dict,
    records: list[dict],
    raw_path: pathlib.Path,
    execution_id: str,
    model: str,
    repeats: int,
    reasoning: str,
    sdk_version: str | None,
) -> dict:
    status_counts = dict(
        sorted(collections.Counter(
            record.get("validity_status", "UNKNOWN") for record in records
        ).items())
    )
    requirements_hash = (
        file_sha256(REQUIREMENTS_PATH) if REQUIREMENTS_PATH.exists() else None
    )

    return {
        "manifest_schema_version": MANIFEST_SCHEMA_VERSION,
        "execution_id": execution_id,
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "protocol_version": pack["protocol_version"],
        "scope": pack.get("scope"),
        "provider": "openai",
        "requested_model": model,
        "reasoning_effort": reasoning,
        "repeats": repeats,
        "expected_record_count": expected_record_count(pack, repeats),
        "actual_record_count": len(records),
        "status_counts": status_counts,
        "lineage": {
            "benchmark_pack_sha256": pack_sha256(pack),
            "runner_sha256": file_sha256(pathlib.Path(__file__).resolve()),
            "requirements_live_sha256": requirements_hash,
            "source_revision": source_revision(),
            "fixture_ids": [fixture["id"] for fixture in pack["fixtures"]],
            "treatment_ids": list(pack["treatments"].keys()),
        },
        "raw_results": {
            "file": raw_path.name,
            "sha256": file_sha256(raw_path),
            "size_bytes": raw_path.stat().st_size,
        },
        "leakage_boundary": {
            "runtime_input_fields": [
                "base_instruction",
                "treatment.instruction",
                "evidence",
                "task",
            ],
            "evaluation_only_fields": [
                "expected_core",
                "fatal_criterion",
                "shared_rubric",
            ],
            "evaluation_fields_in_model_input": False,
        },
        "environment": {
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "openai_sdk_version": sdk_version,
        },
        "scoring": {
            "status": "UNSCORED",
            "fatal_override_defined": bool(
                pack.get("shared_rubric", {}).get("fatal_override")
            ),
        },
    }


def write_run_bundle(
    *,
    pack: dict,
    records: list[dict],
    model: str,
    repeats: int,
    reasoning: str,
    execution_id: str,
    sdk_version: str | None,
    result_dir: pathlib.Path = RESULT_DIR,
) -> tuple[pathlib.Path, pathlib.Path]:
    raw_path = write_jsonl(
        records,
        model=model,
        repeats=repeats,
        execution_id=execution_id,
        result_dir=result_dir,
    )
    manifest = build_run_manifest(
        pack=pack,
        records=records,
        raw_path=raw_path,
        execution_id=execution_id,
        model=model,
        repeats=repeats,
        reasoning=reasoning,
        sdk_version=sdk_version,
    )
    manifest_path = raw_path.with_suffix(".manifest.json")
    with manifest_path.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")
    return raw_path, manifest_path


def verify_run_manifest(manifest_path: pathlib.Path) -> dict:
    manifest_path = manifest_path.resolve()
    with manifest_path.open("r", encoding="utf-8") as f:
        manifest = json.load(f)

    errors: list[str] = []
    warnings: list[str] = []

    if manifest.get("manifest_schema_version") != MANIFEST_SCHEMA_VERSION:
        errors.append("unsupported manifest_schema_version")

    raw_name = manifest.get("raw_results", {}).get("file")
    if not raw_name:
        errors.append("raw_results.file is missing")
        raw_path = manifest_path.parent / "__missing__"
    else:
        raw_path = manifest_path.parent / raw_name

    records: list[dict] = []
    if not raw_path.exists():
        errors.append(f"raw result file not found: {raw_path.name}")
    else:
        actual_hash = file_sha256(raw_path)
        expected_hash = manifest.get("raw_results", {}).get("sha256")
        if actual_hash != expected_hash:
            errors.append("raw result SHA-256 mismatch")

        with raw_path.open("r", encoding="utf-8") as f:
            for line_number, line in enumerate(f, start=1):
                if not line.strip():
                    continue
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    errors.append(
                        f"invalid JSONL at line {line_number}: {exc.msg}"
                    )

    declared_actual_count = manifest.get("actual_record_count")
    if declared_actual_count != len(records):
        errors.append(
            "record count mismatch: "
            f"manifest={declared_actual_count} actual={len(records)}"
        )

    expected_count = manifest.get("expected_record_count")
    if expected_count != len(records):
        errors.append(
            "incomplete benchmark execution: "
            f"expected={expected_count} actual={len(records)}"
        )

    execution_id = manifest.get("execution_id")
    record_execution_ids = {
        record.get("execution_id") for record in records if record.get("execution_id")
    }
    if records and record_execution_ids != {execution_id}:
        errors.append("records do not share the manifest execution_id")

    manifest_pack_hash = manifest.get("lineage", {}).get("benchmark_pack_sha256")
    record_pack_hashes = {
        record.get("benchmark_pack_sha256")
        for record in records
        if record.get("benchmark_pack_sha256")
    }
    if records and record_pack_hashes != {manifest_pack_hash}:
        errors.append("record pack hash does not match manifest lineage")

    manifest_runner_hash = manifest.get("lineage", {}).get("runner_sha256")
    record_runner_hashes = {
        record.get("runner_sha256")
        for record in records
        if record.get("runner_sha256")
    }
    if records and record_runner_hashes != {manifest_runner_hash}:
        errors.append("record runner hash does not match manifest lineage")

    fixture_ids = manifest.get("lineage", {}).get("fixture_ids") or []
    treatment_ids = manifest.get("lineage", {}).get("treatment_ids") or []
    repeats = manifest.get("repeats")

    if isinstance(repeats, int) and repeats > 0:
        expected_shape_count = len(fixture_ids) * len(treatment_ids) * repeats
        if manifest.get("expected_record_count") != expected_shape_count:
            errors.append(
                "manifest expected_record_count does not match fixture/treatment/repeat shape"
            )

        expected_keys = {
            (fixture_id, treatment_id, repeat)
            for repeat in range(1, repeats + 1)
            for fixture_id in fixture_ids
            for treatment_id in treatment_ids
        }
        actual_keys = [
            (
                record.get("fixture_id"),
                record.get("treatment"),
                record.get("repeat"),
            )
            for record in records
        ]
        actual_key_set = set(actual_keys)

        if len(actual_keys) != len(actual_key_set):
            errors.append("duplicate fixture/treatment/repeat rows detected")

        missing_keys = expected_keys - actual_key_set
        unexpected_keys = actual_key_set - expected_keys
        if missing_keys:
            errors.append(
                f"missing fixture/treatment/repeat rows: {len(missing_keys)}"
            )
        if unexpected_keys:
            errors.append(
                f"unexpected fixture/treatment/repeat rows: {len(unexpected_keys)}"
            )
    else:
        errors.append("invalid repeats value in manifest")

    actual_status_counts = dict(
        sorted(collections.Counter(
            record.get("validity_status", "UNKNOWN") for record in records
        ).items())
    )
    if manifest.get("status_counts") != actual_status_counts:
        errors.append("status_counts do not match raw records")

    current_pack_matches = pack_sha256(load_pack()) == manifest_pack_hash
    current_runner_matches = (
        file_sha256(pathlib.Path(__file__).resolve())
        == manifest_runner_hash
    )
    recorded_revision = manifest.get("lineage", {}).get("source_revision")
    current_revision = source_revision()
    current_revision_matches = (
        recorded_revision is None
        or current_revision is None
        or recorded_revision == current_revision
    )
    if not current_pack_matches:
        warnings.append("current pack differs from the recorded run pack")
    if not current_runner_matches:
        warnings.append("current runner differs from the recorded run runner")
    if not current_revision_matches:
        warnings.append("current source revision differs from the recorded run revision")

    return {
        "integrity_ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "manifest": manifest_path.name,
        "raw_results": raw_path.name if raw_name else None,
        "record_count": len(records),
        "current_pack_matches": current_pack_matches,
        "current_runner_matches": current_runner_matches,
        "current_revision_matches": current_revision_matches,
    }


def run_openai(
    pack: dict,
    model: str,
    repeats: int,
    reasoning: str,
) -> tuple[pathlib.Path, pathlib.Path]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required for live mode")

    try:
        from openai import OpenAI
        import openai
    except ImportError as exc:
        raise RuntimeError(
            "OpenAI SDK is not installed. Install the pinned dependency: openai==3.7.0"
        ) from exc

    client = OpenAI(api_key=api_key)
    records: list[dict] = []
    execution_id = str(uuid.uuid4())
    benchmark_pack_sha256 = pack_sha256(pack)
    runner_hash = file_sha256(pathlib.Path(__file__).resolve())

    for repeat in range(1, repeats + 1):
        for fixture in pack["fixtures"]:
            for treatment_id, treatment in pack["treatments"].items():
                run_id = str(uuid.uuid4())
                started_at = dt.datetime.now(dt.timezone.utc)
                started = time.perf_counter()
                instructions = compose_instructions(fixture, treatment)
                user_input = compose_input(fixture)

                record = {
                    "execution_id": execution_id,
                    "run_id": run_id,
                    "protocol_version": pack["protocol_version"],
                    "benchmark_pack_sha256": benchmark_pack_sha256,
                    "runner_sha256": runner_hash,
                    "fixture_id": fixture["id"],
                    "fixture_risk": fixture["risk"],
                    "input_sha256": text_sha256(user_input),
                    "effective_instructions_sha256": text_sha256(instructions),
                    "treatment": treatment_id,
                    "treatment_name": treatment["name"],
                    "treatment_instruction_sha256": text_sha256(
                        treatment.get("instruction", "")
                    ),
                    "repeat": repeat,
                    "provider": "openai",
                    "requested_model": model,
                    "returned_model": None,
                    "reasoning_effort": reasoning,
                    "sdk_version": getattr(openai, "__version__", None),
                    "started_at": started_at.isoformat(),
                    "latency_ms": None,
                    "input_tokens": None,
                    "output_tokens": None,
                    "tool_calls": 0,
                    "provider_response_id": None,
                    "raw_output": None,
                    "validity_status": "UNSCORED",
                    "score_0_8": None,
                    "fatal_failure": None,
                    "grader_notes": None,
                    "error_type": None,
                    "error_message": None,
                }

                try:
                    kwargs = {
                        "model": model,
                        "input": user_input,
                    }
                    if instructions:
                        kwargs["instructions"] = instructions
                    if reasoning != "default":
                        kwargs["reasoning"] = {"effort": reasoning}

                    response = client.responses.create(**kwargs)
                    record["returned_model"] = getattr(response, "model", None)
                    record["provider_response_id"] = getattr(response, "id", None)
                    record["raw_output"] = response.output_text

                    usage = getattr(response, "usage", None)
                    if usage is not None:
                        record["input_tokens"] = getattr(
                            usage, "input_tokens", None
                        )
                        record["output_tokens"] = getattr(
                            usage, "output_tokens", None
                        )
                except Exception as exc:
                    record["validity_status"] = "INFRA_ERROR"
                    record["error_type"] = type(exc).__name__
                    record["error_message"] = str(exc)[:2000]

                record["latency_ms"] = round(
                    (time.perf_counter() - started) * 1000
                )
                records.append(record)
                print(
                    f"{fixture['id']} {treatment_id} r{repeat}: "
                    f"{record['validity_status']} "
                    f"{record['latency_ms']}ms",
                    flush=True,
                )

    return write_run_bundle(
        pack=pack,
        records=records,
        model=model,
        repeats=repeats,
        reasoning=reasoning,
        execution_id=execution_id,
        sdk_version=getattr(openai, "__version__", None),
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="AFP Benchmark v0.1 validation and lineage-aware runner"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser(
        "validate",
        help="Validate the frozen benchmark pack without API calls",
    )

    live = sub.add_parser(
        "live",
        help="Generate raw A/B/C/D outputs through OpenAI",
    )
    live.add_argument("--model", required=True)
    live.add_argument("--repeats", type=int, choices=[1, 3], default=1)
    live.add_argument(
        "--reasoning",
        choices=["default", "none", "low", "medium", "high", "xhigh", "max"],
        default="none",
    )

    verify = sub.add_parser(
        "verify-run",
        help="Verify a run manifest against its raw JSONL artifact",
    )
    verify.add_argument("manifest", type=pathlib.Path)

    args = parser.parse_args()

    if args.command == "verify-run":
        report = verify_run_manifest(args.manifest)
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if report["integrity_ok"] else 3

    pack = load_pack()
    errors = validate_pack(pack)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 2

    if args.command == "validate":
        print(
            f"AFP Benchmark {pack['protocol_version']} pack valid: "
            f"{len(pack['fixtures'])} fixtures × "
            f"{len(pack['treatments'])} treatments"
        )
        print(f"Pack SHA-256: {pack_sha256(pack)}")
        print(f"Runner SHA-256: {file_sha256(pathlib.Path(__file__).resolve())}")
        print("No model API was called.")
        return 0

    raw_path, manifest_path = run_openai(
        pack=pack,
        model=args.model,
        repeats=args.repeats,
        reasoning=args.reasoning,
    )
    print(f"Raw results written to: {raw_path}")
    print(f"Run manifest written to: {manifest_path}")
    print("Outputs are UNSCORED. Do not publish benchmark claims before grading.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
