"""
TransitPulse AI - Standalone FastAPI Backend Server
Provides RESTful API endpoints for:
- Pre-flight CSV schema validation
- Multi-modal telemetry consolidation
- Deterministic exception and anomaly detection
- Evidence-grounded root-cause explanation
- Executive daily brief synthesis (JSON, HTML & binary PDF)
"""

import os
import io
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, UploadFile, File, Form, Query, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import APP_NAME, VERSION, PROBLEM_STATEMENT, HACKATHON_EVENT, DEFAULT_THRESHOLDS, OPERATOR_CONFIG
from engine.validator import validate_csv
from engine.consolidator import consolidate_datasets
from engine.detector import DetectionEngine
from engine.explainer import AIExplainerEngine
from engine.pdf_generator import generate_pdf_brief, generate_html_brief
from engine.track_monitor import GMRCTrackMonitor

app = FastAPI(
    title=f"{APP_NAME} Backend API",
    description="Operational Analytics & Automated Two-Minute Morning Briefing REST API for Metro (GMRC), Janmarg BRTS, and AMTS.",
    version="1.0"
)

# Enable CORS for external dashboards and clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DetectionParams(BaseModel):
    baseline_strategy: str = "same_weekday"
    ridership_critical_pct: float = DEFAULT_THRESHOLDS["ridership_critical_pct"]
    ridership_warning_pct: float = DEFAULT_THRESHOLDS["ridership_warning_pct"]
    availability_critical_pct: float = DEFAULT_THRESHOLDS["availability_critical_pct"]
    availability_warning_pct: float = DEFAULT_THRESHOLDS["availability_warning_pct"]
    delay_absolute_critical_min: float = DEFAULT_THRESHOLDS["delay_absolute_critical_min"]

@app.get("/")
def root():
    return {
        "app": APP_NAME,
        "version": VERSION,
        "event": HACKATHON_EVENT,
        "problem_statement": PROBLEM_STATEMENT,
        "status": "OPERATIONAL",
        "interactive_docs": "/docs",
        "endpoints": {
            "health": "/api/health",
            "run_pipeline": "/api/demo/run?dataset_type=incident",
            "download_pdf": "/api/demo/pdf?dataset_type=incident",
            "validate_csv": "POST /api/validate",
        }
    }

@app.get("/api/health")
def health_check():
    return {
        "status": "HEALTHY",
        "backend": "TransitPulse AI Engine",
        "offline_ready": True,
        "operators_supported": list(OPERATOR_CONFIG.keys())
    }

@app.post("/api/validate")
async def validate_uploaded_csv(
    file: UploadFile = File(...),
    operator: Optional[str] = Form(None)
):
    """
    Validates an uploaded transit CSV against schema, negative values, and date parsing.
    """
    contents = await file.read()
    buffer = io.BytesIO(contents)
    buffer.name = file.filename
    res = validate_csv(buffer, expected_operator=operator)
    return {
        "filename": res.filename,
        "is_valid": res.is_valid,
        "operator": res.operator_detected,
        "row_count": res.row_count,
        "unique_dates": res.unique_dates_count,
        "date_range": res.date_range,
        "errors": res.errors,
        "warnings": res.warnings
    }

@app.get("/api/demo/run")
def run_demo_pipeline(
    dataset_type: str = Query("incident", enum=["incident", "baseline"]),
    baseline_strategy: str = Query("same_weekday", enum=["same_weekday", "7day_avg", "previous_day"])
):
    """
    Executes the complete backend pipeline across 14 days of Metro, BRTS, and AMTS data.
    """
    base_path = f"data/{dataset_type}"
    metro_path = f"{base_path}/metro_{dataset_type}.csv"
    brts_path = f"{base_path}/brts_{dataset_type}.csv"
    amts_path = f"{base_path}/amts_{dataset_type}.csv"

    if not (os.path.exists(metro_path) and os.path.exists(brts_path) and os.path.exists(amts_path)):
        raise HTTPException(status_code=404, detail="Dataset files not found")

    v_m = validate_csv(metro_path, "Metro")
    v_b = validate_csv(brts_path, "BRTS")
    v_a = validate_csv(amts_path, "AMTS")

    if not (v_m.is_valid and v_b.is_valid and v_a.is_valid):
        return {
            "status": "VALIDATION_FAILED",
            "errors": {
                "Metro": v_m.errors,
                "BRTS": v_b.errors,
                "AMTS": v_a.errors
            }
        }

    consolidated = consolidate_datasets([v_m.cleaned_df, v_b.cleaned_df, v_a.cleaned_df])
    detector = DetectionEngine()
    exceptions = detector.detect_exceptions(
        consolidated,
        target_date=consolidated.latest_date,
        baseline_strategy=baseline_strategy
    )

    explainer = AIExplainerEngine()
    explained_list = [explainer.explain_exception(ex) for ex in exceptions]

    target_date = consolidated.latest_date
    metrics = consolidated.get_date_metrics(target_date)
    brief = explainer.generate_morning_brief(
        date_str=target_date,
        citywide_metrics=metrics.get("citywide", {}),
        operator_metrics=metrics.get("operators", {}),
        explained_exceptions=explained_list
    )

    return {
        "status": "SUCCESS",
        "dataset_type": dataset_type,
        "report_date": target_date,
        "health_score": brief.get("overall_health_score"),
        "status_label": brief.get("status_label"),
        "critical_exceptions_count": brief.get("critical_exceptions_count"),
        "warning_exceptions_count": brief.get("warning_exceptions_count"),
        "executive_narrative": brief.get("executive_narrative"),
        "top_actions": brief.get("top_actions"),
        "operator_metrics": brief.get("operator_metrics"),
        "citywide_metrics": brief.get("citywide_metrics"),
        "detailed_exceptions": brief.get("detailed_exceptions")
    }

@app.get("/api/demo/pdf")
def download_brief_pdf(
    dataset_type: str = Query("incident", enum=["incident", "baseline"])
):
    """
    Compiles and streams the 1-Page ReportLab Vector PDF Brief.
    """
    res = run_demo_pipeline(dataset_type=dataset_type)
    if res.get("status") != "SUCCESS":
        raise HTTPException(status_code=400, detail="Failed to run pipeline for PDF")
    
    # Reconstruct brief data structure
    pdf_bytes = generate_pdf_brief(res)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=TransitPulse_Daily_Brief_{res.get('report_date')}.pdf"}
    )

# -----------------------------------------------------------------------------
# GMRC METRO TRACK & WAYSIDE TELEMETRY REST ENDPOINTS
# -----------------------------------------------------------------------------

@app.get("/api/gmrc/track/corridors")
def get_gmrc_corridors():
    """
    Returns list of GMRC Metro corridors, route lengths, and stations.
    """
    from config import GMRC_CORRIDORS
    return {
        "status": "SUCCESS",
        "operator": "Gujarat Metro Rail Corporation (GMRC)",
        "corridors": GMRC_CORRIDORS
    }

@app.get("/api/gmrc/track/status")
def get_gmrc_track_status(
    corridor_key: str = Query("East-West Line", description="Corridor name (East-West Line, North-South Line, GN Branch)"),
    scenario: str = Query("nominal", enum=["nominal", "incident", "power_trip", "switch_fault"])
):
    """
    Returns granular track circuit occupancy, CBTC signaling health,
    third-rail traction voltage, and temporary speed restrictions for a corridor.
    """
    telemetry = GMRCTrackMonitor.get_corridor_telemetry(corridor_key=corridor_key, scenario=scenario)
    return {
        "status": "SUCCESS",
        "corridor": corridor_key,
        "scenario": scenario,
        "telemetry": telemetry
    }

@app.get("/api/gmrc/track/overview")
def get_gmrc_network_overview(
    scenario: str = Query("nominal", enum=["nominal", "incident", "power_trip", "switch_fault"])
):
    """
    Returns high-level wayside track health overview across all GMRC corridors.
    """
    overview = GMRCTrackMonitor.get_network_overview(scenario=scenario)
    return {
        "status": "SUCCESS",
        "network_overview": overview
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)

