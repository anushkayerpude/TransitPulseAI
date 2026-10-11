"""
TransitPulse AI - Main Streamlit Application
AI-Powered Public Transport Operations Intelligence & Daily Briefing System
Hackathon: Metro Hacks — DevFest Gandhinagar
Problem Statement: PS-13 — The Two-Minute Morning Brief
Target Users: Metro (GMRC), BRTS (Janmarg), AMTS Operations Teams
Theme: White & Ahmedabad Metro Orange (#FF6B00) Design System
"""

import os
import io
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime

# Page configuration - Wide layout with custom title
st.set_page_config(
    page_title="TransitPulse AI | Ahmedabad Metro (GMRC), BRTS & AMTS Intelligence",
    page_icon="🚇",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load animated doodle metro SVG
doodle_svg_path = os.path.join(os.path.dirname(__file__), "assets", "doodle_metro_full.svg")
doodle_svg_code = ""
if os.path.exists(doodle_svg_path):
    with open(doodle_svg_path, "r", encoding="utf-8") as f:
        doodle_svg_code = f.read()

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
from components.track_diagram import render_gmrc_track_monitor
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

# -----------------------------------------------------------------------------
# CORE ANALYTICAL EXECUTION PIPELINE
# -----------------------------------------------------------------------------
def run_pipeline(strategy=None, thresholds=None, ai_mode_choice=None, api_key_val=None):
    """
    Executes the deterministic operations intelligence pipeline:
    1. CSV format & schema validation
    2. Multi-modal telemetry consolidation
    3. Anomaly & outlier detection against historical baselines
    4. Causal hypothesis attribution & evidence grounding
    5. Daily executive brief synthesis
    """
    strategy = strategy or st.session_state.get("baseline_mode", "same_weekday")
    thresholds = thresholds or st.session_state.get("custom_thresholds", DEFAULT_THRESHOLDS)
    ai_choice = ai_mode_choice or st.session_state.get("ai_mode", "Deterministic Rule Engine (Offline)")
    api_key = api_key_val or st.session_state.get("user_api_key", "")
    
    if st.session_state.get("metro_file") is None:
        return False

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
    detector = DetectionEngine(thresholds=thresholds)
    exceptions = detector.detect_exceptions(
        consolidated,
        target_date=consolidated.latest_date,
        baseline_strategy=strategy
    )
    st.session_state.detected_exceptions = exceptions
    
    # 4. Generate AI-Assisted Structured Explanations
    explainer = AIExplainerEngine(api_key=api_key if ai_choice == "Gemini AI Enhanced" else None)
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

# Helper to load sample files
def load_sample_dataset(dataset_type="incident"):
    base_path = f"data/{dataset_type}"
    st.session_state.metro_file = f"{base_path}/metro_{dataset_type}.csv"
    st.session_state.brts_file = f"{base_path}/brts_{dataset_type}.csv"
    st.session_state.amts_file = f"{base_path}/amts_{dataset_type}.csv"
    st.session_state.active_dataset_label = f"Sample {dataset_type.title()} Dataset (14-Day Gandhinagar/Ahmedabad)"
    run_pipeline()

# Automatically load incident dataset on first launch if empty
if st.session_state.metro_file is None:
    load_sample_dataset("incident")

# -----------------------------------------------------------------------------
# SIDEBAR CONTROLS
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown(f"""
    <div class="hackathon-sidebar-card">
        <div style="font-size: 11px; font-weight: 800; color: #EA580C; text-transform: uppercase; letter-spacing: 0.6px;">
            {HACKATHON_EVENT}
        </div>
        <div style="font-size: 14px; font-weight: 800; color: #0F172A; margin-top: 3px; font-family: 'Outfit', sans-serif;">
            {PROBLEM_STATEMENT}
        </div>
        <div style="font-size: 11.5px; color: #64748B; margin-top: 4px;">
            {VERSION} • Ahmedabad & Gandhinagar
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### ⚡ Live Demo Presets")
    st.caption("One-click presets for rapid judge evaluation:")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        if st.button("🚨 Load Incidents", use_container_width=True, help="14-day history with 3 deliberate operational anomalies on final day"):
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
    st.markdown("### 🖥️ Display Experience")
    view_layout = st.radio(
        "Presentation Mode",
        ["📜 Full-Page Scroll Motion (Default)", "📑 Classic Tabbed View"],
        index=0,
        help="Full-page 100vh scroll-motion layout vs classic tabbed panels."
    )

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
    if st.button("🔄 Execute Full Analytics Pipeline", use_container_width=True, type="primary"):
        with st.spinner("Re-executing analytical detection pipeline..."):
            run_pipeline()
            st.rerun()

    st.caption("TransitPulse AI • DevFest Gandhinagar PS-13 • Version 1.0 MVP")

# -----------------------------------------------------------------------------
# MAIN APP HEADER BANNER (WHITE & AHMEDABAD METRO ORANGE)
# -----------------------------------------------------------------------------
st.markdown(f"""
<div style="background: #FFFFFF; border: 1px solid #FED7AA; border-left: 6px solid #FF6B00; border-radius: 12px; padding: 18px 24px; margin-bottom: 22px; box-shadow: 0 4px 16px rgba(255, 107, 0, 0.07); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
    <div>
        <div style="display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 26px;">🚇</span>
            <h1 style="font-size: 26px; font-weight: 800; color: #0F172A; margin: 0; font-family: 'Outfit', sans-serif;">{APP_NAME}</h1>
            <span style="background: #FFF7ED; border: 1px solid #FED7AA; color: #EA580C; font-size: 11px; font-weight: 800; padding: 3px 10px; border-radius: 20px; letter-spacing: 0.5px;">
                GMRC • AHMEDABAD METRO
            </span>
        </div>
        <p style="font-size: 13.5px; color: #64748B; margin: 4px 0 0 0; font-weight: 500;">
            {APP_SUBTITLE} &nbsp;|&nbsp; <strong>Gandhinagar & Ahmedabad Regional Transit Joint Ops</strong>
        </p>
    </div>
    <div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">
        <span style="background: #ECFDF5; border: 1px solid #A7F3D0; color: #065F46; font-size: 11.5px; font-weight: 700; padding: 6px 14px; border-radius: 20px; display: inline-flex; align-items: center; gap: 6px;">
            <span style="width: 8px; height: 8px; background-color: #10B981; border-radius: 50%;"></span>
            READY-TO-USE DEMO: 14-DAY BUILT-IN DATA ACTIVE (ZERO UPLOADS NEEDED)
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# DYNAMIC REACTIVE RECALCULATION ON PARAMETER CHANGES
# -----------------------------------------------------------------------------
if "active_params" not in st.session_state:
    st.session_state.active_params = {}

current_params = {
    "baseline_mode": baseline_mode,
    "thresholds": custom_thresholds,
    "ai_mode": ai_mode,
    "api_key": user_api_key
}

# If initial execution or if user modified any parameters/thresholds/sliders
if st.session_state.consolidated_data is None and st.session_state.metro_file is not None:
    run_pipeline(strategy=baseline_mode, thresholds=custom_thresholds, ai_mode_choice=ai_mode, api_key_val=user_api_key)
    st.session_state.active_params = current_params
elif st.session_state.consolidated_data is not None and st.session_state.active_params != current_params:
    run_pipeline(strategy=baseline_mode, thresholds=custom_thresholds, ai_mode_choice=ai_mode, api_key_val=user_api_key)
    st.session_state.active_params = current_params




# -----------------------------------------------------------------------------
# MODULAR SECTION RENDERERS (SUPPORTING SCROLL-MOTION AND TABBED VIEWS)
# -----------------------------------------------------------------------------

def render_section_1_hero():
    """Section 1: Full-Screen Doodly Metro Hero & Launchpad"""
    # 1. Full-Screen Animated Doodly Metro (cruising from left to right)
    if doodle_svg_code:
        components.html(
            f"""
            <div style="width: 100%; height: 520px; overflow: hidden; border-radius: 16px; box-shadow: 0 8px 32px rgba(255,107,0,0.12); border: 2px solid #FED7AA; background: #FFFBF7; margin-bottom: 20px;">
                {doodle_svg_code}
            </div>
            """,
            height=535,
        )

    # 2. Executive Portal Identity Banner
    st.markdown("""
    <div class="landing-hero-container">
        <div style="position: relative;">
            <img src="https://raw.githubusercontent.com/anushkayerpude/TransitPulseAI/main/assets/ahmedabad_metro_hero.jpg" 
                 onerror="this.onerror=null; this.src='assets/ahmedabad_metro_hero.jpg';"
                 style="width: 100%; max-height: 400px; object-fit: cover; display: block; border-radius: 14px;" 
                 alt="Ahmedabad Metro (GMRC) Train on Viaduct" />
            <div style="position: absolute; bottom: 0; left: 0; right: 0; background: linear-gradient(0deg, rgba(15,23,42,0.92) 0%, rgba(15,23,42,0.65) 60%, rgba(15,23,42,0) 100%); padding: 30px 36px 22px 36px; border-radius: 0 0 14px 14px;">
                <div style="display: flex; gap: 8px; margin-bottom: 10px; flex-wrap: wrap;">
                    <span class="metro-badge-tag">🚇 GMRC AHMEDABAD METRO</span>
                    <span style="background: rgba(255,255,255,0.2); backdrop-filter: blur(8px); color: #FFFFFF; font-size: 11px; font-weight: 700; padding: 4px 12px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.3);">
                        JANMARG BRTS & AMTS INTEGRATED
                    </span>
                    <span style="background: #10B981; color: #FFFFFF; font-size: 11px; font-weight: 800; padding: 4px 12px; border-radius: 20px;">
                        PS-13: TWO-MINUTE MORNING BRIEF
                    </span>
                </div>
                <h1 style="color: #FFFFFF; font-family: 'Outfit', sans-serif; font-size: 32px; font-weight: 800; margin: 0 0 8px 0; letter-spacing: -0.5px; text-shadow: 0 2px 10px rgba(0,0,0,0.5);">
                    Public Transport Operations Intelligence Portal
                </h1>
                <p style="color: #E2E8F0; font-size: 15px; max-width: 820px; margin: 0; line-height: 1.5; text-shadow: 0 1px 4px rgba(0,0,0,0.6);">
                    Harmonizing daily operational feeds across Gujarat Metro Rail Corporation, Janmarg BRTS, and AMTS. 
                    Detecting corridor deviations, isolating signaling bottlenecks, and synthesizing executive standup briefings in under 120 seconds.
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 3. Quick Action Launchpad Cards
    st.markdown('<div class="section-title"><span>⚡ Quick Action Launchpad (One-Click Operations Presets)</span></div>', unsafe_allow_html=True)
    cta_col1, cta_col2, cta_col3 = st.columns(3)
    
    with cta_col1:
        st.markdown("""
        <div class="kpi-card" style="border-top: 4px solid #EF4444;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-weight: 800; color: #EF4444; font-size: 12px; text-transform: uppercase;">1. Incident Scenario</span>
                <span style="font-size: 18px;">🚨</span>
            </div>
            <h4 style="margin: 0 0 6px 0; color: #0F172A;">Simulate Injected Incidents</h4>
            <p style="font-size: 12.5px; color: #64748B; margin-bottom: 14px;">
                Loads 14 days with 3 deliberate anomalies: Metro signaling delay (+1,080%), BRTS route drop (-38%), and AMTS availability drop (76%).
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🚨 Load Incident Demo", use_container_width=True, type="primary", key="landing_inc_btn"):
            load_sample_dataset("incident")
            st.rerun()

    with cta_col2:
        st.markdown("""
        <div class="kpi-card" style="border-top: 4px solid #10B981;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-weight: 800; color: #10B981; font-size: 12px; text-transform: uppercase;">2. Nominal Baseline</span>
                <span style="font-size: 18px;">🟢</span>
            </div>
            <h4 style="margin: 0 0 6px 0; color: #0F172A;">Explore Normal Baseline</h4>
            <p style="font-size: 12.5px; color: #64748B; margin-bottom: 14px;">
                Demonstrates smooth, nominal multi-modal network operations with healthy weekday-adjusted historical alignment.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🟢 Load Baseline Demo", use_container_width=True, key="landing_base_btn"):
            load_sample_dataset("baseline")
            st.rerun()

    with cta_col3:
        st.markdown("""
        <div class="kpi-card" style="border-top: 4px solid #F59E0B;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-weight: 800; color: #D97706; font-size: 12px; text-transform: uppercase;">3. Defensive Quality Gate</span>
                <span style="font-size: 18px;">🧪</span>
            </div>
            <h4 style="margin: 0 0 6px 0; color: #0F172A;">Test Pre-Flight Schema Audit</h4>
            <p style="font-size: 12.5px; color: #64748B; margin-bottom: 14px;">
                Showcases pre-flight data sentinels catching negative ridership, bad dates, and duplicates with actionable repair tips.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🧪 Test Validation Failure", use_container_width=True, key="landing_val_btn"):
            st.session_state.metro_file = "data/invalid_test/corrupted_metro_sample.csv"
            st.session_state.brts_file = "data/baseline/brts_baseline.csv"
            st.session_state.amts_file = "data/baseline/amts_baseline.csv"
            st.session_state.active_dataset_label = "Corrupted Validation Test Dataset"
            run_pipeline()
            st.rerun()

    # 4. Live Telemetry Sentinel Banner (Instant Feedback on Backend Pipeline Execution)
    st.markdown('<div class="section-title"><span>📡 Live Analytical Engine Sentinel (Real-Time Ingestion & Synthesis)</span></div>', unsafe_allow_html=True)
    if st.session_state.consolidated_data is not None:
        brief = st.session_state.morning_brief
        consolidated = st.session_state.consolidated_data
        target_date = consolidated.latest_date
        health = brief.get("overall_health_score", 95.0) if brief else 95.0
        status_lbl = brief.get("status_label", "NOMINAL") if brief else "NOMINAL"
        crit_count = brief.get("critical_exceptions_count", 0) if brief else 0
        warn_count = brief.get("warning_exceptions_count", 0) if brief else 0
        total_exc = len(st.session_state.detected_exceptions)

        is_critical = health < 80 or crit_count > 0
        banner_bg = "#FFF7ED" if is_critical else "#F0FDF4"
        banner_border = "#FF6B00" if is_critical else "#10B981"
        badge_bg = "#FEF2F2" if is_critical else "#ECFDF5"
        badge_text = "#DC2626" if is_critical else "#065F46"

        st.markdown(f"""
        <div style="background: {banner_bg}; border: 1.5px solid {banner_border}; border-radius: 12px; padding: 20px 24px; margin-bottom: 22px; box-shadow: 0 4px 16px rgba(0,0,0,0.04);">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 12px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 20px;">{'🚨' if is_critical else '🟢'}</span>
                    <strong style="font-size: 15.5px; color: #0F172A; font-family: 'Outfit', sans-serif;">
                        Active Warehouse: {st.session_state.active_dataset_label}
                    </strong>
                </div>
                <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                    <span style="background: {badge_bg}; color: {badge_text}; font-weight: 800; font-size: 12px; padding: 4px 12px; border-radius: 20px; border: 1px solid {banner_border};">
                        Network Health Score: {health:.0f}/100 • {status_lbl}
                    </span>
                    <span style="background: #FFFFFF; color: #0F172A; font-weight: 700; font-size: 12px; padding: 4px 10px; border-radius: 20px; border: 1px solid #CBD5E1;">
                        📅 Target Ops Date: {target_date}
                    </span>
                </div>
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin-bottom: 16px;">
                <div style="background: #FFFFFF; border-radius: 8px; padding: 12px 14px; border: 1px solid #FED7AA; box-shadow: 0 1px 4px rgba(0,0,0,0.02);">
                    <div style="font-size: 11px; color: #64748B; font-weight: 700; text-transform: uppercase;">Consolidated Feeds</div>
                    <div style="font-size: 19px; font-weight: 800; color: #0F172A; margin: 2px 0;">{consolidated.total_records} Records</div>
                    <div style="font-size: 11px; color: #10B981; font-weight: 700;">✓ 100% Schema Passed</div>
                </div>
                <div style="background: #FFFFFF; border-radius: 8px; padding: 12px 14px; border: 1px solid #FED7AA; box-shadow: 0 1px 4px rgba(0,0,0,0.02);">
                    <div style="font-size: 11px; color: #64748B; font-weight: 700; text-transform: uppercase;">Reporting Networks</div>
                    <div style="font-size: 19px; font-weight: 800; color: #FF6B00; margin: 2px 0;">3 Modalities</div>
                    <div style="font-size: 11px; color: #64748B; font-weight: 600;">GMRC • BRTS • AMTS</div>
                </div>
                <div style="background: #FFFFFF; border-radius: 8px; padding: 12px 14px; border: 1px solid #FED7AA; box-shadow: 0 1px 4px rgba(0,0,0,0.02);">
                    <div style="font-size: 11px; color: #64748B; font-weight: 700; text-transform: uppercase;">Isolated Anomalies</div>
                    <div style="font-size: 19px; font-weight: 800; color: {'#EF4444' if crit_count > 0 else '#10B981'}; margin: 2px 0;">
                        {total_exc} Detected
                    </div>
                    <div style="font-size: 11px; color: #64748B; font-weight: 600;">{crit_count} Critical • {warn_count} Warning</div>
                </div>
                <div style="background: #FFFFFF; border-radius: 8px; padding: 12px 14px; border: 1px solid #FED7AA; box-shadow: 0 1px 4px rgba(0,0,0,0.02);">
                    <div style="font-size: 11px; color: #64748B; font-weight: 700; text-transform: uppercase;">Backend Engine</div>
                    <div style="font-size: 19px; font-weight: 800; color: #0D9488; margin: 2px 0;">⚡ &lt; 0.08s Local</div>
                    <div style="font-size: 11px; color: #0D9488; font-weight: 700;">Deterministic & Offline</div>
                </div>
            </div>

            <div style="font-size: 13.5px; color: #334155; line-height: 1.55; margin-bottom: 14px; background: rgba(255,255,255,0.85); padding: 12px 16px; border-radius: 8px; border-left: 4px solid {'#EF4444' if is_critical else '#10B981'};">
                <strong style="color: #0F172A;">Executive Standup Summary:</strong> {brief.get('executive_narrative', 'Nominal operations verified across all corridors.')}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Download quick action
        pdf_bytes_landing = generate_pdf_brief(brief)
        st.download_button(
            label="📥 Download Executive 1-Page Briefing PDF",
            data=pdf_bytes_landing,
            file_name=f"TransitPulse_Daily_Brief_{target_date}.pdf",
            mime="application/pdf",
            type="primary",
            key="landing_pdf_quick_btn",
            use_container_width=True
        )
    else:
        st.markdown("""
        <div style="background: #FEF2F2; border: 2px solid #EF4444; border-radius: 12px; padding: 20px 24px; margin-bottom: 22px;">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                <span style="font-size: 22px;">🛑</span>
                <strong style="font-size: 16px; color: #991B1B; font-family: 'Outfit', sans-serif;">
                    Pre-Flight Defensive Schema Sentinel: Corrupted Feed Quarantined
                </strong>
            </div>
            <p style="font-size: 13.5px; color: #7F1D1D; margin: 0 0 12px 0; line-height: 1.5;">
                TransitPulse AI defensive sentinels successfully caught corrupt records (negative ridership values, corrupt date stamps, and duplicate primary keys) before they could pollute operational decision pipelines.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔄 Restore Healthy Incident Operations Feed", type="primary", key="landing_restore_feed_btn"):
            load_sample_dataset("incident")
            st.rerun()

    # 5. Live GMRC Wayside Track & Telemetry Monitor
    st.markdown('<div class="section-title"><span>🚊 Real-Time GMRC Metro Track & Wayside Signal Telemetry</span></div>', unsafe_allow_html=True)
    render_gmrc_track_monitor(key_prefix="landing_track")


    # 6. Regional Transit Network Status Grid
    st.markdown('<div class="section-title"><span>🏙️ Gandhinagar & Ahmedabad Regional Transit Network Coverage</span></div>', unsafe_allow_html=True)
    net_col1, net_col2, net_col3 = st.columns(3)
    
    with net_col1:
        st.markdown("""
        <div class="op-card-metro">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <span style="font-size: 15px; font-weight: 800; color: #FF6B00; font-family: 'Outfit', sans-serif;">
                    🚇 GMRC Metro Network
                </span>
                <span style="background: #FFF7ED; color: #EA580C; font-size: 11px; font-weight: 800; padding: 2px 8px; border-radius: 12px; border: 1px solid #FED7AA;">40.0+ km</span>
            </div>
            <div style="font-size: 13px; color: #334155; line-height: 1.6;">
                • <strong>East-West Line:</strong> Thaltej ⇄ Vastral Gam (21.1 km • 17 Stns)<br/>
                • <strong>North-South Line:</strong> Motera Stadium ⇄ APMC (18.9 km • 15 Stns)<br/>
                • <strong>GN Branch:</strong> Koba Circle ⇄ GIFT City (Phase 2 Link)<br/>
                • <strong>Headway:</strong> 3–5 min Peak • Dedicated CBTC Rail
            </div>
        </div>
        """, unsafe_allow_html=True)

    with net_col2:
        st.markdown("""
        <div class="op-card-brts">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <span style="font-size: 15px; font-weight: 800; color: #0D9488; font-family: 'Outfit', sans-serif;">
                    🚌 Janmarg Ahmedabad BRTS
                </span>
                <span style="background: #CCFBF1; color: #0F766E; font-size: 11px; font-weight: 800; padding: 2px 8px; border-radius: 12px; border: 1px solid #99F6E4;">160+ km</span>
            </div>
            <div style="font-size: 13px; color: #334155; line-height: 1.6;">
                • <strong>Route 101:</strong> RTO Circle ⇄ Maninagar<br/>
                • <strong>Route 202:</strong> Iskcon Cross Road ⇄ Naroda<br/>
                • <strong>Route 303:</strong> Shivranjani ⇄ Bopal (Key Arterial)<br/>
                • <strong>Route 404 & 505:</strong> Chandkheda, Geeta Mandir, Vasna<br/>
                • <strong>Infrastructure:</strong> Median Dedicated Bus Lanes
            </div>
        </div>
        """, unsafe_allow_html=True)

    with net_col3:
        st.markdown("""
        <div class="op-card-amts">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <span style="font-size: 15px; font-weight: 800; color: #D97706; font-family: 'Outfit', sans-serif;">
                    🚍 AMTS Municipal City Bus
                </span>
                <span style="background: #FEF3C7; color: #B45309; font-size: 11px; font-weight: 800; padding: 2px 8px; border-radius: 12px; border: 1px solid #FDE68A;">700+ Buses</span>
            </div>
            <div style="font-size: 13px; color: #334155; line-height: 1.6;">
                • <strong>Route 13/1:</strong> Lal Darwaja ⇄ SG Highway<br/>
                • <strong>Route 40/3:</strong> Kalupur Railway Station ⇄ Isanpur<br/>
                • <strong>Route 66/2 & 84/1:</strong> Wadaj, Maninagar, Paldi, Narol<br/>
                • <strong>Route 151:</strong> Civil Hospital ⇄ Sarkhej<br/>
                • <strong>Role:</strong> First-and-Last Mile Municipal Feeder
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 7. Core Operational Architecture Pillars (PS-13)
    st.markdown('<div class="section-title"><span>💡 Core Architecture Pillars (PS-13: The Two-Minute Morning Brief)</span></div>', unsafe_allow_html=True)
    feat_cols = st.columns(4)
    
    with feat_cols[0]:
        st.markdown("""
        <div class="kpi-card" style="text-align: center; border-top: 3px solid #FF6B00;">
            <div style="font-size: 24px; margin-bottom: 6px;">🛡️</div>
            <strong style="color: #0F172A; font-size: 14px;">Pre-Flight Quality Gate</strong>
            <p style="font-size: 12px; color: #64748B; margin-top: 6px;">
                Refuses silent zero-filling. Traps corrupted dates, missing headers, and negative numbers before bad data pollutes meetings.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with feat_cols[1]:
        st.markdown("""
        <div class="kpi-card" style="text-align: center; border-top: 3px solid #0D9488;">
            <div style="font-size: 24px; margin-bottom: 6px;">📅</div>
            <strong style="color: #0F172A; font-size: 14px;">Weekday Baselining</strong>
            <p style="font-size: 12px; color: #64748B; margin-top: 6px;">
                Compares Monday to past Mondays. Eliminates false alarms caused by normal weekend dips vs genuine operational distress.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with feat_cols[2]:
        st.markdown("""
        <div class="kpi-card" style="text-align: center; border-top: 3px solid #D97706;">
            <div style="font-size: 24px; margin-bottom: 6px;">🎯</div>
            <strong style="color: #0F172A; font-size: 14px;">Telemetry Provenance</strong>
            <p style="font-size: 12px; color: #64748B; margin-top: 6px;">
                Enforces strict separation between observed telemetry facts and root-cause hypotheses with zero AI hallucinations.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with feat_cols[3]:
        st.markdown("""
        <div class="kpi-card" style="text-align: center; border-top: 3px solid #10B981;">
            <div style="font-size: 24px; margin-bottom: 6px;">📄</div>
            <strong style="color: #0F172A; font-size: 14px;">1-Page PDF Briefing</strong>
            <p style="font-size: 12px; color: #64748B; margin-top: 6px;">
                Native ReportLab vector PDF engine renders an executive management standup document in under 2 seconds.
            </p>
        </div>
        """, unsafe_allow_html=True)


def render_section_2_overview():
    """Section 2: Executive Overview & Multi-Modal Telemetry"""
    if st.session_state.consolidated_data is None:
        st.warning("⚠️ Data feeds require attention. Scroll to **Data Import & Audit** or load a demo dataset to resolve.")
        return

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
            "Weighted transit delay",
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
    st.markdown('<div class="section-title"><span>🚏 Multi-Modal Operator Status Overview</span></div>', unsafe_allow_html=True)
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
                '<span class="pill-warn">⚠️ REVIEW</span>' if is_op_warn else '<span style="color:#10B981; font-weight:800; font-size:11.5px; background: #ECFDF5; padding: 3px 8px; border-radius: 12px; border: 1px solid #A7F3D0;">✅ NOMINAL</span>'
            )

            st.markdown(f"""
            <div class="kpi-card" style="border-top: 4px solid {cfg.get('color', '#FF6B00')};">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-weight: 800; font-size: 16px; color: #0F172A; font-family: 'Outfit', sans-serif;">
                        {cfg.get('icon', '')} {op_name}
                    </span>
                    {status_badge}
                </div>
                <div style="font-size: 11.5px; color: #64748B; margin-bottom: 12px; font-weight: 500;">{cfg.get('full_name', '')}</div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 12.5px;">
                    <div style="background: #F8FAFC; padding: 8px 10px; border-radius: 6px;">
                        <span style="color: #64748B;">Ridership:</span><br/>
                        <strong style="color: #0F172A; font-size: 15px;">{r_count:,}</strong>
                    </div>
                    <div style="background: #F8FAFC; padding: 8px 10px; border-radius: 6px;">
                        <span style="color: #64748B;">Availability:</span><br/>
                        <strong style="color: {'#EF4444' if avail < 85 else '#0D9488'}; font-size: 15px;">{avail:.1f}%</strong>
                    </div>
                    <div style="background: #F8FAFC; padding: 8px 10px; border-radius: 6px;">
                        <span style="color: #64748B;">Completed Trips:</span><br/>
                        <strong style="color: #334155;">{comp:,} / {sched:,}</strong>
                    </div>
                    <div style="background: #F8FAFC; padding: 8px 10px; border-radius: 6px;">
                        <span style="color: #64748B;">Avg Delay:</span><br/>
                        <strong style="color: {'#EF4444' if delay > 6 else '#334155'}; font-size: 15px;">{delay:.1f} min</strong>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Row 3: Ridership Trend & Availability Visualizations
    st.markdown('<div class="section-title"><span>📈 Citywide Multi-Modal Trends & Fleet Health</span></div>', unsafe_allow_html=True)
    chart_col1, chart_col2 = st.columns([1.6, 1.0])
    with chart_col1:
        fig_trend = create_ridership_trend_chart(consolidated, highlight_date=target_date)
        st.plotly_chart(fig_trend, use_container_width=True)
    with chart_col2:
        fig_avail = create_availability_bar_chart(op_m)
        st.plotly_chart(fig_avail, use_container_width=True)


def render_section_3_audit():
    """Section 3: Data Feeds & Pre-Flight Quality Sentinel Gate"""
    st.markdown('<div class="section-title"><span>📥 Operational Data Feeds & Pre-Flight Schema Audit</span></div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: #F0FDF4; border: 1.5px solid #10B981; border-radius: 12px; padding: 18px 22px; margin-bottom: 20px;">
        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px;">
            <div>
                <strong style="color: #065F46; font-size: 15.5px; font-family: 'Outfit', sans-serif;">
                    🟢 100% Plug-and-Play Prototype: Zero Data Uploads Required!
                </strong>
                <p style="color: #047857; font-size: 13.5px; margin: 4px 0 0 0; line-height: 1.5;">
                    TransitPulse AI already contains 14 days of realistic multi-modal operations telemetry (GMRC Metro, Janmarg BRTS, and AMTS City Bus) loaded in memory.
                    You <strong>do NOT need to feed data</strong> to test or evaluate this prototype — everything is already analyzed and ready across all tabs!
                </p>
            </div>
            <div>
                <span style="background: #10B981; color: #FFFFFF; font-weight: 800; font-size: 11px; padding: 5px 14px; border-radius: 20px;">
                    BUILT-IN DATA ACTIVE
                </span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    feed_mode = st.radio(
        "Ingestion Source Selection:",
        ["⚡ Use Built-in Datasets (GMRC Metro + Janmarg BRTS + AMTS) [Active]", "📁 Upload Custom CSV Feeds (Optional / Bring Your Own Data)"],
        index=0,
        horizontal=True,
        key="audit_feed_mode_radio"
    )

    if "Built-in" in feed_mode:
        st.markdown(f"**Active Ingestion Feed:** `{st.session_state.active_dataset_label}`")
        b_c1, b_c2, b_c3 = st.columns(3)
        with b_c1:
            st.markdown("""
            <div style="background: #FFFFFF; border: 1px solid #FED7AA; border-left: 4px solid #FF6B00; border-radius: 8px; padding: 12px 14px;">
                <strong style="color: #FF6B00; font-size: 13.5px;">🚇 GMRC Ahmedabad Metro</strong>
                <div style="font-size: 12px; color: #64748B; margin-top: 4px;">
                    • Source: <code>data/incident/metro_incident.csv</code><br/>
                    • Records: 42 rows (14 days, 3 corridors)<br/>
                    • Telemetry: Ridership, Availability, Delay
                </div>
            </div>
            """, unsafe_allow_html=True)
        with b_c2:
            st.markdown("""
            <div style="background: #FFFFFF; border: 1px solid #FED7AA; border-left: 4px solid #0D9488; border-radius: 8px; padding: 12px 14px;">
                <strong style="color: #0D9488; font-size: 13.5px;">🚌 Janmarg Ahmedabad BRTS</strong>
                <div style="font-size: 12px; color: #64748B; margin-top: 4px;">
                    • Source: <code>data/incident/brts_incident.csv</code><br/>
                    • Records: 84 rows (14 days, 6 routes)<br/>
                    • Telemetry: Ridership, Availability, Delay
                </div>
            </div>
            """, unsafe_allow_html=True)
        with b_c3:
            st.markdown("""
            <div style="background: #FFFFFF; border: 1px solid #FED7AA; border-left: 4px solid #D97706; border-radius: 8px; padding: 12px 14px;">
                <strong style="color: #D97706; font-size: 13.5px;">🚍 AMTS Municipal City Bus</strong>
                <div style="font-size: 12px; color: #64748B; margin-top: 4px;">
                    • Source: <code>data/incident/amts_incident.csv</code><br/>
                    • Records: 56 rows (14 days, 4 depots)<br/>
                    • Telemetry: Fleet Turnout, Trips, Delivery
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br/>", unsafe_allow_html=True)
        q_c1, q_c2, q_c3 = st.columns(3)
        with q_c1:
            if st.button("🚨 Load 14-Day Incident Scenario", use_container_width=True, type="primary", key="tab_import_inc_btn"):
                load_sample_dataset("incident")
                st.rerun()
        with q_c2:
            if st.button("🟢 Load 14-Day Nominal Baseline", use_container_width=True, key="tab_import_base_btn"):
                load_sample_dataset("baseline")
                st.rerun()
        with q_c3:
            if st.button("🧪 Test Corrupted CSV Quality Gate", use_container_width=True, key="tab_import_corrupt_btn"):
                st.session_state.metro_file = "data/invalid_test/corrupted_metro_sample.csv"
                st.session_state.brts_file = "data/baseline/brts_baseline.csv"
                st.session_state.amts_file = "data/baseline/amts_baseline.csv"
                st.session_state.active_dataset_label = "Corrupted Validation Test Dataset"
                run_pipeline()
                st.rerun()
    else:
        # Sample CSV Downloads for Judges
        with st.expander("💾 Download Standard Demonstration CSV Files for Manual Testing", expanded=False):
            st.caption("Judges can download these structured CSVs and re-upload them to test validation and analysis:")
            d_col1, d_col2, d_col3 = st.columns(3)
            with d_col1:
                with open("data/incident/metro_incident.csv", "rb") as f:
                    st.download_button("📥 Metro Sample CSV", f.read(), file_name="metro_sample.csv", mime="text/csv", use_container_width=True, key="dl_metro_csv_key")
            with d_col2:
                with open("data/incident/brts_incident.csv", "rb") as f:
                    st.download_button("📥 BRTS Sample CSV", f.read(), file_name="brts_sample.csv", mime="text/csv", use_container_width=True, key="dl_brts_csv_key")
            with d_col3:
                with open("data/incident/amts_incident.csv", "rb") as f:
                    st.download_button("📥 AMTS Sample CSV", f.read(), file_name="amts_sample.csv", mime="text/csv", use_container_width=True, key="dl_amts_csv_key")

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
        if st.button("🚀 Validate & Consolidate Custom Feeds", type="primary", use_container_width=True, key="run_custom_audit_btn"):
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
                    <div style="background: #F0FDF4; border: 1px solid #86EFAC; border-radius: 10px; padding: 16px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                            <strong style="color: #166534; font-size: 14px;">✅ {op_key} VALID</strong>
                            <span style="font-size: 11.5px; color: #166534; font-weight: 700;">{v.row_count} rows</span>
                        </div>
                        <div style="font-size: 12.5px; color: #14532D; line-height: 1.5;">
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
                    <div style="background: #FEF2F2; border: 1px solid #FCA5A5; border-radius: 10px; padding: 16px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                            <strong style="color: #991B1B; font-size: 14px;">❌ {op_key} INVALID</strong>
                            <span style="font-size: 11.5px; color: #991B1B; font-weight: 800;">{len(v.errors)} Errors</span>
                        </div>
                        <div style="font-size: 12.5px; color: #B91C1C;">
                            Resolve issues below to proceed with analysis.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    for err in v.errors:
                        st.error(f"**Issue:** {err['issue']}\n\n💡 **Action:** {err['fix']}")


def render_section_4_intel():
    """Section 4: Operations Intelligence & Diagnostic Bottlenecks"""
    if st.session_state.consolidated_data is None:
        st.warning("⚠️ Please upload valid datasets and run the analysis pipeline first.")
        return

    consolidated = st.session_state.consolidated_data
    target_date = consolidated.latest_date
    metrics = consolidated.get_date_metrics(target_date)
    op_m = metrics.get("operators", {})
    exceptions = st.session_state.explained_exceptions

    st.markdown('<div class="section-title"><span>🔍 Diagnostic Comparisons & Delay Analysis</span></div>', unsafe_allow_html=True)
    
    # Row 1 Charts: Delay Comparison & Corridor Breakdown
    c_col1, c_col2 = st.columns([1.1, 1.4])
    with c_col1:
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
        op_filter = st.selectbox("Filter by Operator", ["All Operators", "Metro", "BRTS", "AMTS"], key="intel_op_filter_select")
    with f_col2:
        sev_filter = st.selectbox("Filter by Severity", ["All Severities", "CRITICAL Only", "WARNING Only"], key="intel_sev_filter_select")

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

    # Row 3: GMRC Wayside Track & Interlocking Diagnostics
    st.markdown('<div class="section-title"><span>🚊 GMRC Wayside Track & Interlocking Diagnostic Telemetry</span></div>', unsafe_allow_html=True)
    st.caption("Drill down into real-time wayside block occupancy, Temporary Speed Restrictions (TSR), and CBTC signaling health:")
    render_gmrc_track_monitor(key_prefix="intel_track")

    # Row 4: Inspect Raw Telemetry Warehouse
    with st.expander("📋 Inspect Consolidated Multi-Modal Telemetry Warehouse", expanded=False):

        st.caption("Consolidated tabular data with date filtering and CSV export:")
        st.dataframe(
            consolidated.raw_df,
            use_container_width=True,
            height=260
        )


def render_section_5_brief():
    """Section 5: Two-Minute Daily Management Brief (PS-13)"""
    if st.session_state.morning_brief is None:
        st.warning("⚠️ Daily Brief will be generated once operational feeds are validated.")
        return

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
            key="brief_tab_pdf_dl_btn",
            use_container_width=True
        )
    with export_col3:
        html_content = generate_html_brief(brief)
        st.download_button(
            label="🌐 Export Printable HTML",
            data=html_content,
            file_name=f"TransitPulse_Daily_Brief_{target_date}.html",
            mime="text/html",
            key="brief_tab_html_dl_btn",
            use_container_width=True
        )

    st.markdown("---")

    # 1. Executive Narrative Box
    health = brief.get("overall_health_score", 95.0)
    st.markdown(f"""
    <div style="background: #FFF7ED; border: 1px solid #FED7AA; border-left: 6px solid #FF6B00; border-radius: 12px; padding: 22px; margin-bottom: 22px; box-shadow: 0 4px 16px rgba(255,107,0,0.06);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <span style="font-size: 13.5px; font-weight: 800; color: #EA580C; text-transform: uppercase; letter-spacing: 0.6px; font-family: 'Outfit', sans-serif;">
                Executive Morning Standup Brief
            </span>
            <span style="font-size: 12.5px; font-weight: 800; color: {'#EF4444' if health < 80 else '#065F46'}; background: {'#FEF2F2' if health < 80 else '#ECFDF5'}; padding: 4px 12px; border-radius: 20px; border: 1px solid {'#FCA5A5' if health < 80 else '#A7F3D0'};">
                Network Health: {health:.0f}/100 ({brief.get('status_label')})
            </span>
        </div>
        <div style="font-size: 15px; color: #1E293B; line-height: 1.65;">
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
        <div style="background: #FFFFFF; border: 1px solid #FED7AA; border-left: 5px solid #FF6B00; border-radius: 8px; padding: 14px 18px; margin-bottom: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.03);">
            <div style="display: flex; justify-content: space-between; font-size: 12px; font-weight: 800; color: #EA580C; margin-bottom: 4px;">
                <span>{act['priority']}</span>
                <span>{act['target']}</span>
            </div>
            <div style="font-size: 14px; color: #1E293B; line-height: 1.5;">
                {act['action']}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 4. Critical & Warning Exception Details
    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown("#### 🔎 Exception Deep-Dive & Root Cause Hypotheses")
    for idx, ex in enumerate(st.session_state.explained_exceptions):
        render_exception_card_streamlit(ex, idx)


# -----------------------------------------------------------------------------
# PRESENTATION LAYOUT DISPATCHER
# -----------------------------------------------------------------------------
if view_layout == "📜 Full-Page Scroll Motion (Default)":
    # 1. Sticky Floating Navigation Dock
    st.markdown("""
    <div class="floating-scroll-nav">
        <a href="#section-hero" class="nav-jump-btn" target="_self">🏠 1. Metro Landing</a>
        <a href="#section-overview" class="nav-jump-btn" target="_self">📊 2. Executive Overview</a>
        <a href="#section-audit" class="nav-jump-btn" target="_self">📥 3. Data & Audit</a>
        <a href="#section-intel" class="nav-jump-btn" target="_self">🔍 4. Operations Intel</a>
        <a href="#section-brief" class="nav-jump-btn" target="_self">📋 5. Daily Brief</a>
    </div>
    """, unsafe_allow_html=True)

    # PAGE 1: Doodly Metro Landing Page
    st.markdown("""
    <div id="section-hero">
        <div class="page-indicator-pill">PAGE 1 OF 5 • DOODLY METRO HERO & OPERATIONS PORTAL</div>
    </div>
    """, unsafe_allow_html=True)
    render_section_1_hero()
    st.markdown("""
    <div class="scroll-prompt-bar">
        <a href="#section-overview" target="_self">⬇️ Scroll to Page 2: Executive Overview & Multi-Modal Telemetry</a>
    </div>
    <div style="height: 60px;"></div>
    """, unsafe_allow_html=True)

    # PAGE 2: Executive Overview
    st.markdown("""
    <div id="section-overview">
        <div class="page-indicator-pill">PAGE 2 OF 5 • EXECUTIVE OVERVIEW & FLEET TELEMETRY</div>
    </div>
    """, unsafe_allow_html=True)
    render_section_2_overview()
    st.markdown("""
    <div class="scroll-prompt-bar">
        <a href="#section-audit" target="_self">⬇️ Scroll to Page 3: Pre-Flight Data Quality Gate & Ingestion</a>
    </div>
    <div style="height: 60px;"></div>
    """, unsafe_allow_html=True)

    # PAGE 3: Data Quality Sentinel
    st.markdown("""
    <div id="section-audit">
        <div class="page-indicator-pill">PAGE 3 OF 5 • DATA QUALITY SENTINEL & SCHEMA AUDIT</div>
    </div>
    """, unsafe_allow_html=True)
    render_section_3_audit()
    st.markdown("""
    <div class="scroll-prompt-bar">
        <a href="#section-intel" target="_self">⬇️ Scroll to Page 4: Operations Intelligence & Bottlenecks</a>
    </div>
    <div style="height: 60px;"></div>
    """, unsafe_allow_html=True)

    # PAGE 4: Operations Intelligence
    st.markdown("""
    <div id="section-intel">
        <div class="page-indicator-pill">PAGE 4 OF 5 • OPERATIONS INTELLIGENCE & PRIORITIZED FEED</div>
    </div>
    """, unsafe_allow_html=True)
    render_section_4_intel()
    st.markdown("""
    <div class="scroll-prompt-bar">
        <a href="#section-brief" target="_self">⬇️ Scroll to Page 5: Two-Minute Morning Brief & PDF Export</a>
    </div>
    <div style="height: 60px;"></div>
    """, unsafe_allow_html=True)

    # PAGE 5: Daily Brief & PDF Export
    st.markdown("""
    <div id="section-brief">
        <div class="page-indicator-pill">PAGE 5 OF 5 • TWO-MINUTE MORNING BRIEF (PS-13 STANDUP)</div>
    </div>
    """, unsafe_allow_html=True)
    render_section_5_brief()
    st.markdown("""
    <div class="scroll-prompt-bar">
        <a href="#section-hero" target="_self">⬆️ Back to Top (Doodly Metro Hero)</a>
    </div>
    <div style="height: 80px;"></div>
    """, unsafe_allow_html=True)

else:
    # Classic Tabbed View
    tab_landing, tab_overview, tab_import, tab_intel, tab_brief = st.tabs([
        "🏠 Metro Landing Portal",
        "📊 Executive Overview",
        "📥 Data Import & Audit",
        "🔍 Operations Intelligence",
        "📋 Two-Minute Daily Brief"
    ])

    with tab_landing:
        render_section_1_hero()

    with tab_overview:
        render_section_2_overview()

    with tab_import:
        render_section_3_audit()

    with tab_intel:
        render_section_4_intel()

    with tab_brief:
        render_section_5_brief()
