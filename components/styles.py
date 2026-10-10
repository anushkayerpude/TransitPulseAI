"""
TransitPulse AI - White & Ahmedabad Metro Orange Design System
Inspired by Gujarat Metro Rail Corporation (GMRC) branding:
Pure White (#FFFFFF), Warm Cream (#FFF7ED), Vibrant Metro Orange (#FF6B00 / #EA580C),
Dark Slate typography (#0F172A), and Clean Modern Cards.
"""

CUSTOM_CSS = """
<style>
/* Import Inter & Outfit Fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Outfit:wght@500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Base App Theme - Clean White & Warm Light Slate */
.stApp {
    background-color: #FAFAFC;
    color: #0F172A;
}

/* Header Adjustments */
header[data-testid="stHeader"] {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    border-bottom: 2px solid #FF6B00;
}

/* Sidebar Customization - Crisp White with Orange Accents */
section[data-testid="stSidebar"] {
    background-color: #FFFFFF;
    border-right: 1px solid #E2E8F0;
}

section[data-testid="stSidebar"] .block-container {
    padding-top: 1.5rem;
}

/* Sidebar Branding Card */
.hackathon-sidebar-card {
    background: linear-gradient(135deg, #FFF7ED 0%, #FFEDD5 100%);
    border: 1px solid #FED7AA;
    border-left: 4px solid #FF6B00;
    border-radius: 10px;
    padding: 14px 16px;
    margin-bottom: 20px;
    box-shadow: 0 2px 8px rgba(255, 107, 0, 0.08);
}

/* Primary Streamlit Buttons - Ahmedabad Orange */
div.stButton > button[kind="primary"],
div.stButton > button:first-child:not([kind="secondary"]) {
    background: linear-gradient(135deg, #FF6B00 0%, #EA580C 100%) !important;
    color: #FFFFFF !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 8px 18px !important;
    box-shadow: 0 4px 12px rgba(255, 107, 0, 0.25) !important;
    transition: all 0.2s ease !important;
}

div.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 16px rgba(255, 107, 0, 0.35) !important;
}

/* Download Buttons */
div.stDownloadButton > button {
    background: linear-gradient(135deg, #FF6B00 0%, #EA580C 100%) !important;
    color: #FFFFFF !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 8px !important;
    box-shadow: 0 4px 12px rgba(255, 107, 0, 0.25) !important;
}

/* Tabs Navigation - White and Ahmedabad Orange Pill Style */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background-color: #F1F5F9;
    padding: 6px;
    border-radius: 12px;
    border: 1px solid #E2E8F0;
    margin-bottom: 18px;
}

.stTabs [data-baseweb="tab"] {
    height: 44px;
    padding: 0 22px;
    background-color: transparent;
    border-radius: 8px;
    color: #475569;
    font-weight: 600;
    font-size: 13.5px;
    border: none;
    transition: all 0.2s ease;
}

.stTabs [data-baseweb="tab"]:hover {
    background-color: #E2E8F0;
    color: #0F172A;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #FF6B00 0%, #EA580C 100%) !important;
    color: #FFFFFF !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 12px rgba(255, 107, 0, 0.28) !important;
}

/* Metric KPI Cards (White & Orange) */
.kpi-card {
    background: #FFFFFF;
    border: 1px solid #FED7AA;
    border-radius: 12px;
    padding: 18px 20px;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.04);
    position: relative;
    overflow: hidden;
    transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}

.kpi-card:hover {
    border-color: #FF6B00;
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(255, 107, 0, 0.12);
}

.kpi-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}

.kpi-title {
    font-size: 11.5px;
    font-weight: 700;
    color: #64748B;
    text-transform: uppercase;
    letter-spacing: 0.6px;
}

.kpi-icon {
    font-size: 20px;
}

.kpi-value {
    font-size: 28px;
    font-weight: 800;
    color: #0F172A;
    line-height: 1.1;
    font-family: 'Outfit', sans-serif;
}

.kpi-sub {
    font-size: 12px;
    color: #64748B;
    margin-top: 6px;
    display: flex;
    align-items: center;
    gap: 6px;
}

/* Section Titles with Orange Underline Indicator */
.section-title {
    display: flex;
    align-items: center;
    font-family: 'Outfit', sans-serif;
    font-size: 18px;
    font-weight: 700;
    color: #0F172A;
    margin: 24px 0 16px 0;
    padding-bottom: 8px;
    border-bottom: 2px solid #FED7AA;
}

.section-title span {
    border-bottom: 3px solid #FF6B00;
    padding-bottom: 7px;
    margin-bottom: -10px;
}

/* Operator Status Cards */
.op-card-metro {
    background: #FFFFFF;
    border: 1px solid #FED7AA;
    border-top: 4px solid #FF6B00;
    border-radius: 12px;
    padding: 18px 20px;
    box-shadow: 0 4px 14px rgba(255, 107, 0, 0.06);
}

.op-card-brts {
    background: #FFFFFF;
    border: 1px solid #CCFBF1;
    border-top: 4px solid #0D9488;
    border-radius: 12px;
    padding: 18px 20px;
    box-shadow: 0 4px 14px rgba(13, 148, 136, 0.06);
}

.op-card-amts {
    background: #FFFFFF;
    border: 1px solid #FEF3C7;
    border-top: 4px solid #D97706;
    border-radius: 12px;
    padding: 18px 20px;
    box-shadow: 0 4px 14px rgba(217, 119, 6, 0.06);
}

/* Exception Cards (White & Elevated) */
.exception-box {
    background: #FFFFFF;
    border-radius: 12px;
    padding: 22px;
    margin-bottom: 18px;
    border-left: 6px solid;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
    border-top: 1px solid #F1F5F9;
    border-right: 1px solid #F1F5F9;
    border-bottom: 1px solid #F1F5F9;
    transition: transform 0.2s ease;
}

.exception-box:hover {
    transform: translateY(-1px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

.exception-critical {
    border-left-color: #EF4444;
    background: linear-gradient(180deg, #FFFDFD 0%, #FFFFFF 100%);
}

.exception-warning {
    border-left-color: #F59E0B;
    background: linear-gradient(180deg, #FFFDF5 0%, #FFFFFF 100%);
}

.exception-info {
    border-left-color: #0284C7;
    background: linear-gradient(180deg, #F8FAFC 0%, #FFFFFF 100%);
}

.ex-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 12px;
}

.ex-title {
    font-family: 'Outfit', sans-serif;
    font-size: 17px;
    font-weight: 700;
    color: #0F172A;
    margin: 4px 0 0 0;
}

.pill-crit {
    background: #EF4444;
    color: #FFFFFF;
    font-size: 11px;
    font-weight: 800;
    padding: 4px 12px;
    border-radius: 20px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.pill-warn {
    background: #F59E0B;
    color: #FFFFFF;
    font-size: 11px;
    font-weight: 800;
    padding: 4px 12px;
    border-radius: 20px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.ex-observation {
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 12px 16px;
    font-size: 13.5px;
    color: #334155;
    margin-bottom: 14px;
    line-height: 1.5;
}

.evidence-box {
    background: #FFF7ED;
    border: 1px solid #FED7AA;
    border-radius: 8px;
    padding: 14px 18px;
    font-size: 13px;
    color: #7C2D12;
    margin-bottom: 12px;
}

.hypothesis-box {
    background: #F0FDF4;
    border: 1px solid #BBF7D0;
    border-radius: 8px;
    padding: 14px 18px;
    font-size: 13px;
    color: #14532D;
    margin-bottom: 12px;
}

.action-box {
    background: #FFFBEB;
    border: 1px solid #FDE68A;
    border-radius: 8px;
    padding: 14px 18px;
    font-size: 13px;
    color: #78350F;
}

/* Realistic Landing Page Styles */
.landing-hero-container {
    position: relative;
    border-radius: 16px;
    overflow: hidden;
    margin-bottom: 28px;
    box-shadow: 0 10px 30px rgba(255, 107, 0, 0.12);
    border: 2px solid #FED7AA;
}

.landing-overlay-card {
    background: rgba(255, 255, 255, 0.94);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(254, 215, 170, 0.8);
    border-radius: 14px;
    padding: 24px 28px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
}

.metro-badge-tag {
    background: linear-gradient(135deg, #FF6B00 0%, #EA580C 100%);
    color: #FFFFFF;
    font-size: 11px;
    font-weight: 800;
    padding: 4px 12px;
    border-radius: 20px;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    letter-spacing: 0.6px;
    text-transform: uppercase;
}

.corridor-pill {
    background: #FFFFFF;
    border: 1px solid #FED7AA;
    border-radius: 10px;
    padding: 14px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    transition: all 0.2s ease;
}

.corridor-pill:hover {
    border-color: #FF6B00;
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(255, 107, 0, 0.1);
}

/* Expander Styling */
.streamlit-expanderHeader {
    background-color: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 8px !important;
    color: #0F172A !important;
    font-weight: 600 !important;
}

/* Plotly Chart Card Container */
.chart-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 16px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.03);
}

/* ========================================================================= */
/* SCROLL MOTION & FULL-PAGE SECTION SYSTEM                                 */
/* ========================================================================= */
html, body, [data-testid="stAppViewContainer"], section.main {
    scroll-behavior: smooth !important;
}

[id^="section-"] {
    scroll-margin-top: 85px;
    display: block;
    position: relative;
}

.scroll-container {
    scroll-snap-type: y proximity;
    overflow-y: visible;
}

.fullpage-section {
    min-height: 92vh;
    padding: 24px 8px 48px 8px;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    position: relative;
    border-bottom: 2px dashed #FED7AA;
    margin-bottom: 36px;
}

.page-indicator-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: #FFF7ED;
    border: 1px solid #FED7AA;
    color: #EA580C;
    font-size: 11px;
    font-weight: 800;
    padding: 5px 16px;
    border-radius: 20px;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    margin-bottom: 16px;
    width: fit-content;
    box-shadow: 0 2px 8px rgba(255, 107, 0, 0.06);
}

.scroll-prompt-bar {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    background: linear-gradient(135deg, #FFF7ED 0%, #FFFFFF 100%);
    border: 1.5px solid #FED7AA;
    border-radius: 30px;
    padding: 10px 24px;
    margin-top: 24px;
    box-shadow: 0 4px 16px rgba(255, 107, 0, 0.08);
    cursor: pointer;
    text-decoration: none;
    color: #0F172A;
    font-weight: 700;
    font-size: 13px;
    transition: all 0.2s ease;
    width: fit-content;
    margin-left: auto;
    margin-right: auto;
}

.scroll-prompt-bar:hover {
    transform: translateY(-2px);
    border-color: #FF6B00;
    box-shadow: 0 6px 20px rgba(255, 107, 0, 0.16);
    color: #EA580C;
}

@keyframes bouncePrompt {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(5px); }
}

.bounce-icon {
    display: inline-block;
    animation: bouncePrompt 1.4s ease-in-out infinite;
}

/* Floating Navigation Dock (Quick Page Jumper) */
.floating-scroll-nav {
    position: sticky;
    top: 50px;
    z-index: 999;
    background: rgba(255, 255, 255, 0.94);
    backdrop-filter: blur(14px);
    border: 1.5px solid #FED7AA;
    border-radius: 40px;
    padding: 7px 16px;
    box-shadow: 0 8px 30px rgba(255, 107, 0, 0.12);
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 10px;
    margin: 0 auto 26px auto;
    max-width: 860px;
    flex-wrap: wrap;
}

.nav-jump-btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
    text-decoration: none !important;
    color: #475569 !important;
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    transition: all 0.2s ease;
}

.nav-jump-btn:hover {
    background: #FFF7ED !important;
    color: #EA580C !important;
    border-color: #FF6B00 !important;
    transform: translateY(-1px);
}

/* Doodly Metro Landing Page Stage */
.doodle-hero-container {
    position: relative;
    width: 100%;
    min-height: 84vh;
    border-radius: 18px;
    overflow: hidden;
    border: 2px solid #FED7AA;
    box-shadow: 0 12px 40px rgba(255, 107, 0, 0.1);
    background: #FFFDF9;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
}

.doodle-hero-floating-card {
    position: absolute;
    top: 24px;
    left: 24px;
    max-width: 640px;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(14px);
    border: 1.5px solid rgba(254, 215, 170, 0.9);
    border-radius: 16px;
    padding: 22px 26px;
    box-shadow: 0 10px 36px rgba(0, 0, 0, 0.08);
    z-index: 10;
}
</style>
"""
