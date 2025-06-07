import requests
import os


def search_bing(keywords: list) -> list:
    key = os.getenv("BING_API_KEY")
    results = []
    headers = {"Ocp-Apim-Subscription-Key": key}
    for kw in keywords:
        resp = requests.get("https://api.bing.microsoft.com/v7.0/search", params={"q": kw}, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            for item in data.get('webPages', {}).get('value', []):
                results.append({'name': item.get('name'), 'url': item.get('url')})
    return results
