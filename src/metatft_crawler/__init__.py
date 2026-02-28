"""
MetaTFT Crawler - Extract competitive Teamfight Tactics meta data from MetaTFT.com
"""

__version__ = "0.1.0"
__author__ = "albertphan"

from .crawlers.comps import crawl_tft_meta
from .crawlers.units import crawl_all_units
from .crawlers.items import crawl_all_items
from .crawlers.augments import crawl_all_augments

__all__ = ["crawl_tft_meta", "crawl_all_units", "crawl_all_items", "crawl_all_augments"]
