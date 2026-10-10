"""
TransitPulse AI - Executive Daily Brief PDF & HTML Generator
Produces a high-density, professional one-page Operations Management Brief.
Uses ReportLab for direct binary PDF generation and provides an HTML print fallback.
"""

import io
from datetime import datetime
from typing import Dict, Any, List

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def generate_pdf_brief(brief_data: Dict[str, Any]) -> bytes:
    """
    Generates a high-quality 1-page A4 PDF binary for download.
    """
    buffer = io.BytesIO()
    
    # 0.4 inch margins for maximum 1-page density
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=28,
        rightMargin=28,
        topMargin=26,
        bottomMargin=26
    )
    
    styles = getSampleStyleSheet()
    
    # Brand Colors (Ahmedabad Metro White & Orange Theme)
    c_navy = colors.HexColor("#0F172A")
    c_slate = colors.HexColor("#1E293B")
    c_teal = colors.HexColor("#FF6B00")  # Ahmedabad Metro Saffron Orange Accent
    c_red = colors.HexColor("#DC2626")
    c_amber = colors.HexColor("#D97706")
    c_green = colors.HexColor("#059669")
    c_gray_bg = colors.HexColor("#FFF7ED")
    c_border = colors.HexColor("#FED7AA")
    
    # Custom Typography Styles
    title_style = ParagraphStyle(
        "DocTitle",
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=18,
        textColor=c_navy
    )
    subtitle_style = ParagraphStyle(
        "DocSub",
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#475569")
    )
    meta_style = ParagraphStyle(
        "DocMeta",
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=c_teal,
        alignment=2 # Right aligned
    )
    section_heading = ParagraphStyle(
        "SectionHead",
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=12,
        textColor=c_navy
    )
    body_style = ParagraphStyle(
        "BodyTextCustom",
        fontName="Helvetica",
        fontSize=7.5,
        leading=10,
        textColor=c_slate
    )
    bold_style = ParagraphStyle(
        "BoldTextCustom",
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=10,
        textColor=c_slate
    )
    crit_tag_style = ParagraphStyle(
        "CritTag",
        fontName="Helvetica-Bold",
        fontSize=7,
        leading=8,
        textColor=c_red
    )
    warn_tag_style = ParagraphStyle(
        "WarnTag",
        fontName="Helvetica-Bold",
        fontSize=7,
        leading=8,
        textColor=c_amber
    )

    elements = []
    
    # -------------------------------------------------------------
    # 1. HEADER & METADATA BAR
    # -------------------------------------------------------------
    header_data = [
        [
            Paragraph("<b>TRANSITPULSE AI</b> &nbsp;|&nbsp; Daily Operations Management Brief", title_style),
            Paragraph(f"<b>Reporting Date:</b> {brief_data.get('report_date', 'N/A')}<br/>"
                      f"<b>Generated:</b> {datetime.now().strftime('%H:%M IST')}<br/>"
                      f"<b>Territory:</b> Ahmedabad-Gandhinagar", meta_style)
        ]
    ]
    t_header = Table(header_data, colWidths=[360, 180])
    t_header.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(t_header)
    elements.append(HRFlowable(width="100%", thickness=1.5, color=c_teal, spaceAfter=6, spaceBefore=2))

    # -------------------------------------------------------------
    # 2. EXECUTIVE OVERVIEW & KPI CARDS
    # -------------------------------------------------------------
    city_m = brief_data.get("citywide_metrics", {})
    health = brief_data.get("overall_health_score", 95.0)
    status_label = brief_data.get("status_label", "NOMINAL")
    
    kpi_card_data = [
        [
            Paragraph("<b>TRANSIT HEALTH</b>", subtitle_style),
            Paragraph("<b>TOTAL RIDERSHIP</b>", subtitle_style),
            Paragraph("<b>FLEET AVAILABILITY</b>", subtitle_style),
            Paragraph("<b>AVG NETWORK DELAY</b>", subtitle_style),
            Paragraph("<b>EXCEPTIONS</b>", subtitle_style),
        ],
        [
            Paragraph(f"<font size=12 color='{c_red.hexval() if health < 80 else c_green.hexval()}'><b>{health:.0f}/100</b></font><br/>{status_label}", body_style),
            Paragraph(f"<font size=12 color='{c_navy.hexval()}'><b>{int(city_m.get('total_ridership', 0)):,}</b></font><br/>Riders across 3 modes", body_style),
            Paragraph(f"<font size=12 color='{c_teal.hexval()}'><b>{city_m.get('network_availability_pct', 0):.1f}%</b></font><br/>Completed / Scheduled", body_style),
            Paragraph(f"<font size=12 color='{c_navy.hexval()}'><b>{city_m.get('citywide_avg_delay_minutes', 0):.1f}m</b></font><br/>Weighted mean", body_style),
            Paragraph(f"<font size=12 color='{c_red.hexval()}'><b>{brief_data.get('critical_exceptions_count', 0)} Critical</b></font><br/>{brief_data.get('warning_exceptions_count', 0)} Warnings", body_style),
        ]
    ]
    t_kpis = Table(kpi_card_data, colWidths=[108, 108, 108, 108, 108])
    t_kpis.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_gray_bg),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(t_kpis)
    elements.append(Spacer(1, 6))

    # Executive Narrative Callout
    elements.append(Paragraph(f"<b>Executive Summary:</b> {brief_data.get('executive_narrative', '')}", body_style))
    elements.append(Spacer(1, 6))

    # -------------------------------------------------------------
    # 3. OPERATOR PERFORMANCE MATRIX TABLE
    # -------------------------------------------------------------
    elements.append(Paragraph("<b>Operator Fleet & Performance Breakdown</b>", section_heading))
    elements.append(Spacer(1, 3))
    
    op_table_data = [
        [
            Paragraph("<b>Operator</b>", bold_style),
            Paragraph("<b>Scope / Units</b>", bold_style),
            Paragraph("<b>Ridership</b>", bold_style),
            Paragraph("<b>Scheduled</b>", bold_style),
            Paragraph("<b>Completed</b>", bold_style),
            Paragraph("<b>Availability</b>", bold_style),
            Paragraph("<b>Avg Delay</b>", bold_style),
            Paragraph("<b>Operational Status</b>", bold_style),
        ]
    ]
    
    op_metrics = brief_data.get("operator_metrics", {})
    for op_name, m in op_metrics.items():
        avail = m.get("service_availability_pct", 0)
        delay = m.get("average_delay_minutes", 0)
        
        # Determine quick status
        if avail < 85 or delay > 6:
            st_text = "<font color='#DC2626'><b>CRITICAL DEVIATION</b></font>"
        elif avail < 92 or delay > 4:
            st_text = "<font color='#D97706'><b>REVIEW REQUIRED</b></font>"
        else:
            st_text = "<font color='#059669'><b>NOMINAL</b></font>"
            
        unit_label = "Corridors" if op_name == "Metro" else "BRTS Routes" if op_name == "BRTS" else "City Routes"
        
        op_table_data.append([
            Paragraph(f"<b>{op_name}</b>", bold_style),
            Paragraph(f"{int(m.get('active_routes_count', 0))} {unit_label}", body_style),
            Paragraph(f"{int(m.get('ridership', 0)):,}", body_style),
            Paragraph(f"{int(m.get('scheduled_services', 0)):,}", body_style),
            Paragraph(f"{int(m.get('completed_services', 0)):,}", body_style),
            Paragraph(f"{avail:.1f}%", body_style),
            Paragraph(f"{delay:.1f} min", body_style),
            Paragraph(st_text, body_style),
        ])
        
    t_ops = Table(op_table_data, colWidths=[65, 80, 65, 55, 55, 60, 60, 100])
    t_ops.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F1F5F9")),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    elements.append(t_ops)
    elements.append(Spacer(1, 6))

    # -------------------------------------------------------------
    # 4. HIGHEST-PRIORITY OPERATIONAL EXCEPTIONS (EVIDENCE & ACTION)
    # -------------------------------------------------------------
    elements.append(Paragraph("<b>Prioritized Operational Exceptions & Actionable Intelligence</b>", section_heading))
    elements.append(Spacer(1, 3))
    
    detailed_ex = brief_data.get("detailed_exceptions", [])[:3] # Top 3 for 1-page brevity
    
    if detailed_ex:
        for ex in detailed_ex:
            sev = ex.get("severity", "INFORMATIONAL")
            tag_color = c_red if sev == "CRITICAL" else c_amber
            
            ex_rows = [
                [
                    Paragraph(f"<font color='{tag_color.hexval()}'><b>[{sev}]</b></font> <b>{ex.get('title', '')}</b>", bold_style),
                    Paragraph(f"<b>Delta:</b> {ex.get('pct_change', 0):+.1f}%", crit_tag_style if sev == "CRITICAL" else warn_tag_style)
                ],
                [
                    Paragraph(f"<b>Observation:</b> {ex.get('observation', '')}", body_style),
                    Paragraph("", body_style)
                ],
                [
                    Paragraph(f"<b>Hypotheses:</b> {' | '.join(ex.get('possible_explanations', [])[:2])}", body_style),
                    Paragraph("", body_style)
                ],
                [
                    Paragraph(f"<b>Recommended Action:</b> <u>{ex.get('recommended_action', '')}</u>", bold_style),
                    Paragraph("", body_style)
                ]
            ]
            t_ex = Table(ex_rows, colWidths=[460, 80])
            t_ex.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FAFAFA")),
                ('BOX', (0,0), (-1,-1), 0.75, tag_color),
                ('SPAN', (0,1), (1,1)),
                ('SPAN', (0,2), (1,2)),
                ('SPAN', (0,3), (1,3)),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('TOPPADDING', (0,0), (-1,-1), 2),
                ('BOTTOMPADDING', (0,0), (-1,-1), 2),
                ('LEFTPADDING', (0,0), (-1,-1), 6),
                ('RIGHTPADDING', (0,0), (-1,-1), 6),
            ]))
            elements.append(t_ex)
            elements.append(Spacer(1, 3))
    else:
        elements.append(Paragraph("<i>No critical operational exceptions detected for this reporting cycle.</i>", body_style))
        elements.append(Spacer(1, 4))

    # -------------------------------------------------------------
    # 5. GOVERNANCE & AUDIT FOOTER
    # -------------------------------------------------------------
    elements.append(Spacer(1, 3))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=c_border, spaceAfter=3, spaceBefore=0))
    footer_text = (
        "<b>Governance Notice:</b> TransitPulse AI v1.0 (Hackathon MVP). Deterministic calculations verified against uploaded "
        "telemetry CSV feeds. AI explanations distinguish observed telemetry facts from unverified external causes. "
        "Generated for Gandhinagar / Ahmedabad Transit Joint Task Force. Confidential internal briefing."
    )
    elements.append(Paragraph(footer_text, ParagraphStyle("Footer", fontName="Helvetica", fontSize=6.5, leading=8, textColor=colors.HexColor("#64748B"))))

    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()


def generate_html_brief(brief_data: Dict[str, Any]) -> str:
    """
    Generates an executive-ready standalone HTML report for instant browser viewing and printing.
    """
    city_m = brief_data.get("citywide_metrics", {})
    health = brief_data.get("overall_health_score", 95.0)
    status_label = brief_data.get("status_label", "NOMINAL")
    report_date = brief_data.get("report_date", "N/A")
    op_metrics = brief_data.get("operator_metrics", {})
    exceptions = brief_data.get("detailed_exceptions", [])

    op_rows_html = ""
    for op_name, m in op_metrics.items():
        avail = m.get("service_availability_pct", 0)
        delay = m.get("average_delay_minutes", 0)
        badge_class = "crit-badge" if (avail < 85 or delay > 6) else "warn-badge" if (avail < 92 or delay > 4) else "ok-badge"
        badge_text = "CRITICAL DEVIATION" if (avail < 85 or delay > 6) else "REVIEW REQUIRED" if (avail < 92 or delay > 4) else "NOMINAL"
        
        op_rows_html += f"""
        <tr>
            <td style="font-weight: 700; color: #0A192F;">{op_name}</td>
            <td>{int(m.get('active_routes_count', 0))} Units</td>
            <td>{int(m.get('ridership', 0)):,}</td>
            <td>{int(m.get('scheduled_services', 0)):,}</td>
            <td>{int(m.get('completed_services', 0)):,}</td>
            <td style="font-weight: 600;">{avail:.1f}%</td>
            <td>{delay:.1f}m</td>
            <td><span class="{badge_class}">{badge_text}</span></td>
        </tr>
        """

    ex_cards_html = ""
    for ex in exceptions[:4]:
        sev = ex.get("severity", "INFORMATIONAL")
        card_class = "ex-crit" if sev == "CRITICAL" else "ex-warn"
        ex_cards_html += f"""
        <div class="ex-card {card_class}">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                <span class="ex-badge-{sev.lower()}">{sev} EXCEPTION</span>
                <span style="font-weight: 700; font-size: 13px; color: {'#DC2626' if sev=='CRITICAL' else '#D97706'};">{ex.get('pct_change', 0):+.1f}%</span>
            </div>
            <div style="font-weight: 700; font-size: 14px; color: #0A192F; margin-bottom: 4px;">{ex.get('title', '')}</div>
            <div style="font-size: 12px; color: #334155; margin-bottom: 4px;"><strong>Observation:</strong> {ex.get('observation', '')}</div>
            <div style="font-size: 12px; color: #475569; margin-bottom: 4px;"><strong>Hypotheses:</strong> {' | '.join(ex.get('possible_explanations', [])[:2])}</div>
            <div style="font-size: 12px; background: #F1F5F9; padding: 6px 10px; border-radius: 4px; margin-top: 4px;">
                <strong>Recommended Action:</strong> {ex.get('recommended_action', '')}
            </div>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>TransitPulse AI — Two-Minute Operations Brief ({report_date})</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background: #F8FAFC;
            color: #0F172A;
            margin: 0;
            padding: 24px;
        }}
        .brief-container {{
            max-width: 900px;
            margin: 0 auto;
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            padding: 28px;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            border-bottom: 2px solid #0D9488;
            padding-bottom: 12px;
            margin-bottom: 16px;
        }}
        .title {{ font-size: 20px; font-weight: 800; color: #0A192F; margin: 0; }}
        .subtitle {{ font-size: 12px; color: #64748B; margin-top: 2px; }}
        .meta {{ text-align: right; font-size: 12px; color: #0D9488; font-weight: 600; line-height: 1.4; }}
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 10px;
            margin-bottom: 16px;
        }}
        .kpi-card {{
            background: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 6px;
            padding: 10px;
            text-align: center;
        }}
        .kpi-label {{ font-size: 10px; font-weight: 700; color: #64748B; text-transform: uppercase; }}
        .kpi-val {{ font-size: 18px; font-weight: 800; color: #0A192F; margin: 4px 0; }}
        .kpi-sub {{ font-size: 11px; color: #64748B; }}
        .exec-narrative {{
            background: #EFF6FF;
            border-left: 4px solid #2563EB;
            padding: 10px 14px;
            border-radius: 4px;
            font-size: 12.5px;
            line-height: 1.45;
            color: #1E3A8A;
            margin-bottom: 18px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 12px;
            margin-bottom: 18px;
        }}
        th {{
            background: #F1F5F9;
            color: #334155;
            font-weight: 700;
            text-align: left;
            padding: 8px 10px;
            border: 1px solid #CBD5E1;
        }}
        td {{
            padding: 7px 10px;
            border: 1px solid #CBD5E1;
        }}
        .crit-badge {{ background: #FEE2E2; color: #991B1B; font-size: 10px; font-weight: 700; padding: 2px 6px; border-radius: 4px; }}
        .warn-badge {{ background: #FEF3C7; color: #92400E; font-size: 10px; font-weight: 700; padding: 2px 6px; border-radius: 4px; }}
        .ok-badge {{ background: #ECFDF5; color: #065F46; font-size: 10px; font-weight: 700; padding: 2px 6px; border-radius: 4px; }}
        .ex-card {{
            border-radius: 6px;
            padding: 12px;
            margin-bottom: 10px;
            border: 1px solid #CBD5E1;
        }}
        .ex-crit {{ background: #FEF2F2; border-color: #F87171; }}
        .ex-warn {{ background: #FFFBEB; border-color: #FCD34D; }}
        .ex-badge-critical {{ background: #DC2626; color: #fff; font-size: 10px; font-weight: 700; padding: 2px 6px; border-radius: 3px; }}
        .ex-badge-warning {{ background: #D97706; color: #fff; font-size: 10px; font-weight: 700; padding: 2px 6px; border-radius: 3px; }}
        .footer {{
            border-top: 1px solid #E2E8F0;
            padding-top: 10px;
            font-size: 10px;
            color: #94A3B8;
            line-height: 1.4;
            margin-top: 16px;
        }}
        @media print {{
            body {{ padding: 0; background: #fff; }}
            .brief-container {{ border: none; box-shadow: none; padding: 0; }}
            button {{ display: none; }}
        }}
    </style>
</head>
<body>
    <div class="brief-container">
        <div class="header">
            <div>
                <h1 class="title">TRANSITPULSE AI</h1>
                <div class="subtitle">AI-Powered Public Transport Operations Intelligence & Daily Briefing System</div>
            </div>
            <div class="meta">
                Reporting Date: {report_date}<br/>
                Generated: {datetime.now().strftime("%H:%M IST")}<br/>
                Territory: Ahmedabad - Gandhinagar
            </div>
        </div>

        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-label">Transit Health</div>
                <div class="kpi-val" style="color: {'#DC2626' if health < 80 else '#059669'};">{health:.0f}/100</div>
                <div class="kpi-sub">{status_label}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Total Ridership</div>
                <div class="kpi-val">{int(city_m.get('total_ridership', 0)):,}</div>
                <div class="kpi-sub">Citywide Passengers</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Network Availability</div>
                <div class="kpi-val" style="color: #0D9488;">{city_m.get('network_availability_pct', 0):.1f}%</div>
                <div class="kpi-sub">Completed Trips</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Average Delay</div>
                <div class="kpi-val">{city_m.get('citywide_avg_delay_minutes', 0):.1f}m</div>
                <div class="kpi-sub">Weighted Across 3 Modes</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Exceptions</div>
                <div class="kpi-val" style="color: #DC2626;">{brief_data.get('critical_exceptions_count', 0)} Crit</div>
                <div class="kpi-sub">{brief_data.get('warning_exceptions_count', 0)} Warnings</div>
            </div>
        </div>

        <div class="exec-narrative">
            <strong>Executive Overview:</strong> {brief_data.get('executive_narrative', '')}
        </div>

        <h3 style="font-size: 13px; text-transform: uppercase; color: #0A192F; margin-bottom: 6px; letter-spacing: 0.5px;">Operator Fleet & Performance Breakdown</h3>
        <table>
            <thead>
                <tr>
                    <th>Operator</th>
                    <th>Scope</th>
                    <th>Ridership</th>
                    <th>Scheduled</th>
                    <th>Completed</th>
                    <th>Availability</th>
                    <th>Avg Delay</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                {op_rows_html}
            </tbody>
        </table>

        <h3 style="font-size: 13px; text-transform: uppercase; color: #0A192F; margin-bottom: 6px; letter-spacing: 0.5px;">Prioritized Exceptions & Actionable Intelligence</h3>
        {ex_cards_html}

        <div class="footer">
            <strong>Governance Notice:</strong> TransitPulse AI v1.0 (Hackathon MVP). Deterministic calculations verified against uploaded telemetry CSV feeds. Explanations distinguish observed telemetry facts from unverified external causes. Confidential internal briefing.
        </div>
    </div>
</body>
</html>
"""
    return html
