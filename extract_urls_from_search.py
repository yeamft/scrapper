"""
Helper script to extract accommodation URLs from OLX search results page
and add them to the database (PostgreSQL).
"""
from playwright.sync_api import sync_playwright
import re
from db import get_connection, init_database


def extract_accommodation_urls(search_url: str, max_pages: int = 5):
    """
    Extract accommodation URLs from OLX search results page
    
    Args:
        search_url: URL of the search results page (e.g., https://www.olx.ua/uk/nedvizhimost/kvartiry/)
        max_pages: Maximum number of pages to scrape (default: 5)
    
    Returns:
        List of accommodation URLs
    """
    urls = set()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
            print(f"Opening search results: {search_url}")
            page.goto(search_url, wait_until="networkidle")
            
            # Close cookie banner if it appears
            try:
                page.get_by_role("button", name=re.compile("Погоджуюсь|Прийняти|Згода", re.I)).click(timeout=3000)
            except Exception:
                pass
            
            page_num = 1
            
            while page_num <= max_pages:
                print(f"\nScraping page {page_num}...")
                
                # Wait for listings to load
                page.wait_for_timeout(2000)
                
                # Find all accommodation links
                # OLX accommodation links typically have pattern: /d/uk/obyavlenie/...
                links = page.locator("a[href*='/d/uk/obyavlenie/']").all()
                
                page_urls = []
                for link in links:
                    href = link.get_attribute("href")
                    if href:
                        # Make sure it's a full URL
                        if href.startswith("/"):
                            href = "https://www.olx.ua" + href
                        elif href.startswith("http"):
                            pass  # Already full URL
                        else:
                            continue
                        
                        # Filter out non-accommodation links
                        if "/d/uk/obyavlenie/" in href and href not in urls:
                            urls.add(href)
                            page_urls.append(href)
                
                print(f"  Found {len(page_urls)} new accommodation URLs on this page")
                print(f"  Total unique URLs so far: {len(urls)}")
                
                # Try to go to next page
                if page_num < max_pages:
                    try:
                        # Look for "Next" or "Наступна" button
                        next_button = page.get_by_role("link", name=re.compile("Наступна|Next|→", re.I)).first
                        if next_button.count() > 0:
                            next_button.click()
                            page.wait_for_timeout(3000)
                            page_num += 1
                        else:
                            print("  No more pages found")
                            break
                    except Exception as e:
                        print(f"  Could not navigate to next page: {e}")
                        break
                else:
                    break
            
            browser.close()
            
        except Exception as e:
            print(f"Error: {e}")
            browser.close()
    
    return list(urls)


def add_urls_to_database(urls: list):
    """Add URLs to the database"""
    conn = get_connection()
    added = 0
    skipped = 0
    try:
        with conn.cursor() as cursor:
            for url in urls:
                try:
                    cursor.execute(
                        "INSERT INTO accommodations (url) VALUES (%s) ON CONFLICT (url) DO NOTHING",
                        (url,),
                    )
                    if cursor.rowcount > 0:
                        added += 1
                    else:
                        skipped += 1
                except Exception as e:
                    print(f"Error adding URL {url}: {e}")
        conn.commit()
    finally:
        conn.close()
    print(f"\n✓ Added {added} new URLs to database")
    print(f"  Skipped {skipped} URLs (already exist)")


def main():
    import sys
    
    init_database()
    
    # Default search URL for apartments
    search_url = "https://www.olx.ua/uk/nedvizhimost/kvartiry/"
    max_pages = 5
    
    if len(sys.argv) > 1:
        search_url = sys.argv[1]
    
    if len(sys.argv) > 2:
        try:
            max_pages = int(sys.argv[2])
        except ValueError:
            print("Invalid max_pages value, using default: 5")
    
    print(f"Extracting accommodation URLs from: {search_url}")
    print(f"Maximum pages to scrape: {max_pages}\n")
    
    urls = extract_accommodation_urls(search_url, max_pages)
    
    if urls:
        print(f"\nFound {len(urls)} unique accommodation URLs")
        add_urls_to_database(urls)
    else:
        print("\nNo accommodation URLs found")


if __name__ == "__main__":
    main()
