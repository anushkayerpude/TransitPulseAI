"""
TransitPulse AI - Interactive Plotly Transit Visualizations
Customized with high-contrast transit control room theme:
Deep Navy backgrounds, crisp teal and mode-specific colorways.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Dict, Any
from config import OPERATOR_CONFIG
from engine.consolidator import ConsolidatedData

DARK_LAYOUT = dict(
    paper_bgcolor="rgba(15, 23, 42, 0.95)",
    plot_bgcolor="rgba(15, 23, 42, 0.95)",
    font=dict(family="Inter, sans-serif", color="#CBD5E1", size=12),
    margin=dict(l=40, r=40, t=45, b=40),
    hoverlabel=dict(bgcolor="#0A192F", font_size=12, font_family="Inter"),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
        font=dict(size=11, color="#94A3B8")
    ),
    xaxis=dict(
        showgrid=True,
        gridcolor="#1E293B",
        linecolor="#334155",
        tickfont=dict(color="#94A3B8")
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor="#1E293B",
        linecolor="#334155",
        tickfont=dict(color="#94A3B8")
    )
)

def create_ridership_trend_chart(consolidated: ConsolidatedData, highlight_date: str = None) -> go.Figure:
    """
    Renders 14-day multi-operator ridership trend chart with area fills and anomaly flags.
    """
    op_daily = consolidated.daily_operator_summary
    fig = go.Figure()
    
    for op in consolidated.operators:
        op_df = op_daily[op_daily["operator"] == op].sort_values("date")
        cfg = OPERATOR_CONFIG.get(op, {"color": "#38BDF8", "icon": ""})
        
        fig.add_trace(go.Scatter(
            x=op_df["date"],
            y=op_df["ridership"],
            name=f"{cfg.get('icon', '')} {op}",
            mode="lines+markers",
            line=dict(color=cfg["color"], width=2.5),
            marker=dict(size=5),
            hovertemplate="<b>%{x}</b><br>" + f"{op} Ridership: <b>%{{y:,.0f}}</b><extra></extra>"
        ))
        
    # Highlight final target date if provided
    if highlight_date and highlight_date in consolidated.dates:
        fig.add_vline(
            x=highlight_date,
            line_width=1.5,
            line_dash="dash",
            line_color="#EF4444",
            annotation_text="Report Date",
            annotation_position="top left",
            annotation_font=dict(color="#EF4444", size=11, family="Inter")
        )
        
    layout = DARK_LAYOUT.copy()
    fig.update_layout(
        **layout,
        title=dict(text="<b>Multi-Operator Ridership Trend (14-Day View)</b>", font=dict(color="#F8FAFC", size=14)),
        height=320,
    )
    fig.update_yaxes(title="Passenger Volume", tickformat=",.0s")
    fig.update_xaxes(title=None)
    return fig

def create_availability_bar_chart(op_metrics: Dict[str, Dict[str, Any]]) -> go.Figure:
    """
    Service Availability Percentage across Metro, BRTS, and AMTS with operational thresholds.
    """
    operators = list(op_metrics.keys())
    availabilities = []
    colors = []
    
    for op in operators:
        val = op_metrics[op].get("service_availability_pct", 0)
        availabilities.append(val)
        if val >= 95.0:
            colors.append("#10B981") # Green
        elif val >= 88.0:
            colors.append("#F59E0B") # Amber
        else:
            colors.append("#EF4444") # Red

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=operators,
        y=availabilities,
        marker_color=colors,
        text=[f"{v:.1f}%" for v in availabilities],
        textposition="outside",
        textfont=dict(color="#F8FAFC", size=12, family="Inter"),
        hovertemplate="<b>%{x}</b><br>Availability: <b>%{y:.1f}%</b><extra></extra>",
        width=0.45
    ))
    
    # 95% target line
    fig.add_hline(
        y=95.0,
        line_width=1.5,
        line_dash="dot",
        line_color="#2DD4BF",
        annotation_text="95% Target Standard",
        annotation_position="bottom right",
        annotation_font=dict(color="#2DD4BF", size=10)
    )
    
    layout = DARK_LAYOUT.copy()
    fig.update_layout(
        **layout,
        title=dict(text="<b>Fleet Service Availability (% Completed)</b>", font=dict(color="#F8FAFC", size=14)),
        height=280,
        yaxis=dict(range=[50, 105], showgrid=True, gridcolor="#1E293B", title="Availability %"),
        showlegend=False
    )
    return fig

def create_delay_comparison_chart(op_metrics: Dict[str, Dict[str, Any]], baseline_delays: Dict[str, float] = None) -> go.Figure:
    """
    Compares current delays against baseline delays for each operator.
    """
    baseline_delays = baseline_delays or {}
    operators = list(op_metrics.keys())
    current_delays = [op_metrics[op].get("average_delay_minutes", 0) for op in operators]
    base_delays = [baseline_delays.get(op, 2.0) for op in operators]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Historical Baseline",
        x=operators,
        y=base_delays,
        marker_color="#475569",
        width=0.3
    ))
    fig.add_trace(go.Bar(
        name="Current Reporting Day",
        x=operators,
        y=current_delays,
        marker_color=["#EF4444" if cur > base * 1.4 else "#38BDF8" for cur, base in zip(current_delays, base_delays)],
        text=[f"{v:.1f}m" for v in current_delays],
        textposition="outside",
        textfont=dict(color="#F8FAFC", size=11),
        width=0.3
    ))

    layout = DARK_LAYOUT.copy()
    fig.update_layout(
        **layout,
        barmode="group",
        title=dict(text="<b>Average Route Delay (Baseline vs Current)</b>", font=dict(color="#F8FAFC", size=14)),
        height=280,
        yaxis=dict(showgrid=True, gridcolor="#1E293B", title="Minutes"),
    )
    return fig

def create_corridor_breakdown_chart(raw_df: pd.DataFrame, target_date: str) -> go.Figure:
    """
    Detailed horizontal bar breakdown of passenger volume by route/corridor on target date.
    """
    day_df = raw_df[raw_df["date"] == target_date].sort_values("ridership", ascending=True)
    
    color_map = {"Metro": "#38BDF8", "BRTS": "#2DD4BF", "AMTS": "#F59E0B"}
    bar_colors = [color_map.get(op, "#CBD5E1") for op in day_df["operator"]]
    
    fig = go.Figure(go.Bar(
        y=day_df["station_or_route"],
        x=day_df["ridership"],
        orientation="h",
        marker_color=bar_colors,
        text=[f"{r:,}" for r in day_df["ridership"]],
        textposition="inside",
        textfont=dict(color="#0A192F", size=10, family="Inter"),
        hovertemplate="<b>%{y}</b><br>Ridership: <b>%{x:,}</b><extra></extra>"
    ))
    
    layout = DARK_LAYOUT.copy()
    fig.update_layout(
        **layout,
        title=dict(text="<b>Corridor & Route Passenger Volume Breakdown</b>", font=dict(color="#F8FAFC", size=14)),
        height=380,
        xaxis=dict(showgrid=True, gridcolor="#1E293B", title="Ridership"),
        yaxis=dict(tickfont=dict(size=10, color="#CBD5E1")),
        showlegend=False
    )
    return fig
