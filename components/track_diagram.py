"""
TransitPulse AI - GMRC Metro Track & Signaling Visualizer Component
Renders interactive wayside track status, station schematics, block occupancies,
CBTC signal health, and 750V DC third-rail traction telemetry in
White & Ahmedabad Metro Orange (#FF6B00) styling.
"""

import streamlit as st
from config import GMRC_CORRIDORS, GMRC_TRACK_STATUSES
from engine.track_monitor import GMRCTrackMonitor

def render_gmrc_track_monitor(key_prefix: str = "main"):
    """
    Renders an interactive, control-room grade GMRC Metro track & signal monitor.
    Includes corridor selection, operational scenario simulation, wayside KPI strip,
    linear track block diagram, and detailed wayside block inspector.
    """
    st.markdown("""
    <div style="background: linear-gradient(135deg, #FFF7ED 0%, #FFFFFF 100%); border: 1.5px solid #FED7AA; border-radius: 14px; padding: 18px 22px; margin-bottom: 20px; box-shadow: 0 4px 18px rgba(255, 107, 0, 0.06);">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
            <div>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 22px;">🚇</span>
                    <h3 style="margin: 0; font-size: 19px; font-weight: 800; color: #0F172A; font-family: 'Outfit', sans-serif;">
                        GMRC Wayside Metro Track & Signaling Monitor
                    </h3>
                    <span style="background: #FFF7ED; color: #EA580C; font-size: 11px; font-weight: 800; padding: 3px 10px; border-radius: 20px; border: 1px solid #FDBA74;">
                        LIVE TELEMETRY
                    </span>
                </div>
                <p style="margin: 4px 0 0 0; font-size: 13px; color: #64748B;">
                    Real-time track circuit occupancy, Alstom Urbalis 400 CBTC health, 750V DC third-rail power, and Temporary Speed Restrictions (TSR).
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Controls Row: Corridor & Scenario Selection
    col_c1, col_c2 = st.columns([1.2, 1.8])
    with col_c1:
        corridor_options = list(GMRC_CORRIDORS.keys())
        selected_corridor = st.selectbox(
            "Select Metro Corridor",
            corridor_options,
            index=0,
            key=f"{key_prefix}_gmrc_corridor_select",
            help="Choose between East-West Line (Line 1), North-South Line (Line 2), or GN Branch."
        )

    with col_c2:
        scenario_map = {
            "🟢 Nominal Operations (All Blocks Clear / Normal Headway)": "nominal",
            "🚨 Injected Incident (Kalupur CBTC Jitter & 25 km/h TSR)": "incident",
            "⚡ Third-Rail Power Fault (Apparel Park TSS 0V DC Trip)": "power_trip",
            "🔀 Interchange Point Lock (Old High Court Switch Lock)": "switch_fault"
        }
        scenario_labels = list(scenario_map.keys())
        selected_label = st.selectbox(
            "Telemetry Simulation Scenario",
            scenario_labels,
            index=1 if st.session_state.get("active_dataset_label") == "Incident Dataset" else 0,
            key=f"{key_prefix}_gmrc_scenario_select",
            help="Simulate wayside track circuit and traction power conditions."
        )
        selected_scenario = scenario_map[selected_label]

    # Fetch Telemetry Data
    corr_data = GMRCTrackMonitor.get_corridor_telemetry(selected_corridor, scenario=selected_scenario)
    summary = corr_data["summary"]
    blocks = corr_data["blocks"]
    stations = corr_data["stations"]

    # Wayside Telemetry Metric Strip
    m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns(5)
    
    with m_col1:
        st.markdown(f"""
        <div class="kpi-card" style="padding: 12px 14px;">
            <div style="font-size: 11px; font-weight: 700; color: #64748B; text-transform: uppercase;">Track Blocks</div>
            <div style="font-size: 20px; font-weight: 800; color: #0F172A; margin: 2px 0;">
                {summary['clear_blocks']} <span style="font-size: 13px; color: #64748B; font-weight: 600;">/ {corr_data['block_count']} Clear</span>
            </div>
            <div style="font-size: 11px; color: #10B981; font-weight: 600;">🟢 {summary['occupied_blocks']} Block(s) Occupied</div>
        </div>
        """, unsafe_allow_html=True)

    with m_col2:
        st.markdown(f"""
        <div class="kpi-card" style="padding: 12px 14px;">
            <div style="font-size: 11px; font-weight: 700; color: #64748B; text-transform: uppercase;">Active Fleet</div>
            <div style="font-size: 20px; font-weight: 800; color: #2563EB; margin: 2px 0;">
                {summary['active_trains_count']} Trains
            </div>
            <div style="font-size: 11px; color: #64748B;">Avg Speed: {summary['average_speed_kmh']} km/h</div>
        </div>
        """, unsafe_allow_html=True)

    with m_col3:
        tsr_color = "#EA580C" if summary['tsr_blocks'] > 0 else "#10B981"
        st.markdown(f"""
        <div class="kpi-card" style="padding: 12px 14px; border-top: 3px solid {tsr_color};">
            <div style="font-size: 11px; font-weight: 700; color: #64748B; text-transform: uppercase;">Active TSR Zones</div>
            <div style="font-size: 20px; font-weight: 800; color: {tsr_color}; margin: 2px 0;">
                {summary['tsr_blocks']} Restriction{'s' if summary['tsr_blocks'] != 1 else ''}
            </div>
            <div style="font-size: 11px; color: {tsr_color}; font-weight: 600;">
                {'⚠️ Speed Cap Enforced' if summary['tsr_blocks'] > 0 else '✅ Max 80 km/h Clean'}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with m_col4:
        power_color = "#EF4444" if summary['fault_blocks'] > 0 else "#0D9488"
        power_status = "0V DC TRIP" if summary['fault_blocks'] > 0 else "750V DC NOMINAL"
        st.markdown(f"""
        <div class="kpi-card" style="padding: 12px 14px; border-top: 3px solid {power_color};">
            <div style="font-size: 11px; font-weight: 700; color: #64748B; text-transform: uppercase;">Traction Power</div>
            <div style="font-size: 18px; font-weight: 800; color: {power_color}; margin: 2px 0;">
                {power_status}
            </div>
            <div style="font-size: 11px; color: #64748B;">Third-Rail Bottom Contact</div>
        </div>
        """, unsafe_allow_html=True)

    with m_col5:
        headway_color = "#EF4444" if summary['operating_headway_min'] > 6.0 else "#10B981"
        st.markdown(f"""
        <div class="kpi-card" style="padding: 12px 14px; border-top: 3px solid {headway_color};">
            <div style="font-size: 11px; font-weight: 700; color: #64748B; text-transform: uppercase;">Line Headway</div>
            <div style="font-size: 20px; font-weight: 800; color: {headway_color}; margin: 2px 0;">
                {summary['operating_headway_min']:.1f} min
            </div>
            <div style="font-size: 11px; color: {headway_color}; font-weight: 600;">
                {'🚨 Severe Headway Gap' if summary['operating_headway_min'] > 10 else ('⚠️ Minor Spacing' if summary['operating_headway_min'] > 5 else '✅ Peak 3.5 min Target')}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Track Schematic Visualizer (HTML & SVG Container)
    st.markdown(f"""
    <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 20px; margin-top: 16px; margin-bottom: 20px; box-shadow: 0 4px 16px rgba(15, 23, 42, 0.04);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; border-bottom: 1px solid #F1F5F9; padding-bottom: 10px;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="background: {corr_data['color']}; width: 14px; height: 14px; border-radius: 4px; display: inline-block;"></span>
                <strong style="font-size: 15px; color: #0F172A; font-family: 'Outfit', sans-serif;">
                    {corr_data['name']} • {corr_data['route_label']} ({corr_data['length_km']} km)
                </strong>
            </div>
            <div style="display: flex; gap: 12px; font-size: 11.5px; font-weight: 600; color: #64748B;">
                <span>🟢 Clear Track</span>
                <span>🔵 Train Active</span>
                <span>⚠️ TSR (25 km/h)</span>
                <span>🔴 Power Trip</span>
            </div>
        </div>
        <div style="overflow-x: auto; padding-bottom: 12px;">
            <div style="min-width: 950px;">
                {generate_track_svg(corr_data)}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Granular Wayside Block Inspection Table
    with st.expander("🔍 Inspect Detailed Wayside Block Circuits & Interlocking Telemetry", expanded=False):
        st.caption(f"Showing all {corr_data['block_count']} track blocks along {selected_corridor}:")
        
        # Build tabular data
        table_rows = []
        for b in blocks:
            table_rows.append({
                "Block ID": b["block_id"],
                "From Station": b["from_station"],
                "To Station": b["to_station"],
                "Status": f"{b['status_icon']} {b['status_label']}",
                "Speed Limit": f"{b['speed_limit_kmh']} km/h",
                "Actual Speed": f"{b['actual_speed_kmh']} km/h",
                "Third Rail Voltage": f"{b['third_rail_voltage_v']} V DC",
                "CBTC / Signaling": b["cbtc_status"],
                "Active Train": b["active_train"] or "None (Clear)",
                "Notes": b["notes"]
            })
        
        import pandas as pd
        df_blocks = pd.DataFrame(table_rows)
        st.dataframe(df_blocks, use_container_width=True, height=280)


def generate_track_svg(corr_data: dict) -> str:
    """
    Renders an SVG string diagram of the corridor's stations, track rails,
    active trains, and color-coded block occupancy.
    """
    stations = corr_data["stations"]
    blocks = corr_data["blocks"]
    n_st = len(stations)
    
    # SVG Dimensions
    svg_w = max(960, n_st * 88)
    svg_h = 175
    y_rail_top = 85
    y_rail_bot = 97
    
    # Calculate X coordinate for each station
    margin_x = 55
    usable_w = svg_w - (2 * margin_x)
    dx = usable_w / max(n_st - 1, 1)

    elements = []
    
    # 1. Base Viaduct & Ballast Deck
    elements.append(f"""
    <rect x="{margin_x - 30}" y="70" width="{usable_w + 60}" height="42" rx="8" fill="#F8FAFC" stroke="#E2E8F0" stroke-width="1.5" />
    """)

    # 2. Block Segments between stations
    for i, b in enumerate(blocks):
        x1 = margin_x + (i * dx)
        x2 = margin_x + ((i + 1) * dx)
        
        status = b["status"]
        if status == "CLEAR":
            track_color = "#10B981"  # Emerald
            stroke_width = "4"
            dash = "none"
        elif status == "OCCUPIED":
            track_color = "#2563EB"  # Blue
            stroke_width = "5"
            dash = "none"
        elif status == "SPEED_RESTRICTION":
            track_color = "#EA580C"  # Orange TSR
            stroke_width = "5"
            dash = "6,4"
        elif status == "POWER_FAULT":
            track_color = "#EF4444"  # Red
            stroke_width = "5"
            dash = "4,4"
        else:
            track_color = "#94A3B8"
            stroke_width = "4"
            dash = "none"

        # Top & Bottom Rails for this block
        elements.append(f"""
        <!-- Block {b['block_id']} -->
        <line x1="{x1}" y1="{y_rail_top}" x2="{x2}" y2="{y_rail_top}" stroke="{track_color}" stroke-width="{stroke_width}" stroke-dasharray="{dash}" stroke-linecap="round" />
        <line x1="{x1}" y1="{y_rail_bot}" x2="{x2}" y2="{y_rail_bot}" stroke="{track_color}" stroke-width="{stroke_width}" stroke-dasharray="{dash}" stroke-linecap="round" />
        """)

        # Sleepers / Ties along this block
        num_ties = 5
        tie_dx = (x2 - x1) / (num_ties + 1)
        for t in range(1, num_ties + 1):
            tx = x1 + (t * tie_dx)
            elements.append(f"""
            <line x1="{tx}" y1="80" x2="{tx}" y2="102" stroke="#CBD5E1" stroke-width="2" />
            """)

        # If occupied by train, draw train carriage badge
        if b["active_train"]:
            mid_x = (x1 + x2) / 2
            train_color = "#EF4444" if status == "POWER_FAULT" else ("#EA580C" if status == "SPEED_RESTRICTION" else "#2563EB")
            elements.append(f"""
            <g transform="translate({mid_x - 36}, {y_rail_top - 36})">
                <rect x="0" y="0" width="72" height="24" rx="6" fill="{train_color}" stroke="#FFFFFF" stroke-width="1.5" filter="drop-shadow(0 2px 4px rgba(0,0,0,0.2))" />
                <text x="36" y="16" fill="#FFFFFF" font-size="10" font-weight="700" font-family="'Outfit', sans-serif" text-anchor="middle">
                    🚆 {b['active_train'].split()[0]}
                </text>
            </g>
            """)

        # If TSR active, draw warning hazard icon
        elif status == "SPEED_RESTRICTION":
            mid_x = (x1 + x2) / 2
            elements.append(f"""
            <g transform="translate({mid_x - 14}, {y_rail_top - 30})">
                <rect x="0" y="0" width="28" height="20" rx="4" fill="#FFF7ED" stroke="#EA580C" stroke-width="1.5" />
                <text x="14" y="14" fill="#EA580C" font-size="10.5" font-weight="800" font-family="'Outfit', sans-serif" text-anchor="middle">⚠️</text>
            </g>
            """)

    # 3. Station Nodes
    for i, stn in enumerate(stations):
        sx = margin_x + (i * dx)
        sy = (y_rail_top + y_rail_bot) / 2
        
        st_type = stn.get("type", "station")
        is_interchange = (st_type == "interchange")
        is_depot = (st_type == "depot")
        is_hub = (st_type in ["railway_hub", "stadium", "terminal"])
        
        node_radius = 8 if not is_interchange else 11
        node_fill = "#FFFFFF"
        node_stroke = "#FF6B00" if is_interchange else ("#0D9488" if is_depot else "#0F172A")
        node_stroke_w = 3 if is_interchange else 2.5

        # Station Circle
        elements.append(f"""
        <!-- Station: {stn['name']} -->
        <circle cx="{sx}" cy="{sy}" r="{node_radius}" fill="{node_fill}" stroke="{node_stroke}" stroke-width="{node_stroke_w}" />
        """)

        if is_interchange:
            elements.append(f"""
            <circle cx="{sx}" cy="{sy}" r="4" fill="#FF6B00" />
            """)

        # Station Label & Badges
        # Alternate text y offset to prevent collision
        label_y = 126 if (i % 2 == 0) else 142
        station_name_short = stn["name"].replace("Railway Station", "Jct").replace("Doordarshan Kendra", "DD Kendra").replace("Gujarat University", "Gujarat Univ").replace("Commerce Six Road", "Commerce Six")

        elements.append(f"""
        <text x="{sx}" y="{label_y}" font-size="10.5" font-weight="600" fill="#1E293B" font-family="'Inter', sans-serif" text-anchor="middle">
            {station_name_short}
        </text>
        """)

        # If special station, add top badge
        if "badge" in stn:
            badge_y = 36
            elements.append(f"""
            <g transform="translate({sx - 38}, {badge_y})">
                <rect x="0" y="0" width="76" height="18" rx="9" fill="#FFF7ED" stroke="#FDBA74" stroke-width="1" />
                <text x="38" y="13" font-size="9" font-weight="800" fill="#EA580C" font-family="'Outfit', sans-serif" text-anchor="middle">
                    {stn['badge']}
                </text>
            </g>
            """)

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="100%" height="{svg_h}" style="display: block; font-family: 'Inter', sans-serif;">
        {''.join(elements)}
    </svg>"""
    return svg_content.strip()

