"""
Redis Task Queue Integration
Handles task queuing and distribution for scraping tasks
"""
import redis
import json
import time
from typing import Optional, Dict, Any
from datetime import datetime

class RedisTaskQueue:
    """Redis-based task queue for scraping tasks"""
    
    def __init__(self, redis_host='localhost', redis_port=6379, redis_db=0, password=None):
        """
        Initialize Redis connection
        
        Args:
            redis_host: Redis server host
            redis_port: Redis server port
            redis_db: Redis database number
            password: Redis password (if required)
        """
        self.redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            password=password,
            decode_responses=True,
            socket_connect_timeout=5
        )
        
        # Queue names
        self.QUEUE_NAME = 'olx:scraping:queue'
        self.PROCESSING_QUEUE = 'olx:scraping:processing'
        self.RESULTS_QUEUE = 'olx:scraping:results'
        self.FAILED_QUEUE = 'olx:scraping:failed'
        
        # Test connection
        try:
            self.redis_client.ping()
            print(f"Connected to Redis at {redis_host}:{redis_port}")
        except redis.ConnectionError as e:
            print(f"Warning: Could not connect to Redis: {e}")
            print("Tasks will be processed without Redis queue")
            self.redis_client = None
    
    def is_connected(self) -> bool:
        """Check if Redis is connected"""
        if not self.redis_client:
            return False
        try:
            return self.redis_client.ping()
        except:
            return False
    
    def enqueue_url(self, url: str, priority: int = 0) -> bool:
        """
        Add a URL to the scraping queue
        
        Args:
            url: OLX accommodation URL
            priority: Task priority (higher = more important)
            
        Returns:
            True if enqueued successfully
        """
        if not self.is_connected():
            return False
        
        task = {
            'url': url,
            'priority': priority,
            'created_at': datetime.now().isoformat(),
            'status': 'pending'
        }
        
        try:
            # Use sorted set for priority queue
            score = time.time() + (priority * 1000)  # Higher priority = higher score
            self.redis_client.zadd(self.QUEUE_NAME, {json.dumps(task): score})
            return True
        except Exception as e:
            print(f"Error enqueuing task: {e}")
            return False
    
    def dequeue_url(self, timeout: int = 5) -> Optional[Dict[str, Any]]:
        """
        Get next URL from queue (blocking)
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            Task dictionary or None
        """
        if not self.is_connected():
            return None
        
        try:
            # Get highest priority task (highest score)
            result = self.redis_client.zrevrange(self.QUEUE_NAME, 0, 0, withscores=True)
            
            if result:
                task_json, score = result[0]
                task = json.loads(task_json)
                
                # Move to processing queue
                self.redis_client.zrem(self.QUEUE_NAME, task_json)
                self.redis_client.zadd(self.PROCESSING_QUEUE, {task_json: time.time()})
                
                return task
            return None
        except Exception as e:
            print(f"Error dequeuing task: {e}")
            return None
    
    def mark_complete(self, url: str, phone: Optional[str] = None, error: Optional[str] = None):
        """
        Mark task as complete
        
        Args:
            url: The URL that was processed
            phone: Extracted phone number (if found)
            error: Error message (if failed)
        """
        if not self.is_connected():
            return
        
        result = {
            'url': url,
            'phone': phone,
            'error': error,
            'completed_at': datetime.now().isoformat()
        }
        
        try:
            # Remove from processing queue
            processing_tasks = self.redis_client.zrange(self.PROCESSING_QUEUE, 0, -1)
            for task_json in processing_tasks:
                task = json.loads(task_json)
                if task.get('url') == url:
                    self.redis_client.zrem(self.PROCESSING_QUEUE, task_json)
                    break
            
            # Add to results or failed queue
            if error:
                self.redis_client.lpush(self.FAILED_QUEUE, json.dumps(result))
            else:
                self.redis_client.lpush(self.RESULTS_QUEUE, json.dumps(result))
        except Exception as e:
            print(f"Error marking task complete: {e}")
    
    def get_queue_size(self) -> Dict[str, int]:
        """Get sizes of all queues"""
        if not self.is_connected():
            return {'pending': 0, 'processing': 0, 'results': 0, 'failed': 0}
        
        return {
            'pending': self.redis_client.zcard(self.QUEUE_NAME),
            'processing': self.redis_client.zcard(self.PROCESSING_QUEUE),
            'results': self.redis_client.llen(self.RESULTS_QUEUE),
            'failed': self.redis_client.llen(self.FAILED_QUEUE)
        }
    
    def clear_queues(self):
        """Clear all queues (use with caution!)"""
        if not self.is_connected():
            return
        
        self.redis_client.delete(self.QUEUE_NAME)
        self.redis_client.delete(self.PROCESSING_QUEUE)
        self.redis_client.delete(self.RESULTS_QUEUE)
        self.redis_client.delete(self.FAILED_QUEUE)
        print("All queues cleared")


# Global Redis queue instance
_redis_queue = None

def get_redis_queue() -> RedisTaskQueue:
    """Get or create Redis queue instance"""
    global _redis_queue
    if _redis_queue is None:
        _redis_queue = RedisTaskQueue()
    return _redis_queue
