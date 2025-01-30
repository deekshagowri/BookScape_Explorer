import requests
from typing import Dict, List, Optional
import time

class GoogleBooksAPI:
    """Handler for Google Books API interactions."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.googleapis.com/books/v1/volumes"
    
    def search_books(self, query: str, max_results: int = 40) -> List[Dict]:
        """
        Search for books using the Google Books API.
        
        Args:
            query: Search term
            max_results: Maximum number of results to return
            
        Returns:
            List of book data dictionaries
        """
        all_books = []
        start_index = 0
        
        while len(all_books) < max_results:
            params = {
                'q': query,
                'key': self.api_key,
                'maxResults': min(40, max_results - len(all_books)),
                'startIndex': start_index
            }
            
            try:
                response = requests.get(self.base_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                if 'items' not in data:
                    break
                    
                all_books.extend(data['items'])
                start_index += len(data['items'])
                
                time.sleep(1)  # Rate limiting
                
            except requests.exceptions.RequestException as e:
                print(f"API request failed: {e}")
                break
                
        return all_books[:max_results]