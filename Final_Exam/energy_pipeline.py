"""Clean Smart Campus EV sessions and derive transparent operating metrics."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Final

import numpy as np
import pandas as pd
try:
    import streamlit as st
except ImportError:  # Allow the batch pipeline to run without the dashboard extra.
    class _StreamlitCacheFallback:
        """Provide an identity cache decorator when Streamlit is not installed."""

        @staticmethod
        def cache_data(*args, **kwargs):
            """Return a no-op decorator so batch cleaning remains reusable."""
            def decorate(function):
                return function
            return decorate

    st = _StreamlitCacheFallback()

LOGGER = logging.getLogger(__name__)
REQUIRED_COLUMNS: Final[set[str]] = {
    "Session_ID", "Charger_Type", "User_Type", "Start_Hour",
    "Duration_Mins", "Energy_kWh", "Overstay_Mins",
    "Battery_Temp_C", "Grid_Status_Label",
}
VALID_CATEGORIES: Final[dict[str, set[str]]] = {
    "Charger_Type": {"AC", "DC"},
    "User_Type": {"Student", "Staff", "Visitor"},
    "Grid_Status_Label": {"Normal", "Grid_Surge", "Overheated"},
}
BASE_RATE_MYR_PER_HOUR: Final[dict[str, float]] = {"AC": 6.0, "DC": 15.0}
PEAK_HOURS: Final[set[int]] = set(range(12, 18))
PEAK_SURCHARGE_RATE: Final[float] = 0.25
OVERTIME_GRACE_MINUTES: Final[int] = 15
OVERTIME_RATE_MYR_PER_MINUTE: Final[float] = 0.50
CARBON_FACTOR_KG_PER_KWH: Final[float] = 0.475


@st.cache_data(show_spinner=False)  # Cache the CSV read to avoid repeated I/O.
def read_sessions(csv_path: str | Path) -> pd.DataFrame:
    """Read the raw EV session CSV and fail with a useful error message."""
    try:
        frame = pd.read_csv(csv_path)
    except (OSError, pd.errors.ParserError, UnicodeDecodeError) as exc:
        LOGGER.exception("Unable to read EV session data from %s", csv_path)
        raise ValueError(f"Could not read CSV file: {csv_path}") from exc

    missing_columns = REQUIRED_COLUMNS.difference(frame.columns)
    if missing_columns:
        raise ValueError(f"CSV is missing required columns: {sorted(missing_columns)}")
    LOGGER.info("Loaded %s EV session records from %s", len(frame), csv_path)
    return frame


@st.cache_data(show_spinner="Loading and cleaning EV session data...")
def load_and_clean_data(csv_path: str) -> pd.DataFrame:
    """Load and clean the CSV once, then cache the serializable DataFrame.

    The cache avoids repeated file I/O and cleaning during UI interactions.
    """
    raw = read_sessions(csv_path)
    return clean_sessions(raw)


@st.cache_data(show_spinner=False)  # Cache cleaning during repeated dashboard reruns.
def clean_sessions(raw: pd.DataFrame) -> pd.DataFrame:
    """Validate, impute, and derive session-level energy and billing metrics."""
    frame = raw.copy()

    numeric_columns = [
        "Start_Hour", "Duration_Mins", "Energy_kWh", "Overstay_Mins",
        "Battery_Temp_C",
    ]
    for column in numeric_columns:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")

    # Physical validation: sensor noise that violates physical common sense has been filtered out.
    frame = frame.loc[frame["Battery_Temp_C"].between(-20, 100) | frame["Battery_Temp_C"].isna()].copy()

    # Fill missing energy with charger-specific medians because AC and DC
    # sessions have different charging-energy distributions.
    frame["Charger_Type"] = frame["Charger_Type"].astype("string").str.strip().str.upper()
    overall_energy_median = frame["Energy_kWh"].median()
    group_medians = frame.groupby("Charger_Type")["Energy_kWh"].transform("median")
    frame["Energy_kWh"] = frame["Energy_kWh"].fillna(group_medians)
    frame["Energy_kWh"] = frame["Energy_kWh"].fillna(overall_energy_median)

    # Use median imputation for other numeric fields and then enforce domains.
    for column in ("Duration_Mins", "Battery_Temp_C"):
        frame[column] = frame[column].fillna(frame[column].median())
    frame["Start_Hour"] = frame["Start_Hour"].fillna(frame["Start_Hour"].median()).round().clip(0, 23)
    frame["Overstay_Mins"] = frame["Overstay_Mins"].fillna(0).clip(lower=0)
    frame["Duration_Mins"] = frame["Duration_Mins"].clip(lower=1)
    frame["Energy_kWh"] = frame["Energy_kWh"].clip(lower=0)

    # Normalize and validate categorical values. Unknown labels remain visible.
    for column, allowed in VALID_CATEGORIES.items():
        frame[column] = frame[column].astype("string").str.strip()
        invalid = ~frame[column].isin(allowed)
        if invalid.any():
            LOGGER.warning("Replacing %d invalid labels in %s with Unknown", int(invalid.sum()), column)
            frame.loc[invalid, column] = "Unknown"

    frame["Duration_Hours"] = frame["Duration_Mins"] / 60.0
    frame["Power_Rate_kW"] = np.divide(
        frame["Energy_kWh"].to_numpy(dtype=float),
        frame["Duration_Hours"].to_numpy(dtype=float),
        out=np.zeros(len(frame), dtype=float),
        where=frame["Duration_Hours"].to_numpy(dtype=float) > 0,
    )
    frame["Carbon_Savings_kgCO2"] = frame["Energy_kWh"] * CARBON_FACTOR_KG_PER_KWH
    frame["Base_Rate_MYR"] = frame["Charger_Type"].map(BASE_RATE_MYR_PER_HOUR).fillna(0.0)
    frame["Base_Fee_MYR"] = frame["Duration_Hours"] * frame["Base_Rate_MYR"]
    frame["Peak_Surge_MYR"] = np.where(
        frame["Start_Hour"].isin(PEAK_HOURS),
        frame["Base_Fee_MYR"] * PEAK_SURCHARGE_RATE,
        0.0,
    )
    billable_overstay = (frame["Overstay_Mins"] - OVERTIME_GRACE_MINUTES).clip(lower=0)
    frame["Overstay_Fee_MYR"] = billable_overstay * OVERTIME_RATE_MYR_PER_MINUTE
    frame["Net_Billable_MYR"] = (
        frame["Base_Fee_MYR"] + frame["Peak_Surge_MYR"] + frame["Overstay_Fee_MYR"]
    )

    # The supplied EV file has no date. This repeatable demo date exists solely
    # to demonstrate the requested date-range filter; it is not observed data.
    ordered = frame.sort_values("Session_ID", kind="stable").index
    demo_day_offsets = (np.arange(len(ordered)) * 20 // max(len(ordered), 1)).astype(int)
    demo_dates = pd.Timestamp("2026-04-01") + pd.to_timedelta(demo_day_offsets, unit="D")
    frame.loc[ordered, "Session_Date_Demo"] = demo_dates.strftime("%Y-%m-%d")
    frame["Session_Date_Demo"] = pd.to_datetime(frame["Session_Date_Demo"])

    LOGGER.info("Completed cleaning and feature engineering for %s records", len(frame))
    return frame.reset_index(drop=True)


def export_clean_data(frame: pd.DataFrame, output_path: str | Path) -> None:
    """Write the cleaned data with derived features to a UTF-8 CSV file."""
    try:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(output_path, index=False, encoding="utf-8")
    except OSError as exc:
        LOGGER.exception("Unable to write cleaned data to %s", output_path)
        raise ValueError(f"Could not write cleaned CSV file: {output_path}") from exc
    LOGGER.info("Exported %s cleaned records to %s", len(frame), output_path)


def main() -> None:
    """Run the command-line cleaning workflow and print summary statistics."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    source = Path(__file__).parent / "data" / "ev_campus_dataset.csv"
    destination = Path(__file__).parent / "data" / "cleaned_energy_sales_data.csv"
    try:
        cleaned = clean_sessions(read_sessions(source))
        export_clean_data(cleaned, destination)
        print(cleaned.describe(include="all").to_string())
    except (ValueError, OSError) as exc:
        LOGGER.error("Pipeline stopped: %s", exc)
        raise


if __name__ == "__main__":
    main()
