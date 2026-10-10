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
        "color": "#38BDF8",  # Sky / Rail Blue
        "light_color": "#E0F2FE",
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
