# 🚇 TransitPulse AI
### AI-Powered Public Transport Operations Intelligence & Daily Briefing System

**Hackathon:** Metro Hacks — DevFest Gandhinagar  
**Problem Statement:** PS-13 — The Two-Minute Morning Brief  
**Product Type:** Web Application / Operational Analytics Dashboard  
**Target Operators:** Metro (GMRC), Janmarg BRTS, and AMTS Operations Teams  
**Version:** 1.0 — Hackathon MVP  

---

## 📌 Executive Summary

TransitPulse AI transforms fragmented daily operational CSV feeds from **Metro**, **BRTS**, and **AMTS** into a unified, actionable **Two-Minute Morning Management Brief**.

Public transport authorities currently spend hours manually reconciling spreadsheets across disparate operators, making it easy to miss service degradations, route cancellations, and headway spikes. **TransitPulse AI** eliminates this latency with:
- **Rigorous Multi-Feed Validation:** Detects schema discrepancies, corrupted dates, and invalid measurements without silent zero-filling.
- **Harmonized Multi-Modal Warehouse:** Normalizes routes, corridors, and telemetry into fair comparisons.
- **Deterministic Exception Detection:** Compares metrics against weekday-adjusted historical baselines to flag critical ridership drops, delay spikes, and fleet availability deficits.
- **Evidence-Backed Explanations:** Formulates transparent, auditable hypotheses backed by telemetry evidence and actionable next steps.
- **One-Page Downloadable Management Brief:** Generates a 1-page PDF briefing and clean printable report in seconds.

---

## 🚀 Key Features

| Capability | Technical Implementation | Value to Transport Authority |
| :--- | :--- | :--- |
| **Multi-Operator Ingestion** | 3 dedicated upload cards for Metro, BRTS, and AMTS CSV feeds | Zero manual cross-spreadsheet copying |
| **Pre-Flight Schema Audit** | Checks column presence, negative values, and date parsing | Prevents bad data from polluting management meetings |
| **Weekday-Adjusted Baselines** | Automatically compares against same-day-of-week averages | Isolates legitimate operational anomalies from normal weekend drops |
| **Severity Scoring Matrix** | 3-tier severity classification (`CRITICAL`, `WARNING`, `INFORMATIONAL`) | Focuses leadership attention on highest-risk corridor incidents |
| **Telemetry Provenance** | Clear separation between observed telemetry facts and hypotheses | No AI hallucinations or unverified assertions |
| **1-Page Executive PDF Export** | Native ReportLab document engine (fits cleanly on 1 page) | Ready for executive morning standup in under 2 minutes |
| **100% Offline Resilience** | Complete deterministic analytics and local rule engine | Operates reliably in network-restricted control room environments |

---

## 🛠️ Tech Stack & Architecture

- **Frontend & App Framework:** [Streamlit](https://streamlit.io/) (Control room UI with high-contrast Dark Navy `#0A192F` and Teal `#14B8A6` palette)
- **Data Engineering:** [Pandas 3.0](https://pandas.pydata.org/) & [NumPy](https://numpy.org/)
- **Visual Analytics:** [Plotly](https://plotly.com/) (Interactive multi-modal trends, availability gauges, and delay waterfalls)
- **PDF Generation:** [ReportLab](https://www.reportlab.com/) (Direct binary 1-page PDF rendering)
- **AI Intelligence Layer:** Built-in Deterministic Domain Engine with optional [Google GenAI SDK](https://github.com/google-gemini/generative-ai-python) integration

---

## ⏱️ Two-Minute Hackathon Demo Script (Judge Walkthrough)

| Time | Action | Demonstration Highlight |
| :--- | :--- | :--- |
| **0:00 – 0:20** | **The Challenge** | Show three separate CSV files (Metro, BRTS, AMTS) and explain the operational friction of manual consolidation. |
| **0:20 – 0:40** | **Pre-Flight Validation** | Click **"🧪 Test Validation Failure"** to showcase pre-flight checking catching corrupted dates and negative ridership with actionable fix suggestions. |
| **0:40 – 1:00** | **Ingestion & Baseline** | Click **"🚨 Load Incidents"** (or upload the sample files) to run the full consolidation pipeline across 14 days of Gandhinagar/Ahmedabad transit data. |
| **1:00 – 1:30** | **Operations Intelligence** | Inspect the 3 deliberately injected incidents detected on the reporting day: <br/>1. **Metro:** Signaling delay spike (+1,080%) on East-West Line.<br/>2. **BRTS:** Corridor ridership drop (-38%) on Route 303 (Shivranjani-Bopal).<br/>3. **AMTS:** Service availability drop to 76% from depot maintenance shortage. |
| **1:30 – 1:50** | **The Morning Brief** | Open **"Two-Minute Daily Brief"** tab: review executive narrative, fleet health index (74/100), and priority operational checklist. |
| **1:50 – 2:00** | **Export & Close** | Click **"📥 Download 1-Page PDF Brief"** to display the downloaded PDF document. |

---

## 🏃 Quickstart Guide

### 1. Prerequisites
- Python 3.10+
- macOS / Linux / Windows

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/anushkayerpuday/TransitPulseAI.git
cd TransitPulseAI

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 3. Generate Demonstration Datasets
```bash
python data/sample_generator.py
```

### 4. Run Automated Test Suite
```bash
python -m unittest tests/test_pipeline.py
```

### 5. Launch Application
```bash
streamlit run app.py
```
Open **`http://localhost:8501`** in your browser.

---

## 📄 License
TransitPulse AI is developed for Metro Hacks — DevFest Gandhinagar (PS-13). All synthetic demonstration data is calibrated to Gandhinagar & Ahmedabad public transit network geographies.
