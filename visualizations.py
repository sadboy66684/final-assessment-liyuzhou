"""Create labelled figures for the Smart Campus EV analysis."""
from __future__ import annotations

import logging
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

LOGGER = logging.getLogger(__name__)


def build_analysis_figures(frame: pd.DataFrame, output_dir: str | Path) -> list[Path]:
    """Save three publication-style figures and return their file paths.

    The source does not contain grid-load, solar, or ambient-temperature
    telemetry. Figures therefore use explicitly labelled proxies and models.
    """
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid", context="notebook", palette="colorblind")
    outputs: list[Path] = []

    # Figure 1: modelled campus load proxy versus a deliberately synthetic
    # daylight solar curve. It is not presented as measured solar telemetry.
    hourly = frame.groupby("Start_Hour", as_index=True).agg(
        Session_Power_Proxy_kW=("Power_Rate_kW", "sum"),
        Session_Count=("Session_ID", "count"),
    ).reindex(range(24), fill_value=0)
    hours = pd.Series(range(24), index=range(24), dtype=float)
    solar_proxy = (hourly["Session_Power_Proxy_kW"].max() * 0.45) * (
        ((hours - 6) / 12).clip(0, 1) * ((18 - hours) / 12).clip(0, 1) * 4
    )
    fig, ax = plt.subplots(figsize=(10, 5.4), constrained_layout=True)
    ax.plot(hourly.index, hourly["Session_Power_Proxy_kW"], marker="o", linewidth=2.2,
            label="Observed session power-rate proxy")
    ax.plot(hourly.index, solar_proxy, linestyle="--", linewidth=2.2,
            label="Illustrative solar profile (synthetic)")
    ax.set(title="Hourly Charging Demand Proxy and Illustrative Solar Profile",
           xlabel="Session start hour", ylabel="Aggregated power proxy (kW)")
    ax.set_xticks(range(0, 24, 2))
    ax.legend(frameon=False)
    ax.text(0.01, -0.22, "EV source contains no grid-meter or solar-generation telemetry.",
            transform=ax.transAxes, fontsize=9)
    path = destination / "hourly_demand_solar_proxy.png"
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    outputs.append(path)

    # Figure 2: session cost distribution for the three known user groups.
    fig, ax = plt.subplots(figsize=(8.5, 5.2), constrained_layout=True)
    sns.boxplot(data=frame, x="User_Type", y="Net_Billable_MYR",
                order=["Student", "Staff", "Visitor"], showfliers=False, ax=ax)
    sns.stripplot(data=frame, x="User_Type", y="Net_Billable_MYR", color="#263238",
                  alpha=0.18, size=2.5, jitter=0.22, ax=ax)
    ax.set(title="Session Cost Distribution by User Type", xlabel="User type",
           ylabel="Modelled session charge (MYR)")
    path = destination / "cost_by_user_type.png"
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    outputs.append(path)

    # Figure 3: measured battery temperature versus energy, with trend line.
    fig, ax = plt.subplots(figsize=(8.5, 5.2), constrained_layout=True)
    sns.scatterplot(data=frame, x="Energy_kWh", y="Battery_Temp_C", hue="Charger_Type",
                    alpha=0.65, s=38, ax=ax)
    sns.regplot(data=frame, x="Energy_kWh", y="Battery_Temp_C", scatter=False,
                color="#263238", line_kws={"linewidth": 2}, ax=ax)
    ax.set(title="Battery Temperature and Energy Delivered", xlabel="Energy delivered (kWh)",
           ylabel="Battery temperature (°C)")
    path = destination / "battery_temperature_vs_energy.png"
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    outputs.append(path)

    # Figure 4: hourly revenue split by charger type (Section A comparison).
    revenue = frame.pivot_table(index="Start_Hour", columns="Charger_Type",
                                values="Net_Billable_MYR", aggfunc="sum", fill_value=0)
    revenue = revenue.reindex(range(24), fill_value=0)
    fig, ax = plt.subplots(figsize=(10, 5.2), constrained_layout=True)
    revenue.plot(kind="bar", ax=ax, width=0.82, color={"AC": "#2878B5", "DC": "#E07A2D"})
    ax.set(title="Hourly Charging Revenue by Charger Type", xlabel="Session start hour",
           ylabel="Modelled revenue (MYR)")
    ax.legend(title="Charger type", frameon=False)
    ax.tick_params(axis="x", rotation=0)
    path = destination / "hourly_revenue_by_charger.png"
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    outputs.append(path)

    # Figure 5: requested conceptual correlation panel. Ambient temperature and
    # measured grid load are absent, so Battery_Temp_C and power proxy are used.
    correlation = frame[["Battery_Temp_C", "Duration_Hours", "Power_Rate_kW"]].corr()
    correlation = correlation.rename(index={"Battery_Temp_C": "Battery temp (°C)",
                                             "Duration_Hours": "Duration (h)",
                                             "Power_Rate_kW": "Session power proxy (kW)"},
                                   columns={"Battery_Temp_C": "Battery temp (°C)",
                                            "Duration_Hours": "Duration (h)",
                                            "Power_Rate_kW": "Session power proxy (kW)"})
    fig, ax = plt.subplots(figsize=(7.3, 5.5), constrained_layout=True)
    sns.heatmap(correlation, annot=True, fmt=".2f", cmap="vlag", center=0,
                vmin=-1, vmax=1, square=True, linewidths=0.6, cbar_kws={"label": "Pearson r"}, ax=ax)
    ax.set(title="Correlation of Available Session Metrics")
    path = destination / "available_metrics_correlation_heatmap.png"
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    outputs.append(path)
    LOGGER.info("Saved %d labelled figures to %s", len(outputs), destination)
    return outputs


def main() -> None:
    """Render chart outputs using the generated cleaned CSV."""
    from energy_pipeline import read_sessions, clean_sessions

    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    base = Path(__file__).parent
    source = base / "data" / "ev_campus_dataset.csv"
    cleaned_path = base / "data" / "cleaned_energy_sales_data.csv"
    try:
        frame = pd.read_csv(cleaned_path) if cleaned_path.exists() else clean_sessions(read_sessions(source))
        build_analysis_figures(frame, base / "figures")
    except (OSError, ValueError, pd.errors.ParserError):
        LOGGER.exception("Unable to generate visualization outputs")
        raise


if __name__ == "__main__":
    main()
