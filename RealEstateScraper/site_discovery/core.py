from .google_scraper import scrape_google
from .bing_api import search_bing
from .custom_crawler import custom_discover

def discover_sites(method: str, keywords: list) -> list:
    if method == "google":
        return scrape_google(keywords)
    elif method == "bing":
        return search_bing(keywords)
    elif method == "custom":
        return custom_discover(keywords)
    else:
        return []
