
"""Utilities for fuzzy matching and deduplication."""


from fuzzywuzzy import fuzz


def is_duplicate(a: str, b: str, threshold: int = 80) -> bool:
    return fuzz.ratio(a, b) >= threshold



def dedup_listings(session, new_listings: list, threshold: int = 85) -> list:
    """Return only listings that do not already exist in DB."""
    from .db import Listing

    unique = []
    existing = session.query(Listing).all()
    for listing in new_listings:
        text_new = f"{listing.get('title','')} {listing.get('price','')} {listing.get('location','')}"
        dup = False
        for ex in existing:
            text_ex = f"{ex.title} {ex.price} {ex.location}"
            if fuzz.token_set_ratio(text_new, text_ex) >= threshold:
                dup = True
                break
        if not dup:
            unique.append(listing)
    return unique

