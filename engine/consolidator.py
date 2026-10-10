"""
TransitPulse AI - Data Consolidation Engine
Combines validated operational datasets from Metro, BRTS, and AMTS into
a unified multi-modal transit intelligence warehouse.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from config import OPERATOR_CONFIG

class ConsolidatedData:
    def __init__(self, unified_df: pd.DataFrame):
        self.raw_df = unified_df
        self.dates = sorted(unified_df["date"].unique().tolist())
        self.operators = sorted(unified_df["operator"].unique().tolist())
        self.latest_date = self.dates[-1] if self.dates else None
        
        # Pre-calculated aggregates
        self.daily_operator_summary = self._build_daily_operator_summary()
        self.daily_citywide_summary = self._build_daily_citywide_summary()
        self.route_level_df = unified_df.copy()

    @property
    def total_records(self) -> int:
        """Total row count across all combined feeds."""
        return len(self.raw_df)

    @property
    def route_count(self) -> int:
        """Total distinct stations and routes across all feeds."""
        return self.raw_df["station_or_route"].nunique() if "station_or_route" in self.raw_df else 0

    @property
    def date_range_str(self) -> str:
        """Formatted date span of the consolidated historical warehouse."""
        return f"{self.dates[0]} to {self.dates[-1]}" if self.dates else ""

    def _build_daily_operator_summary(self) -> pd.DataFrame:
        """Calculates operator-level aggregated metrics for every date."""
        def agg_operator(group):
            total_ridership = group["ridership"].sum()
            total_sched = group["scheduled_services"].sum() if "scheduled_services" in group else np.nan
            total_comp = group["completed_services"].sum() if "completed_services" in group else np.nan
            
            avail = np.nan
            if pd.notna(total_sched) and total_sched > 0 and pd.notna(total_comp):
                avail = round((total_comp / total_sched) * 100.0, 2)
            
            # Average delay
            avg_delay = np.nan
            if "average_delay_minutes" in group and not group["average_delay_minutes"].isna().all():
                avg_delay = round(group["average_delay_minutes"].mean(), 2)

            return pd.Series({
                "ridership": total_ridership,
                "scheduled_services": total_sched,
                "completed_services": total_comp,
                "service_availability_pct": avail,
                "average_delay_minutes": avg_delay,
                "active_routes_count": group["station_or_route"].nunique()
            })

        summary = self.raw_df.groupby(["date", "operator"]).apply(agg_operator).reset_index()
        return summary

    def _build_daily_citywide_summary(self) -> pd.DataFrame:
        """Calculates citywide aggregated transit totals for each date."""
        def agg_city(group):
            total_ridership = group["ridership"].sum()
            total_sched = group["scheduled_services"].sum()
            total_comp = group["completed_services"].sum()
            
            avail = np.nan
            if pd.notna(total_sched) and total_sched > 0:
                avail = round((total_comp / total_sched) * 100.0, 2)
                
            avg_delay = np.nan
            if not group["average_delay_minutes"].isna().all():
                avg_delay = round(group["average_delay_minutes"].mean(), 2)

            return pd.Series({
                "total_ridership": total_ridership,
                "total_scheduled": total_sched,
                "total_completed": total_comp,
                "network_availability_pct": avail,
                "citywide_avg_delay_minutes": avg_delay,
                "reporting_operators_count": group["operator"].nunique()
            })

        summary = self.raw_df.groupby("date").apply(agg_city).reset_index()
        return summary

    def get_date_metrics(self, target_date: str) -> Dict:
        """Fetches all operational metrics for a specific target date."""
        op_data = self.daily_operator_summary[self.daily_operator_summary["date"] == target_date]
        city_data = self.daily_citywide_summary[self.daily_citywide_summary["date"] == target_date]
        
        if city_data.empty:
            return {}
            
        city_row = city_data.iloc[0].to_dict()
        operators_dict = {}
        for _, row in op_data.iterrows():
            operators_dict[row["operator"]] = row.to_dict()
            
        return {
            "date": target_date,
            "citywide": city_row,
            "operators": operators_dict
        }

def consolidate_datasets(dataframes: List[pd.DataFrame]) -> ConsolidatedData:
    """
    Normalizes and merges individual operator DataFrames into ConsolidatedData.
    """
    valid_dfs = [df for df in dataframes if df is not None and not df.empty]
    if not valid_dfs:
        raise ValueError("No valid DataFrames provided for consolidation.")
        
    unified = pd.concat(valid_dfs, ignore_index=True)
    
    # Standardize string formatting
    unified["operator"] = unified["operator"].astype(str).str.strip()
    unified["station_or_route"] = unified["station_or_route"].astype(str).str.strip()
    unified["date"] = pd.to_datetime(unified["date"]).dt.strftime("%Y-%m-%d")
    
    # Sort chronologically and by operator
    unified = unified.sort_values(by=["date", "operator", "station_or_route"]).reset_index(drop=True)
    
    return ConsolidatedData(unified)
