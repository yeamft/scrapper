# API Documentation

## OLX Phone Scraper REST API

FastAPI-based REST API for managing OLX accommodation phone scraping.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the API Server

```bash
python api.py
```

Or with uvicorn directly:
```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

### 3. Access API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **API Root**: http://localhost:8000/

## API Endpoints

### 1. Root Endpoint

**GET** `/`

Get API information and available endpoints.

**Response:**
```json
{
  "message": "OLX Phone Scraper API",
  "version": "1.0.0",
  "endpoints": {...}
}
```

---

### 2. Add URL

**POST** `/api/urls`

Add a URL to the database for processing.

**Request Body:**
```json
{
  "url": "https://www.olx.ua/d/uk/obyavlenie/...",
  "priority": 10
}
```

**Response:**
```json
{
  "id": 1,
  "url": "https://www.olx.ua/d/uk/obyavlenie/...",
  "phone": null,
  "processed_at": null,
  "created_at": "2026-01-30 10:42:36",
  "error": null
}
```

**Example (curl):**
```bash
curl -X POST "http://localhost:8000/api/urls" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.olx.ua/d/uk/obyavlenie/...", "priority": 10}'
```

---

### 3. Get All URLs

**GET** `/api/urls`

Get all URLs from the database.

**Query Parameters:**
- `skip` (int, default: 0) - Number of records to skip
- `limit` (int, default: 100) - Maximum number of records to return

**Response:**
```json
[
  {
    "id": 1,
    "url": "https://www.olx.ua/...",
    "phone": "0260127010",
    "processed_at": "2026-01-30T13:56:06.927621",
    "created_at": "2026-01-30 10:42:36",
    "error": null
  }
]
```

**Example:**
```bash
curl "http://localhost:8000/api/urls?limit=10&skip=0"
```

---

### 4. Get URL by ID

**GET** `/api/urls/{url_id}`

Get a specific URL by its ID.

**Path Parameters:**
- `url_id` (int) - The ID of the URL

**Response:**
```json
{
  "id": 1,
  "url": "https://www.olx.ua/...",
  "phone": "0260127010",
  "processed_at": "2026-01-30T13:56:06.927621",
  "created_at": "2026-01-30 10:42:36",
  "error": null
}
```

**Example:**
```bash
curl "http://localhost:8000/api/urls/1"
```

---

### 5. Get Statistics

**GET** `/api/statistics`

Get database statistics.

**Response:**
```json
{
  "total": 10,
  "with_phone": 8,
  "pending": 1,
  "errors": 1
}
```

**Example:**
```bash
curl "http://localhost:8000/api/statistics"
```

---

### 6. Process URLs

**POST** `/api/process`

Process unprocessed URLs.

**Request Body:**
```json
{
  "batch_size": 10,
  "headless": true
}
```

**Query Parameters:**
- `batch_size` (int, default: 10) - Number of URLs to process
- `headless` (bool, default: true) - Run browser in headless mode

**Response:**
```json
{
  "message": "Processed 5 accommodations",
  "processed_count": 5
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/process?batch_size=5&headless=true"
```

---

### 7. Get Queue Status

**GET** `/api/queue/status`

Get Redis queue status (if Redis is connected).

**Response:**
```json
{
  "pending": 5,
  "processing": 2,
  "results": 10,
  "failed": 1,
  "redis_connected": true
}
```

**Example:**
```bash
curl "http://localhost:8000/api/queue/status"
```

---

### 8. Add to Redis Queue

**POST** `/api/queue/add`

Add URL directly to Redis queue.

**Request Body:**
```json
{
  "url": "https://www.olx.ua/d/uk/obyavlenie/...",
  "priority": 10
}
```

**Response:**
```json
{
  "message": "URL added to queue",
  "url": "https://www.olx.ua/...",
  "priority": 10
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/queue/add" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.olx.ua/...", "priority": 10}'
```

---

## Testing the API

### Using the Test Script

```bash
# Make sure API is running first. Use Postman or curl to test endpoints.
```

### Using curl

```bash
# Get statistics
curl http://localhost:8000/api/statistics

# Add URL
curl -X POST http://localhost:8000/api/urls \
  -H "Content-Type: application/json" \
  -d "{\"url\": \"https://www.olx.ua/...\", \"priority\": 10}"

# Process URLs
curl -X POST "http://localhost:8000/api/process?batch_size=5"
```

### Using Python requests

```python
import requests

# Add URL
response = requests.post(
    "http://localhost:8000/api/urls",
    json={"url": "https://www.olx.ua/...", "priority": 10}
)
print(response.json())

# Get statistics
response = requests.get("http://localhost:8000/api/statistics")
print(response.json())

# Process URLs
response = requests.post(
    "http://localhost:8000/api/process",
    params={"batch_size": 5, "headless": True}
)
print(response.json())
```

### Using Swagger UI

1. Start the API server
2. Open http://localhost:8000/docs in your browser
3. Click on any endpoint to expand it
4. Click "Try it out"
5. Fill in parameters and click "Execute"

---

## Error Responses

All endpoints return standard HTTP status codes:

- `200` - Success
- `400` - Bad Request (invalid input)
- `404` - Not Found
- `500` - Internal Server Error
- `503` - Service Unavailable (Redis not connected)

Error response format:
```json
{
  "detail": "Error message here"
}
```

---

## Integration Examples

### Example 1: Add and Process URL

```python
import requests

BASE_URL = "http://localhost:8000"

# Add URL
response = requests.post(
    f"{BASE_URL}/api/urls",
    json={"url": "https://www.olx.ua/...", "priority": 10}
)
url_data = response.json()
print(f"Added URL ID: {url_data['id']}")

# Process it
response = requests.post(
    f"{BASE_URL}/api/process",
    params={"batch_size": 1}
)
print(response.json())
```

### Example 2: Monitor Processing

```python
import requests
import time

BASE_URL = "http://localhost:8000"

# Get initial statistics
stats = requests.get(f"{BASE_URL}/api/statistics").json()
initial_pending = stats['pending']

# Process URLs
requests.post(f"{BASE_URL}/api/process", params={"batch_size": 10})

# Wait and check again
time.sleep(5)
stats = requests.get(f"{BASE_URL}/api/statistics").json()
processed = initial_pending - stats['pending']
print(f"Processed {processed} URLs")
```

---

## Notes

- The API runs on port 8000 by default
- Redis integration is optional - API works without Redis
- Processing URLs may take time (depends on website response)
- Use `headless=True` for production, `headless=False` for debugging
