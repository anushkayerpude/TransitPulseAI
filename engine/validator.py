"""
TransitPulse AI - Data Validation Engine
Validates CSV files uploaded for Metro, BRTS, and AMTS.
Enforces:
- Mandatory schema compliance
- Strict type checking without silent zero-fills
- Missing value audit
- Duplicate record detection
- Logical operational rules (e.g. non-negative counts, availability bounds)
"""

import io
import re
import pandas as pd
import numpy as np
from datetime import datetime
from config import MANDATORY_COLUMNS, OPTIONAL_COLUMNS

class ValidationResult:
    def __init__(self, is_valid: bool, filename: str, operator_detected: str = "Unknown"):
        self.is_valid = is_valid
        self.filename = filename
        self.operator_detected = operator_detected
        self.row_count = 0
        self.date_range = (None, None)
        self.unique_dates_count = 0
        self.unique_units_count = 0
        self.errors = []       # Blockers that prevent analytical processing
        self.warnings = []     # Data quality notices (missing optional metrics, etc.)
        self.cleaned_df = None

    def add_error(self, issue: str, column: str = None, row_index: int = None, fix_suggestion: str = None):
        self.errors.append({
            "severity": "ERROR",
            "issue": issue,
            "column": column,
            "row": row_index,
            "fix": fix_suggestion or "Correct the CSV cell before proceeding."
        })
        self.is_valid = False

    def add_warning(self, issue: str, column: str = None, impact: str = None):
        self.warnings.append({
            "severity": "WARNING",
            "issue": issue,
            "column": column,
            "impact": impact or "Will be flagged as unavailable in comparative views."
        })

    def summary_dict(self):
        return {
            "filename": self.filename,
            "is_valid": self.is_valid,
            "operator": self.operator_detected,
            "row_count": self.row_count,
            "unique_dates": self.unique_dates_count,
            "date_range": f"{self.date_range[0]} to {self.date_range[1]}" if self.date_range[0] else "N/A",
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
        }

def validate_csv(file_or_path, expected_operator: str = None) -> ValidationResult:
    """
    Validates a CSV file buffer or file path.
    """
    filename = getattr(file_or_path, "name", str(file_or_path))
    result = ValidationResult(is_valid=True, filename=filename)
    
    # 1. Read CSV
    try:
        if hasattr(file_or_path, "read"):
            # Streamlit UploadedFile or BytesIO
            if hasattr(file_or_path, "seek"):
                file_or_path.seek(0)
            df = pd.read_csv(file_or_path)
        else:
            df = pd.read_csv(file_or_path)
    except Exception as e:
        result.add_error(f"Failed to parse CSV file: {str(e)}", fix_suggestion="Ensure file is valid UTF-8 CSV text.")
        return result

    if df.empty:
        result.add_error("The uploaded file is empty (0 rows).", fix_suggestion="Upload a CSV with operational data rows.")
        return result

    result.row_count = len(df)
    
    # Normalize column names (strip whitespace, lowercase)
    df.columns = [str(c).strip().lower() for c in df.columns]
    
    # 2. Check Mandatory Columns
    missing_cols = [col for col in MANDATORY_COLUMNS if col not in df.columns]
    if missing_cols:
        result.add_error(
            f"Missing required columns: {', '.join(missing_cols)}",
            fix_suggestion=f"Your CSV must include: {', '.join(MANDATORY_COLUMNS)}"
        )
        return result
    
    # Check operator content
    detected_operators = df["operator"].dropna().unique().tolist()
    if len(detected_operators) == 0:
        result.add_error("Column 'operator' contains only empty or NaN values.", column="operator")
        return result
    
    norm_detected = detected_operators[0].strip().title()
    if norm_detected.lower() == "brts":
        norm_detected = "BRTS"
    elif norm_detected.lower() == "amts":
        norm_detected = "AMTS"
    elif norm_detected.lower() == "metro":
        norm_detected = "Metro"
    result.operator_detected = norm_detected
    
    if expected_operator and norm_detected.lower() != expected_operator.lower():
        result.add_warning(
            f"File uploaded to '{expected_operator}' slot contains operator identifier '{norm_detected}'.",
            column="operator",
            impact=f"Data will be normalized as {norm_detected}."
        )

    # 3. Check Date Format and Validity
    parsed_dates = []
    invalid_date_rows = []
    
    for idx, raw_val in df["date"].items():
        if pd.isna(raw_val) or str(raw_val).strip() == "":
            invalid_date_rows.append((idx + 2, "Missing/blank date"))
            continue
        val_str = str(raw_val).strip()
        parsed = None
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y", "%Y/%m/%d"):
            try:
                parsed = datetime.strptime(val_str, fmt).strftime("%Y-%m-%d")
                break
            except ValueError:
                pass
        if parsed:
            parsed_dates.append(parsed)
        else:
            invalid_date_rows.append((idx + 2, f"Unrecognized date '{val_str}'"))
    
    if invalid_date_rows:
        sample_bad = invalid_date_rows[:3]
        sample_str = "; ".join([f"Row {r}: {msg}" for r, msg in sample_bad])
        result.add_error(
            f"Found {len(invalid_date_rows)} invalid date entries ({sample_str}).",
            column="date",
            fix_suggestion="Format dates as YYYY-MM-DD or DD/MM/YYYY."
        )
    else:
        df["date"] = parsed_dates
        dates_sorted = sorted(set(parsed_dates))
        result.date_range = (dates_sorted[0], dates_sorted[-1])
        result.unique_dates_count = len(dates_sorted)

    # 4. Station or Route column check
    blank_units = df["station_or_route"].isna() | (df["station_or_route"].astype(str).str.strip() == "")
    if blank_units.any():
        bad_count = blank_units.sum()
        result.add_error(
            f"Found {bad_count} rows with missing 'station_or_route' identifiers.",
            column="station_or_route",
            fix_suggestion="Every observation must specify a corridor, station, or route identifier."
        )
    else:
        result.unique_units_count = df["station_or_route"].nunique()

    # 5. Check Numeric Measurements (No Silent Zero Filling)
    # Check Ridership
    numeric_ridership = pd.to_numeric(df["ridership"], errors="coerce")
    nan_ridership_count = numeric_ridership.isna().sum()
    if nan_ridership_count > 0:
        result.add_error(
            f"Found {nan_ridership_count} invalid or non-numeric ridership records. (Missing data must not be silently converted to zero).",
            column="ridership",
            fix_suggestion="Provide valid non-negative integer passenger counts for all observations."
        )
    else:
        negative_ridership = (numeric_ridership < 0).sum()
        if negative_ridership > 0:
            result.add_error(
                f"Found {negative_ridership} negative ridership values.",
                column="ridership",
                fix_suggestion="Ridership values cannot be negative."
            )
        else:
            df["ridership"] = numeric_ridership.astype(int)

    # Check Scheduled Services (if present)
    sched_is_valid = False
    if "scheduled_services" in df.columns:
        sched_num = pd.to_numeric(df["scheduled_services"], errors="coerce")
        bad_sched = sched_num.isna().sum()
        if bad_sched > 0:
            result.add_error(
                f"Found {bad_sched} non-numeric or missing values in 'scheduled_services'.",
                column="scheduled_services",
                fix_suggestion="Ensure scheduled trips are non-negative integers."
            )
        else:
            df["scheduled_services"] = sched_num.astype(int)
            sched_is_valid = True
    else:
        result.add_warning("Optional field 'scheduled_services' missing.", "scheduled_services")

    # Check Completed Services (if present)
    comp_is_valid = False
    if "completed_services" in df.columns:
        comp_num = pd.to_numeric(df["completed_services"], errors="coerce")
        bad_comp = comp_num.isna().sum()
        if bad_comp > 0:
            result.add_error(
                f"Found {bad_comp} non-numeric or missing values in 'completed_services'.",
                column="completed_services",
                fix_suggestion="Ensure completed trips are non-negative integers."
            )
        else:
            df["completed_services"] = comp_num.astype(int)
            comp_is_valid = True
            
            # Logical rule: completed <= scheduled
            if sched_is_valid:
                over_completed = (df["completed_services"] > df["scheduled_services"]).sum()
                if over_completed > 0:
                    result.add_warning(
                        f"Detected {over_completed} observations where completed services exceed scheduled services.",
                        column="completed_services",
                        impact="May indicate special or unscheduled relief trips."
                    )
    else:
        result.add_warning("Optional field 'completed_services' missing.", "completed_services")

    # Check Average Delay (if present)
    if "average_delay_minutes" in df.columns:
        delay_num = pd.to_numeric(df["average_delay_minutes"], errors="coerce")
        bad_delay = delay_num.isna().sum()
        if bad_delay > 0:
            result.add_warning(
                f"Found {bad_delay} missing delay measurements. Preserved as unrecorded rather than zero.",
                column="average_delay_minutes"
            )
        df["average_delay_minutes"] = delay_num
    else:
        result.add_warning("Optional field 'average_delay_minutes' missing.", "average_delay_minutes")

    # Check Service Availability % (if present, else compute if scheduled & completed exist)
    if "service_availability_pct" in df.columns:
        avail_num = pd.to_numeric(df["service_availability_pct"], errors="coerce")
        df["service_availability_pct"] = avail_num
    elif "scheduled_services" in df.columns and "completed_services" in df.columns:
        df["service_availability_pct"] = np.where(
            df["scheduled_services"] > 0,
            (df["completed_services"] / df["scheduled_services"]) * 100.0,
            np.nan
        )

    # 6. Check Duplicate Records
    dup_mask = df.duplicated(subset=["date", "operator", "station_or_route"], keep=False)
    dup_count = dup_mask.sum()
    if dup_count > 0:
        result.add_error(
            f"Found {dup_count} duplicate records for same date, operator, and route.",
            fix_suggestion="Remove duplicate rows so each route/corridor has exactly one observation per date."
        )

    # Normalise operator field
    df["operator"] = result.operator_detected
    
    if result.is_valid:
        result.cleaned_df = df
        
    return result
