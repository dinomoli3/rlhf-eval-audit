import tempfile
import unittest
from pathlib import Path

from eval_audit import AuditError, audit, load_pairs


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


if __name__ == "__main__":
    unittest.main()
