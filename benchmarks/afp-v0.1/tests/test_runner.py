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
                rows.append(
                    {
                        "execution_id": execution_id,
                        "benchmark_pack_sha256": runner.pack_sha256(pack),
                        "runner_sha256": runner_hash,
                        "fixture_id": fixture["id"],
                        "treatment": treatment_id,
                        "repeat": repeat,
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



if __name__ == "__main__":
    unittest.main()
