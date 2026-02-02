# Airflow Setup (Optional)

Airflow lets you run the OLX scraper on a schedule (e.g. daily). The DAG uses the same PostgreSQL database and scraper as the API.

## Requirements

- **Python 3.10 or 3.11** (Airflow may not support 3.12+; use a separate venv if you have 3.14)
- Project dependencies already installed (`requirements.txt`)

## Install Airflow

```bash
pip install -r requirements-airflow.txt
```

If you use Python 3.14, create a venv with 3.11 and install there:

```batch
py -3.11 -m venv venv_airflow
venv_airflow\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-airflow.txt
playwright install chromium
```

## Initialize Airflow

From the project folder:

```bash
python setup_airflow.py
```

This sets `AIRFLOW_HOME=./airflow_home`, creates `airflow_home/dags`, copies the DAG, and runs `airflow db init`. Default admin user: **admin** / **admin**.

## Run Airflow

1. **Webserver** (UI): `airflow webserver --port 8080` → open http://localhost:8080  
2. **Scheduler** (runs DAGs): `airflow scheduler` in a second terminal  

From the project folder (set AIRFLOW_HOME first if needed):

```bash
set AIRFLOW_HOME=./airflow_home   # Windows
# export AIRFLOW_HOME=./airflow_home   # Linux/Mac
python -m airflow webserver --port 8080
python -m airflow scheduler
```

## DAG: olx_phone_scraper

- **init_database** – ensures PostgreSQL `accommodations` table exists  
- **process_accommodations** – processes up to 10 unprocessed URLs (Playwright, same as API)  

Schedule: daily. You can trigger a run manually from the UI.

## PostgreSQL

The DAG uses the same DB as the API. Set env vars if needed:

- `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`

See `db.py` for defaults.
