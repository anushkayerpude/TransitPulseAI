"""
TransitPulse AI - Interactive Leaflet GIS Transit Map Component
Renders full-bleed, control-room grade Leaflet.js interactive maps of
Ahmedabad & Gandhinagar GMRC Metro corridors, stations, live train positions,
750V DC third-rail status, and wayside Temporary Speed Restrictions (TSR).
"""

import json
from typing import Dict, Any, Optional
import streamlit.components.v1 as components
from config import GMRC_CORRIDORS, GMRC_TRACK_STATUSES
from engine.track_monitor import GMRCTrackMonitor

def generate_leaflet_map_html(selected_corridor: str = "East-West Line", scenario: str = "nominal") -> str:
    """
    Builds a standalone HTML/JS document embedding Leaflet.js with CartoDB Positron
    light tiles, GMRC metro corridors, interactive station pins, and live train telemetry.
    """
    # Fetch telemetry for all corridors
    corridor_data = {}
    for c_key in GMRC_CORRIDORS.keys():
        corridor_data[c_key] = GMRCTrackMonitor.get_corridor_telemetry(c_key, scenario=scenario)

    active_corr = corridor_data.get(selected_corridor, corridor_data["East-West Line"])
    summary = active_corr["summary"]

    # Serialize corridor data for JavaScript
    corridors_json = json.dumps(corridor_data)
    active_corridor_key = selected_corridor
    active_scenario = scenario

    html_code = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>GMRC Metro GIS Map</title>
    <!-- Leaflet CSS & JS CDN -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin="" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Outfit:wght@600;700;800&display=swap" rel="stylesheet">
    <style>
        html, body {{
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
            font-family: 'Inter', -apple-system, sans-serif;
            background: #FAFAFC;
            overflow: hidden;
        }}
        #map {{
            width: 100%;
            height: 100%;
            border-radius: 12px;
        }}
        /* Station Marker Styles */
        .station-pin {{
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            background: #FFFFFF;
            border: 2.5px solid #FF6B00;
            box-shadow: 0 2px 6px rgba(0,0,0,0.25);
            transition: transform 0.2s ease;
            cursor: pointer;
        }}
        .station-pin:hover {{
            transform: scale(1.25);
            z-index: 1000 !important;
        }}
        .pin-interchange {{
            border: 3.5px solid #FF6B00 !important;
            background: #FFF7ED !important;
            box-shadow: 0 0 12px rgba(255,107,0,0.6) !important;
        }}
        .pin-depot {{
            border: 3px solid #0D9488 !important;
            background: #CCFBF1 !important;
        }}
        .pin-hub {{
            border: 3px solid #2563EB !important;
            background: #EFF6FF !important;
        }}
        /* Pulsing Train Marker */
        .train-marker {{
            position: relative;
            background: #2563EB;
            color: #FFFFFF;
            font-size: 11px;
            font-weight: 800;
            font-family: 'Outfit', sans-serif;
            padding: 3px 8px;
            border-radius: 14px;
            border: 2px solid #FFFFFF;
            box-shadow: 0 4px 12px rgba(37,99,235,0.45);
            white-space: nowrap;
            display: flex;
            align-items: center;
            gap: 4px;
        }}
        .train-marker-alert {{
            background: #EA580C !important;
            box-shadow: 0 4px 12px rgba(234,88,12,0.5) !important;
        }}
        .train-pulse {{
            position: absolute;
            top: -4px;
            left: -4px;
            right: -4px;
            bottom: -4px;
            border-radius: 16px;
            border: 2px solid #38BDF8;
            animation: pulse-ring 1.8s cubic-bezier(0.215, 0.61, 0.355, 1) infinite;
        }}
        @keyframes pulse-ring {{
            0% {{ transform: scale(0.9); opacity: 0.9; }}
            100% {{ transform: scale(1.4); opacity: 0; }}
        }}
        /* Popup Custom Styling */
        .leaflet-popup-content-wrapper {{
            border-radius: 10px;
            box-shadow: 0 6px 20px rgba(0,0,0,0.18);
            border: 1px solid #FED7AA;
            padding: 2px;
        }}
        .leaflet-popup-content {{
            margin: 12px 14px;
            font-family: 'Inter', sans-serif;
            font-size: 12.5px;
            line-height: 1.5;
            color: #1E293B;
        }}
        .popup-title {{
            font-family: 'Outfit', sans-serif;
            font-size: 15px;
            font-weight: 800;
            color: #0F172A;
            margin: 0 0 4px 0;
        }}
        .popup-badge {{
            display: inline-block;
            font-size: 10px;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 10px;
            margin-bottom: 8px;
        }}
        /* Floating HUD Control Box */
        .hud-panel {{
            position: absolute;
            top: 14px;
            right: 14px;
            z-index: 1000;
            background: rgba(255, 255, 255, 0.94);
            backdrop-filter: blur(10px);
            border: 1px solid #FED7AA;
            border-radius: 10px;
            padding: 12px 16px;
            box-shadow: 0 6px 20px rgba(255, 107, 0, 0.12);
            font-size: 12px;
            max-width: 250px;
        }}
        .hud-title {{
            font-family: 'Outfit', sans-serif;
            font-weight: 800;
            font-size: 13px;
            color: #FF6B00;
            margin-bottom: 6px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .hud-item {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 4px;
            color: #475569;
        }}
        .hud-item strong {{
            color: #0F172A;
        }}
        /* Legend Box */
        .legend-panel {{
            position: absolute;
            bottom: 24px;
            left: 14px;
            z-index: 1000;
            background: rgba(255, 255, 255, 0.94);
            backdrop-filter: blur(8px);
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            padding: 10px 14px;
            box-shadow: 0 4px 14px rgba(0,0,0,0.08);
            font-size: 11px;
            color: #334155;
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 5px;
            font-weight: 600;
        }}
        .legend-color {{
            width: 14px;
            height: 4px;
            border-radius: 2px;
        }}
    </style>
</head>
<body>
    <div id="map"></div>

    <!-- HUD Control Box -->
    <div class="hud-panel">
        <div class="hud-title">
            <span>🚇 GMRC OCC RADAR</span>
            <span style="font-size: 10px; background: #ECFDF5; color: #047857; padding: 2px 6px; border-radius: 8px; font-weight: 700;">LIVE</span>
        </div>
        <div class="hud-item">
            <span>Corridor:</span>
            <strong>{active_corr['name'].split('(')[0].strip()}</strong>
        </div>
        <div class="hud-item">
            <span>Wayside Health:</span>
            <strong style="color: {'#EF4444' if summary['fault_blocks'] > 0 else ('#EA580C' if summary['tsr_blocks'] > 0 else '#10B981')};">
                {summary['overall_health']}
            </strong>
        </div>
        <div class="hud-item">
            <span>Active Trains:</span>
            <strong>{summary['active_trains_count']} Active</strong>
        </div>
        <div class="hud-item">
            <span>Operating Headway:</span>
            <strong>{summary['operating_headway_min']:.1f} min</strong>
        </div>
        <div class="hud-item">
            <span>Traction Voltage:</span>
            <strong>{'750V DC (Nominal)' if summary['fault_blocks'] == 0 else '0V DC TRIP'}</strong>
        </div>
    </div>

    <!-- Legend Panel -->
    <div class="legend-panel">
        <div class="legend-item">
            <span class="legend-color" style="background: #FF6B00;"></span>
            <span>East-West (Line 1)</span>
        </div>
        <div class="legend-item">
            <span class="legend-color" style="background: #0D9488;"></span>
            <span>North-South (Line 2)</span>
        </div>
        <div class="legend-item">
            <span class="legend-color" style="background: #8B5CF6;"></span>
            <span>GN Branch (GIFT City)</span>
        </div>
        <div class="legend-item">
            <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:#FF6B00; border:2px solid #FFF7ED;"></span>
            <span>🔄 Interchange</span>
        </div>
        <div class="legend-item">
            <span style="color:#EA580C;">⚠️ TSR 25 km/h</span>
        </div>
    </div>

    <script>
        const corridorData = {corridors_json};
        const activeCorridorKey = "{active_corridor_key}";
        const activeScenario = "{active_scenario}";

        // Initialize Leaflet Map centered on Ahmedabad Metro Center (Old High Court Interchange)
        const map = L.map('map', {{
            zoomControl: true,
            scrollWheelZoom: true,
            attributionControl: true
        }}).setView([23.0375, 72.5715], 12);

        // Add CartoDB Positron clean light tiles with automatic OSM fallback
        const baseLayer = L.tileLayer('https://{{s}}.basemaps.cartocdn.com/light_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
            subdomains: 'abcd',
            maxZoom: 19
        }});
        let fallbackTriggered = false;
        baseLayer.on('tileerror', function() {{
            if (!fallbackTriggered) {{
                fallbackTriggered = true;
                L.tileLayer('https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
                    maxZoom: 19
                }}).addTo(map);
            }}
        }});
        baseLayer.addTo(map);


        // Store all polyline bounds to fit view
        let allCoordinates = [];

        // Render Corridors
        Object.keys(corridorData).forEach(cKey => {{
            const c = corridorData[cKey];
            const stations = c.stations;
            const blocks = c.blocks;
            const color = c.color;
            const isSelected = (cKey === activeCorridorKey);

            // Extract lat-long points
            const linePoints = stations.filter(st => st.coords).map(st => st.coords);
            if (linePoints.length > 0) {{
                allCoordinates = allCoordinates.concat(linePoints);

                // Draw Base Route Polyline
                const polyline = L.polyline(linePoints, {{
                    color: color,
                    weight: isSelected ? 6 : 4,
                    opacity: isSelected ? 0.85 : 0.45,
                    lineCap: 'round',
                    lineJoin: 'round'
                }}).addTo(map);

                // Highlight Block Segments with live status (TSR or Fault)
                blocks.forEach((blk, idx) => {{
                    if (idx < stations.length - 1) {{
                        const p1 = stations[idx].coords;
                        const p2 = stations[idx + 1].coords;
                        if (p1 && p2) {{
                            if (blk.status === "SPEED_RESTRICTION") {{
                                // Glowing Amber TSR segment
                                L.polyline([p1, p2], {{
                                    color: "#EA580C",
                                    weight: 8,
                                    opacity: 0.95,
                                    dashArray: "8, 8"
                                }}).addTo(map).bindPopup(`
                                    <div class="popup-title">⚠️ TSR Active: ${{blk.block_id}}</div>
                                    <span class="popup-badge" style="background:#FFF7ED; color:#EA580C; border:1px solid #FDBA74;">TEMPORARY SPEED RESTRICTION</span>
                                    <div><strong>Segment:</strong> ${{blk.segment_label}}</div>
                                    <div><strong>Speed Cap:</strong> ${{blk.speed_limit_kmh}} km/h (Reduced from 80 km/h)</div>
                                    <div><strong>Reason:</strong> ${{blk.notes}}</div>
                                `);
                            }} else if (blk.status === "POWER_FAULT") {{
                                // Red Fault segment
                                L.polyline([p1, p2], {{
                                    color: "#EF4444",
                                    weight: 8,
                                    opacity: 0.95,
                                    dashArray: "6, 6"
                                }}).addTo(map).bindPopup(`
                                    <div class="popup-title">⚡ Third-Rail Power Trip</div>
                                    <span class="popup-badge" style="background:#FEF2F2; color:#DC2626; border:1px solid #FCA5A5;">0V DC DE-ENERGIZED</span>
                                    <div><strong>Segment:</strong> ${{blk.segment_label}}</div>
                                    <div><strong>Voltage:</strong> 0.0 V DC (Substation Breaker Open)</div>
                                    <div><strong>Incident Note:</strong> ${{blk.notes}}</div>
                                `);
                            }}

                            // If block has active train, place train marker at midpoint
                            if (blk.active_train) {{
                                const midLat = (p1[0] + p2[0]) / 2;
                                const midLng = (p1[1] + p2[1]) / 2;
                                const isDelayed = blk.status === "SPEED_RESTRICTION" || blk.status === "POWER_FAULT";
                                const trainClass = isDelayed ? "train-marker train-marker-alert" : "train-marker";

                                const trainIcon = L.divIcon({{
                                    className: 'custom-train-div',
                                    html: `
                                        <div class="${{trainClass}}">
                                            <div class="train-pulse"></div>
                                            🚆 ${{blk.active_train.split(' ')[0]}}
                                        </div>
                                    `,
                                    iconSize: [85, 26],
                                    iconAnchor: [42, 13]
                                }});

                                L.marker([midLat, midLng], {{ icon: trainIcon, zIndexOffset: 800 }}).addTo(map).bindPopup(`
                                    <div class="popup-title">🚆 ${{blk.active_train}}</div>
                                    <span class="popup-badge" style="background:${{isDelayed ? '#FFF7ED' : '#EFF6FF'}}; color:${{isDelayed ? '#EA580C' : '#2563EB'}};">
                                        ${{isDelayed ? 'DELAYED / HOLDING' : 'AUTOMATIC TRAIN OPERATION (ATO)'}}
                                    </span>
                                    <div><strong>Block Section:</strong> ${{blk.block_id}} (${{blk.segment_label}})</div>
                                    <div><strong>Speed:</strong> ${{blk.actual_speed_kmh}} km/h (Limit: ${{blk.speed_limit_kmh}} km/h)</div>
                                    <div><strong>CBTC Mode:</strong> ${{blk.cbtc_status}}</div>
                                    <div><strong>Third Rail:</strong> ${{blk.third_rail_voltage_v}} V DC</div>
                                `);
                            }}
                        }}
                    }}
                }});

                // Add Station Markers
                stations.forEach(stn => {{
                    if (!stn.coords) return;

                    const isInterchange = (stn.type === "interchange");
                    const isDepot = (stn.type === "depot");
                    const isHub = (stn.type === "railway_hub" || stn.type === "stadium");
                    
                    let pinClass = "station-pin";
                    let pinSize = 14;
                    if (isInterchange) {{
                        pinClass += " pin-interchange";
                        pinSize = 20;
                    }} else if (isDepot) {{
                        pinClass += " pin-depot";
                        pinSize = 16;
                    }} else if (isHub) {{
                        pinClass += " pin-hub";
                        pinSize = 16;
                    }}

                    const markerHtml = `
                        <div class="${{pinClass}}" style="width:${{pinSize}}px; height:${{pinSize}}px; border-color:${{color}};">
                            ${{isInterchange ? '<span style="font-size:10px;">🔄</span>' : (isDepot ? '<span style="font-size:9px;">🏢</span>' : '')}}
                        </div>
                    `;

                    const stationIcon = L.divIcon({{
                        className: 'custom-station-pin',
                        html: markerHtml,
                        iconSize: [pinSize, pinSize],
                        iconAnchor: [pinSize / 2, pinSize / 2]
                    }});

                    const popupContent = `
                        <div class="popup-title">${{stn.name}}</div>
                        <span class="popup-badge" style="background:#FFF7ED; color:#EA580C; border:1px solid #FED7AA;">
                            ${{stn.badge || c.name}}
                        </span>
                        <div><strong>Line:</strong> ${{c.name}} (${{c.code}})</div>
                        <div><strong>Station ID:</strong> ${{stn.id}}</div>
                        <div><strong>Wayside Signaling:</strong> Urbalis 400 CBTC Zone</div>
                        <div><strong>Third Rail:</strong> 750V DC Bottom-Contact Feeder</div>
                        <div style="margin-top:6px; font-size:11px; color:#64748B;">
                            ${{isInterchange ? '🔄 Direct Interchange with Line 2 & High Court Junction' : (isDepot ? '🏢 Apparel Park Central Maintenance & OCC Facility' : '🟢 Automated Passenger Fare Gates & Platform Screen Doors')}}
                        </div>
                    `;

                    L.marker(stn.coords, {{ icon: stationIcon, zIndexOffset: isInterchange ? 500 : 200 }})
                        .addTo(map)
                        .bindPopup(popupContent);
                }});
            }}
        }});

        // Fit map bounds to selected corridor
        const activeStations = activeCorr.stations.filter(st => st.coords).map(st => st.coords);
        if (activeStations.length > 0) {{
            const corridorBounds = L.latLngBounds(activeStations);
            map.fitBounds(corridorBounds, {{ padding: [40, 40] }});
        }} else if (allCoordinates.length > 0) {{
            map.fitBounds(L.latLngBounds(allCoordinates), {{ padding: [30, 30] }});
        }}
    </script>
</body>
</html>
"""
    return html_code


def render_gmrc_leaflet_map(selected_corridor: str = "East-West Line", scenario: str = "nominal", height: int = 580):
    """
    Renders the Leaflet.js interactive GMRC GIS transit map inside Streamlit.
    """
    html_content = generate_leaflet_map_html(selected_corridor=selected_corridor, scenario=scenario)
    components.html(html_content, height=height)
