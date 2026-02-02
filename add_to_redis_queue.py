"""
Script to add URLs to Redis queue
Usage: python add_to_redis_queue.py <URL> [priority]
"""
import sys
from redis_queue import get_redis_queue

def main():
    if len(sys.argv) < 2:
        print("Usage: python add_to_redis_queue.py <URL> [priority]")
        print("Example: python add_to_redis_queue.py 'https://www.olx.ua/...' 10")
        sys.exit(1)
    
    url = sys.argv[1]
    priority = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    
    queue = get_redis_queue()
    
    if not queue.is_connected():
        print("Error: Redis is not connected!")
        print("Please start Redis server first:")
        print("  Windows: redis-server.exe")
        print("  Linux/Mac: redis-server")
        sys.exit(1)
    
    success = queue.enqueue_url(url, priority)
    
    if success:
        print(f"✓ Added URL to Redis queue: {url}")
        print(f"  Priority: {priority}")
        
        sizes = queue.get_queue_size()
        print(f"\nQueue Status:")
        print(f"  Pending: {sizes['pending']}")
        print(f"  Processing: {sizes['processing']}")
        print(f"  Results: {sizes['results']}")
        print(f"  Failed: {sizes['failed']}")
    else:
        print("✗ Failed to add URL to queue")
        sys.exit(1)

if __name__ == "__main__":
    main()
