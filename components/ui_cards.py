"""
TransitPulse AI - UI Card Renderers
Generates sleek HTML-based components for KPIs, operator status,
and prioritized exception drill-downs in White & Ahmedabad Metro Orange styling.
"""

import streamlit as st
from typing import Dict, Any
from config import OPERATOR_CONFIG, SEVERITY_STYLES
from engine.explainer import ExplainedException

def render_kpi_metric(title: str, value: str, subtext: str, icon: str = "📊", delta_str: str = None, is_alert: bool = False):
    """
    Renders a control-room styled KPI metric card in crisp white & orange styling.
    """
    val_color = "#EF4444" if is_alert else "#0F172A"
    delta_html = ""
    if delta_str:
        delta_color = "#EF4444" if ("-" in delta_str or "Crit" in delta_str) else "#0D9488"
        delta_html = f"<span style='color: {delta_color}; font-weight: 700; font-size: 11.5px;'>{delta_str}</span>"

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
    
    op_cfg = OPERATOR_CONFIG.get(ex.raw.operator, {"icon": "🚏", "color": "#FF6B00"})
    pct_str = f"{ex.raw.pct_change:+.1f}%" if ex.raw.pct_change is not None else "N/A"
    
    # Outer Card Container
    with st.container():
        st.markdown(f"""
        <div class="exception-box {card_class}">
            <div class="ex-header">
                <div>
                    <span style="font-size: 11.5px; font-weight: 800; color: {op_cfg.get('color', '#FF6B00')}; text-transform: uppercase; letter-spacing: 0.5px;">
                        {op_cfg.get('icon', '')} {ex.raw.operator} &nbsp;•&nbsp; {ex.raw.scope}
                    </span>
                    <h3 class="ex-title">{ex.title}</h3>
                </div>
                <div style="display: flex; gap: 8px; align-items: center;">
                    <span style="font-size: 15px; font-weight: 800; color: {'#EF4444' if sev=='CRITICAL' else '#EA580C'};">{pct_str}</span>
                    <span class="{pill_class}">{style['icon']} {sev}</span>
                </div>
            </div>
            <div class="ex-observation">
                <strong style="color: #0F172A;">Observation:</strong> {ex.observation}
            </div>
            <div class="evidence-box">
                <div style="font-weight: 700; color: #9A3412; margin-bottom: 6px;">Telemetry Evidence & Measured Deltas:</div>
                <ul style="margin: 0; padding-left: 20px; color: #7C2D12;">
                    {''.join([f"<li style='margin-bottom: 3px;'>{pt}</li>" for pt in ex.evidence_points])}
                </ul>
                <div style="margin-top: 8px; font-size: 11.5px; color: #9A3412;">
                    <strong>Baseline Grounding:</strong> {ex.raw.baseline_method} (Baseline: {ex.raw.baseline_val:,.1f} {ex.raw.unit_str})
                </div>
            </div>
            <div class="hypothesis-box">
                <div style="font-weight: 700; color: #166534; margin-bottom: 6px;">Plausible Operational Hypotheses:</div>
                <ul style="margin: 0; padding-left: 20px; color: #14532D;">
                    {''.join([f"<li style='margin-bottom: 3px;'>{hyp}</li>" for hyp in ex.possible_explanations])}
                </ul>
            </div>
            <div class="action-box">
                <strong style="color: #92400E;">Recommended Standup Action:</strong> {ex.recommended_action}
            </div>
            <div style="margin-top: 8px; font-size: 11px; color: #64748B; font-style: italic;">
                ℹ️ {ex.uncertainty_statement}
            </div>
        </div>
        """, unsafe_allow_html=True)
