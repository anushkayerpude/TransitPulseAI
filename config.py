"""
TransitPulse AI - Configuration & Metadata Constants
"""

# App Metadata
APP_NAME = "TransitPulse AI"
APP_SUBTITLE = "AI-Powered Public Transport Operations Intelligence & Daily Briefing System"
HACKATHON_EVENT = "Metro Hacks — DevFest Gandhinagar"
PROBLEM_STATEMENT = "PS-13: The Two-Minute Morning Brief"
VERSION = "1.0 — Hackathon MVP"

# Supported Operators & Regional Context (Ahmedabad / Gandhinagar)
OPERATOR_CONFIG = {
    "Metro": {
        "full_name": "Gujarat Metro Rail Corporation (GMRC)",
        "color": "#FF6B00",  # Ahmedabad Metro Saffron Orange
        "light_color": "#FFF7ED",
        "icon": "🚇",
        "unit_label": "Lines & Corridors",
        "typical_delay_threshold_min": 2.0,
        "critical_delay_threshold_min": 5.0,
        "availability_target_pct": 98.0,
    },
    "BRTS": {
        "full_name": "Janmarg Ahmedabad BRTS",
        "color": "#14B8A6",  # Teal
        "light_color": "#CCFBF1",
        "icon": "🚌",
        "unit_label": "Dedicated Bus Corridors",
        "typical_delay_threshold_min": 4.5,
        "critical_delay_threshold_min": 7.0,
        "availability_target_pct": 95.0,
    },
    "AMTS": {
        "full_name": "Ahmedabad Municipal Transport Service (AMTS)",
        "color": "#F59E0B",  # Amber
        "light_color": "#FEF3C7",
        "icon": "🚍",
        "unit_label": "City Bus Routes",
        "typical_delay_threshold_min": 7.5,
        "critical_delay_threshold_min": 10.0,
        "availability_target_pct": 90.0,
    }
}

# Required & Optional Schema Fields
MANDATORY_COLUMNS = [
    "date",
    "operator",
    "station_or_route",
    "ridership",
]

OPTIONAL_COLUMNS = [
    "scheduled_services",
    "completed_services",
    "average_delay_minutes",
    "service_availability_pct",
]

ALL_COLUMNS = MANDATORY_COLUMNS + OPTIONAL_COLUMNS

# Default Exception Detection Thresholds (Configurable in UI sidebar)
DEFAULT_THRESHOLDS = {
    "ridership_warning_pct": -8.0,       # -8% drop triggers Warning
    "ridership_critical_pct": -15.0,     # -15% drop triggers Critical
    "availability_warning_pct": 92.0,    # below 92% triggers Warning
    "availability_critical_pct": 85.0,   # below 85% triggers Critical
    "delay_warning_delta_pct": 30.0,     # +30% delay jump triggers Warning
    "delay_critical_delta_pct": 75.0,    # +75% delay jump triggers Critical
    "delay_absolute_critical_min": 5.0,  # +5 min absolute delay jump triggers Critical
}

# Severity Styling
SEVERITY_STYLES = {
    "CRITICAL": {
        "badge_bg": "#FEF2F2",
        "badge_text": "#991B1B",
        "border": "#EF4444",
        "icon": "🚨",
        "label": "CRITICAL EXCEPTION"
    },
    "WARNING": {
        "badge_bg": "#FFFBEB",
        "badge_text": "#92400E",
        "border": "#F59E0B",
        "icon": "⚠️",
        "label": "OPERATIONAL WARNING"
    },
    "INFORMATIONAL": {
        "badge_bg": "#EFF6FF",
        "badge_text": "#1E40AF",
        "border": "#3B82F6",
        "icon": "ℹ️",
        "label": "INFORMATIONAL"
    },
    "HEALTHY": {
        "badge_bg": "#ECFDF5",
        "badge_text": "#065F46",
        "border": "#10B981",
        "icon": "✅",
        "label": "NOMINAL"
    }
}

# GMRC Metro Track & Wayside Telemetry Configuration
GMRC_TRACK_STATUSES = {
    "CLEAR": {
        "label": "Track Clear / Nominal",
        "color": "#10B981",
        "badge_bg": "#ECFDF5",
        "border": "#A7F3D0",
        "icon": "🟢",
        "max_speed_kmh": 80
    },
    "OCCUPIED": {
        "label": "Block Occupied (Train Active)",
        "color": "#2563EB",
        "badge_bg": "#EFF6FF",
        "border": "#BFDBFE",
        "icon": "🚆",
        "max_speed_kmh": 75
    },
    "SPEED_RESTRICTION": {
        "label": "Temporary Speed Restriction (TSR)",
        "color": "#EA580C",
        "badge_bg": "#FFF7ED",
        "border": "#FDBA74",
        "icon": "⚠️",
        "max_speed_kmh": 25
    },
    "POWER_FAULT": {
        "label": "Third Rail Power Fault (750V DC)",
        "color": "#DC2626",
        "badge_bg": "#FEF2F2",
        "border": "#FCA5A5",
        "icon": "⚡",
        "max_speed_kmh": 0
    },
    "MAINTENANCE_POSSESSION": {
        "label": "Track Possession Block",
        "color": "#64748B",
        "badge_bg": "#F1F5F9",
        "border": "#CBD5E1",
        "icon": "🔧",
        "max_speed_kmh": 0
    }
}

GMRC_CORRIDORS = {
    "East-West Line": {
        "code": "EW",
        "name": "East-West Line (Line 1)",
        "route_label": "Thaltej Gam ⇄ Vastral Gam",
        "color": "#FF6B00",
        "length_km": 21.16,
        "stations": [
            {"id": "EW-01", "name": "Thaltej Gam", "type": "terminal", "coords": [23.0543, 72.5028]},
            {"id": "EW-02", "name": "Thaltej", "type": "station", "coords": [23.0505, 72.5160]},
            {"id": "EW-03", "name": "Doordarshan Kendra", "type": "station", "coords": [23.0485, 72.5270]},
            {"id": "EW-04", "name": "Gurukul Road", "type": "station", "coords": [23.0465, 72.5350]},
            {"id": "EW-05", "name": "Gujarat University", "type": "station", "coords": [23.0385, 72.5450]},
            {"id": "EW-06", "name": "Commerce Six Road", "type": "station", "coords": [23.0360, 72.5540]},
            {"id": "EW-07", "name": "Stadium", "type": "station", "coords": [23.0390, 72.5630]},
            {"id": "EW-08", "name": "Old High Court", "type": "interchange", "badge": "Line 2 Interchange", "coords": [23.0375, 72.5715]},
            {"id": "EW-09", "name": "Shahpur", "type": "station", "coords": [23.0370, 72.5800]},
            {"id": "EW-10", "name": "Gheekanta", "type": "station", "coords": [23.0315, 72.5890]},
            {"id": "EW-11", "name": "Kalupur Railway Station", "type": "railway_hub", "badge": "IR Junction", "coords": [23.0265, 72.6000]},
            {"id": "EW-12", "name": "Kankaria East", "type": "station", "coords": [23.0120, 72.6060]},
            {"id": "EW-13", "name": "Apparel Park", "type": "depot", "badge": "OCC & Depot", "coords": [23.0070, 72.6200]},
            {"id": "EW-14", "name": "Amraiwadi", "type": "station", "coords": [23.0035, 72.6320]},
            {"id": "EW-15", "name": "Rabari Colony", "type": "station", "coords": [23.0010, 72.6450]},
            {"id": "EW-16", "name": "Vastral", "type": "station", "coords": [22.9990, 72.6570]},
            {"id": "EW-17", "name": "Nirant Cross Road", "type": "station", "coords": [22.9975, 72.6680]},
            {"id": "EW-18", "name": "Vastral Gam", "type": "terminal", "coords": [22.9960, 72.6780]}
        ]
    },
    "North-South Line": {
        "code": "NS",
        "name": "North-South Line (Line 2)",
        "route_label": "Motera Stadium ⇄ APMC",
        "color": "#0D9488",
        "length_km": 18.87,
        "stations": [
            {"id": "NS-01", "name": "Motera Stadium", "type": "stadium", "badge": "Cricket Stadium", "coords": [23.0915, 72.5975]},
            {"id": "NS-02", "name": "Sabarmati", "type": "station", "coords": [23.0805, 72.5930]},
            {"id": "NS-03", "name": "Sabarmati Railway Station", "type": "railway_hub", "badge": "IR / HSR", "coords": [23.0710, 72.5890]},
            {"id": "NS-04", "name": "Ranip", "type": "station", "coords": [23.0610, 72.5830]},
            {"id": "NS-05", "name": "Vadaj", "type": "station", "coords": [23.0520, 72.5770]},
            {"id": "NS-06", "name": "Vijay Nagar", "type": "station", "coords": [23.0450, 72.5740]},
            {"id": "NS-07", "name": "Usmanpura", "type": "station", "coords": [23.0400, 72.5725]},
            {"id": "NS-08", "name": "Old High Court", "type": "interchange", "badge": "Line 1 Interchange", "coords": [23.0375, 72.5715]},
            {"id": "NS-09", "name": "Gandhigram", "type": "station", "coords": [23.0270, 72.5710]},
            {"id": "NS-10", "name": "Paldi", "type": "station", "coords": [23.0135, 72.5670]},
            {"id": "NS-11", "name": "Shreyas", "type": "station", "coords": [23.0040, 72.5630]},
            {"id": "NS-12", "name": "Rajiv Nagar", "type": "station", "coords": [22.9950, 72.5560]},
            {"id": "NS-13", "name": "Jivraj Park", "type": "station", "coords": [22.9860, 72.5480]},
            {"id": "NS-14", "name": "APMC", "type": "terminal", "badge": "Gyaspur Depot", "coords": [22.9770, 72.5410]}
        ]
    },
    "GN Branch": {
        "code": "GN",
        "name": "GN Branch (Phase 2 Link)",
        "route_label": "Koba Circle ⇄ GIFT City",
        "color": "#8B5CF6",
        "length_km": 10.5,
        "stations": [
            {"id": "GN-01", "name": "Koba Circle", "type": "junction", "badge": "Phase 2 Jct", "coords": [23.1480, 72.6350]},
            {"id": "GN-02", "name": "GNLU", "type": "station", "coords": [23.1610, 72.6470]},
            {"id": "GN-03", "name": "PDPU", "type": "station", "coords": [23.1680, 72.6650]},
            {"id": "GN-04", "name": "GIFT City", "type": "terminal", "badge": "Fintech Hub", "coords": [23.1590, 72.6840]}
        ]
    }
}


