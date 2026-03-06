# CDP Insights

Operational analytics dashboard built with Streamlit, covering our 11 KPIs across the transaction, document, eSign, user activity, and survey pipelines.

## Current Dashboards

| Dashboard | KPIs | Description |
|---|---|---|
| Pipeline Health | 01 · 02 · 03 · 04 | Transactions → Documents → Execution rate funnel |
| eSign & Engagement | 05 · 06 | Parties per transaction + eSign funnel drop-off |
| User Activity & Consent | 07 · 09 · 10 | TCPA compliance, users updated, Long Realty window |
| Speed & Survey | 08 · 11 | Time to execution + PHM survey outcomes |

## Project Structure

```
apps/
├── io_layer/           # Data loading from zip — checksum-aware extraction
│   ├── data_loader.py
│   ├── file_readers.py
│   └── zip_utils.py
├── transforms/         # Per-KPI data cleaning and derived metrics
│   ├── kpi01.py … kpi11.py
│   └── __init__.py
├── streamlit/          # Streamlit app
│   ├── app.py          # Overview / landing page
│   ├── pages/
│   │   ├── 01_pipeline_health.py
│   │   ├── 02_esign_engagement.py
│   │   ├── 03_user_activity.py
│   │   └── 04_speed_survey.py
│   ├── utils/
│   │   └── dashboard_utils.py
│   └── assets/
│       └── kpis.zip    # Drop updated zip here to refresh data
├── run_me_once.py      # Dev tool: test io_layer in isolation
├── requirements.txt
└── .gitignore

## Running Locally

```bash
# 1. Clone the repo
git clone https://github.com/our-org/apps.git
cd apps

# 2. Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run streamlit/app.py
```

## Updating Data

1. Drop the new `kpis.zip` into `streamlit/assets/`
2. Restart the Streamlit app
3. The app detects the checksum change and re-extracts automatically

## Deploying to Streamlit Community Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Set **Main file path** to `streamlit/app.py`
5. Click Deploy — done