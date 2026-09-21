import copy
import importlib.util
import json
import pathlib
import tempfile
import unittest


RUNNER_PATH = pathlib.Path(__file__).resolve().parents[1] / "runner.py"
SPEC = importlib.util.spec_from_file_location("afp_runner", RUNNER_PATH)
runner = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(runner)


def make_records(pack, execution_id, count=None):
    rows = []
    sequence = 0
    runner_hash = runner.file_sha256(RUNNER_PATH)
    for repeat in range(1, 2):
        for fixture in pack["fixtures"]:
            for treatment_id in pack["treatments"]:
                treatment = pack["treatments"][treatment_id]
                instructions = runner.compose_instructions(fixture, treatment)
                user_input = runner.compose_input(fixture)
                rows.append(
                    {
                        "execution_id": execution_id,
                        "run_id": f"run-{sequence}",
                        "protocol_version": pack["protocol_version"],
                        "provider": "openai",
                        "requested_model": "test-model",
                        "reasoning_effort": "none",
                        "benchmark_pack_sha256": runner.pack_sha256(pack),
                        "runner_sha256": runner_hash,
                        "fixture_id": fixture["id"],
                        "fixture_risk": fixture["risk"],
                        "treatment": treatment_id,
                        "treatment_instruction_sha256": runner.text_sha256(
                            treatment.get("instruction", "")
                        ),
                        "repeat": repeat,
                        "input_sha256": runner.text_sha256(user_input),
                        "effective_instructions_sha256": runner.text_sha256(
                            instructions
                        ),
                        "validity_status": "UNSCORED",
                        "sequence": sequence,
                    }
                )
                sequence += 1

    return rows if count is None else rows[:count]


class BenchmarkRunnerTests(unittest.TestCase):
    def test_pack_validates(self):
        pack = runner.load_pack()
        self.assertEqual(runner.validate_pack(pack), [])

    def test_pack_hash_is_stable_for_key_order(self):
        a = {"b": 2, "a": 1}
        b = {"a": 1, "b": 2}
        self.assertEqual(
            runner.canonical_json_sha256(a),
            runner.canonical_json_sha256(b),
        )

    def test_pack_hash_changes_when_content_changes(self):
        pack = runner.load_pack()
        changed = copy.deepcopy(pack)
        changed["fixtures"][0]["task"] += " changed"
        self.assertNotEqual(
            runner.pack_sha256(pack),
            runner.pack_sha256(changed),
        )

    def test_compose_input_excludes_hidden_evaluation_fields(self):
        fixture = runner.load_pack()["fixtures"][0]
        rendered = runner.compose_input(fixture)
        self.assertIn(fixture["evidence"], rendered)
        self.assertIn(fixture["task"], rendered)
        self.assertNotIn(fixture["expected_core"], rendered)
        self.assertNotIn(fixture["fatal_criterion"], rendered)

    def test_expected_record_count_matches_pack_shape(self):
        pack = runner.load_pack()
        self.assertEqual(runner.expected_record_count(pack, 1), 32)
        self.assertEqual(runner.expected_record_count(pack, 3), 96)

    def test_run_bundle_round_trip_verifies(self):
        pack = runner.load_pack()
        execution_id = "execution-test"
        records = make_records(pack, execution_id)

        with tempfile.TemporaryDirectory() as temp_dir:
            raw_path, manifest_path = runner.write_run_bundle(
                pack=pack,
                records=records,
                model="test-model",
                repeats=1,
                reasoning="none",
                execution_id=execution_id,
                sdk_version="test-sdk",
                result_dir=pathlib.Path(temp_dir),
            )

            self.assertTrue(raw_path.exists())
            self.assertTrue(manifest_path.exists())

            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["execution_id"], execution_id)
            self.assertEqual(manifest["actual_record_count"], 32)
            self.assertEqual(
                manifest["raw_results"]["sha256"],
                runner.file_sha256(raw_path),
            )
            self.assertFalse(
                manifest["leakage_boundary"]["evaluation_fields_in_model_input"]
            )
            self.assertIn("source_revision", manifest["lineage"])

            report = runner.verify_run_manifest(manifest_path)
            self.assertTrue(report["integrity_ok"], report)
            self.assertEqual(report["record_count"], 32)

    def test_run_bundle_detects_tampered_raw_results(self):
        pack = runner.load_pack()
        execution_id = "execution-tamper"
        records = make_records(pack, execution_id)

        with tempfile.TemporaryDirectory() as temp_dir:
            raw_path, manifest_path = runner.write_run_bundle(
                pack=pack,
                records=records,
                model="test-model",
                repeats=1,
                reasoning="none",
                execution_id=execution_id,
                sdk_version="test-sdk",
                result_dir=pathlib.Path(temp_dir),
            )
            with raw_path.open("a", encoding="utf-8") as f:
                f.write('{"tampered": true}\n')

            report = runner.verify_run_manifest(manifest_path)
            self.assertFalse(report["integrity_ok"])
            self.assertTrue(
                any("SHA-256 mismatch" in error for error in report["errors"]),
                report,
            )

    def test_run_bundle_detects_cross_execution_rows(self):
        pack = runner.load_pack()
        records = make_records(pack, "expected-execution")
        records[0]["execution_id"] = "wrong-execution"

        with tempfile.TemporaryDirectory() as temp_dir:
            _, manifest_path = runner.write_run_bundle(
                pack=pack,
                records=records,
                model="test-model",
                repeats=1,
                reasoning="none",
                execution_id="expected-execution",
                sdk_version="test-sdk",
                result_dir=pathlib.Path(temp_dir),
            )

            report = runner.verify_run_manifest(manifest_path)
            self.assertFalse(report["integrity_ok"])
            self.assertIn(
                "records do not share the manifest execution_id",
                report["errors"],
            )


    def test_run_bundle_detects_incomplete_execution(self):
        pack = runner.load_pack()
        execution_id = "execution-incomplete"
        records = make_records(pack, execution_id, count=31)

        with tempfile.TemporaryDirectory() as temp_dir:
            _, manifest_path = runner.write_run_bundle(
                pack=pack,
                records=records,
                model="test-model",
                repeats=1,
                reasoning="none",
                execution_id=execution_id,
                sdk_version="test-sdk",
                result_dir=pathlib.Path(temp_dir),
            )

            report = runner.verify_run_manifest(manifest_path)
            self.assertFalse(report["integrity_ok"])
            self.assertTrue(
                any(
                    "incomplete benchmark execution" in error
                    for error in report["errors"]
                ),
                report,
            )



    def test_run_bundle_detects_duplicate_case_rows(self):
        pack = runner.load_pack()
        execution_id = "execution-duplicate"
        records = make_records(pack, execution_id)
        records[-1] = dict(records[0])

        with tempfile.TemporaryDirectory() as temp_dir:
            _, manifest_path = runner.write_run_bundle(
                pack=pack,
                records=records,
                model="test-model",
                repeats=1,
                reasoning="none",
                execution_id=execution_id,
                sdk_version="test-sdk",
                result_dir=pathlib.Path(temp_dir),
            )

            report = runner.verify_run_manifest(manifest_path)
            self.assertFalse(report["integrity_ok"])
            self.assertTrue(
                any(
                    "duplicate fixture/treatment/repeat rows" in error
                    for error in report["errors"]
                ),
                report,
            )
            self.assertTrue(
                any(
                    "missing fixture/treatment/repeat rows" in error
                    for error in report["errors"]
                ),
                report,
            )

    def test_run_bundle_detects_runner_lineage_mismatch(self):
        pack = runner.load_pack()
        execution_id = "execution-runner-mismatch"
        records = make_records(pack, execution_id)
        records[0]["runner_sha256"] = "wrong-runner"

        with tempfile.TemporaryDirectory() as temp_dir:
            _, manifest_path = runner.write_run_bundle(
                pack=pack,
                records=records,
                model="test-model",
                repeats=1,
                reasoning="none",
                execution_id=execution_id,
                sdk_version="test-sdk",
                result_dir=pathlib.Path(temp_dir),
            )

            report = runner.verify_run_manifest(manifest_path)
            self.assertFalse(report["integrity_ok"])
            self.assertIn(
                "record runner hash does not match manifest lineage",
                report["errors"],
            )



    def test_verify_rejects_raw_path_outside_bundle_directory(self):
        pack = runner.load_pack()
        execution_id = "execution-path"
        records = make_records(pack, execution_id)

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = pathlib.Path(temp_dir)
            _, manifest_path = runner.write_run_bundle(
                pack=pack,
                records=records,
                model="test-model",
                repeats=1,
                reasoning="none",
                execution_id=execution_id,
                sdk_version="test-sdk",
                result_dir=temp_path,
            )

            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["raw_results"]["file"] = "../outside.jsonl"
            manifest_path.write_text(
                json.dumps(manifest, ensure_ascii=False),
                encoding="utf-8",
            )

            report = runner.verify_run_manifest(manifest_path)
            self.assertFalse(report["integrity_ok"])
            self.assertIn(
                "raw_results.file must be a sibling filename",
                report["errors"],
            )

    def test_verify_detects_raw_size_mismatch(self):
        pack = runner.load_pack()
        execution_id = "execution-size"
        records = make_records(pack, execution_id)

        with tempfile.TemporaryDirectory() as temp_dir:
            _, manifest_path = runner.write_run_bundle(
                pack=pack,
                records=records,
                model="test-model",
                repeats=1,
                reasoning="none",
                execution_id=execution_id,
                sdk_version="test-sdk",
                result_dir=pathlib.Path(temp_dir),
            )

            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["raw_results"]["size_bytes"] += 1
            manifest_path.write_text(
                json.dumps(manifest, ensure_ascii=False),
                encoding="utf-8",
            )

            report = runner.verify_run_manifest(manifest_path)
            self.assertFalse(report["integrity_ok"])
            self.assertTrue(
                any("raw result size mismatch" in error for error in report["errors"]),
                report,
            )



    def test_verify_detects_duplicate_run_ids(self):
        pack = runner.load_pack()
        execution_id = "execution-duplicate-run-id"
        records = make_records(pack, execution_id)
        records[1]["run_id"] = records[0]["run_id"]

        with tempfile.TemporaryDirectory() as temp_dir:
            _, manifest_path = runner.write_run_bundle(
                pack=pack,
                records=records,
                model="test-model",
                repeats=1,
                reasoning="none",
                execution_id=execution_id,
                sdk_version="test-sdk",
                result_dir=pathlib.Path(temp_dir),
            )

            report = runner.verify_run_manifest(manifest_path)
            self.assertFalse(report["integrity_ok"])
            self.assertIn("duplicate run_id values detected", report["errors"])

    def test_verify_detects_mixed_requested_models(self):
        pack = runner.load_pack()
        execution_id = "execution-mixed-model"
        records = make_records(pack, execution_id)
        records[0]["requested_model"] = "other-model"

        with tempfile.TemporaryDirectory() as temp_dir:
            _, manifest_path = runner.write_run_bundle(
                pack=pack,
                records=records,
                model="test-model",
                repeats=1,
                reasoning="none",
                execution_id=execution_id,
                sdk_version="test-sdk",
                result_dir=pathlib.Path(temp_dir),
            )

            report = runner.verify_run_manifest(manifest_path)
            self.assertFalse(report["integrity_ok"])
            self.assertTrue(
                any(
                    "record requested_model values do not match manifest" in error
                    for error in report["errors"]
                ),
                report,
            )

    def test_verify_recomputes_input_hash_when_pack_matches(self):
        pack = runner.load_pack()
        execution_id = "execution-input-hash"
        records = make_records(pack, execution_id)
        records[0]["input_sha256"] = "wrong-input-hash"

        with tempfile.TemporaryDirectory() as temp_dir:
            _, manifest_path = runner.write_run_bundle(
                pack=pack,
                records=records,
                model="test-model",
                repeats=1,
                reasoning="none",
                execution_id=execution_id,
                sdk_version="test-sdk",
                result_dir=pathlib.Path(temp_dir),
            )

            report = runner.verify_run_manifest(manifest_path)
            self.assertFalse(report["integrity_ok"])
            self.assertTrue(
                any(
                    "input_sha256 does not match pack" in error
                    for error in report["errors"]
                ),
                report,
            )



    def test_run_bundle_supports_single_fixture_treatment_smoke_shape(self):
        pack = runner.load_pack()
        execution_id = "execution-smoke"
        fixture = pack["fixtures"][0]
        treatment_id = "A"
        treatment = pack["treatments"][treatment_id]
        instructions = runner.compose_instructions(fixture, treatment)
        user_input = runner.compose_input(fixture)
        records = [{
            "execution_id": execution_id,
            "run_id": "run-smoke",
            "protocol_version": pack["protocol_version"],
            "provider": "openai",
            "requested_model": "test-model",
            "reasoning_effort": "none",
            "benchmark_pack_sha256": runner.pack_sha256(pack),
            "runner_sha256": runner.file_sha256(RUNNER_PATH),
            "fixture_id": fixture["id"],
            "fixture_risk": fixture["risk"],
            "treatment": treatment_id,
            "treatment_instruction_sha256": runner.text_sha256(
                treatment.get("instruction", "")
            ),
            "repeat": 1,
            "input_sha256": runner.text_sha256(user_input),
            "effective_instructions_sha256": runner.text_sha256(instructions),
            "validity_status": "UNSCORED",
        }]

        with tempfile.TemporaryDirectory() as temp_dir:
            _, manifest_path = runner.write_run_bundle(
                pack=pack,
                records=records,
                model="test-model",
                repeats=1,
                reasoning="none",
                execution_id=execution_id,
                sdk_version="test-sdk",
                result_dir=pathlib.Path(temp_dir),
            )

            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["expected_record_count"], 1)
            self.assertEqual(manifest["actual_record_count"], 1)
            self.assertEqual(manifest["lineage"]["fixture_ids"], [fixture["id"]])
            self.assertEqual(manifest["lineage"]["treatment_ids"], [treatment_id])

            report = runner.verify_run_manifest(manifest_path)
            self.assertTrue(report["integrity_ok"], report)
            self.assertEqual(report["record_count"], 1)



if __name__ == "__main__":
    unittest.main()
