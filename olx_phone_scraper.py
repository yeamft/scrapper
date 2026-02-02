"""OLX accommodation phone scraper (Playwright, PostgreSQL)."""
from playwright.sync_api import sync_playwright
import re
import time
from datetime import datetime
from typing import Optional

from db import get_connection, init_database

def normalize_phone(raw: str) -> Optional[str]:
    """
    Normalize and validate Ukrainian phone number.
    Returns normalized form (e.g. +380XXXXXXXXX) or None if invalid.
    Accepts: 0260127010, 0 26 012 70 10, +380260127010, 380260127010, +38 098 2669582
    """
    if not raw or not isinstance(raw, str):
        return None
    
    # Skip placeholder numbers
    if "+380123456789" in raw:
        return None
        
    digits = re.sub(r"\D", "", raw)
    if not digits:
        return None
    
    # Handle +38 format (should be +380)
    if digits.startswith("38") and len(digits) == 11:
        digits = "380" + digits[2:]
    elif digits.startswith("380") and len(digits) == 12:
        pass
    elif digits.startswith("0") and len(digits) == 10:
        digits = "380" + digits[1:]
    elif len(digits) == 9 and digits[0] in "356789":
        digits = "380" + digits
    else:
        return None
    
    if len(digits) != 12 or not digits.isdigit():
        return None
    
    return "+" + digits

def add_accommodation_url(url: str):
    """Add a new accommodation URL to the database"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO accommodations (url) VALUES (%s) ON CONFLICT (url) DO NOTHING",
                (url,),
            )
        conn.commit()
        print(f"Added URL: {url}")
    except Exception as e:
        print(f"Error adding URL: {e}")
    finally:
        conn.close()


def get_unprocessed_accommodations():
    """Get all accommodations that haven't been processed yet"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, url FROM accommodations
                WHERE phone IS NULL AND error IS NULL
                ORDER BY id
            """)
            return cursor.fetchall()
    finally:
        conn.close()


def update_accommodation_phone(accommodation_id: int, phone: Optional[str], error: Optional[str] = None):
    """Update accommodation with phone number or error"""
    conn = get_connection()
    try:
        processed_at = datetime.now().isoformat()
        with conn.cursor() as cursor:
            if error:
                cursor.execute("""
                    UPDATE accommodations
                    SET error = %s, processed_at = %s
                    WHERE id = %s
                """, (error, processed_at, accommodation_id))
            else:
                cursor.execute("""
                    UPDATE accommodations
                    SET phone = %s, processed_at = %s, error = NULL
                    WHERE id = %s
                """, (phone, processed_at, accommodation_id))
        conn.commit()
    finally:
        conn.close()


def extract_phone_from_url(url: str, context) -> Optional[str]:
    """
    Extract phone number from an OLX accommodation URL
    """
    page = context.new_page()
    phone = None
    
    try:
        print(f"  Opening: {url}")
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(5000)
        
        # Check if login is required
        if "login" in page.url.lower() or page.locator("input[type='email']").count() > 0:
            print(f"  Login required, filling email...")
            # Fill email field
            email_input = page.locator("input[type='email'], input[name='email'], input[placeholder*='email']").first
            if email_input.count() > 0:
                email_input.fill("test@example.com")
                # Look for continue/submit button
                continue_btn = page.locator("button:has-text('Продовжити'), button:has-text('Continue'), button[type='submit']").first
                if continue_btn.count() > 0:
                    continue_btn.click()
                    page.wait_for_timeout(3000)
        
        # Close cookie banner
        try:
            page.locator("button:has-text('Погоджуюсь')").first.click(timeout=3000)
        except:
            pass
        
        # Click show phone button
        try:
            button_selectors = [
                "button:has-text('показати')",
                "button:has-text('Показати')", 
                "[data-testid='show-phone']",
                "button:has-text('показати телефон')",
                "a:has-text('показати')"
            ]
            
            clicked = False
            for selector in button_selectors:
                buttons = page.locator(selector)
                if buttons.count() > 0:
                    print(f"  Found button: {selector}")
                    buttons.last.scroll_into_view_if_needed()
                    page.wait_for_timeout(1000)
                    buttons.last.click(force=True)
                    print(f"  Clicked 'показати' button")
                    clicked = True
                    break
            
            if clicked:
                page.wait_for_timeout(5000)
            else:
                print(f"  No 'показати' button found")
        except Exception as e:
            print(f"  Error clicking button: {e}")
        
        # Extract phone from tel: links
        tel_links = page.locator("a[href^='tel:']")
        for i in range(tel_links.count()):
            href = tel_links.nth(i).get_attribute("href") or ""
            raw = href.replace("tel:", "").strip()
            if raw and "+380123456789" not in raw:
                phone = normalize_phone(raw)
                if phone:
                    print(f"  Found phone: {phone}")
                    return phone
        
        # Extract from page text
        text = page.text_content("body") or ""
        patterns = [
            r"\+38\s*0?\s*\d{2}\s*\d{3}\s*\d{2}\s*\d{2}\s*\d{2}",
            r"\+380\s*\d{2}\s*\d{3}\s*\d{2}\s*\d{2}\s*\d{2}",
            r"0\s*\d{2}\s*\d{3}\s*\d{2}\s*\d{2}\s*\d{2}"
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if "+380123456789" not in match:
                    phone = normalize_phone(match)
                    if phone:
                        print(f"  Found phone: {phone}")
                        return phone
        
    except Exception as e:
        print(f"  Error: {e}")
    finally:
        page.close()
    
    return phone


def create_browser_context(browser, headless: bool = True):
    """
    Create a browser context with anti-detection measures to bypass Cloudflare
    
    Args:
        browser: Playwright browser instance
        headless: Run in headless mode
        
    Returns:
        Browser context with stealth settings
    """
    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        locale='uk-UA',
        timezone_id='Europe/Kiev',
        # Add realistic headers to avoid detection
        extra_http_headers={
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
        }
    )
    
    # Hide automation indicators
    context.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        window.chrome = {
            runtime: {}
        };
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });
    """)
    
    return context


def process_accommodations(headless: bool = True, delay: float = 2.0):
    """
    Process all unprocessed accommodations from the database
    
    Args:
        headless: Run browser in headless mode
        delay: Delay between requests in seconds
    """
    accommodations = get_unprocessed_accommodations()
    
    if not accommodations:
        print("No unprocessed accommodations found in database.")
        return
    
    print(f"Found {len(accommodations)} unprocessed accommodation(s)")
    
    with sync_playwright() as p:
        # Launch browser with anti-detection args
        browser = p.chromium.launch(
            headless=headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
            ]
        )
        
        # Create stealth context
        context = create_browser_context(browser, headless)
        
        for idx, (accommodation_id, url) in enumerate(accommodations, 1):
            print(f"\n[{idx}/{len(accommodations)}] Processing accommodation ID: {accommodation_id}")
            
            try:
                phone = extract_phone_from_url(url, context)
                
                if phone:
                    update_accommodation_phone(accommodation_id, phone)
                    print(f"  [+] Successfully extracted phone: {phone}")
                else:
                    update_accommodation_phone(accommodation_id, None, "Phone number not found")
                    print(f"  [-] Phone number not found")
                
            except Exception as e:
                error_msg = str(e)
                update_accommodation_phone(accommodation_id, None, error_msg)
                print(f"  [-] Error: {error_msg}")
            
            # Delay between requests to avoid being blocked
            if idx < len(accommodations):
                time.sleep(delay)
        
        context.close()
        browser.close()
    
    print("\nProcessing complete!")


def get_statistics():
    """Get statistics about processed accommodations"""
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
        print("\n=== Database Statistics ===")
        print(f"Total accommodations: {total}")
        print(f"With phone numbers: {with_phone}")
        print(f"Pending: {pending}")
        print(f"Errors: {errors}")
    finally:
        conn.close()


def main():
    """Main function with CLI interface"""
    import sys
    
    init_database()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "add":
            if len(sys.argv) < 3:
                print("Usage: python olx_phone_scraper.py add <URL>")
                return
            url = sys.argv[2]
            add_accommodation_url(url)
        
        elif command == "process":
            headless = "--headless" in sys.argv or "-h" in sys.argv
            process_accommodations(headless=headless)
        
        elif command == "stats":
            get_statistics()
        
        elif command == "add-batch":
            # Add multiple URLs from a file (one URL per line)
            if len(sys.argv) < 3:
                print("Usage: python olx_phone_scraper.py add-batch <file.txt>")
                return
            file_path = sys.argv[2]
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    urls = [line.strip() for line in f if line.strip()]
                for url in urls:
                    add_accommodation_url(url)
                print(f"\nAdded {len(urls)} URLs from {file_path}")
            except Exception as e:
                print(f"Error reading file: {e}")
        
        else:
            print("Unknown command. Available commands:")
            print("  add <URL>          - Add a single accommodation URL")
            print("  add-batch <file>   - Add URLs from a text file (one per line)")
            print("  process            - Process all unprocessed accommodations")
            print("  process --headless - Process in headless mode")
            print("  stats              - Show database statistics")
    else:
        print("OLX Phone Scraper - Database Edition")
        print("\nUsage:")
        print("  python olx_phone_scraper.py add <URL>")
        print("  python olx_phone_scraper.py add-batch <file.txt>")
        print("  python olx_phone_scraper.py process")
        print("  python olx_phone_scraper.py stats")


if __name__ == "__main__":
    import sys
    import io
    
    # Fix encoding for Windows console to handle Ukrainian characters
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    main()
