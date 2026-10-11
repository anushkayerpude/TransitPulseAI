"""
TransitPulse AI - GMRC Track & Wayside Telemetry Test Suite
Tests:
1. GMRC corridor metadata integrity
2. Wayside block telemetry generation across Nominal, Incident, Power Trip, and Switch Lock scenarios
3. Factual track evidence generation for AI Explainer grounding
4. SVG track schematic diagram compilation
5. FastAPI GMRC track endpoints (/api/gmrc/track/corridors, /api/gmrc/track/status, /api/gmrc/track/overview)
"""

import unittest
from fastapi.testclient import TestClient
from config import GMRC_CORRIDORS, GMRC_TRACK_STATUSES
from engine.track_monitor import GMRCTrackMonitor
from components.track_diagram import generate_track_svg
from components.transit_map import generate_leaflet_map_html
from api import app

class TestGMRCTrackMonitor(unittest.TestCase):
    def test_01_corridor_metadata(self):
        """Verify all three corridors are defined with stations and codes."""
        self.assertIn("East-West Line", GMRC_CORRIDORS)
        self.assertIn("North-South Line", GMRC_CORRIDORS)
        self.assertIn("GN Branch", GMRC_CORRIDORS)
        
        ew = GMRC_CORRIDORS["East-West Line"]
        self.assertEqual(ew["code"], "EW")
        self.assertEqual(len(ew["stations"]), 18)
        
        # Check Old High Court is interchange
        ohc = [s for s in ew["stations"] if s["name"] == "Old High Court"]
        self.assertEqual(len(ohc), 1)
        self.assertEqual(ohc[0]["type"], "interchange")

    def test_02_nominal_telemetry(self):
        """Verify nominal scenario has clean 750V DC and no active TSRs."""
        data = GMRCTrackMonitor.get_corridor_telemetry("East-West Line", scenario="nominal")
        summary = data["summary"]
        self.assertEqual(summary["overall_health"], "NOMINAL")
        self.assertEqual(summary["tsr_blocks"], 0)
        self.assertEqual(summary["fault_blocks"], 0)
        self.assertGreater(summary["active_trains_count"], 0)
        self.assertEqual(summary["operating_headway_min"], 3.5)

    def test_03_incident_telemetry(self):
        """Verify incident scenario injects TSR on Kalupur zone matching 15.6m headway."""
        data = GMRCTrackMonitor.get_corridor_telemetry("East-West Line", scenario="incident")
        summary = data["summary"]
        self.assertEqual(summary["overall_health"], "WARNING")
        self.assertGreaterEqual(summary["tsr_blocks"], 1)
        self.assertEqual(summary["operating_headway_min"], 15.6)
        
        # Verify specific TSR block parameters
        tsr_blocks = [b for b in data["blocks"] if b["status"] == "SPEED_RESTRICTION"]
        self.assertTrue(any("25" in str(b["speed_limit_kmh"]) for b in tsr_blocks))

    def test_04_power_trip_scenario(self):
        """Verify third rail power trip injects 0V DC on affected block."""
        data = GMRCTrackMonitor.get_corridor_telemetry("East-West Line", scenario="power_trip")
        summary = data["summary"]
        self.assertEqual(summary["overall_health"], "CRITICAL")
        self.assertGreaterEqual(summary["fault_blocks"], 1)
        
        fault_blocks = [b for b in data["blocks"] if b["status"] == "POWER_FAULT"]
        self.assertTrue(any(b["third_rail_voltage_v"] == 0.0 for b in fault_blocks))

    def test_05_track_evidence_for_explainer(self):
        """Verify factual track evidence lines are generated for daily briefing."""
        evidence = GMRCTrackMonitor.get_track_evidence_for_explainer("East-West Line", scenario="incident")
        self.assertGreater(len(evidence), 0)
        self.assertTrue(any("TSR" in line or "Speed" in line or "Wayside" in line for line in evidence))
        self.assertTrue(any("headway" in line.lower() for line in evidence))

    def test_06_svg_schematic_generation(self):
        """Verify SVG diagram compiles with stations and track segments."""
        data = GMRCTrackMonitor.get_corridor_telemetry("East-West Line", scenario="incident")
        svg_code = generate_track_svg(data)
        self.assertTrue(svg_code.startswith("<svg"))
        self.assertTrue(svg_code.endswith("</svg>\n") or svg_code.endswith("</svg>"))
        self.assertIn("Thaltej Gam", svg_code)
        self.assertIn("Old High Court", svg_code)
        self.assertIn("Kalupur", svg_code)

    def test_07_fastapi_track_endpoints(self):
        """Verify FastAPI REST endpoints serve GMRC track telemetry."""
        client = TestClient(app)
        
        # 1. Corridors list
        r_corr = client.get("/api/gmrc/track/corridors")
        self.assertEqual(r_corr.status_code, 200)
        self.assertIn("East-West Line", r_corr.json()["corridors"])
        
        # 2. Track status
        r_status = client.get("/api/gmrc/track/status?corridor_key=East-West%20Line&scenario=incident")
        self.assertEqual(r_status.status_code, 200)
        res_json = r_status.json()
        self.assertEqual(res_json["status"], "SUCCESS")
        self.assertIn("blocks", res_json["telemetry"])
        
        # 3. Network overview
        r_over = client.get("/api/gmrc/track/overview?scenario=nominal")
        self.assertEqual(r_over.status_code, 200)
        self.assertEqual(r_over.json()["status"], "SUCCESS")

    def test_08_leaflet_map_generation(self):
        """Verify Leaflet GIS HTML compiles with stations, coordinates, and Leaflet CDN scripts."""
        html_code = generate_leaflet_map_html(selected_corridor="East-West Line", scenario="incident")
        self.assertIn("leaflet.js", html_code)
        self.assertIn("leaflet.css", html_code)
        self.assertIn("L.map('map'", html_code)
        self.assertIn("Thaltej Gam", html_code)
        self.assertIn("Old High Court", html_code)
        self.assertIn("23.0375", html_code)  # Coordinate check
        self.assertIn("72.5715", html_code)

if __name__ == "__main__":
    unittest.main()

