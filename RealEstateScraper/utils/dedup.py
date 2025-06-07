"""Utilities for fuzzy matching to remove duplicates"""
from fuzzywuzzy import fuzz


def is_duplicate(a: str, b: str, threshold: int = 80) -> bool:
    return fuzz.ratio(a, b) >= threshold
