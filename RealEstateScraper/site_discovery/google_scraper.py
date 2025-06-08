import os
import yaml
import requests
from bs4 import BeautifulSoup


def _load_config():
    cfg_path = os.path.join(os.path.dirname(__file__), "..", "config.yaml")
    cfg_path = os.path.abspath(cfg_path)
    with open(cfg_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def scrape_google(keywords: list) -> list:
    """Collect Google search results for each keyword and return list of dicts."""
    config = _load_config()
    proxy = config.get("network", {}).get("proxy")
    proxies = {"http": proxy, "https": proxy} if proxy else None

    results = []
    for kw in keywords:
        resp = requests.get(
            "https://www.google.com/search",
            params={"q": kw},
            headers={"User-Agent": "Mozilla/5.0"},
            proxies=proxies,
            timeout=10,
        )
        soup = BeautifulSoup(resp.text, "html.parser")
        for g in soup.select("div.g"):
            link = g.find("a", href=True)
            if link and link["href"].startswith("http"):
                title = link.get_text(strip=True)
                results.append({"name": title, "url": link["href"]})
    return results

