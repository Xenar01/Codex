"""Scraper for yabaiti.com using BeautifulSoup."""

from datetime import datetime
from pathlib import Path
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://yabaiti.com"


def scrape(fields=None, save_path="images", credentials=None, proxy=None):
    session = requests.Session()
    if proxy:
        session.proxies.update({"http": proxy, "https": proxy})

    resp = session.get(BASE_URL)
    soup = BeautifulSoup(resp.text, "html.parser")
    out_dir = Path(save_path) / "yabaiti" / datetime.now().strftime("%Y%m%d")
    out_dir.mkdir(parents=True, exist_ok=True)

    listings = []
    for i, item in enumerate(soup.select(".listing")):
        data = {}
        if not fields or "title" in fields:
            t = item.select_one(".title")
            data["title"] = t.get_text(strip=True) if t else ""
        if not fields or "price" in fields:
            p = item.select_one(".price")
            data["price"] = p.get_text(strip=True) if p else ""
        if not fields or "description" in fields:
            d = item.select_one(".desc")
            data["description"] = d.get_text(strip=True) if d else ""
        if not fields or "location" in fields:
            l = item.select_one(".city")
            data["location"] = l.get_text(strip=True) if l else ""
        if not fields or "images" in fields:
            data["images"] = []
            for idx, img in enumerate(item.select("img")):
                src = img.get("src")
                if not src:
                    continue
                img_data = session.get(src)
                fname = f"{data.get('title','listing')}_{data.get('location','')}_{idx}.jpg"
                fname = fname.replace("/", "_")
                path = out_dir / fname
                with open(path, "wb") as f:
                    f.write(img_data.content)
                data["images"].append(str(path))
        listings.append(data)

    return listings
