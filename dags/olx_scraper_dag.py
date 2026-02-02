"""
Airflow DAG for OLX Phone Scraper (PostgreSQL).
Ensure project root is on PYTHONPATH or run from project dir so db and olx_phone_scraper can be imported.
"""
import os
import sys

# Add project root so we can import db and olx_phone_scraper when Airflow loads this DAG
# File may be in project/dags/ or airflow_home/dags/ (after setup_airflow copy)
_f = os.path.abspath(__file__)
_dags_dir = os.path.dirname(_f)
_project_root = os.path.dirname(_dags_dir)
if os.path.basename(_project_root) == "airflow_home":
    _project_root = os.path.dirname(_project_root)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

BATCH_SIZE = 10
HEADLESS = True


def task_init_database(**context):
    from db import init_database
    init_database()
    return "Database initialized"


def task_process_accommodations(**context):
    from olx_phone_scraper import (
        get_unprocessed_accommodations,
        extract_phone_from_url,
        update_accommodation_phone,
        create_browser_context,
    )
    from playwright.sync_api import sync_playwright

    accommodations = get_unprocessed_accommodations()
    if not accommodations:
        return "No unprocessed accommodations"

    processed = 0
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=HEADLESS,
            args=["--disable-blink-features=AutomationControlled"],
        )
        context = create_browser_context(browser, HEADLESS)
        try:
            for accommodation_id, url in accommodations[:BATCH_SIZE]:
                try:
                    phone = extract_phone_from_url(url, context)
                    if phone:
                        update_accommodation_phone(accommodation_id, phone)
                    else:
                        update_accommodation_phone(accommodation_id, None, "Phone number not found")
                    processed += 1
                except Exception as e:
                    update_accommodation_phone(accommodation_id, None, str(e))
        finally:
            context.close()
            browser.close()
    return f"Processed {processed} accommodations"


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 0,
}

dag = DAG(
    "olx_phone_scraper",
    default_args=default_args,
    description="OLX accommodation phone scraper (PostgreSQL)",
    schedule_interval="@daily",
    start_date=days_ago(1),
    tags=["olx", "scraper"],
)

t_init = PythonOperator(
    task_id="init_database",
    python_callable=task_init_database,
    dag=dag,
)

t_process = PythonOperator(
    task_id="process_accommodations",
    python_callable=task_process_accommodations,
    dag=dag,
)

t_init >> t_process
