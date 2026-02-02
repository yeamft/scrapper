# OLX Accommodation Phone Scraper

A Python web scraper for extracting phone numbers from OLX accommodation listings, with a REST API and optional Redis queue.

## Features

- Extract phone numbers from OLX accommodation URLs (Playwright, anti-detection)
- SQLite database for URLs and results
- REST API (FastAPI) for submitting URLs and processing
- Optional Redis task queue
- Batch processing and error handling

## Requirements

- Python 3.9+
- Playwright (Chromium)

## Installation

1. **Install dependencies**
   ```batch
   run.bat -m pip install -r requirements.txt
   ```
   Or with full path:
   ```batch
   C:\Users\fkt21\AppData\Local\Programs\Python\Python314\python.exe -m pip install -r requirements.txt
   ```

2. **Install Playwright browser**
   ```batch
   run.bat -m playwright install chromium
   ```

3. **(Optional)** Redis for queue: install and start Redis if you use the queue endpoints.

## Using the project Python path

All commands use the project Python (no PATH needed):

```batch
run.bat api.py
run.bat clear_db.py
run.bat -m pip list
```

Or full path:
```batch
C:\Users\fkt21\AppData\Local\Programs\Python\Python314\python.exe api.py
```

## Quick start

1. **Start the API**
   ```batch
   start_api.bat
   ```
   API: http://localhost:8000 — Docs: http://localhost:8000/docs

2. **Submit URLs** — POST to `/api/scrape` or `/api/scrape/batch` (see `API_DOCUMENTATION.md` and Postman collection).

3. **Process URLs** — POST `/api/process?batch_size=10` to run the scraper on pending URLs.

4. **View data** — GET `/api/urls`, `/api/statistics`, or use `show_database.py` / `clear_db.bat` for DB admin.

## CLI (scraper only)

From project folder:

```batch
run.bat olx_phone_scraper.py add "https://www.olx.ua/d/uk/obyavlenie/..."
run.bat olx_phone_scraper.py process --headless
run.bat olx_phone_scraper.py stats
```

Or extract URLs from a search page:
```batch
run.bat extract_urls_from_search.py
```

## Database

- File: `accommodations.db`
- Table: `accommodations` (id, url, phone, processed_at, created_at, error)
- Clear all rows: `clear_db.bat` or `run.bat clear_db.py`
- Inspect: `run.bat show_database.py`

## Project layout (production)

```
api.py                    # REST API
olx_phone_scraper.py      # Core scraper
redis_queue.py            # Optional Redis queue
add_to_redis_queue.py     # CLI to add URLs to queue
clear_db.py               # Clear DB utility
show_database.py          # DB inspection
extract_urls_from_search.py  # Extract URLs from OLX search
requirements.txt
run.bat / start_api.bat / clear_db.bat
README.md
API_DOCUMENTATION.md
POSTMAN_GUIDE.md
OLX_Scraper_API.postman_collection.json
```

## Documentation

- **API_DOCUMENTATION.md** — API reference
- **POSTMAN_GUIDE.md** — Testing with Postman
