#!/usr/bin/env python3
"""
Caching request module
"""
import redis
import requests
from functools import wraps
from typing import Callable


def track_get_page(fn: Callable) -> Callable:
    """Decorator for get_page to add caching and access count tracking."""
    @wraps(fn)
    def wrapper(url: str) -> str:
        """Wrapper function to handle caching and counting accesses."""
        try:
            client = redis.Redis(host='localhost', port=6379, db=0)

            # Increment the count of accesses to the URL
            client.incr(f'count:{url}')

            # Check if the URL's content is already cached
            cached_page = client.get(f'page:{url}')
            if cached_page:
                print(f"Cache hit for {url}")
                return cached_page.decode('utf-8')

            # If not cached, fetch the content from the URL
            print(f"Cache miss for {url}, fetching from the internet...")
            response = fn(url)

            # Cache the fetched content with an expiration time of 10 seconds
            client.setex(f'page:{url}', 10, response)
            return response
        except redis.ConnectionError as e:
            print(f"Redis connection error: {e}")
            return fn(url)
        except requests.RequestException as e:
            print(f"HTTP request error: {e}")
            return ""
    return wrapper


@track_get_page
def get_page(url: str) -> str:
    """Makes an HTTP request to a given endpoint."""
    response = requests.get(url)
    response.raise_for_status()
    return response.text


if __name__ == "__main__":
    test_url = "http://slowwly.robertomurray.co.uk"

    # Fetching the page for the first time (expected to be a cache miss)
    print("Fetching page content...")
    content = get_page(test_url)
    print(content[:200])  # Print the first 200 characters of the content

    # Fetching the page again (expected to be a cache hit)
    print("\nFetching page content again (should be cached)...")
    content = get_page(test_url)
    print(content[:200])  # Print the first 200 characters of the content
