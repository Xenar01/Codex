"""Scraper for opensooq.sy using requests and BeautifulSoup."""

from datetime import datetime
from pathlib import Path
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://sy.opensooq.com"


def scrape(fields=None, save_path="images", credentials=None, proxy=None):
    session = requests.Session()
    if proxy:
        session.proxies.update({"http": proxy, "https": proxy})

    if credentials:
        session.post(f"{BASE_URL}/login", data={"username": credentials['username'], "password": credentials['password']})

    listings = []
    resp = session.get(BASE_URL)
    soup = BeautifulSoup(resp.text, "html.parser")
    out_dir = Path(save_path) / "opensooq" / datetime.now().strftime("%Y%m%d")
    out_dir.mkdir(parents=True, exist_ok=True)

    for i, item in enumerate(soup.select(".post")):
        data = {}
        if not fields or "title" in fields:
            title = item.select_one("h2")
            data["title"] = title.get_text(strip=True) if title else ""
        if not fields or "price" in fields:
            price = item.select_one(".price")
            data["price"] = price.get_text(strip=True) if price else ""
        if not fields or "description" in fields:
            desc = item.select_one(".description")
            data["description"] = desc.get_text(strip=True) if desc else ""
        if not fields or "location" in fields:
            loc = item.select_one(".city")
            data["location"] = loc.get_text(strip=True) if loc else ""
        if not fields or "images" in fields:
            data["images"] = []
            for idx, img in enumerate(item.select("img")):
                url = img.get("data-src") or img.get("src")
                if not url:
                    continue
                img_data = session.get(url)
                fname = f"{data.get('title','listing')}_{data.get('location','')}_{idx}.jpg"
                fname = fname.replace("/", "_")
                path = out_dir / fname
                with open(path, "wb") as f:
                    f.write(img_data.content)
                data.setdefault("images", []).append(str(path))
        listings.append(data)

    return listings
