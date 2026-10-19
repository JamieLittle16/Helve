"""No-source 26.2 noise-family Atlas frontier contract tests."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import worldgen_26_2_noise_family_frontier as frontier  # noqa: E402


class NoiseFamilyFrontierTests(unittest.TestCase):
    def fake_inventory(self) -> dict[str, object]:
        index = 0

        def rows(conn, owner, cap):
            nonlocal index
            index += 1
            self.assertEqual(cap, frontier.MAX_METHODS)
            return [{"id": index, "signature": "sample(double x,double y,double z)"}]

        def template(conn, row, candidate):
            owner = list(frontier.OWNERS.values())[row["id"] - 1]
            return {
                "source": {
                    "type": owner,
                    "signature": row["signature"],
                    "body_sha256": "a" * 64,
                    "normalized_sha256": "b" * 64,
                },
                "atlas_observed_hazards": ["floating_point_order"],
            }

        calls = {
            "call_sites": 2,
            "resolved_targets": ["synthetic.Owner#method()"],
            "unresolved_call_sites": 1,
            "top_unresolved_callees": [{"callee": "unresolved/1", "sites": 1}],
        }
        with mock.patch.object(frontier.projection, "_exact_type_methods", side_effect=rows), \
             mock.patch.object(frontier.source_probe, "record_template", side_effect=template), \
             mock.patch.object(frontier.projection, "_call_inventory", return_value=calls):
            return frontier.inventory(mock.MagicMock())

    def test_bounded_four_roots_and_source_free_method_metadata(self):
        result = self.fake_inventory()
        self.assertEqual(set(result), set(frontier.OWNERS))
        for label, group in result.items():
            self.assertEqual(group["owner"], frontier.OWNERS[label])
            self.assertEqual(group["method_count"], 1)
            method = group["methods"][0]
            self.assertEqual(method["body_sha256"], "a" * 64)
            self.assertEqual(method["normalized_sha256"], "b" * 64)
            self.assertEqual(method["call_sites"], 2)
            self.assertEqual(method["unresolved_call_sites"], 1)
            self.assertNotIn("source_text", method)
            self.assertFalse(method["declaration_only"])

    def test_exact_method_roots_fail_closed_on_missing_and_ambiguous_rows(self):
        with mock.patch.object(frontier.projection, "_exact_type_methods", return_value=[]):
            with self.assertRaisesRegex(frontier.FrontierError, "no indexed declarations"):
                frontier.inventory(mock.MagicMock())
        with mock.patch.object(frontier.projection, "_exact_type_methods", return_value=[
            {"id": 1, "signature": "noise()"},
            {"id": 2, "signature": "noise()"},
        ]), mock.patch.object(frontier.source_probe, "record_template", return_value={
            "source": {
                "type": list(frontier.OWNERS.values())[0],
                "signature": "noise()",
                "body_sha256": "a" * 64,
                "normalized_sha256": "b" * 64,
            }
        }), mock.patch.object(frontier.projection, "_call_inventory", return_value={
            "call_sites": 0, "resolved_targets": [],
            "unresolved_call_sites": 0, "top_unresolved_callees": [],
        }):
            with self.assertRaisesRegex(frontier.FrontierError, "ambiguous"):
                frontier.inventory(mock.MagicMock())

    def test_invalid_hash_fails(self):
        with self.assertRaisesRegex(frontier.FrontierError, "invalid exact SHA"):
            frontier._hash_or_none("not a sha")
        self.assertIsNone(frontier._hash_or_none(None))

    def test_capture_pinned_source_only_and_no_semantic_admission(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            lock = root / "lock.toml"
            lock.write_text(
                'minecraft = "26.2"\nprotocol = 776\ndata_version = 4903\n'
                f'[runtime]\nserver_sha256 = "{"f" * 64}"\n',
                encoding="utf-8",
            )
            out = root / "source-method-frontier.json"
            conn = mock.MagicMock()
            with mock.patch.object(frontier.vanilla_atlas, "connect_db", return_value=conn), \
                 mock.patch.object(frontier.source_probe, "require_pinned_source", return_value="a" * 64), \
                 mock.patch.object(frontier, "inventory", return_value=self.fake_inventory()):
                result = frontier.capture(source=root / "zip", db=root / "db", lock=lock, output=out)
            self.assertEqual(result["root_types"], 4)
            self.assertEqual(result["method_declarations"], 4)
            self.assertTrue(conn.close.called)
            report = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(report["source_archive_sha256"], "a" * 64)
            self.assertFalse(report["source_text_included"])
            self.assertFalse(report["independent_var_sem_admitted"])
            self.assertFalse(report["production_worldgen_enabled"])
            with self.assertRaisesRegex(ValueError, "already exists"):
                frontier.capture(source=root / "zip", db=root / "db", lock=lock, output=out)

    def test_wrong_version_rejected_before_any_atlas_access(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            lock = root / "invalid.lock.toml"
            lock.write_text('minecraft = "26.1"\nprotocol = 776\ndata_version = 4903\n', encoding="utf-8")
            with mock.patch.object(frontier.vanilla_atlas, "connect_db") as connection:
                with self.assertRaisesRegex(frontier.FrontierError, "not the pinned"):
                    frontier.capture(source=root / "zip", db=root / "db", lock=lock, output=root / "out.json")
                connection.assert_not_called()


if __name__ == "__main__":
    unittest.main()
