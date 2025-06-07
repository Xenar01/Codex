
import os
import yaml
import requests


def _load_config():
    cfg_path = os.path.join(os.path.dirname(__file__), "..", "config.yaml")
    cfg_path = os.path.abspath(cfg_path)
    with open(cfg_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def search_bing(keywords: list) -> list:
    config = _load_config()
    key = os.getenv("BING_API_KEY") or config.get("bing_api_key", "")
    proxy = config.get("network", {}).get("proxy")
    proxies = {"http": proxy, "https": proxy} if proxy else None

    results = []
    headers = {"Ocp-Apim-Subscription-Key": key}
    for kw in keywords:
        resp = requests.get(
            "https://api.bing.microsoft.com/v7.0/search",
            params={"q": kw},
            headers=headers,
            proxies=proxies,
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            for item in data.get("webPages", {}).get("value", []):
                results.append({"name": item.get("name"), "url": item.get("url")})
    return results


