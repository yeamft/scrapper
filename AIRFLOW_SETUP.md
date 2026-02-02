# Airflow Setup (Optional)

Airflow lets you run the OLX scraper on a schedule (e.g. daily). The project uses **PostgreSQL** for data; Airflow only orchestrates tasks.

## Python version

- Use **Python 3.10 or 3.11** for Airflow (3.12+ is often not fully supported).
- You can keep Python 3.14 for the API and scraper; use a separate venv with 3.11 for Airflow.

## Install

1. **Create a venv with Python 3.11** (recommended):
   ```batch
   py -3.11 -m venv venv_airflow
   venv_airflow\Scripts\activate
   ```

2. **Install base + Airflow deps**:
   ```batch
   pip install -r requirements.txt
   pip install -r requirements-airflow.txt
   ```

3. **Initialize Airflow**:
   ```batch
   python setup_airflow.py
   ```
   This creates `airflow_home/`, copies the DAG, and runs `airflow db init`.

## Run Airflow

1. **Terminal 1 – webserver**:
   ```batch
   start_airflow.bat
   ```
   Or: `set AIRFLOW_HOME=%CD%\airflow_home` then `python -m airflow webserver --port 8080`

2. **Terminal 2 – scheduler**:
   ```batch
   start_scheduler.bat
   ```
   Or: `python -m airflow scheduler`

3. Open **http://localhost:8080** (login: admin / admin).

## DAG

- **DAG id:** `olx_phone_scraper`
- **Schedule:** daily
- **Tasks:** `init_database` → `process_accommodations` (scrapes pending URLs from PostgreSQL using Playwright).

Ensure **PostgreSQL** env vars are set (`POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`) so the DAG can connect to the same DB as the API.
