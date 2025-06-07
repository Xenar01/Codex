import csv
import json
from typing import List, Dict


def export_csv(listings: List[Dict], path: str) -> None:
    if not listings:
        return
    with open(path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=listings[0].keys())
        writer.writeheader()
        writer.writerows(listings)


def export_json(listings: List[Dict], path: str) -> None:
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(listings, f, ensure_ascii=False, indent=2)
