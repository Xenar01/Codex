
"""Scraper for ikar.sy using BeautifulSoup."""

import os
from datetime import datetime
from pathlib import Path
import requests
from bs4 import BeautifulSoup


BASE_URL = "https://ikar.sy"


def scrape(fields=None, save_path="images", credentials=None, proxy=None):
    """Scrape listings from ikar.sy and return list of dictionaries."""
    session = requests.Session()
    if proxy:
        session.proxies.update({"http": proxy, "https": proxy})

    if credentials:
        session.post(f"{BASE_URL}/login", data={"username": credentials['username'], "password": credentials['password']})

    listings = []
    resp = session.get(BASE_URL)
    soup = BeautifulSoup(resp.text, "html.parser")
    out_dir = Path(save_path) / "ikar" / datetime.now().strftime("%Y%m%d")
    out_dir.mkdir(parents=True, exist_ok=True)

    for i, item in enumerate(soup.select(".listing")):
        data = {}
        title = item.select_one(".title")
        if (not fields) or ("title" in fields):
            data["title"] = title.get_text(strip=True) if title else ""
        price = item.select_one(".price")
        if not fields or "price" in fields:
            data["price"] = price.get_text(strip=True) if price else ""
        desc = item.select_one(".desc")
        if not fields or "description" in fields:
            data["description"] = desc.get_text(strip=True) if desc else ""
        loc = item.select_one(".city")
        if not fields or "location" in fields:
            data["location"] = loc.get_text(strip=True) if loc else ""
        if not fields or "images" in fields:
            data["images"] = []
            for idx, img in enumerate(item.select("img")):
                url = img.get("src")
                if not url:
                    continue
                img_resp = session.get(url)
                fname = f"{data.get('title','listing')}_{data.get('location','')}_{idx}.jpg"
                fname = fname.replace("/", "_")
                path = out_dir / fname
                with open(path, "wb") as f:
                    f.write(img_resp.content)
                data["images"].append(str(path))
        listings.append(data)
    return listings