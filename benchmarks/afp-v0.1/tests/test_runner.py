import copy
import importlib.util
import pathlib
import unittest


RUNNER_PATH = pathlib.Path(__file__).resolve().parents[1] / "runner.py"
SPEC = importlib.util.spec_from_file_location("afp_runner", RUNNER_PATH)
runner = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(runner)


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


if __name__ == "__main__":
    unittest.main()
