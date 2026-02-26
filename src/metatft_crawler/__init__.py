"""
MetaTFT Crawler - Extract competitive Teamfight Tactics meta data from MetaTFT.com
"""

__version__ = "0.1.0"
__author__ = "albertphan"

from .crawlers.comps import crawl_tft_meta
from .crawlers.units import crawl_all_units

__all__ = ["crawl_tft_meta", "crawl_all_units"]
