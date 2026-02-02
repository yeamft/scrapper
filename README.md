# OLX Accommodation Phone Scraper

Python scraper for OLX accommodation phone numbers, with REST API, PostgreSQL, optional Redis and Airflow.

## Features

- Extract phone numbers from OLX URLs (Playwright, anti-detection)
- PostgreSQL database; REST API (FastAPI); optional Redis queue; optional Airflow scheduling
- Batch processing and error handling

## Requirements

- Python 3.9+
- Playwright (Chromium)

## Installation

1. **Environment** — Create `.env` from template:
   ```bash
   python create_env.py
   ```
   Edit `.env` with PostgreSQL (`POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`) and optional Redis (`REDIS_HOST`, `REDIS_PORT`). Optional: `POSTGRES_POOL_SIZE=5` for connection pooling.

2. **Dependencies**
   ```bash
   pip install -r requirements.txt
   python -m playwright install chromium
   ```

3. **(Optional)** Redis — Install and start Redis if using queue endpoints.

## Quick start

- **API:** `python api.py` → http://localhost:8000, docs at /docs  
- **Submit URLs:** POST `/api/scrape` or `/api/scrape/batch`  
- **Process:** POST `/api/process?batch_size=10`  
- **Data:** GET `/api/urls`, `/api/statistics`; or `python show_database.py`, `python clear_db.py`  

Import `OLX_Scraper_API.postman_collection.json` in Postman to test. See **API_DOCUMENTATION.md**.

## CLI

```bash
python olx_phone_scraper.py add "https://www.olx.ua/d/uk/obyavlenie/..."
python olx_phone_scraper.py process --headless
python olx_phone_scraper.py stats
python extract_urls_from_search.py
```

## Airflow (optional)

Schedule scraping: install `requirements-airflow.txt` (Python 3.10/3.11), run `python setup_airflow.py`, then `airflow webserver --port 8080` and `airflow scheduler`. See **AIRFLOW_SETUP.md**.

## Project layout

| File / folder | Purpose |
|---------------|---------|
| `api.py` | REST API |
| `olx_phone_scraper.py` | Core scraper |
| `db.py` | PostgreSQL connection |
| `redis_queue.py` | Optional Redis queue |
| `clear_db.py`, `show_database.py` | DB admin |
| `extract_urls_from_search.py` | Extract URLs from OLX search |
| `dags/olx_scraper_dag.py` | Airflow DAG (optional) |
| `.env.example` | Env template → copy to `.env` |
| `create_env.py` | Create `.env` from template |

## Docs

- **API_DOCUMENTATION.md** — API reference  
- **AIRFLOW_SETUP.md** — Airflow setup
