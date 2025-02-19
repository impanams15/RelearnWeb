"""
Quadropic OSS
https://oss.quadropic.com
Author: Mohamed Kamran
Date: Feb 19th 2025

This file contains the implementation of the Firecrawl search functionality.
"""

from firecrawl import FirecrawlApp
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

REQUIRED_ENV_VARS = {
    "FIRECRAWL_API_KEY": "Firecrawl API key for authentication"
}

def validate_environment():
    missing_vars = [var for var, description in REQUIRED_ENV_VARS.items() 
                   if not os.getenv(var)]
    if missing_vars:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing_vars)}")

def crawl_firechain(query: str, timeout: int = 15000, 
                   limit: int = 5, verbose: bool = False) -> dict:
    validate_environment()
    
    firecrawlapp = FirecrawlApp(
        api_key=os.getenv("FIRECRAWL_API_KEY"),
    )
    
    search_results = firecrawlapp.search(
        query=query,
        params={
            "timeout": timeout,
            "limit": limit,
            "scrapeOptions": {"formats": ['markdown']},
        }
    )
    
    return search_results

# To test this function, run the following command:
if __name__ == "__main__":
    response = crawl_firechain(
        query="How to make a Flutter Firebase Riverpod App?",
        verbose=True
    )
    print(response)