"""
TransitPulse AI - UI Card Renderers
Generates sleek HTML-based components for KPIs, operator status,
and prioritized exception drill-downs.
"""

import streamlit as st
from typing import Dict, Any
from config import OPERATOR_CONFIG, SEVERITY_STYLES
from engine.explainer import ExplainedException

def render_kpi_metric(title: str, value: str, subtext: str, icon: str = "📊", delta_str: str = None, is_alert: bool = False):
    """
    Renders a control-room styled KPI metric card.
    """
    val_color = "#EF4444" if is_alert else "#F8FAFC"
    delta_html = ""
    if delta_str:
        delta_color = "#EF4444" if ("-" in delta_str or "Crit" in delta_str) else "#10B981"
        delta_html = f"<span style='color: {delta_color}; font-weight: 700; font-size: 11px;'>{delta_str}</span>"

    html = f"""
    <div class="kpi-card">
        <div class="kpi-top">
            <span class="kpi-title">{title}</span>
            <span class="kpi-icon">{icon}</span>
        </div>
        <div class="kpi-value" style="color: {val_color};">{value}</div>
        <div class="kpi-sub">
            {delta_html}
            <span>{subtext}</span>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_exception_card_streamlit(ex: ExplainedException, idx: int):
    """
    Renders an expandable, high-density exception card with evidence drill-down.
    """
    sev = ex.raw.severity
    style = SEVERITY_STYLES.get(sev, SEVERITY_STYLES["INFORMATIONAL"])
    card_class = "exception-critical" if sev == "CRITICAL" else ("exception-warning" if sev == "WARNING" else "exception-info")
    pill_class = "pill-crit" if sev == "CRITICAL" else "pill-warn"
    
    op_cfg = OPERATOR_CONFIG.get(ex.raw.operator, {"icon": "🚏"})
    pct_str = f"{ex.raw.pct_change:+.1f}%" if ex.raw.pct_change is not None else "N/A"
    
    # Outer Card Container
    with st.container():
        st.markdown(f"""
        <div class="exception-box {card_class}">
            <div class="ex-header">
                <div>
                    <span style="font-size: 11px; font-weight: 700; color: #94A3B8; text-transform: uppercase;">
                        {op_cfg.get('icon', '')} {ex.raw.operator} &nbsp;•&nbsp; {ex.raw.scope}
                    </span>
                    <h3 class="ex-title">{ex.title}</h3>
                </div>
                <div style="display: flex; gap: 8px; align-items: center;">
                    <span style="font-size: 14px; font-weight: 800; color: {'#EF4444' if sev=='CRITICAL' else '#F59E0B'};">{pct_str}</span>
                    <span class="{pill_class}">{style['icon']} {sev}</span>
                </div>
            </div>
            <div class="ex-observation">
                <strong>Observation:</strong> {ex.observation}
            </div>
            <div class="evidence-box">
                <div style="font-weight: 600; color: #E2E8F0; margin-bottom: 4px;">Telemetry Evidence & Measurements:</div>
                <ul style="margin: 0; padding-left: 18px;">
                    {''.join([f"<li>{pt}</li>" for pt in ex.evidence_points])}
                </ul>
                <div style="margin-top: 6px; font-size: 11px; color: #64748B;">
                    <strong>Baseline Used:</strong> {ex.raw.baseline_method} (Value: {ex.raw.baseline_val:,.1f} {ex.raw.unit_str})
                </div>
            </div>
            <div style="font-size: 12.5px; color: #CBD5E1; margin-bottom: 8px;">
                <div style="font-weight: 600; color: #94A3B8; margin-bottom: 2px;">Plausible Operational Hypotheses:</div>
                <ul style="margin: 0; padding-left: 18px;">
                    {''.join([f"<li>{hyp}</li>" for hyp in ex.possible_explanations])}
                </ul>
            </div>
            <div class="action-box">
                <strong>Recommended Next Step:</strong> {ex.recommended_action}
            </div>
            <div style="margin-top: 8px; font-size: 11px; color: #64748B; font-style: italic;">
                {ex.uncertainty_statement}
            </div>
        </div>
        """, unsafe_allow_html=True)
