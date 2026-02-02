# Testing the API with Postman

## Prerequisites

1. **Start the API server** (if not already running):
   - Double-click `start_api.bat`, or
   - Run: `C:\Users\fkt21\AppData\Local\Programs\Python\Python314\python.exe -m uvicorn api:app --host 0.0.0.0 --port 8000`

2. **Base URL:** `http://localhost:8000`

---

## Endpoints to Test

### 1. Root / API info

- **Method:** GET  
- **URL:** `http://localhost:8000/`  
- **Body:** None  

**What to do in Postman:**  
- New Request → GET → `http://localhost:8000/` → Send  

**Expected:** JSON with `message`, `version`, and list of `endpoints`.

---

### 2. Accept URL for scraping (single)

- **Method:** POST  
- **URL:** `http://localhost:8000/api/scrape`  
- **Headers:**  
  - `Content-Type`: `application/json`  
- **Body (raw, JSON):**

```json
{
  "url": "https://www.olx.ua/d/uk/obyavlenie/na-zavdatku-zdam-v-orendu-1-kmnatnu-kvartiru-IDZKqPF.html",
  "priority": 0
}
```

**What to do in Postman:**  
1. New Request → POST → `http://localhost:8000/api/scrape`  
2. Headers tab → Add: `Content-Type` = `application/json`  
3. Body tab → raw → JSON  
4. Paste the JSON above (change `url` if you want)  
5. Send  

**Expected:** 200, JSON with `id`, `url`, `phone` (null at first), `processed_at`, `created_at`, `error`.

---

### 3. Accept multiple URLs for scraping (batch)

- **Method:** POST  
- **URL:** `http://localhost:8000/api/scrape/batch`  
- **Headers:**  
  - `Content-Type`: `application/json`  
- **Body (raw, JSON):**

```json
{
  "urls": [
    "https://www.olx.ua/d/uk/obyavlenie/na-zavdatku-zdam-v-orendu-1-kmnatnu-kvartiru-IDZKqPF.html",
    "https://www.olx.ua/d/uk/obyavlenie/another-listing-ID123.html"
  ],
  "priority": 0
}
```

**Expected:** 200, JSON with `message`, `added_count`, `added` (array of URL objects), `errors_count`, `errors` (if any).

---

### 4. Get statistics

- **Method:** GET  
- **URL:** `http://localhost:8000/api/statistics`  
- **Body:** None  

**Expected:** 200, JSON like:

```json
{
  "total": 1,
  "with_phone": 0,
  "pending": 1,
  "errors": 0
}
```

---

### 5. Get all URLs

- **Method:** GET  
- **URL:** `http://localhost:8000/api/urls`  
- **Query (optional):** `skip=0`, `limit=100`  
- **Full URL example:** `http://localhost:8000/api/urls?limit=10`  

**Expected:** 200, JSON array of URL objects.

---

### 6. Get one URL by ID

- **Method:** GET  
- **URL:** `http://localhost:8000/api/urls/1`  
- Replace `1` with the actual `id` from a previous response.  

**Expected:** 200, single URL object.

---

### 7. Process URLs (run the scraper)

- **Method:** POST  
- **URL:** `http://localhost:8000/api/process`  
- **Query (optional):**  
  - `batch_size=10` (how many to process)  
  - `headless=true` (browser in background)  
- **Full URL example:** `http://localhost:8000/api/process?batch_size=5&headless=true`  
- **Body:** None (or leave empty)  

**Expected:** 200, JSON like:

```json
{
  "message": "Processed 1 accommodations",
  "processed_count": 1
}
```

**Note:** This can take 30–60+ seconds per URL while the browser runs.

---

### 8. Queue status (Redis)

- **Method:** GET  
- **URL:** `http://localhost:8000/api/queue/status`  

**Expected:** 200, JSON with `pending`, `processing`, `results`, `failed`, `redis_connected` (false if Redis not installed/running).

---

## Suggested order in Postman

1. **GET** `http://localhost:8000/` — check API is up  
2. **POST** `http://localhost:8000/api/scrape` — add one URL (use the JSON body above)  
3. **GET** `http://localhost:8000/api/statistics` — see total/pending  
4. **GET** `http://localhost:8000/api/urls` — see the URL you added  
5. **POST** `http://localhost:8000/api/process?batch_size=1&headless=true` — run scraper (wait for response)  
6. **GET** `http://localhost:8000/api/statistics` — check with_phone increased  
7. **GET** `http://localhost:8000/api/urls/1` — see the URL with `phone` filled  

---

## Quick copy-paste for Postman Body

**POST /api/scrape (single URL):**
```json
{"url": "https://www.olx.ua/d/uk/obyavlenie/na-zavdatku-zdam-v-orendu-1-kmnatnu-kvartiru-IDZKqPF.html", "priority": 0}
```

**POST /api/scrape/batch (multiple URLs):**
```json
{"urls": ["https://www.olx.ua/d/uk/obyavlenie/na-zavdatku-zdam-v-orendu-1-kmnatnu-kvartiru-IDZKqPF.html"], "priority": 0}
```

---

## Troubleshooting

- **Connection refused:** Start the API with `start_api.bat` and ensure it says "Uvicorn running on http://0.0.0.0:8000".  
- **422 Unprocessable Entity:** Check Body is **raw** and **JSON**, and `url`/`urls` are valid strings.  
- **Process takes long:** Normal; the browser is loading OLX and clicking "Show phone". Use `batch_size=1` for testing.
