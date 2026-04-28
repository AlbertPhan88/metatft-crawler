#!/usr/bin/env python3
"""
TFT Meta Crawler - Extracts competitive meta data from MetaTFT.com/comps
"""

import asyncio
import json
from datetime import datetime
from playwright.async_api import async_playwright
from typing import Dict, Any

from ..utils.browser import switch_language
from ..languages.loader import get_language_config


async def crawl_tft_meta(language: str = "en") -> Dict[str, Any]:
    """
    Crawl MetaTFT.com/comps and extract all comp, unit, and item data.

    Args:
        language: Language code ('en' for English, 'vi' for Vietnamese, etc.)

    Returns:
        Dictionary containing timestamp and all extracted comp data
    """

    base_url = "https://www.metatft.com/comps"

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        print(f"Navigating to {base_url} (Language: {language})...")
        try:
            await page.goto(base_url, wait_until="domcontentloaded", timeout=60000)
        except Exception as e:
            print(f"Navigation timeout: {e}")

        print("Waiting for page to fully render...")
        await page.wait_for_timeout(5000)

        # Scroll to load all lazy-loaded comp rows
        print("Scrolling to load all comps...")
        for _ in range(15):
            await page.evaluate("window.scrollBy(0, 1000)")
            await page.wait_for_timeout(400)
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(500)

        if language == "vi":
            print("Switching to Vietnamese...")
            await switch_language(page, "vi")
            await page.wait_for_timeout(2000)

        lang_config = get_language_config(language)

        print("Extracting comp data from page...")
        comps_data = await page.evaluate("""
            (langConfig) => {
                const comps = [];

                // Each comp is in a CompRowWrapper div
                const rows = document.querySelectorAll('div[class*="CompRowWrapper"]');

                for (const row of rows) {
                    // Comp name
                    const titleEl = row.querySelector('[class*="Comp_Title"]');
                    if (!titleEl) continue;
                    const name = titleEl.innerText.trim();
                    if (!name) continue;

                    // Tier (S/A/B/C/D)
                    const tierEl = row.querySelector('[class*="CompRowTier"]');
                    const tier = tierEl ? tierEl.innerText.trim() : '';

                    // Tags (playstyle, difficulty)
                    const tagEls = row.querySelectorAll('[class*="CompRowTag"]');
                    const tags = Array.from(tagEls).map(el => el.innerText.trim()).filter(t => t);
                    const playstyle = tags[0] || '';
                    const difficulty = tags[1] || '';

                    // Stats — parse from row innerText
                    const text = row.innerText;
                    const lines = text.split('\\n').map(l => l.trim()).filter(l => l);

                    const stats = {};
                    for (let i = 0; i < lines.length; i++) {
                        if (lines[i] === langConfig.avg_place && i + 1 < lines.length)
                            stats.avg_placement = parseFloat(lines[i + 1]) || null;
                        if (lines[i] === langConfig.pick_rate && i + 1 < lines.length)
                            stats.pick_rate = parseFloat(lines[i + 1]) || null;
                        if (lines[i] === langConfig.win_rate && i + 1 < lines.length)
                            stats.win_rate = lines[i + 1];
                        if (lines[i] === langConfig.top_4_rate && i + 1 < lines.length)
                            stats.top_4_rate = lines[i + 1];
                    }

                    // Units — from Unit_Wrapper divs (no hardcoded champion list)
                    const unitWrappers = row.querySelectorAll('div[class*="Unit_Wrapper"]');
                    const units = [];
                    for (const uw of unitWrappers) {
                        const imgs = uw.querySelectorAll('img');
                        const alts = Array.from(imgs)
                            .map(i => (i.alt || '').trim())
                            .filter(a => a.length > 1);

                        const isThreeStar = alts.some(a =>
                            a.includes('Three Star') || a.includes('Tướng 3 Sao'));
                        const filtered = alts.filter(a =>
                            !a.includes('Three Star') && !a.includes('Tướng 3 Sao') &&
                            a !== 'Teambuilder' && !a.includes('Copy') && !a.includes('Open In'));

                        if (filtered.length >= 1) {
                            units.push({
                                name: filtered[0],
                                items: filtered.slice(1),
                                is_three_star: isThreeStar,
                            });
                        }
                    }

                    if (units.length === 0) continue;

                    comps.push({ name, tier, playstyle, difficulty, stats, units });
                }

                return comps;
            }
        """, {
            'avg_place': lang_config.avg_place,
            'pick_rate': lang_config.pick_rate,
            'win_rate': lang_config.win_rate,
            'top_4_rate': lang_config.top_4_rate,
        })

        print(f"Found {len(comps_data)} comps")

        await browser.close()

        return {
            "timestamp": datetime.now().isoformat(),
            "source": "https://www.metatft.com/comps",
            "language": language,
            "total_comps_found": len(comps_data),
            "total_comps_crawled": len(comps_data),
            "comps": comps_data
        }


async def main(language: str = "en"):
    """Main entry point for the crawler."""
    result = await crawl_tft_meta(language=language)
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    import sys
    lang = sys.argv[1] if len(sys.argv) > 1 else "en"
    asyncio.run(main(language=lang))
