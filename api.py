"""
REST API for OLX Phone Scraper
FastAPI-based API to interact with the scraper, database, and Redis queue
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl
from typing import Optional, List
import asyncio
import sys
import os
import io

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Import scraper and db
from db import get_connection, init_database
from olx_phone_scraper import (
    add_accommodation_url,
    get_unprocessed_accommodations,
    update_accommodation_phone,
)
try:
    from redis_queue import get_redis_queue
except ImportError:
    # Redis optional - provide a no-op queue when redis not installed
    def get_redis_queue():
        class _NoRedisQueue:
            def is_connected(self): return False
            def enqueue_url(self, url, priority=0): return False
            def get_queue_size(self): return {'pending': 0, 'processing': 0, 'results': 0, 'failed': 0}
        return _NoRedisQueue()
from datetime import datetime

app = FastAPI(
    title="OLX Phone Scraper API",
    description="API for managing OLX accommodation phone scraping",
    version="1.0.0"
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_database()
    print("API started - PostgreSQL database initialized")

# Request/Response Models
class URLRequest(BaseModel):
    url: HttpUrl
    priority: Optional[int] = 0

class ScrapeURLRequest(BaseModel):
    """Accept a URL for scraping (OLX accommodation page)"""
    url: HttpUrl
    priority: Optional[int] = 0

class ScrapeBatchRequest(BaseModel):
    """Accept multiple URLs for scraping"""
    urls: List[HttpUrl]
    priority: Optional[int] = 0

class URLResponse(BaseModel):
    id: int
    url: str
    phone: Optional[str]
    processed_at: Optional[str]
    created_at: str
    error: Optional[str]

class StatisticsResponse(BaseModel):
    total: int
    with_phone: int
    pending: int
    errors: int

class QueueStatusResponse(BaseModel):
    pending: int
    processing: int
    results: int
    failed: int
    redis_connected: bool

class ProcessResponse(BaseModel):
    message: str
    processed_count: int

# API Endpoints

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "OLX Phone Scraper API",
        "version": "1.0.0",
        "endpoints": {
            "scrape_url": "POST /api/scrape - submit URL for scraping",
            "scrape_batch": "POST /api/scrape/batch - submit multiple URLs",
            "add_url": "POST /api/urls",
            "get_urls": "GET /api/urls",
            "get_url": "GET /api/urls/{id}",
            "process": "POST /api/process",
            "statistics": "GET /api/statistics",
            "queue_status": "GET /api/queue/status",
            "add_to_queue": "POST /api/queue/add"
        }
    }

@app.post("/api/urls", response_model=URLResponse)
async def add_url(request: URLRequest):
    """
    Add a URL to the database for processing
    
    - **url**: OLX accommodation URL
    - **priority**: Priority for Redis queue (if using Redis)
    """
    try:
        # Add to database
        add_accommodation_url(str(request.url))
        
        # Also add to Redis queue if available
        redis_queue = get_redis_queue()
        if redis_queue.is_connected():
            redis_queue.enqueue_url(str(request.url), request.priority)
        
        # Get the added record
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM accommodations WHERE url = %s", (str(request.url),))
                row = cursor.fetchone()
        finally:
            conn.close()
        if row:
            return URLResponse(
                id=row[0],
                url=row[1],
                phone=row[2],
                processed_at=row[3],
                created_at=row[4],
                error=row[5]
            )
        else:
            raise HTTPException(status_code=404, detail="URL not found after adding")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error adding URL: {str(e)}")


@app.post("/api/scrape", response_model=URLResponse)
async def accept_url_for_scraping(request: ScrapeURLRequest):
    """
    Accept a URL for scraping.
    Submit an OLX accommodation URL to be queued for phone number extraction.
    
    - **url**: OLX accommodation page URL (e.g. https://www.olx.ua/d/uk/obyavlenie/...)
    - **priority**: Optional priority (higher = processed first when using Redis)
    """
    try:
        add_accommodation_url(str(request.url))
        redis_queue = get_redis_queue()
        if redis_queue.is_connected():
            redis_queue.enqueue_url(str(request.url), request.priority)
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM accommodations WHERE url = %s", (str(request.url),))
                row = cursor.fetchone()
        finally:
            conn.close()
        if row:
            return URLResponse(
                id=row[0],
                url=row[1],
                phone=row[2],
                processed_at=row[3],
                created_at=row[4],
                error=row[5]
            )
        raise HTTPException(status_code=404, detail="URL not found after adding")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error accepting URL: {str(e)}")


@app.post("/api/scrape/batch")
async def accept_urls_for_scraping_batch(request: ScrapeBatchRequest):
    """
    Accept multiple URLs for scraping.
    Submit a list of OLX accommodation URLs to be queued for phone number extraction.
    
    - **urls**: List of OLX accommodation page URLs
    - **priority**: Optional priority for all URLs (when using Redis)
    """
    added: List[URLResponse] = []
    errors: List[dict] = []
    for url in request.urls:
        try:
            add_accommodation_url(str(url))
            redis_queue = get_redis_queue()
            if redis_queue.is_connected():
                redis_queue.enqueue_url(str(url), request.priority or 0)
            conn = get_connection()
            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT * FROM accommodations WHERE url = %s", (str(url),))
                    row = cursor.fetchone()
            finally:
                conn.close()
            if row:
                added.append(URLResponse(
                    id=row[0],
                    url=row[1],
                    phone=row[2],
                    processed_at=row[3],
                    created_at=row[4],
                    error=row[5]
                ))
        except Exception as e:
            errors.append({"url": str(url), "error": str(e)})
    return {
        "message": f"Accepted {len(added)} URL(s) for scraping",
        "added_count": len(added),
        "added": added,
        "errors_count": len(errors),
        "errors": errors if errors else None
    }


@app.get("/api/urls", response_model=List[URLResponse])
async def get_urls(skip: int = 0, limit: int = 100):
    """Get all URLs from database"""
    try:
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM accommodations ORDER BY id DESC LIMIT %s OFFSET %s", (limit, skip))
                rows = cursor.fetchall()
        finally:
            conn.close()
        return [
            URLResponse(
                id=row[0],
                url=row[1],
                phone=row[2],
                processed_at=row[3],
                created_at=row[4],
                error=row[5]
            )
            for row in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching URLs: {str(e)}")

@app.get("/api/urls/{url_id}", response_model=URLResponse)
async def get_url(url_id: int):
    """Get a specific URL by ID"""
    try:
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM accommodations WHERE id = %s", (url_id,))
                row = cursor.fetchone()
        finally:
            conn.close()
        if not row:
            raise HTTPException(status_code=404, detail="URL not found")
        
        return URLResponse(
            id=row[0],
            url=row[1],
            phone=row[2],
            processed_at=row[3],
            created_at=row[4],
            error=row[5]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching URL: {str(e)}")

@app.get("/api/statistics", response_model=StatisticsResponse)
async def get_statistics():
    """Get database statistics"""
    try:
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM accommodations")
                total = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM accommodations WHERE phone IS NOT NULL")
                with_phone = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM accommodations WHERE phone IS NULL AND error IS NULL")
                pending = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM accommodations WHERE error IS NOT NULL")
                errors = cursor.fetchone()[0]
        finally:
            conn.close()
        return StatisticsResponse(
            total=total,
            with_phone=with_phone,
            pending=pending,
            errors=errors
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching statistics: {str(e)}")

def _process_urls_sync(batch_size: int, headless: bool) -> int:
    """
    Synchronous Playwright processing. Must be run in a thread when called from async (FastAPI).
    """
    from olx_phone_scraper import extract_phone_from_url, create_browser_context
    from playwright.sync_api import sync_playwright

    accommodations = get_unprocessed_accommodations()
    if not accommodations:
        return 0

    processed_count = 0
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=headless,
            args=['--disable-blink-features=AutomationControlled']
        )
        context = create_browser_context(browser, headless)
        try:
            for accommodation_id, url in accommodations[:batch_size]:
                try:
                    phone = extract_phone_from_url(url, context)
                    if phone:
                        update_accommodation_phone(accommodation_id, phone)
                    else:
                        update_accommodation_phone(accommodation_id, None, "Phone number not found")
                    processed_count += 1
                except Exception as e:
                    update_accommodation_phone(accommodation_id, None, str(e))
        finally:
            context.close()
            browser.close()
    return processed_count


@app.post("/api/process", response_model=ProcessResponse)
async def process_urls(background_tasks: BackgroundTasks, batch_size: int = 10, headless: bool = True):
    """
    Process unprocessed URLs
    
    - **batch_size**: Number of URLs to process (default: 10)
    - **headless**: Run browser in headless mode (default: True)
    """
    try:
        accommodations = get_unprocessed_accommodations()
        if not accommodations:
            return ProcessResponse(
                message="No unprocessed accommodations found",
                processed_count=0
            )
        # Run sync Playwright in a thread to avoid "Sync API inside asyncio loop" error
        processed_count = await asyncio.to_thread(_process_urls_sync, batch_size, headless)
        return ProcessResponse(
            message=f"Processed {processed_count} accommodations",
            processed_count=processed_count
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing URLs: {str(e)}")

@app.get("/api/queue/status", response_model=QueueStatusResponse)
async def get_queue_status():
    """Get Redis queue status"""
    try:
        redis_queue = get_redis_queue()
        is_connected = redis_queue.is_connected()
        
        if is_connected:
            sizes = redis_queue.get_queue_size()
            return QueueStatusResponse(
                pending=sizes['pending'],
                processing=sizes['processing'],
                results=sizes['results'],
                failed=sizes['failed'],
                redis_connected=True
            )
        else:
            return QueueStatusResponse(
                pending=0,
                processing=0,
                results=0,
                failed=0,
                redis_connected=False
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching queue status: {str(e)}")

@app.post("/api/queue/add")
async def add_to_queue(request: URLRequest):
    """Add URL to Redis queue"""
    try:
        redis_queue = get_redis_queue()
        
        if not redis_queue.is_connected():
            raise HTTPException(status_code=503, detail="Redis is not connected")
        
        success = redis_queue.enqueue_url(str(request.url), request.priority)
        
        if success:
            return {
                "message": "URL added to queue",
                "url": str(request.url),
                "priority": request.priority
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to add URL to queue")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding to queue: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
