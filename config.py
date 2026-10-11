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
        "name": "Blue Line (East-West Line)",
        "route_label": "Thaltej Gam ⇄ Vastral Gam",
        "color": "#0066CC",  # Official GMRC Blue Line
        "length_km": 21.16,
        "stations": [
            {"id": "EW-01", "name": "Thaltej Gam", "type": "terminal", "coords": [23.0543, 72.5028]},
            {"id": "EW-02", "name": "Thaltej", "type": "station", "coords": [23.0505, 72.5160]},
            {"id": "EW-03", "name": "Doordarshan Kendra", "type": "station", "coords": [23.0485, 72.5270]},
            {"id": "EW-04", "name": "Gurukul Road", "type": "station", "coords": [23.0465, 72.5350]},
            {"id": "EW-05", "name": "Gujarat University", "type": "station", "coords": [23.0385, 72.5450]},
            {"id": "EW-06", "name": "Commerce Six Road", "type": "station", "coords": [23.0360, 72.5540]},
            {"id": "EW-07", "name": "SP Stadium", "type": "station", "coords": [23.0390, 72.5630]},
            {"id": "EW-08", "name": "Old High Court", "type": "interchange", "badge": "Red Line Interchange", "coords": [23.0375, 72.5715]},
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
        "name": "Red Line (North-South & Gandhinagar)",
        "route_label": "APMC ⇄ Motera Stadium ⇄ Mahatma Mandir",
        "color": "#DC2626",  # Official GMRC Red Line
        "length_km": 47.07,
        "stations": [
            {"id": "NS-01", "name": "APMC", "type": "terminal", "badge": "Gyaspur Depot", "coords": [22.9770, 72.5410]},
            {"id": "NS-02", "name": "Jivraj Park", "type": "station", "coords": [22.9860, 72.5480]},
            {"id": "NS-03", "name": "Rajiv Nagar", "type": "station", "coords": [22.9950, 72.5560]},
            {"id": "NS-04", "name": "Shreyas", "type": "station", "coords": [23.0040, 72.5630]},
            {"id": "NS-05", "name": "Paldi", "type": "station", "coords": [23.0135, 72.5670]},
            {"id": "NS-06", "name": "Gandhigram", "type": "station", "coords": [23.0270, 72.5710]},
            {"id": "NS-07", "name": "Old High Court", "type": "interchange", "badge": "Blue Line Interchange", "coords": [23.0375, 72.5715]},
            {"id": "NS-08", "name": "Usmanpura", "type": "station", "coords": [23.0400, 72.5725]},
            {"id": "NS-09", "name": "Vijay Nagar", "type": "station", "coords": [23.0450, 72.5740]},
            {"id": "NS-10", "name": "Vadaj", "type": "station", "coords": [23.0520, 72.5770]},
            {"id": "NS-11", "name": "Ranip", "type": "station", "coords": [23.0610, 72.5830]},
            {"id": "NS-12", "name": "Sabarmati Railway Station", "type": "railway_hub", "badge": "IR / HSR", "coords": [23.0710, 72.5890]},
            {"id": "NS-13", "name": "Sabarmati", "type": "station", "coords": [23.0805, 72.5930]},
            {"id": "NS-14", "name": "AEC", "type": "station", "badge": "Torrent Power", "coords": [23.0860, 72.5955]},
            {"id": "NS-15", "name": "Motera Stadium", "type": "stadium", "badge": "Cricket Stadium", "coords": [23.0915, 72.5975]},
            {"id": "NS-16", "name": "Koteshwar Road", "type": "station", "coords": [23.1040, 72.6030]},
            {"id": "NS-17", "name": "Vishwakarma College", "type": "station", "coords": [23.1140, 72.6090]},
            {"id": "NS-18", "name": "Tapovan Circle", "type": "station", "coords": [23.1250, 72.6160]},
            {"id": "NS-19", "name": "Narmada Canal", "type": "station", "coords": [23.1360, 72.6240]},
            {"id": "NS-20", "name": "Koba Circle", "type": "station", "coords": [23.1480, 72.6350]},
            {"id": "NS-21", "name": "Juna Koba", "type": "station", "coords": [23.1530, 72.6390]},
            {"id": "NS-22", "name": "Koba Gam", "type": "station", "coords": [23.1570, 72.6430]},
            {"id": "NS-23", "name": "GNLU", "type": "interchange", "badge": "GIFT City Jct", "coords": [23.1610, 72.6470]},
            {"id": "NS-24", "name": "Raysan", "type": "station", "coords": [23.1700, 72.6510]},
            {"id": "NS-25", "name": "Randesan", "type": "station", "coords": [23.1790, 72.6540]},
            {"id": "NS-26", "name": "Dholakuva Circle", "type": "station", "coords": [23.1880, 72.6450]},
            {"id": "NS-27", "name": "Infocity", "type": "hub", "badge": "IT Hub", "coords": [23.1930, 72.6350]},
            {"id": "NS-28", "name": "Sector-1", "type": "station", "coords": [23.2030, 72.6410]},
            {"id": "NS-29", "name": "Sector-10A", "type": "station", "coords": [23.2120, 72.6470]},
            {"id": "NS-30", "name": "Sachivalaya", "type": "hub", "badge": "Secretariat", "coords": [23.2200, 72.6530]},
            {"id": "NS-31", "name": "Akshardham", "type": "hub", "badge": "Temple", "coords": [23.2270, 72.6580]},
            {"id": "NS-32", "name": "Juna Sachivalaya", "type": "station", "coords": [23.2330, 72.6590]},
            {"id": "NS-33", "name": "Sector-16", "type": "station", "coords": [23.2380, 72.6530]},
            {"id": "NS-34", "name": "Sector-24", "type": "station", "coords": [23.2470, 72.6470]},
            {"id": "NS-35", "name": "Mahatma Mandir", "type": "terminal", "badge": "Convention Center", "coords": [23.2540, 72.6410]}
        ]
    },
    "GN Branch": {
        "code": "GN",
        "name": "Violet Line (GIFT City Spur)",
        "route_label": "GNLU ⇄ GIFT City",
        "color": "#8B5CF6",  # Official GMRC Violet Line
        "length_km": 5.4,
        "stations": [
            {"id": "GN-01", "name": "GNLU", "type": "interchange", "badge": "Red Line Jct", "coords": [23.1610, 72.6470]},
            {"id": "GN-02", "name": "PDPU", "type": "station", "badge": "University", "coords": [23.1680, 72.6650]},
            {"id": "GN-03", "name": "GIFT City", "type": "terminal", "badge": "Fintech Hub", "coords": [23.1590, 72.6840]}
        ]
    }
}



