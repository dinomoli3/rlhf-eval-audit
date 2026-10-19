import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from eval_audit import AuditError, audit, load_pairs
from eval_audit.inspect_adapter import pairs_from_summaries


class AuditTests(unittest.TestCase):
    def test_directionality_and_exact_sign_test(self):
        pairs = [(1, 0)] * 8 + [(1, 1)] * 12 + [(0, 0)] * 4
        report = audit(pairs, "A", "B")
        self.assertEqual(report["paired_difference"], 8 / 24)
        self.assertEqual(report["flip_rate"], 8 / 24)
        self.assertEqual(report["exact_two_sided_sign_p"], 2 / 256)
        self.assertEqual(report["status"], "REVIEW")
        self.assertEqual(report["paired_bootstrap_95"], audit(pairs, "A", "B")["paired_bootstrap_95"])

    def test_all_ties_and_coverage_gate(self):
        report = audit([(1, 1)] * 3, "A", "B")
        self.assertIsNone(report["exact_two_sided_sign_p"])
        self.assertEqual(report["paired_bootstrap_95"], [0.0, 0.0])
        self.assertEqual(report["status"], "INSUFFICIENT_COVERAGE")

    def test_missing_duplicate_and_invalid_scores_rejected(self):
        for body in ("x,A,1\n", "x,A,1\nx,A,0\nx,B,1\n", "x,A,maybe\nx,B,0\n"):
            with self.subTest(body=body), tempfile.TemporaryDirectory() as temp:
                path = Path(temp) / "input.csv"
                path.write_text("pair_id,group,outcome\n" + body, encoding="utf-8")
                with self.assertRaises(AuditError):
                    load_pairs(path, "A", "B")

    def test_rejects_extra_group(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "input.csv"
            path.write_text("pair_id,group,outcome\nx,A,1\nx,B,1\nx,C,1\n")
            with self.assertRaises(AuditError):
                load_pairs(path, "A", "B")

    def test_inspect_summary_adapter_and_missing_score(self):
        def sample(pair, group, value, error=None):
            return SimpleNamespace(metadata={"pair_id": pair, "group": group},
                                   scores={"human_rubric": SimpleNamespace(value=value)}, error=error)

        rows = [sample("q1", "A", 1), sample("q1", "B", 0),
                sample("q2", "A", 1), sample("q2", "B", 1)]
        self.assertEqual(pairs_from_summaries(rows, "A", "B", "human_rubric"),
                         [(1, 0), (1, 1)])
        rows[1].scores = {}
        with self.assertRaisesRegex(AuditError, "missing"):
            pairs_from_summaries(rows, "A", "B", "human_rubric")

    def test_inspect_summary_rejects_bad_score_and_repeated_epoch(self):
        def sample(value):
            return SimpleNamespace(metadata={"pair_id": "q1", "group": "A"},
                                   scores={"rubric": SimpleNamespace(value=value)}, error=None)

        with self.assertRaisesRegex(AuditError, "numeric 0 or 1"):
            pairs_from_summaries([sample("C")], "A", "B", "rubric")
        with self.assertRaisesRegex(AuditError, "duplicate"):
            pairs_from_summaries([sample(1), sample(0)], "A", "B", "rubric")


if __name__ == "__main__":
    unittest.main()
