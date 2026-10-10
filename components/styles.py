"""
TransitPulse AI - Custom Operations Control Center Styling
Color Palette: Deep Navy (#0A192F), Midnight (#0F2444), Teal (#0D9488, #14B8A6),
Slate Neutral, and Clear Status Colors (Red, Amber, Emerald).
"""

CUSTOM_CSS = """
<style>
/* Import Inter Font */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Header & Title Adjustments */
header[data-testid="stHeader"] {
    background: rgba(10, 25, 47, 0.95);
    backdrop-filter: blur(8px);
}

.stApp {
    background-color: #0B132B;
    color: #F1F5F9;
}

/* Sidebar Customization */
section[data-testid="stSidebar"] {
    background-color: #0A192F;
    border-right: 1px solid #1E293B;
}

/* Control Room Header Banner */
.ops-banner {
    background: linear-gradient(135deg, #0A192F 0%, #112240 60%, #0F3854 100%);
    border: 1px solid #1E3A5F;
    border-radius: 12px;
    padding: 22px 28px;
    margin-bottom: 24px;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.ops-title-block h1 {
    font-size: 26px;
    font-weight: 800;
    color: #F8FAFC;
    margin: 0;
    letter-spacing: -0.5px;
}

.ops-title-block p {
    font-size: 13px;
    color: #94A3B8;
    margin: 4px 0 0 0;
    font-weight: 500;
}

.ops-live-badge {
    background: rgba(13, 148, 136, 0.15);
    border: 1px solid #14B8A6;
    color: #2DD4BF;
    font-size: 11px;
    font-weight: 700;
    padding: 6px 14px;
    border-radius: 20px;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.ops-live-dot {
    width: 8px;
    height: 8px;
    background-color: #2DD4BF;
    border-radius: 50%;
    box-shadow: 0 0 8px #2DD4BF;
}

/* Top Navigation Tabs Styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background-color: #0A192F;
    padding: 6px;
    border-radius: 10px;
    border: 1px solid #1E293B;
}

.stTabs [data-baseweb="tab"] {
    height: 42px;
    padding: 0 20px;
    background-color: transparent;
    border-radius: 6px;
    color: #94A3B8;
    font-weight: 600;
    font-size: 13px;
    border: none;
    transition: all 0.2s ease;
}

.stTabs [aria-selected="true"] {
    background-color: #14B8A6 !important;
    color: #0A192F !important;
    font-weight: 700 !important;
}

/* Metric KPI Cards */
.kpi-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
    margin-bottom: 24px;
}

.kpi-card {
    background: #0F172A;
    border: 1px solid #1E293B;
    border-radius: 10px;
    padding: 18px 20px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    position: relative;
    overflow: hidden;
    transition: transform 0.2s ease, border-color 0.2s ease;
}

.kpi-card:hover {
    border-color: #0D9488;
    transform: translateY(-2px);
}

.kpi-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}

.kpi-title {
    font-size: 12px;
    font-weight: 600;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.kpi-icon {
    font-size: 18px;
}

.kpi-value {
    font-size: 26px;
    font-weight: 800;
    color: #F8FAFC;
    line-height: 1.1;
    font-family: 'Inter', sans-serif;
}

.kpi-sub {
    font-size: 12px;
    color: #64748B;
    margin-top: 6px;
    display: flex;
    align-items: center;
    gap: 4px;
}

/* Operator Status Badges */
.badge-metro {
    background: rgba(56, 189, 248, 0.15);
    border: 1px solid #38BDF8;
    color: #38BDF8;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 700;
}

.badge-brts {
    background: rgba(20, 184, 166, 0.15);
    border: 1px solid #14B8A6;
    color: #2DD4BF;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 700;
}

.badge-amts {
    background: rgba(245, 158, 11, 0.15);
    border: 1px solid #F59E0B;
    color: #FBBF24;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 700;
}

/* Exception Cards */
.exception-box {
    background: #0F172A;
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 16px;
    border-left: 5px solid;
    box-shadow: 0 4px 12px rgba(0,0,0,0.25);
}

.exception-critical {
    border-left-color: #EF4444;
    border-top: 1px solid rgba(239, 68, 68, 0.3);
    border-right: 1px solid rgba(239, 68, 68, 0.2);
    border-bottom: 1px solid rgba(239, 68, 68, 0.2);
}

.exception-warning {
    border-left-color: #F59E0B;
    border-top: 1px solid rgba(245, 158, 11, 0.3);
    border-right: 1px solid rgba(245, 158, 11, 0.2);
    border-bottom: 1px solid rgba(245, 158, 11, 0.2);
}

.exception-info {
    border-left-color: #3B82F6;
    border-top: 1px solid rgba(59, 130, 246, 0.3);
    border-right: 1px solid rgba(59, 130, 246, 0.2);
    border-bottom: 1px solid rgba(59, 130, 246, 0.2);
}

.ex-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 12px;
}

.ex-title {
    font-size: 16px;
    font-weight: 700;
    color: #F8FAFC;
    margin: 0;
}

.pill-crit {
    background: #EF4444;
    color: #FFFFFF;
    font-size: 11px;
    font-weight: 800;
    padding: 3px 10px;
    border-radius: 20px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.pill-warn {
    background: #F59E0B;
    color: #000000;
    font-size: 11px;
    font-weight: 800;
    padding: 3px 10px;
    border-radius: 20px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.ex-observation {
    font-size: 13.5px;
    color: #CBD5E1;
    margin-bottom: 12px;
    line-height: 1.5;
}

.evidence-box {
    background: rgba(15, 23, 42, 0.8);
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 10px 14px;
    margin-bottom: 12px;
    font-size: 12.5px;
    color: #94A3B8;
}

.action-box {
    background: rgba(20, 184, 166, 0.08);
    border-left: 3px solid #14B8A6;
    padding: 10px 14px;
    border-radius: 0 6px 6px 0;
    font-size: 13px;
    color: #E2E8F0;
    margin-top: 10px;
}

/* Upload Cards */
.upload-card {
    background: #0F172A;
    border: 1px dashed #334155;
    border-radius: 10px;
    padding: 18px;
    text-align: center;
    transition: all 0.2s ease;
}

.upload-card:hover {
    border-color: #14B8A6;
    background: #111E38;
}

/* Section Headings */
.section-title {
    font-size: 18px;
    font-weight: 700;
    color: #F8FAFC;
    margin: 20px 0 12px 0;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* Hackathon Badge in Sidebar */
.hackathon-sidebar-card {
    background: #0F1D38;
    border: 1px solid #1E3A5F;
    border-radius: 8px;
    padding: 14px;
    margin-bottom: 16px;
}
</style>
"""
