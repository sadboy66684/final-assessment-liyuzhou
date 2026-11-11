# Smart Campus Energy and EV Fleet Dashboard

## Run locally

1. Install Python 3.10 or later.
2. Install the dependencies with `pip install -r requirements.txt`.
3. Start the dashboard with `streamlit run app.py`.
4. Run the batch pipeline with `python energy_pipeline.py`.
5. Regenerate the figures with `python visualizations.py`.

## Project files

- `app.py`: interactive Streamlit dashboard.
- `energy_pipeline.py`: CSV validation, cleaning, median imputation, feature engineering, and export.
- `visualizations.py`: five labelled chart outputs.
- `data/ev_campus_dataset.csv`: raw EV charging sessions used by the application.
- `data/cleaned_energy_sales_data.csv`: processed sessions and derived metrics.
- `data/sales_data.csv`: separate transaction dataset; it is not merged into EV sessions because the records have different meanings and grain.
- `figures/`: generated chart files.
- `screenshots/pipeline_execution.png`: execution-output evidence included in the report.

## Data limitations and assumptions

The raw EV session file has no session timestamp, solar generation, ambient temperature, or grid-meter load. The dashboard therefore assigns stable demonstration dates by record order for the required date filter. The demand chart uses aggregated session power-rate as a proxy and shows a clearly labelled synthetic solar profile. These values must not be treated as measured operations data.

Illustrative billing assumptions: AC rate MYR 6/hour, DC rate MYR 15/hour, a 25% surcharge for sessions starting from 12:00 through 17:00, 15-minute overstay grace period, then MYR 0.50 per minute. Carbon savings use 0.475 kg CO2 per kWh as specified in the assignment.
