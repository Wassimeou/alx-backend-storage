# web.py
import requests
import redis
import time
from functools import wraps

# Initialize Redis client
cache = redis.Redis(host='localhost', port=6379, db=0)

def cache_page(expiration=10):
    def decorator(func):
        @wraps(func)
        def wrapper(url):
            cache_key = f"page:{url}"
            count_key = f"count:{url}"
            
            # Increment access count
            cache.incr(count_key)

            # Try to get cached content
            cached_content = cache.get(cache_key)
            if cached_content:
                return cached_content.decode('utf-8')

            # Fetch the page content
            content = func(url)
            
            # Cache the fetched content
            cache.setex(cache_key, expiration, content)
            return content
        return wrapper
    return decorator

@cache_page(expiration=10)
def get_page(url: str) -> str:
    response = requests.get(url)
    return response.text

if __name__ == "__main__":
    test_url = "http://slowwly.robertomurray.co.uk"
    print("Fetching page content...")
    content = get_page(test_url)
    print(content[:200])  # Print first 200 characters of the content

    # Fetch again to see the caching effect
    print("\nFetching page content again (should be cached)...")
    content = get_page(test_url)
    print(content[:200])
