#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import pathlib
import re
import sys
import time
import uuid


ROOT = pathlib.Path(__file__).resolve().parent
PACK_PATH = ROOT / "pack.json"
RESULT_DIR = ROOT / "results"


def load_pack() -> dict:
    with PACK_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


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


def write_jsonl(records: list[dict], model: str, repeats: int) -> pathlib.Path:
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = RESULT_DIR / f"raw-{stamp}-{safe_name(model)}-r{repeats}.jsonl"
    with path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return path


def run_openai(pack: dict, model: str, repeats: int, reasoning: str) -> pathlib.Path:
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

    for repeat in range(1, repeats + 1):
        for fixture in pack["fixtures"]:
            for treatment_id, treatment in pack["treatments"].items():
                run_id = str(uuid.uuid4())
                started_at = dt.datetime.now(dt.timezone.utc)
                started = time.perf_counter()
                instructions = compose_instructions(fixture, treatment)
                user_input = compose_input(fixture)

                record = {
                    "run_id": run_id,
                    "protocol_version": pack["protocol_version"],
                    "fixture_id": fixture["id"],
                    "treatment": treatment_id,
                    "treatment_name": treatment["name"],
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
                        record["input_tokens"] = getattr(usage, "input_tokens", None)
                        record["output_tokens"] = getattr(usage, "output_tokens", None)
                except Exception as exc:
                    record["validity_status"] = "INFRA_ERROR"
                    record["error_type"] = type(exc).__name__
                    record["error_message"] = str(exc)[:2000]

                record["latency_ms"] = round((time.perf_counter() - started) * 1000)
                records.append(record)
                print(
                    f"{fixture['id']} {treatment_id} r{repeat}: "
                    f"{record['validity_status']} "
                    f"{record['latency_ms']}ms",
                    flush=True,
                )

    return write_jsonl(records, model=model, repeats=repeats)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="AFP Benchmark v0.1 validation and raw-output runner"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("validate", help="Validate the frozen benchmark pack without API calls")

    live = sub.add_parser("live", help="Generate raw A/B/C/D outputs through OpenAI")
    live.add_argument("--model", required=True)
    live.add_argument("--repeats", type=int, choices=[1, 3], default=1)
    live.add_argument(
        "--reasoning",
        choices=["default", "none", "low", "medium", "high", "xhigh", "max"],
        default="none",
    )

    args = parser.parse_args()
    pack = load_pack()
    errors = validate_pack(pack)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 2

    if args.command == "validate":
        print(
            f"AFP Benchmark {pack['protocol_version']} pack valid: "
            f"{len(pack['fixtures'])} fixtures × {len(pack['treatments'])} treatments"
        )
        print("No model API was called.")
        return 0

    path = run_openai(
        pack=pack,
        model=args.model,
        repeats=args.repeats,
        reasoning=args.reasoning,
    )
    print(f"Raw results written to: {path}")
    print("Outputs are UNSCORED. Do not publish benchmark claims before grading.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
