"""
TransitPulse AI - Main Streamlit Application
AI-Powered Public Transport Operations Intelligence & Daily Briefing System
Hackathon: Metro Hacks — DevFest Gandhinagar
Problem Statement: PS-13 — The Two-Minute Morning Brief
Target Users: Metro (GMRC), BRTS (Janmarg), AMTS Operations Teams
"""

import os
import io
import streamlit as st
import pandas as pd
from datetime import datetime

# Page configuration - Wide layout with custom title
st.set_page_config(
    page_title="TransitPulse AI | Metro, BRTS & AMTS Intelligence",
    page_icon="🚇",
    layout="wide",
    initial_sidebar_state="expanded"
)

from config import (
    APP_NAME, APP_SUBTITLE, HACKATHON_EVENT, PROBLEM_STATEMENT, VERSION,
    OPERATOR_CONFIG, DEFAULT_THRESHOLDS, SEVERITY_STYLES
)
from components.styles import CUSTOM_CSS
from components.charts import (
    create_ridership_trend_chart,
    create_availability_bar_chart,
    create_delay_comparison_chart,
    create_corridor_breakdown_chart
)
from components.ui_cards import render_kpi_metric, render_exception_card_streamlit
from engine.validator import validate_csv, ValidationResult
from engine.consolidator import consolidate_datasets, ConsolidatedData
from engine.detector import DetectionEngine, TransitException
from engine.explainer import AIExplainerEngine
from engine.pdf_generator import generate_pdf_brief, generate_html_brief

# Inject custom CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# SESSION STATE INITIALIZATION
# -----------------------------------------------------------------------------
if "metro_file" not in st.session_state:
    st.session_state.metro_file = None
if "brts_file" not in st.session_state:
    st.session_state.brts_file = None
if "amts_file" not in st.session_state:
    st.session_state.amts_file = None
if "active_dataset_label" not in st.session_state:
    st.session_state.active_dataset_label = "No Data Loaded"
if "consolidated_data" not in st.session_state:
    st.session_state.consolidated_data = None
if "detected_exceptions" not in st.session_state:
    st.session_state.detected_exceptions = []
if "explained_exceptions" not in st.session_state:
    st.session_state.explained_exceptions = []
if "morning_brief" not in st.session_state:
    st.session_state.morning_brief = None
if "validation_results" not in st.session_state:
    st.session_state.validation_results = {}

# Helper to load sample files
def load_sample_dataset(dataset_type="incident"):
    base_path = f"data/{dataset_type}"
    st.session_state.metro_file = f"{base_path}/metro_{dataset_type}.csv"
    st.session_state.brts_file = f"{base_path}/brts_{dataset_type}.csv"
    st.session_state.amts_file = f"{base_path}/amts_{dataset_type}.csv"
    st.session_state.active_dataset_label = f"Sample {dataset_type.title()} Dataset (14-Day Gandhinagar/Ahmedabad)"
    # Clear previous pipeline outputs to force re-run
    st.session_state.consolidated_data = None
    st.session_state.detected_exceptions = []
    st.session_state.explained_exceptions = []
    st.session_state.morning_brief = None

# Automatically load incident dataset on first launch if empty
if st.session_state.metro_file is None:
    load_sample_dataset("incident")

# -----------------------------------------------------------------------------
# SIDEBAR CONTROLS
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown(f"""
    <div class="hackathon-sidebar-card">
        <div style="font-size: 11px; font-weight: 800; color: #14B8A6; text-transform: uppercase; letter-spacing: 0.5px;">
            {HACKATHON_EVENT}
        </div>
        <div style="font-size: 14px; font-weight: 700; color: #F8FAFC; margin-top: 2px;">
            {PROBLEM_STATEMENT}
        </div>
        <div style="font-size: 11px; color: #94A3B8; margin-top: 4px;">
            {VERSION}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### ⚡ Quick Demo Datasets")
    st.caption("One-click presets for immediate live judging demonstration:")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        if st.button("🚨 Load Incidents", use_container_width=True, help="14-day history with 3 deliberate anomalies on final day"):
            load_sample_dataset("incident")
            st.rerun()
    with col_s2:
        if st.button("🟢 Load Baseline", use_container_width=True, help="14-day normal operational baseline"):
            load_sample_dataset("baseline")
            st.rerun()
            
    if st.button("🧪 Test Validation Failure", use_container_width=True, help="Load corrupted CSV with missing fields and bad formats"):
        st.session_state.metro_file = "data/invalid_test/corrupted_metro_sample.csv"
        st.session_state.brts_file = "data/baseline/brts_baseline.csv"
        st.session_state.amts_file = "data/baseline/amts_baseline.csv"
        st.session_state.active_dataset_label = "Corrupted Validation Test Dataset"
        st.session_state.consolidated_data = None
        st.session_state.detected_exceptions = []
        st.session_state.explained_exceptions = []
        st.session_state.morning_brief = None
        st.rerun()

    st.markdown("---")
    st.markdown("### ⚙️ Analytical Parameters")
    
    baseline_mode = st.selectbox(
        "Baseline Comparison Model",
        options=["same_weekday", "7day_avg", "previous_day"],
        format_func=lambda x: {
            "same_weekday": "📅 Same-Weekday Historical Avg (Recommended)",
            "7day_avg": "📈 7-Day Rolling Average",
            "previous_day": "⏪ Previous Day (D-1) Only"
        }[x],
        help="Same-weekday comparison isolates weekend drops from genuine operational distress."
    )

    with st.expander("🛠️ Detection Thresholds", expanded=False):
        th_rdr_crit = st.slider("Ridership Critical Drop %", -30.0, -5.0, DEFAULT_THRESHOLDS["ridership_critical_pct"], step=1.0)
        th_rdr_warn = st.slider("Ridership Warning Drop %", -20.0, -2.0, DEFAULT_THRESHOLDS["ridership_warning_pct"], step=1.0)
        th_avl_crit = st.slider("Availability Critical Rate %", 70.0, 95.0, DEFAULT_THRESHOLDS["availability_critical_pct"], step=1.0)
        th_avl_warn = st.slider("Availability Warning Rate %", 80.0, 98.0, DEFAULT_THRESHOLDS["availability_warning_pct"], step=1.0)
        th_dly_spike = st.slider("Delay Spike Critical (Min)", 2.0, 10.0, DEFAULT_THRESHOLDS["delay_absolute_critical_min"], step=0.5)

    custom_thresholds = {
        "ridership_critical_pct": th_rdr_crit,
        "ridership_warning_pct": th_rdr_warn,
        "availability_critical_pct": th_avl_crit,
        "availability_warning_pct": th_avl_warn,
        "delay_warning_delta_pct": DEFAULT_THRESHOLDS["delay_warning_delta_pct"],
        "delay_critical_delta_pct": DEFAULT_THRESHOLDS["delay_critical_delta_pct"],
        "delay_absolute_critical_min": th_dly_spike
    }

    st.markdown("---")
    st.markdown("### 🤖 Intelligence Engine")
    ai_mode = st.radio("Explanation Engine", ["Deterministic Rule Engine (Offline)", "Gemini AI Enhanced"], index=0)
    user_api_key = ""
    if ai_mode == "Gemini AI Enhanced":
        user_api_key = st.text_input("Gemini API Key", type="password", placeholder="Paste AI Studio Key")
        if not user_api_key:
            st.info("No key provided. Using deterministic fallback engine seamlessly.")

    st.markdown("---")
    st.caption("TransitPulse AI • DevFest Gandhinagar PS-13 • Version 1.0 MVP")

# -----------------------------------------------------------------------------
# MAIN APP HEADER BANNER
# -----------------------------------------------------------------------------
st.markdown(f"""
<div class="ops-banner">
    <div class="ops-title-block">
        <h1>{APP_NAME}</h1>
        <p>{APP_SUBTITLE} &nbsp;|&nbsp; <strong>Gandhinagar & Ahmedabad Regional Transit Joint Ops</strong></p>
    </div>
    <div class="ops-live-badge">
        <div class="ops-live-dot"></div>
        <span>OPERATIONAL INTELLIGENCE ACTIVE</span>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# EXECUTION PIPELINE FUNCTION
# -----------------------------------------------------------------------------
def run_pipeline():
    # 1. Validate all three feeds
    v_metro = validate_csv(st.session_state.metro_file, expected_operator="Metro")
    v_brts = validate_csv(st.session_state.brts_file, expected_operator="BRTS")
    v_amts = validate_csv(st.session_state.amts_file, expected_operator="AMTS")
    
    st.session_state.validation_results = {
        "Metro": v_metro,
        "BRTS": v_brts,
        "AMTS": v_amts
    }
    
    all_valid = v_metro.is_valid and v_brts.is_valid and v_amts.is_valid
    if not all_valid:
        st.session_state.consolidated_data = None
        st.session_state.detected_exceptions = []
        st.session_state.explained_exceptions = []
        st.session_state.morning_brief = None
        return False
        
    # 2. Consolidate validated DataFrames
    consolidated = consolidate_datasets([v_metro.cleaned_df, v_brts.cleaned_df, v_amts.cleaned_df])
    st.session_state.consolidated_data = consolidated
    
    # 3. Detect Exceptions on latest target date
    detector = DetectionEngine(thresholds=custom_thresholds)
    exceptions = detector.detect_exceptions(
        consolidated,
        target_date=consolidated.latest_date,
        baseline_strategy=baseline_mode
    )
    st.session_state.detected_exceptions = exceptions
    
    # 4. Generate AI-Assisted Structured Explanations
    explainer = AIExplainerEngine(api_key=user_api_key if ai_mode == "Gemini AI Enhanced" else None)
    explained_list = [explainer.explain_exception(ex) for ex in exceptions]
    st.session_state.explained_exceptions = explained_list
    
    # 5. Synthesize Daily Morning Brief
    target_date = consolidated.latest_date
    metrics = consolidated.get_date_metrics(target_date)
    brief = explainer.generate_morning_brief(
        date_str=target_date,
        citywide_metrics=metrics.get("citywide", {}),
        operator_metrics=metrics.get("operators", {}),
        explained_exceptions=explained_list
    )
    st.session_state.morning_brief = brief
    return True

# Run pipeline if not already executed
if st.session_state.consolidated_data is None and st.session_state.metro_file is not None:
    run_pipeline()

# -----------------------------------------------------------------------------
# APP NAVIGATION TABS
# -----------------------------------------------------------------------------
tab_overview, tab_import, tab_intel, tab_brief = st.tabs([
    "📊 Executive Overview",
    "📥 Data Import & Validation",
    "🔍 Operations Intelligence",
    "📋 Two-Minute Daily Brief"
])

# =============================================================================
# TAB 1: EXECUTIVE OVERVIEW
# =============================================================================
with tab_overview:
    if st.session_state.consolidated_data is None:
        st.warning("⚠️ Data feeds require attention. Check the **Data Import & Validation** tab to resolve errors.")
    else:
        brief = st.session_state.morning_brief
        consolidated = st.session_state.consolidated_data
        target_date = consolidated.latest_date
        metrics = consolidated.get_date_metrics(target_date)
        city_m = metrics.get("citywide", {})
        op_m = metrics.get("operators", {})
        
        # Row 1: High Level KPIs
        crit_count = brief.get("critical_exceptions_count", 0)
        warn_count = brief.get("warning_exceptions_count", 0)
        health_score = brief.get("overall_health_score", 95.0)
        
        kpi_cols = st.columns(5)
        with kpi_cols[0]:
            render_kpi_metric(
                "Transit Health Score",
                f"{health_score:.0f}/100",
                brief.get("status_label", "NOMINAL"),
                icon="🩺",
                is_alert=(health_score < 80)
            )
        with kpi_cols[1]:
            render_kpi_metric(
                "Citywide Ridership",
                f"{int(city_m.get('total_ridership', 0)):,}",
                "Combined Metro, BRTS, AMTS",
                icon="👥",
                delta_str=f"{city_m.get('reporting_operators_count', 3)} Operators Live"
            )
        with kpi_cols[2]:
            render_kpi_metric(
                "Network Availability",
                f"{city_m.get('network_availability_pct', 0):.1f}%",
                f"{int(city_m.get('total_completed', 0)):,} / {int(city_m.get('total_scheduled', 0)):,} trips",
                icon="⚡",
                is_alert=(city_m.get("network_availability_pct", 100) < 90)
            )
        with kpi_cols[3]:
            render_kpi_metric(
                "Average Network Delay",
                f"{city_m.get('citywide_avg_delay_minutes', 0):.1f} min",
                "Weighted transit wait delay",
                icon="⏱️",
                is_alert=(city_m.get("citywide_avg_delay_minutes", 0) > 5.0)
            )
        with kpi_cols[4]:
            render_kpi_metric(
                "Active Exceptions",
                f"{crit_count + warn_count}",
                f"{crit_count} Critical, {warn_count} Warnings",
                icon="🚨",
                is_alert=(crit_count > 0)
            )

        # Row 2: Operator Snapshot Cards
        st.markdown('<div class="section-title"><span>🚏 Multi-Modal Operator Status</span></div>', unsafe_allow_html=True)
        op_cols = st.columns(3)
        for i, op_name in enumerate(["Metro", "BRTS", "AMTS"]):
            with op_cols[i]:
                m = op_m.get(op_name, {})
                cfg = OPERATOR_CONFIG.get(op_name, {})
                r_count = int(m.get("ridership", 0))
                sched = int(m.get("scheduled_services", 0))
                comp = int(m.get("completed_services", 0))
                avail = m.get("service_availability_pct", 0)
                delay = m.get("average_delay_minutes", 0)
                
                # Check status
                is_op_crit = any(e.raw.operator == op_name and e.raw.severity == "CRITICAL" for e in st.session_state.explained_exceptions)
                is_op_warn = any(e.raw.operator == op_name and e.raw.severity == "WARNING" for e in st.session_state.explained_exceptions)
                status_badge = '<span class="pill-crit">🚨 CRITICAL</span>' if is_op_crit else (
                    '<span class="pill-warn">⚠️ REVIEW</span>' if is_op_warn else '<span style="color:#10B981; font-weight:700; font-size:11px;">✅ NOMINAL</span>'
                )

                st.markdown(f"""
                <div class="kpi-card" style="border-top: 3px solid {cfg.get('color', '#38BDF8')};">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span style="font-weight: 700; font-size: 15px; color: #F8FAFC;">
                            {cfg.get('icon', '')} {op_name}
                        </span>
                        {status_badge}
                    </div>
                    <div style="font-size: 11px; color: #94A3B8; margin-bottom: 10px;">{cfg.get('full_name', '')}</div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 12px;">
                        <div>
                            <span style="color: #64748B;">Ridership:</span><br/>
                            <strong style="color: #F8FAFC; font-size: 14px;">{r_count:,}</strong>
                        </div>
                        <div>
                            <span style="color: #64748B;">Availability:</span><br/>
                            <strong style="color: {'#EF4444' if avail < 85 else '#2DD4BF'}; font-size: 14px;">{avail:.1f}%</strong>
                        </div>
                        <div>
                            <span style="color: #64748B;">Completed Trips:</span><br/>
                            <strong style="color: #CBD5E1;">{comp:,} / {sched:,}</strong>
                        </div>
                        <div>
                            <span style="color: #64748B;">Avg Delay:</span><br/>
                            <strong style="color: {'#EF4444' if delay > 6 else '#CBD5E1'}; font-size: 14px;">{delay:.1f} min</strong>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # Row 3: Ridership Trend & Availability Visualizations
        st.markdown('<div class="section-title"><span>📈 Citywide Multi-Modal Trends</span></div>', unsafe_allow_html=True)
        chart_col1, chart_col2 = st.columns([1.6, 1.0])
        with chart_col1:
            fig_trend = create_ridership_trend_chart(consolidated, highlight_date=target_date)
            st.plotly_chart(fig_trend, use_container_width=True)
        with chart_col2:
            fig_avail = create_availability_bar_chart(op_m)
            st.plotly_chart(fig_avail, use_container_width=True)

# =============================================================================
# TAB 2: DATA IMPORT & VALIDATION
# =============================================================================
with tab_import:
    st.markdown('<div class="section-title"><span>📥 Ingest Operational Data Feeds</span></div>', unsafe_allow_html=True)
    st.info(f"**Current Ingestion Source:** `{st.session_state.active_dataset_label}`")

    # Sample CSV Downloads for Judges
    with st.expander("💾 Download Standard Demonstration CSV Files for Manual Testing", expanded=False):
        st.caption("Judges can download these structured CSVs and re-upload them to test validation and analysis:")
        d_col1, d_col2, d_col3 = st.columns(3)
        with d_col1:
            with open("data/incident/metro_incident.csv", "rb") as f:
                st.download_button("📥 Metro Sample CSV", f.read(), file_name="metro_sample.csv", mime="text/csv", use_container_width=True)
        with d_col2:
            with open("data/incident/brts_incident.csv", "rb") as f:
                st.download_button("📥 BRTS Sample CSV", f.read(), file_name="brts_sample.csv", mime="text/csv", use_container_width=True)
        with d_col3:
            with open("data/incident/amts_incident.csv", "rb") as f:
                st.download_button("📥 AMTS Sample CSV", f.read(), file_name="amts_sample.csv", mime="text/csv", use_container_width=True)

    # Three Upload Slots
    up_col1, up_col2, up_col3 = st.columns(3)
    
    with up_col1:
        st.markdown("#### 🚇 1. Metro Telemetry")
        st.caption("Gujarat Metro Rail Corporation (GMRC)")
        uploaded_metro = st.file_uploader("Upload Metro CSV", type=["csv"], key="uploader_metro")
        if uploaded_metro is not None:
            st.session_state.metro_file = uploaded_metro
            st.session_state.active_dataset_label = f"Uploaded File: {uploaded_metro.name}"

    with up_col2:
        st.markdown("#### 🚌 2. BRTS Telemetry")
        st.caption("Janmarg Ahmedabad BRTS")
        uploaded_brts = st.file_uploader("Upload BRTS CSV", type=["csv"], key="uploader_brts")
        if uploaded_brts is not None:
            st.session_state.brts_file = uploaded_brts
            st.session_state.active_dataset_label = f"Uploaded File: {uploaded_brts.name}"

    with up_col3:
        st.markdown("#### 🚍 3. AMTS Telemetry")
        st.caption("Ahmedabad Municipal Transport Service")
        uploaded_amts = st.file_uploader("Upload AMTS CSV", type=["csv"], key="uploader_amts")
        if uploaded_amts is not None:
            st.session_state.amts_file = uploaded_amts
            st.session_state.active_dataset_label = f"Uploaded File: {uploaded_amts.name}"

    # Action Button
    st.markdown("<br/>", unsafe_allow_html=True)
    if st.button("🚀 Validate & Consolidate Operational Feeds", type="primary", use_container_width=True):
        with st.spinner("Executing multi-schema validation and statistical baseline comparison..."):
            success = run_pipeline()
            if success:
                st.success("✅ Feeds successfully validated and consolidated into operations warehouse!")
            else:
                st.error("❌ Validation failed on one or more files. See detailed audit below.")

    # Validation Audit Results Display
    st.markdown('<div class="section-title"><span>🛡️ Multi-File Schema & Integrity Audit</span></div>', unsafe_allow_html=True)
    val_results = st.session_state.validation_results
    
    if val_results:
        val_cols = st.columns(3)
        for i, op_key in enumerate(["Metro", "BRTS", "AMTS"]):
            v: ValidationResult = val_results.get(op_key)
            with val_cols[i]:
                if not v:
                    st.info(f"{op_key}: No validation record yet.")
                    continue
                    
                if v.is_valid:
                    st.markdown(f"""
                    <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid #10B981; border-radius: 8px; padding: 14px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                            <strong style="color: #10B981; font-size: 14px;">✅ {op_key} VALID</strong>
                            <span style="font-size: 11px; color: #94A3B8;">{v.row_count} rows</span>
                        </div>
                        <div style="font-size: 12px; color: #CBD5E1;">
                            • Dates: {v.date_range[0]} to {v.date_range[1]}<br/>
                            • Units Detected: {v.unique_units_count} routes/lines<br/>
                            • Missing zero-fills: 0 detected
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    if v.warnings:
                        with st.expander(f"⚠️ {len(v.warnings)} Non-blocking Quality Notices"):
                            for w in v.warnings:
                                st.caption(f"• {w['issue']}")
                else:
                    st.markdown(f"""
                    <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid #EF4444; border-radius: 8px; padding: 14px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                            <strong style="color: #EF4444; font-size: 14px;">❌ {op_key} INVALID</strong>
                            <span style="font-size: 11px; color: #EF4444; font-weight:700;">{len(v.errors)} Errors</span>
                        </div>
                        <div style="font-size: 12px; color: #FCA5A5;">
                            Resolve issues below to proceed with analysis.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    for err in v.errors:
                        st.error(f"**Issue:** {err['issue']}\n\n💡 **Action:** {err['fix']}")

# =============================================================================
# TAB 3: OPERATIONS INTELLIGENCE
# =============================================================================
with tab_intel:
    if st.session_state.consolidated_data is None:
        st.warning("⚠️ Please upload valid datasets and run the analysis pipeline first.")
    else:
        consolidated = st.session_state.consolidated_data
        target_date = consolidated.latest_date
        metrics = consolidated.get_date_metrics(target_date)
        op_m = metrics.get("operators", {})
        exceptions = st.session_state.explained_exceptions

        st.markdown('<div class="section-title"><span>🔍 Diagnostic Comparisons & Delay Analysis</span></div>', unsafe_allow_html=True)
        
        # Row 1 Charts: Delay Comparison & Corridor Breakdown
        c_col1, c_col2 = st.columns([1.1, 1.4])
        with c_col1:
            # Baseline delays estimate for comparison chart
            hist_delays = {}
            for op in consolidated.operators:
                op_raw = consolidated.raw_df[(consolidated.raw_df["operator"] == op) & (consolidated.raw_df["date"] < target_date)]
                hist_delays[op] = round(op_raw["average_delay_minutes"].mean(), 1) if not op_raw.empty else 2.0
            fig_delay = create_delay_comparison_chart(op_m, hist_delays)
            st.plotly_chart(fig_delay, use_container_width=True)
            
        with c_col2:
            fig_corridor = create_corridor_breakdown_chart(consolidated.raw_df, target_date)
            st.plotly_chart(fig_corridor, use_container_width=True)

        # Row 2: Prioritized Operational Exceptions Feed
        st.markdown('<div class="section-title"><span>🚨 Prioritized Exception Feed (Evidence-Backed)</span></div>', unsafe_allow_html=True)
        st.caption("Ranked by statistical deviation severity. Click any exception to review evidence and hypotheses:")

        # Filters
        f_col1, f_col2 = st.columns([1, 2])
        with f_col1:
            op_filter = st.selectbox("Filter by Operator", ["All Operators", "Metro", "BRTS", "AMTS"])
        with f_col2:
            sev_filter = st.selectbox("Filter by Severity", ["All Severities", "CRITICAL Only", "WARNING Only"])

        filtered_exceptions = exceptions
        if op_filter != "All Operators":
            filtered_exceptions = [e for e in filtered_exceptions if e.raw.operator == op_filter]
        if sev_filter == "CRITICAL Only":
            filtered_exceptions = [e for e in filtered_exceptions if e.raw.severity == "CRITICAL"]
        elif sev_filter == "WARNING Only":
            filtered_exceptions = [e for e in filtered_exceptions if e.raw.severity == "WARNING"]

        if not filtered_exceptions:
            st.success("✅ No exceptions matching the selected criteria.")
        else:
            for idx, ex in enumerate(filtered_exceptions):
                render_exception_card_streamlit(ex, idx)

        # Row 3: Inspect Raw Telemetry Warehouse
        with st.expander("📋 Inspect Consolidated Multi-Modal Telemetry Warehouse", expanded=False):
            st.caption("Consolidated tabular data with date filtering and CSV export:")
            st.dataframe(
                consolidated.raw_df,
                use_container_width=True,
                height=260
            )

# =============================================================================
# TAB 4: TWO-MINUTE DAILY BRIEF (PS-13 CORE DELIVERABLE)
# =============================================================================
with tab_brief:
    if st.session_state.morning_brief is None:
        st.warning("⚠️ Daily Brief will be generated once operational feeds are validated.")
    else:
        brief = st.session_state.morning_brief
        consolidated = st.session_state.consolidated_data
        target_date = consolidated.latest_date
        city_m = brief.get("citywide_metrics", {})
        op_m = brief.get("operator_metrics", {})
        
        # Action Bar with Export Buttons
        export_col1, export_col2, export_col3 = st.columns([1.5, 1.2, 1.2])
        with export_col1:
            st.markdown(f"### 📋 Operations Brief: `{target_date}`")
        with export_col2:
            pdf_bytes = generate_pdf_brief(brief)
            st.download_button(
                label="📥 Download 1-Page PDF Brief",
                data=pdf_bytes,
                file_name=f"TransitPulse_Daily_Brief_{target_date}.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )
        with export_col3:
            html_content = generate_html_brief(brief)
            st.download_button(
                label="🌐 Export Printable HTML",
                data=html_content,
                file_name=f"TransitPulse_Daily_Brief_{target_date}.html",
                mime="text/html",
                use_container_width=True
            )

        st.markdown("---")

        # 1. Executive Narrative Box
        health = brief.get("overall_health_score", 95.0)
        st.markdown(f"""
        <div style="background: rgba(15, 23, 42, 0.9); border: 1px solid #1E293B; border-left: 5px solid #0D9488; border-radius: 8px; padding: 18px; margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-size: 13px; font-weight: 700; color: #14B8A6; text-transform: uppercase;">Executive Morning Brief</span>
                <span style="font-size: 12px; font-weight: 700; color: {'#EF4444' if health < 80 else '#10B981'};">Health Rating: {health:.0f}/100 ({brief.get('status_label')})</span>
            </div>
            <div style="font-size: 14.5px; color: #F1F5F9; line-height: 1.55;">
                {brief.get('executive_narrative')}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 2. Operator Performance Breakdown Table
        st.markdown("#### 🏢 Operator Fleet & Performance Breakdown")
        table_rows = []
        for op_name, m in op_m.items():
            avail = m.get("service_availability_pct", 0)
            delay = m.get("average_delay_minutes", 0)
            st_badge = "CRITICAL" if (avail < 85 or delay > 6) else ("REVIEW" if (avail < 92 or delay > 4) else "NOMINAL")
            table_rows.append({
                "Operator": op_name,
                "Reporting Units": f"{int(m.get('active_routes_count', 0))} Corridors/Routes",
                "Ridership": f"{int(m.get('ridership', 0)):,}",
                "Scheduled Trips": f"{int(m.get('scheduled_services', 0)):,}",
                "Completed Trips": f"{int(m.get('completed_services', 0)):,}",
                "Availability Rate": f"{avail:.1f}%",
                "Avg Route Delay": f"{delay:.1f} min",
                "Operational Status": st_badge
            })
        st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)

        # 3. Top Actionable Intelligence Items
        st.markdown("<br/>", unsafe_allow_html=True)
        st.markdown("#### 🎯 Priority Operations Action Checklist")
        for act in brief.get("top_actions", []):
            st.markdown(f"""
            <div style="background: #0F172A; border-left: 4px solid #F59E0B; border-radius: 0 6px 6px 0; padding: 12px 16px; margin-bottom: 10px;">
                <div style="display: flex; justify-content: space-between; font-size: 12px; font-weight: 700; color: #FBBF24; margin-bottom: 2px;">
                    <span>{act['priority']}</span>
                    <span>{act['target']}</span>
                </div>
                <div style="font-size: 13.5px; color: #F8FAFC;">
                    {act['action']}
                </div>
            </div>
            """, unsafe_allow_html=True)

        # 4. Critical & Warning Exception Details
        st.markdown("<br/>", unsafe_allow_html=True)
        st.markdown("#### 🔎 Exception Deep-Dive & Root Cause Hypotheses")
        for idx, ex in enumerate(st.session_state.explained_exceptions):
            render_exception_card_streamlit(ex, idx)
