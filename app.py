"""Interactive Streamlit dashboard for EV campus energy sessions."""
from __future__ import annotations

import logging
from datetime import date
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

from energy_pipeline import load_and_clean_data

LOGGER = logging.getLogger(__name__)
BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "data" / "ev_campus_dataset.csv"


def filter_sessions(frame: pd.DataFrame, date_range: tuple[date, date],
                    min_energy: float, charger_types: list[str]) -> pd.DataFrame:
    """Apply all dashboard filters to a copy of the cleaned sessions."""
    start_date, end_date = date_range
    mask = (
        frame["Session_Date_Demo"].dt.date.between(start_date, end_date)
        & frame["Energy_kWh"].ge(min_energy)
        & frame["Charger_Type"].isin(charger_types)
    )
    return frame.loc[mask].copy()


def main() -> None:
    """Render the executive dashboard, filters, charts, alerts, and export."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    st.set_page_config(page_title="Smart Campus EV Energy", page_icon="⚡", layout="wide")
    st.title("Smart Campus Energy and EV Fleet Dashboard")
    st.caption("Session analytics • Modeled billing • Operational risk monitoring")

    try:
        data = load_and_clean_data(str(DATA_PATH))
    except (OSError, ValueError) as exc:
        LOGGER.exception("Dashboard data loading failed")
        st.error(f"Unable to load the EV dataset: {exc}")
        st.stop()

    st.sidebar.header("Interactive filters")
    st.sidebar.caption("Date range uses demo dates because the source has no session timestamp.")
    min_day = data["Session_Date_Demo"].min().date()
    max_day = data["Session_Date_Demo"].max().date()
    chosen_range = st.sidebar.date_input(
        "Demo date range", value=(min_day, max_day), min_value=min_day, max_value=max_day,
        help="Stable dates are assigned by record order for demonstrating the date filter only.",
    )
    if isinstance(chosen_range, tuple) and len(chosen_range) == 2:
        date_range = chosen_range
    else:
        date_range = (chosen_range, chosen_range)
    min_energy = st.sidebar.slider("Minimum energy (kWh)", min_value=0.0,
                                    max_value=float(data["Energy_kWh"].max()), value=0.0, step=1.0)
    charger_options = sorted(data["Charger_Type"].dropna().unique().tolist())
    charger_types = st.sidebar.multiselect("Charger type", charger_options,
                                            default=charger_options)
    temp_threshold = st.sidebar.slider("High-risk battery temperature (°C)",
                                        min_value=30, max_value=60, value=40, step=1)

    selected = filter_sessions(data, date_range, min_energy, charger_types)
    high_risk = selected.loc[
        selected["Overstay_Mins"].gt(20)
        & selected["Battery_Temp_C"].gt(temp_threshold)
    ]

    # Dynamic alert appears above the KPI row as required by the assignment.
    if len(high_risk) > 5:
        st.error("⚠️ Warning: large-scale grid overload risk detected; it is recommended to immediately limit DC charging pile power!")
    elif len(high_risk) > 0:
        st.warning(f"Detected {len(high_risk)} high-risk sessions. Review temperature and overstay patterns.")
    else:
        st.success("No high-risk sessions match the current filters.")

    previous_energy = data["Energy_kWh"].sum()
    selected_energy = selected["Energy_kWh"].sum()
    energy_delta = (selected_energy / previous_energy * 100.0) if previous_energy else 0.0
    total_carbon = selected["Carbon_Savings_kgCO2"].sum()
    revenue = selected["Net_Billable_MYR"].sum()
    active_alerts = len(high_risk)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Energy Delivered", f"{selected_energy:,.1f} kWh",
              f"{energy_delta:.1f}% of all sessions")
    c2.metric("Carbon Offset Estimate", f"{total_carbon:,.1f} kg CO₂",
              "0.475 kg per kWh assumption")
    c3.metric("Total Modelled Revenue", f"MYR {revenue:,.2f}",
              f"{len(selected):,} filtered sessions")
    c4.metric("Active Alert Count", f"{active_alerts:,}",
              f"Threshold > {temp_threshold}°C and overstay > 20 min",
              delta_color="inverse")

    st.info("Data limitations: the EV source has no observed session dates, solar generation, ambient temperature, or grid-meter load. Date filtering is demonstrative; solar and demand views use labelled proxies/models.")

    st.subheader("Revenue and session patterns")
    col1, col2 = st.columns(2)
    with col1:
        revenue_by_hour = selected.pivot_table(index="Start_Hour", columns="Charger_Type",
                                               values="Net_Billable_MYR", aggfunc="sum", fill_value=0)
        revenue_by_hour = revenue_by_hour.reindex(range(24), fill_value=0)
        st.bar_chart(revenue_by_hour, x_label="Session start hour", y_label="Modelled revenue (MYR)")
    with col2:
        hourly = selected.groupby("Start_Hour")["Power_Rate_kW"].sum().reindex(range(24), fill_value=0)
        st.line_chart(hourly, x_label="Session start hour", y_label="Session power-rate proxy (kW)")

    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        fig, ax = plt.subplots(figsize=(7, 4))
        sns.boxplot(data=selected, x="User_Type", y="Net_Billable_MYR", showfliers=False, ax=ax)
        ax.set_title("Modelled Session Cost by User Type")
        ax.set_xlabel("User type")
        ax.set_ylabel("MYR")
        st.pyplot(fig, clear_figure=True)
    with chart_col2:
        st.subheader("High-risk session review")
        if high_risk.empty:
            st.write("No sessions match the current risk settings.")
        else:
            st.dataframe(high_risk[["Session_ID", "Charger_Type", "Overstay_Mins",
                                    "Battery_Temp_C", "Energy_kWh"]], hide_index=True,
                         width="stretch")

    st.subheader("Filtered session data")
    st.caption(f"Showing {len(selected):,} of {len(data):,} sessions.")
    st.dataframe(selected, hide_index=True, width="stretch", height=350)
    csv_data = selected.to_csv(index=False).encode("utf-8")
    st.download_button("Download filtered CSV", data=csv_data,
                       file_name="filtered_ev_sessions.csv", mime="text/csv")


if __name__ == "__main__":
    main()
