import requests
from bs4 import BeautifulSoup


def scrape_google(keywords: list) -> list:
    """Collect Google search results for each keyword and return list of dicts."""
    results = []
    for kw in keywords:
        r = requests.get("https://www.google.com/search", params={"q": kw}, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(r.text, 'html.parser')
        for g in soup.select('div.g'):
            link = g.find('a')
            if link:
                title = link.get_text(strip=True)
                href = link['href']
                results.append({'name': title, 'url': href})
    return results
