"""
TransitPulse AI - Exception & Anomaly Detection Engine
Implements deterministic, transparent analytics to identify transit deviations:
- Method A: Baseline Percentage Deviation (Ridership)
- Method B: Service Availability Thresholds (Completed / Scheduled)
- Method C: Delay Deviation (Historical vs Current Delays)
- Method D: Granular Route/Corridor Outlier Tracing
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any
from config import DEFAULT_THRESHOLDS, OPERATOR_CONFIG
from engine.consolidator import ConsolidatedData

class TransitException:
    def __init__(
        self,
        exception_id: str,
        operator: str,
        scope: str,  # "System-Wide", "Operator Aggregate", or specific route
        metric_name: str,
        current_val: float,
        baseline_val: float,
        abs_change: float,
        pct_change: float,
        severity: str,  # "CRITICAL", "WARNING", "INFORMATIONAL"
        baseline_method: str,
        unit_str: str = "",
        corroborating_facts: Dict[str, Any] = None,
        underlying_records: pd.DataFrame = None
    ):
        self.id = exception_id
        self.operator = operator
        self.scope = scope
        self.metric_name = metric_name
        self.current_val = round(current_val, 2)
        self.baseline_val = round(baseline_val, 2) if pd.notna(baseline_val) else None
        self.abs_change = round(abs_change, 2) if pd.notna(abs_change) else None
        self.pct_change = round(pct_change, 1) if pd.notna(pct_change) else None
        self.severity = severity
        self.baseline_method = baseline_method
        self.unit_str = unit_str
        self.corroborating_facts = corroborating_facts or {}
        self.underlying_records = underlying_records

    def to_dict(self):
        return {
            "id": self.id,
            "operator": self.operator,
            "scope": self.scope,
            "metric": self.metric_name,
            "current_value": self.current_val,
            "baseline_value": self.baseline_val,
            "absolute_change": self.abs_change,
            "percent_change": self.pct_change,
            "severity": self.severity,
            "baseline_method": self.baseline_method,
            "unit": self.unit_str,
            "corroborating_facts": self.corroborating_facts
        }

class DetectionEngine:
    def __init__(self, thresholds: Dict[str, float] = None):
        self.thresholds = thresholds or DEFAULT_THRESHOLDS.copy()

    def detect_exceptions(
        self,
        consolidated: ConsolidatedData,
        target_date: str = None,
        baseline_strategy: str = "same_weekday"  # "same_weekday", "7day_avg", "previous_day"
    ) -> List[TransitException]:
        """
        Runs the full deterministic anomaly detection pipeline on consolidated data.
        """
        if not target_date:
            target_date = consolidated.latest_date
            
        exceptions: List[TransitException] = []
        raw_df = consolidated.raw_df
        op_summary = consolidated.daily_operator_summary
        
        # 1. Determine Historical Baseline Subset
        target_dt = datetime.strptime(target_date, "%Y-%m-%d")
        historical_df = raw_df[raw_df["date"] < target_date].copy()
        
        if historical_df.empty:
            # Not enough historical observations to form a baseline
            return exceptions
            
        target_day_of_week = target_dt.weekday()
        historical_df["weekday"] = pd.to_datetime(historical_df["date"]).dt.weekday
        
        # Filter historical baseline data based on selected strategy
        if baseline_strategy == "same_weekday":
            baseline_raw = historical_df[historical_df["weekday"] == target_day_of_week]
            if baseline_raw.empty:
                baseline_raw = historical_df # Fallback to all history if no same-weekday available
            baseline_desc = "Same-Weekday Historical Baseline"
        elif baseline_strategy == "previous_day":
            prev_date = (target_dt - timedelta(days=1)).strftime("%Y-%m-%d")
            baseline_raw = historical_df[historical_df["date"] == prev_date]
            if baseline_raw.empty:
                baseline_raw = historical_df.tail(len(raw_df["station_or_route"].unique()))
            baseline_desc = "Previous Day (D-1) Baseline"
        else: # 7day_avg
            recent_dates = sorted(historical_df["date"].unique())[-7:]
            baseline_raw = historical_df[historical_df["date"].isin(recent_dates)]
            baseline_desc = "7-Day Rolling Baseline"

        # -------------------------------------------------------------
        # STEP 1: OPERATOR-LEVEL AGGREGATE ANOMALIES
        # -------------------------------------------------------------
        target_op_df = op_summary[op_summary["date"] == target_date]
        
        for _, cur_row in target_op_df.iterrows():
            op = cur_row["operator"]
            op_hist_raw = baseline_raw[baseline_raw["operator"] == op]
            
            if op_hist_raw.empty:
                continue
                
            # Aggregate baseline for this operator
            base_daily = op_hist_raw.groupby("date").agg({
                "ridership": "sum",
                "scheduled_services": "sum",
                "completed_services": "sum",
                "average_delay_minutes": "mean"
            }).mean()
            
            base_ridership = base_daily["ridership"]
            cur_ridership = cur_row["ridership"]
            
            # --- Check A: Operator Ridership Deviation ---
            if base_ridership > 0:
                pct_r_change = ((cur_ridership - base_ridership) / base_ridership) * 100.0
                abs_r_change = cur_ridership - base_ridership
                
                # Check critical threshold
                if pct_r_change <= self.thresholds["ridership_critical_pct"]:
                    exceptions.append(TransitException(
                        exception_id=f"EX-RDR-{op}-CRIT",
                        operator=op,
                        scope=f"{op} Overall Network",
                        metric_name="Total Daily Ridership",
                        current_val=cur_ridership,
                        baseline_val=base_ridership,
                        abs_change=abs_r_change,
                        pct_change=pct_r_change,
                        severity="CRITICAL",
                        baseline_method=baseline_desc,
                        unit_str="passengers",
                        corroborating_facts={
                            "current_passengers": int(cur_ridership),
                            "baseline_passengers": int(base_ridership),
                            "passenger_deficit": int(abs(abs_r_change)),
                            "reported_routes": int(cur_row["active_routes_count"])
                        }
                    ))
                elif pct_r_change <= self.thresholds["ridership_warning_pct"]:
                    exceptions.append(TransitException(
                        exception_id=f"EX-RDR-{op}-WARN",
                        operator=op,
                        scope=f"{op} Overall Network",
                        metric_name="Total Daily Ridership",
                        current_val=cur_ridership,
                        baseline_val=base_ridership,
                        abs_change=abs_r_change,
                        pct_change=pct_r_change,
                        severity="WARNING",
                        baseline_method=baseline_desc,
                        unit_str="passengers",
                        corroborating_facts={
                            "current_passengers": int(cur_ridership),
                            "baseline_passengers": int(base_ridership),
                            "passenger_deficit": int(abs(abs_r_change))
                        }
                    ))

            # --- Check B: Operator Service Availability ---
            cur_avail = cur_row["service_availability_pct"]
            if pd.notna(cur_avail):
                base_avail = (base_daily["completed_services"] / base_daily["scheduled_services"]) * 100.0 if base_daily["scheduled_services"] > 0 else 100.0
                abs_avail_change = cur_avail - base_avail
                pct_avail_change = ((cur_avail - base_avail) / base_avail) * 100.0 if base_avail > 0 else 0.0
                
                if cur_avail < self.thresholds["availability_critical_pct"]:
                    exceptions.append(TransitException(
                        exception_id=f"EX-AVL-{op}-CRIT",
                        operator=op,
                        scope=f"{op} Fleet Operations",
                        metric_name="Service Availability Rate",
                        current_val=cur_avail,
                        baseline_val=base_avail,
                        abs_change=abs_avail_change,
                        pct_change=pct_avail_change,
                        severity="CRITICAL",
                        baseline_method=baseline_desc,
                        unit_str="%",
                        corroborating_facts={
                            "scheduled_trips": int(cur_row["scheduled_services"]),
                            "completed_trips": int(cur_row["completed_services"]),
                            "cancelled_trips": int(cur_row["scheduled_services"] - cur_row["completed_services"]),
                            "availability_pct": float(cur_avail)
                        }
                    ))
                elif cur_avail < self.thresholds["availability_warning_pct"]:
                    exceptions.append(TransitException(
                        exception_id=f"EX-AVL-{op}-WARN",
                        operator=op,
                        scope=f"{op} Fleet Operations",
                        metric_name="Service Availability Rate",
                        current_val=cur_avail,
                        baseline_val=base_avail,
                        abs_change=abs_avail_change,
                        pct_change=pct_avail_change,
                        severity="WARNING",
                        baseline_method=baseline_desc,
                        unit_str="%",
                        corroborating_facts={
                            "scheduled_trips": int(cur_row["scheduled_services"]),
                            "completed_trips": int(cur_row["completed_services"]),
                            "cancelled_trips": int(cur_row["scheduled_services"] - cur_row["completed_services"])
                        }
                    ))

            # --- Check C: Operator Average Delay Spike ---
            cur_delay = cur_row["average_delay_minutes"]
            base_delay = base_daily["average_delay_minutes"]
            if pd.notna(cur_delay) and pd.notna(base_delay) and base_delay > 0:
                abs_delay_change = cur_delay - base_delay
                pct_delay_change = ((cur_delay - base_delay) / base_delay) * 100.0
                
                if (abs_delay_change >= self.thresholds["delay_absolute_critical_min"] or 
                    pct_delay_change >= self.thresholds["delay_critical_delta_pct"]):
                    exceptions.append(TransitException(
                        exception_id=f"EX-DLY-{op}-CRIT",
                        operator=op,
                        scope=f"{op} Network Timetable",
                        metric_name="Average Route Delay",
                        current_val=cur_delay,
                        baseline_val=base_delay,
                        abs_change=abs_delay_change,
                        pct_change=pct_delay_change,
                        severity="CRITICAL",
                        baseline_method=baseline_desc,
                        unit_str="minutes",
                        corroborating_facts={
                            "current_avg_delay": float(cur_delay),
                            "baseline_avg_delay": float(base_delay),
                            "delay_inflation_minutes": float(abs_delay_change)
                        }
                    ))
                elif pct_delay_change >= self.thresholds["delay_warning_delta_pct"]:
                    exceptions.append(TransitException(
                        exception_id=f"EX-DLY-{op}-WARN",
                        operator=op,
                        scope=f"{op} Network Timetable",
                        metric_name="Average Route Delay",
                        current_val=cur_delay,
                        baseline_val=base_delay,
                        abs_change=abs_delay_change,
                        pct_change=pct_delay_change,
                        severity="WARNING",
                        baseline_method=baseline_desc,
                        unit_str="minutes",
                        corroborating_facts={
                            "current_avg_delay": float(cur_delay),
                            "baseline_avg_delay": float(base_delay)
                        }
                    ))

        # -------------------------------------------------------------
        # STEP 2: GRANULAR ROUTE / CORRIDOR SPECIFIC OUTLIERS
        # -------------------------------------------------------------
        target_routes = raw_df[raw_df["date"] == target_date]
        for _, r_cur in target_routes.iterrows():
            op = r_cur["operator"]
            route = r_cur["station_or_route"]
            r_hist = baseline_raw[(baseline_raw["operator"] == op) & (baseline_raw["station_or_route"] == route)]
            
            if r_hist.empty:
                continue
                
            base_r_mean = r_hist["ridership"].mean()
            cur_r = r_cur["ridership"]
            cur_delay = r_cur["average_delay_minutes"] if "average_delay_minutes" in r_cur else np.nan
            base_delay_mean = r_hist["average_delay_minutes"].mean() if "average_delay_minutes" in r_hist else np.nan
            cur_comp = r_cur["completed_services"] if "completed_services" in r_cur else np.nan
            cur_sched = r_cur["scheduled_services"] if "scheduled_services" in r_cur else np.nan
            
            # Check severe single corridor drops (> 20% drop)
            if base_r_mean > 0:
                pct_drop = ((cur_r - base_r_mean) / base_r_mean) * 100.0
                if pct_drop <= -20.0:
                    sev = "CRITICAL" if pct_drop <= -28.0 else "WARNING"
                    exceptions.append(TransitException(
                        exception_id=f"EX-LOC-{op}-{hash(route)%10000}",
                        operator=op,
                        scope=f"{route}",
                        metric_name="Corridor Ridership Drop",
                        current_val=cur_r,
                        baseline_val=base_r_mean,
                        abs_change=cur_r - base_r_mean,
                        pct_change=pct_drop,
                        severity=sev,
                        baseline_method=baseline_desc,
                        unit_str="passengers",
                        corroborating_facts={
                            "corridor_delay": float(cur_delay) if pd.notna(cur_delay) else "N/A",
                            "corridor_baseline_delay": float(base_delay_mean) if pd.notna(base_delay_mean) else "N/A",
                            "completed_trips": int(cur_comp) if pd.notna(cur_comp) else "N/A",
                            "scheduled_trips": int(cur_sched) if pd.notna(cur_sched) else "N/A"
                        },
                        underlying_records=pd.DataFrame([r_cur.to_dict()])
                    ))
                    
            # Check severe single corridor delay spikes (> 7 min delay spike)
            if pd.notna(cur_delay) and pd.notna(base_delay_mean):
                delay_delta = cur_delay - base_delay_mean
                if delay_delta >= 6.0:
                    exceptions.append(TransitException(
                        exception_id=f"EX-LOCDLY-{op}-{hash(route)%10000}",
                        operator=op,
                        scope=f"{route}",
                        metric_name="Corridor Extreme Delay Spike",
                        current_val=cur_delay,
                        baseline_val=base_delay_mean,
                        abs_change=delay_delta,
                        pct_change=((cur_delay - base_delay_mean) / base_delay_mean) * 100.0 if base_delay_mean > 0 else 100.0,
                        severity="CRITICAL",
                        baseline_method=baseline_desc,
                        unit_str="minutes",
                        corroborating_facts={
                            "corridor_delay_min": float(cur_delay),
                            "normal_delay_min": float(base_delay_mean),
                            "ridership": int(cur_r)
                        },
                        underlying_records=pd.DataFrame([r_cur.to_dict()])
                    ))

        # Sort exceptions: CRITICAL first, then WARNING, then INFORMATIONAL
        severity_order = {"CRITICAL": 0, "WARNING": 1, "INFORMATIONAL": 2}
        exceptions.sort(key=lambda ex: (severity_order.get(ex.severity, 99), abs(ex.pct_change or 0)), reverse=False)
        
        return exceptions
