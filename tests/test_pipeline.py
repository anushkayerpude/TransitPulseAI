"""
TransitPulse AI - Comprehensive End-to-End Test Suite
Tests:
1. Validation of correct baseline CSVs
2. Validation rejection of corrupted CSVs with proper error messages
3. Multi-modal consolidation of Metro, BRTS, and AMTS
4. Exception detection on incident dataset (detecting Metro delay spike, BRTS drop, AMTS availability)
5. AI Explainer output structure & evidence grounding
6. PDF binary brief generation (validating PDF byte structure)
7. HTML printable brief generation
"""

import os
import unittest
import pandas as pd
from engine.validator import validate_csv
from engine.consolidator import consolidate_datasets
from engine.detector import DetectionEngine
from engine.explainer import AIExplainerEngine
from engine.pdf_generator import generate_pdf_brief, generate_html_brief

class TestTransitPulsePipeline(unittest.TestCase):
    def test_01_baseline_validation(self):
        """Verify baseline files pass validation cleanly."""
        for op in ["metro", "brts", "amts"]:
            path = f"data/baseline/{op}_baseline.csv"
            res = validate_csv(path, expected_operator=op.upper())
            self.assertTrue(res.is_valid, f"{op} baseline should be valid")
            self.assertEqual(len(res.errors), 0)
            self.assertGreater(res.row_count, 0)
            self.assertEqual(res.unique_dates_count, 14)

    def test_02_corrupted_validation(self):
        """Verify corrupted CSV is rejected and produces specific actionable errors."""
        res = validate_csv("data/invalid_test/corrupted_metro_sample.csv", expected_operator="Metro")
        self.assertFalse(res.is_valid, "Corrupted file must fail validation")
        self.assertGreater(len(res.errors), 0, "Must report errors")
        error_issues = [e["issue"] for e in res.errors]
        self.assertTrue(any("negative" in iss.lower() for iss in error_issues), "Should catch negative ridership")
        self.assertTrue(any("date" in iss.lower() for iss in error_issues), "Should catch invalid date")
        self.assertTrue(any("duplicate" in iss.lower() for iss in error_issues), "Should catch duplicate records")

    def test_03_consolidation_and_anomaly_detection(self):
        """Verify incident dataset consolidation and detection of the 3 deliberate anomalies."""
        v_m = validate_csv("data/incident/metro_incident.csv", "Metro")
        v_b = validate_csv("data/incident/brts_incident.csv", "BRTS")
        v_a = validate_csv("data/incident/amts_incident.csv", "AMTS")
        
        self.assertTrue(v_m.is_valid and v_b.is_valid and v_a.is_valid)
        consolidated = consolidate_datasets([v_m.cleaned_df, v_b.cleaned_df, v_a.cleaned_df])
        
        self.assertEqual(len(consolidated.operators), 3)
        self.assertEqual(len(consolidated.dates), 14)
        
        detector = DetectionEngine()
        exceptions = detector.detect_exceptions(consolidated, target_date="2026-10-10", baseline_strategy="same_weekday")
        
        self.assertGreater(len(exceptions), 0, "Must detect exceptions on incident date")
        critical_exceptions = [e for e in exceptions if e.severity == "CRITICAL"]
        self.assertGreater(len(critical_exceptions), 0, "Must detect CRITICAL exceptions")
        
        # Verify Metro delay spike or ridership drop detected
        metro_exs = [e for e in exceptions if e.operator == "Metro"]
        self.assertTrue(len(metro_exs) > 0, "Must detect Metro anomaly")
        
        # Verify BRTS corridor ridership drop detected
        brts_exs = [e for e in exceptions if e.operator == "BRTS"]
        self.assertTrue(len(brts_exs) > 0, "Must detect BRTS anomaly")

    def test_04_ai_explainer_and_brief_synthesis(self):
        """Verify evidence-backed explanation structure."""
        v_m = validate_csv("data/incident/metro_incident.csv", "Metro")
        v_b = validate_csv("data/incident/brts_incident.csv", "BRTS")
        v_a = validate_csv("data/incident/amts_incident.csv", "AMTS")
        consolidated = consolidate_datasets([v_m.cleaned_df, v_b.cleaned_df, v_a.cleaned_df])
        
        detector = DetectionEngine()
        exceptions = detector.detect_exceptions(consolidated, target_date="2026-10-10")
        
        explainer = AIExplainerEngine()
        explained = [explainer.explain_exception(ex) for ex in exceptions]
        
        for exp in explained:
            self.assertIsNotNone(exp.title)
            self.assertGreater(len(exp.evidence_points), 0)
            self.assertGreater(len(exp.possible_explanations), 0)
            self.assertIsNotNone(exp.recommended_action)
            self.assertIn("Hypothesis", exp.possible_explanations[0])

        metrics = consolidated.get_date_metrics("2026-10-10")
        brief = explainer.generate_morning_brief(
            date_str="2026-10-10",
            citywide_metrics=metrics["citywide"],
            operator_metrics=metrics["operators"],
            explained_exceptions=explained
        )
        
        self.assertIn("report_date", brief)
        self.assertIn("overall_health_score", brief)
        self.assertIn("top_actions", brief)

        # Test PDF Generation
        pdf_bytes = generate_pdf_brief(brief)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"), "Must be a valid PDF header")
        self.assertGreater(len(pdf_bytes), 1000)

        # Test HTML Generation
        html_str = generate_html_brief(brief)
        self.assertIn("TRANSITPULSE AI", html_str)
        self.assertIn("Ahmedabad", html_str)

if __name__ == "__main__":
    unittest.main()
