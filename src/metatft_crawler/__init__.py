"""
MetaTFT Crawler - Extract competitive Teamfight Tactics meta data from MetaTFT.com
"""

__version__ = "0.1.0"
__author__ = "albertphan"

from .crawlers.comps import crawl_tft_meta
from .crawlers.units import crawl_all_units
from .crawlers.items import crawl_all_items
from .crawlers.augments import crawl_all_augments
from .languages.loader import get_language_config, get_supported_languages

__all__ = [
    "crawl_tft_meta",
    "crawl_all_units",
    "crawl_all_items",
    "crawl_all_augments",
    "get_language_config",
    "get_supported_languages",
]
