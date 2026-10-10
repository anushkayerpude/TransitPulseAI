"""
TransitPulse AI - Synthetic Data Generator
Generates realistic 14-day operational datasets for Metro, BRTS, and AMTS.
Includes:
- Baseline dataset (normal operations with weekday/weekend variance)
- Incident dataset (injected anomalies on 2026-10-10)
- Corrupted/Invalid dataset for testing validation logic
"""

import os
import random
import pandas as pd
from datetime import datetime, timedelta

def generate_datasets(output_dir="data"):
    # Fix random seed for reproducible, deterministic outputs
    random.seed(42)
    
    start_date = datetime(2026, 9, 27)
    days = 14
    dates = [(start_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days)]
    final_date = dates[-1]  # 2026-10-10
    
    # Corridor and Route configurations
    metro_units = [
        {"name": "East-West Line (Thaltej - Vastral Gam)", "base_ridership": 52000, "scheduled": 150, "delay_range": (0.8, 1.4)},
        {"name": "North-South Line (APMC - Motera Stadium)", "base_ridership": 44000, "scheduled": 140, "delay_range": (0.7, 1.3)},
        {"name": "GN Branch (Koba Circle - GIFT City)", "base_ridership": 18000, "scheduled": 90, "delay_range": (0.5, 1.0)},
    ]
    
    brts_units = [
        {"name": "Route 101: RTO Circle - Maninagar", "base_ridership": 38000, "scheduled": 110, "delay_range": (2.2, 3.8)},
        {"name": "Route 202: Iskcon Cross Road - Naroda", "base_ridership": 34000, "scheduled": 105, "delay_range": (2.5, 4.2)},
        {"name": "Route 303: Shivranjani - Bopal", "base_ridership": 29000, "scheduled": 95, "delay_range": (2.0, 3.5)},
        {"name": "Route 404: Chandkheda - Geeta Mandir", "base_ridership": 32000, "scheduled": 100, "delay_range": (2.8, 4.5)},
        {"name": "Route 505: Vasna - S.P. Ring Road", "base_ridership": 25000, "scheduled": 85, "delay_range": (1.8, 3.2)},
    ]
    
    amts_units = [
        {"name": "Route 13/1: Lal Darwaja - SG Highway", "base_ridership": 48000, "scheduled": 220, "delay_range": (4.5, 7.0)},
        {"name": "Route 40/3: Kalupur Station - Isanpur", "base_ridership": 55000, "scheduled": 240, "delay_range": (5.0, 8.0)},
        {"name": "Route 66/2: Wadaj - Maninagar", "base_ridership": 42000, "scheduled": 200, "delay_range": (4.0, 6.8)},
        {"name": "Route 84/1: Paldi - Narol", "base_ridership": 39000, "scheduled": 190, "delay_range": (4.8, 7.5)},
        {"name": "Route 151: Civil Hospital - Sarkhej", "base_ridership": 52000, "scheduled": 230, "delay_range": (5.2, 8.2)},
    ]

    def build_records(units, operator_name, is_incident=False):
        records = []
        for d_str in dates:
            d_obj = datetime.strptime(d_str, "%Y-%m-%d")
            is_weekend = d_obj.weekday() >= 5
            day_mult = 0.82 if is_weekend else 1.0
            is_target_day = (d_str == final_date)
            
            for u in units:
                base_r = u["base_ridership"] * day_mult
                sched = u["scheduled"]
                if is_weekend:
                    sched = int(sched * 0.88)
                
                # Default variations
                r_var = random.uniform(-0.04, 0.04)
                ridership = int(base_r * (1.0 + r_var))
                comp_pct = random.uniform(0.97, 0.995) if operator_name == "Metro" else (
                    random.uniform(0.94, 0.98) if operator_name == "BRTS" else random.uniform(0.89, 0.94)
                )
                completed = int(sched * comp_pct)
                delay = round(random.uniform(u["delay_range"][0], u["delay_range"][1]), 1)
                
                # INJECT INCIDENTS ON FINAL DAY IF REQUESTED
                if is_incident and is_target_day:
                    if operator_name == "Metro" and "East-West" in u["name"]:
                        # Signaling & Traction power disruption
                        ridership = int(ridership * 0.71) # -29%
                        completed = int(sched * 0.72)     # -28% availability
                        delay = 15.6                      # spike to 15.6 mins
                    elif operator_name == "BRTS" and "Route 303" in u["name"]:
                        # Water main burst near Shivranjani / road collapse
                        ridership = int(ridership * 0.62) # -38%
                        completed = int(sched * 0.83)
                        delay = 10.4                      # spike to 10.4 mins
                    elif operator_name == "BRTS" and "Route 202" in u["name"]:
                        # Minor knock-on delay
                        delay = 6.8
                    elif operator_name == "AMTS" and ("Route 66/2" in u["name"] or "Route 13/1" in u["name"]):
                        # Depot maintenance shortage / bus breakdown
                        ridership = int(ridership * 0.84)
                        completed = int(sched * 0.76)     # availability drops to 76%
                        delay = round(delay * 1.45, 1)
                
                avail_pct = round((completed / sched) * 100, 1) if sched > 0 else 0.0
                
                records.append({
                    "date": d_str,
                    "operator": operator_name,
                    "station_or_route": u["name"],
                    "ridership": ridership,
                    "scheduled_services": sched,
                    "completed_services": completed,
                    "average_delay_minutes": delay,
                    "service_availability_pct": avail_pct
                })
        return pd.DataFrame(records)

    # 1. Generate Baseline Datasets
    baseline_dir = os.path.join(output_dir, "baseline")
    incident_dir = os.path.join(output_dir, "incident")
    invalid_dir = os.path.join(output_dir, "invalid_test")
    os.makedirs(baseline_dir, exist_ok=True)
    os.makedirs(incident_dir, exist_ok=True)
    os.makedirs(invalid_dir, exist_ok=True)
    
    # Save Baseline
    metro_base = build_records(metro_units, "Metro", is_incident=False)
    brts_base = build_records(brts_units, "BRTS", is_incident=False)
    amts_base = build_records(amts_units, "AMTS", is_incident=False)
    
    metro_base.to_csv(os.path.join(baseline_dir, "metro_baseline.csv"), index=False)
    brts_base.to_csv(os.path.join(baseline_dir, "brts_baseline.csv"), index=False)
    amts_base.to_csv(os.path.join(baseline_dir, "amts_baseline.csv"), index=False)

    # Save Incident
    metro_inc = build_records(metro_units, "Metro", is_incident=True)
    brts_inc = build_records(brts_units, "BRTS", is_incident=True)
    amts_inc = build_records(amts_units, "AMTS", is_incident=True)
    
    metro_inc.to_csv(os.path.join(incident_dir, "metro_incident.csv"), index=False)
    brts_inc.to_csv(os.path.join(incident_dir, "brts_incident.csv"), index=False)
    amts_inc.to_csv(os.path.join(incident_dir, "amts_incident.csv"), index=False)
    
    # Save Corrupted / Invalid sample for validation showcase
    invalid_metro = metro_inc.copy()
    invalid_metro["scheduled_services"] = invalid_metro["scheduled_services"].astype(object)
    # Introduce deliberate schema & data issues
    invalid_metro.loc[2, "ridership"] = -500 # negative value
    invalid_metro.loc[5, "date"] = "invalid-date-format"
    invalid_metro.loc[7, "scheduled_services"] = "ABC" # non-numeric
    # Duplicate record
    dup_row = invalid_metro.iloc[[10]]
    invalid_metro = pd.concat([invalid_metro, dup_row], ignore_index=True)
    invalid_metro.to_csv(os.path.join(invalid_dir, "corrupted_metro_sample.csv"), index=False)
    
    print("Successfully generated baseline, incident, and validation test datasets.")

if __name__ == "__main__":
    generate_datasets()
