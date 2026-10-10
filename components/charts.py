"""
TransitPulse AI - Interactive Plotly Transit Visualizations
Customized with White & Ahmedabad Metro Orange theme:
Clean white card canvases, crisp saffron orange (#FF6B00), teal, and slate typography.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Dict, Any
from config import OPERATOR_CONFIG
from engine.consolidator import ConsolidatedData

LIGHT_LAYOUT = dict(
    paper_bgcolor="#FFFFFF",
    plot_bgcolor="#FFFFFF",
    font=dict(family="Inter, -apple-system, sans-serif", color="#0F172A", size=12),
    margin=dict(l=40, r=40, t=50, b=40),
    hoverlabel=dict(bgcolor="#FFFFFF", font_size=12, font_family="Inter", bordercolor="#FF6B00", font_color="#0F172A"),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
        font=dict(size=11, color="#475569")
    ),
    xaxis=dict(
        showgrid=True,
        gridcolor="#F1F5F9",
        linecolor="#E2E8F0",
        tickfont=dict(color="#475569")
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor="#F1F5F9",
        linecolor="#E2E8F0",
        tickfont=dict(color="#475569")
    )
)

def create_ridership_trend_chart(consolidated: ConsolidatedData, highlight_date: str = None) -> go.Figure:
    """
    Renders 14-day multi-operator ridership trend chart in crisp white & orange styling.
    """
    op_daily = consolidated.daily_operator_summary
    fig = go.Figure()
    
    # Preferred order: Metro, BRTS, AMTS
    for op in ["Metro", "BRTS", "AMTS"]:
        if op not in consolidated.operators:
            continue
        op_df = op_daily[op_daily["operator"] == op].sort_values("date")
        cfg = OPERATOR_CONFIG.get(op, {"color": "#FF6B00", "icon": ""})
        
        fig.add_trace(go.Scatter(
            x=op_df["date"],
            y=op_df["ridership"],
            name=f"{cfg.get('icon', '')} {op}",
            mode="lines+markers",
            line=dict(color=cfg["color"], width=3),
            marker=dict(size=6, color=cfg["color"]),
            hovertemplate="<b>%{x}</b><br>" + f"{op} Volume: <b>%{{y:,.0f}}</b><extra></extra>"
        ))
        
    # Highlight final target date if provided
    if highlight_date and highlight_date in consolidated.dates:
        fig.add_vline(
            x=highlight_date,
            line_width=2,
            line_dash="dash",
            line_color="#EA580C",
            annotation_text="Reporting Day",
            annotation_position="top left",
            annotation_font=dict(color="#EA580C", size=11, family="Inter", weight="bold")
        )
        
    layout = LIGHT_LAYOUT.copy()
    fig.update_layout(
        **layout,
        title=dict(text="<b>Multi-Modal Ridership Trend (14-Day Baseline)</b>", font=dict(color="#0F172A", size=14)),
        height=320,
    )
    fig.update_yaxes(title="Passenger Trips", tickformat=",.0s")
    fig.update_xaxes(title=None)
    return fig

def create_availability_bar_chart(op_metrics: Dict[str, Dict[str, Any]]) -> go.Figure:
    """
    Service Availability Percentage across Metro, BRTS, and AMTS with operational thresholds.
    """
    operators = [op for op in ["Metro", "BRTS", "AMTS"] if op in op_metrics]
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
        textfont=dict(color="#0F172A", size=12, family="Inter", weight="bold"),
        hovertemplate="<b>%{x}</b><br>Availability: <b>%{y:.1f}%</b><extra></extra>",
        width=0.45
    ))
    
    # 95% target benchmark line
    fig.add_hline(
        y=95.0,
        line_width=1.5,
        line_dash="dot",
        line_color="#0D9488",
        annotation_text="95% Fleet Target",
        annotation_position="bottom right",
        annotation_font=dict(color="#0D9488", size=10)
    )
    
    layout = LIGHT_LAYOUT.copy()
    layout.pop("yaxis", None)
    fig.update_layout(
        **layout,
        title=dict(text="<b>Fleet Service Availability (% Delivered Trips)</b>", font=dict(color="#0F172A", size=14)),
        height=280,
        yaxis=dict(range=[50, 105], showgrid=True, gridcolor="#F1F5F9", title="Availability %"),
        showlegend=False
    )
    return fig

def create_delay_comparison_chart(op_metrics: Dict[str, Dict[str, Any]], baseline_delays: Dict[str, float] = None) -> go.Figure:
    """
    Compares current route delays against baseline delays for each operator.
    """
    baseline_delays = baseline_delays or {}
    operators = [op for op in ["Metro", "BRTS", "AMTS"] if op in op_metrics]
    current_delays = [op_metrics[op].get("average_delay_minutes", 0) for op in operators]
    base_delays = [baseline_delays.get(op, 2.0) for op in operators]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Historical Baseline",
        x=operators,
        y=base_delays,
        marker_color="#CBD5E1",
        width=0.3
    ))
    fig.add_trace(go.Bar(
        name="Current Reporting Day",
        x=operators,
        y=current_delays,
        marker_color=["#EF4444" if cur > base * 1.4 else "#FF6B00" for cur, base in zip(current_delays, base_delays)],
        text=[f"{v:.1f}m" for v in current_delays],
        textposition="outside",
        textfont=dict(color="#0F172A", size=11, weight="bold"),
        width=0.3
    ))

    layout = LIGHT_LAYOUT.copy()
    layout.pop("yaxis", None)
    fig.update_layout(
        **layout,
        barmode="group",
        title=dict(text="<b>Average Route Delay (Baseline vs Current)</b>", font=dict(color="#0F172A", size=14)),
        height=280,
        yaxis=dict(showgrid=True, gridcolor="#F1F5F9", title="Minutes"),
    )
    return fig

def create_corridor_breakdown_chart(raw_df: pd.DataFrame, target_date: str) -> go.Figure:
    """
    Detailed horizontal bar breakdown of passenger volume by route/corridor on target date.
    """
    day_df = raw_df[raw_df["date"] == target_date].sort_values("ridership", ascending=True)
    
    color_map = {"Metro": "#FF6B00", "BRTS": "#0D9488", "AMTS": "#D97706"}
    bar_colors = [color_map.get(op, "#94A3B8") for op in day_df["operator"]]
    
    fig = go.Figure(go.Bar(
        y=day_df["station_or_route"],
        x=day_df["ridership"],
        orientation="h",
        marker_color=bar_colors,
        text=[f"{r:,}" for r in day_df["ridership"]],
        textposition="inside",
        textfont=dict(color="#FFFFFF", size=11, family="Inter", weight="bold"),
        hovertemplate="<b>%{y}</b><br>Ridership: <b>%{x:,}</b><extra></extra>"
    ))
    
    layout = LIGHT_LAYOUT.copy()
    layout.pop("xaxis", None)
    layout.pop("yaxis", None)
    fig.update_layout(
        **layout,
        title=dict(text="<b>Corridor & Route Volume Breakdown</b>", font=dict(color="#0F172A", size=14)),
        height=380,
        xaxis=dict(showgrid=True, gridcolor="#F1F5F9", title="Passengers"),
        yaxis=dict(tickfont=dict(size=11, color="#0F172A")),
        showlegend=False
    )
    return fig
