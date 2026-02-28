#!/usr/bin/env python3
"""
TFT Items Crawler - Extracts detailed data for each item from MetaTFT.com/items
"""

import asyncio
import json
import time
from datetime import datetime
from playwright.async_api import async_playwright
from typing import Dict, List, Any

from ..utils.browser import switch_language


async def crawl_all_items(language: str = "en", limit_items: int = None) -> Dict[str, Any]:
    """
    Crawl MetaTFT.com/items and extract data for items.

    Args:
        language: Language code ('en' for English, 'vi' for Vietnamese, etc.)
        limit_items: Limit crawling to N items (None = crawl all). Useful for testing.

    Returns:
        Dictionary containing timestamp and item data
    """

    # Use the same base URL for all languages - language switching is done via selector
    base_url = "https://www.metatft.com/items"

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

        # Switch language if needed
        if language == "vi":
            print("Switching to Vietnamese...")
            await switch_language(page, "vi")

        # Extract all items from the main items page
        print("Extracting all items and their links...")
        items_list = await page.evaluate("""
            () => {
                const items = [];
                const pageText = document.body.innerText;

                // Find all item links on the page
                const allLinks = Array.from(document.querySelectorAll('a[href*="/items/"]'));
                const itemLinks = allLinks.filter(a => {
                    const href = a.getAttribute('href') || '';
                    return href.startsWith('/items/') && !href.endsWith('/items');
                });

                // Extract item data from the links
                const uniqueItems = new Set();
                itemLinks.forEach(link => {
                    const href = link.getAttribute('href');
                    const itemName = link.innerText.trim();

                    if (itemName && !uniqueItems.has(itemName)) {
                        uniqueItems.add(itemName);
                        items.push({
                            name: itemName,
                            url: href
                        });
                    }
                });

                return items;
            }
        """)

        print(f"Found {len(items_list)} items")

        # Limit items if specified
        if limit_items:
            items_list = items_list[:limit_items]
            print(f"Limited to {len(items_list)} items")

        # Crawl detailed data for each item
        items_data = []
        for i, item_info in enumerate(items_list, 1):
            print(f"\n[{i}/{len(items_list)}] Crawling {item_info['name']}...")
            try:
                item_url = f"https://www.metatft.com{item_info['url']}"
                await page.goto(item_url, wait_until="domcontentloaded", timeout=60000)
                await page.wait_for_timeout(2000)

                # Extract item details
                item_details = await page.evaluate("""
                    () => {
                        const pageText = document.body.innerText;
                        const lines = pageText.split('\\n').map(l => l.trim()).filter(l => l);

                        // Find item name - "Name TFT Item Stats" -> extract "Name"
                        let itemName = null;
                        let statsData = {};
                        let traitNumber = null;
                        let description = null;

                        // Find the item name from the header that mentions "TFT Item Stats"
                        for (let i = 0; i < lines.length; i++) {
                            if (lines[i].includes('TFT Item Stats')) {
                                itemName = lines[i].replace(/\\s*TFT Item Stats\\s*/i, '').trim();
                                break;
                            }
                        }

                        // Find Recipe section and extract stats
                        // The pattern seems to be: "Recipe" followed by stat values like "+20%", "+20", "+300"
                        for (let i = 0; i < lines.length; i++) {
                            if (lines[i] === 'Recipe') {
                                // Next lines might contain stat values
                                let j = i + 1;
                                let statIndex = 0;
                                const statNames = ['AP/AD', 'Armor/MR', 'Health'];

                                while (j < lines.length && statIndex < 3) {
                                    const line = lines[j];
                                    // Collect stat values (they look like "+20%", "+20", "+300")
                                    if (line.match(/^[+\\-][0-9.%]+$/)) {
                                        if (statIndex < statNames.length) {
                                            statsData[statNames[statIndex]] = line;
                                            statIndex++;
                                        }
                                    } else if (line && !line.match(/^[+\\-][0-9.%]+$/) && statIndex > 0) {
                                        // We hit a non-stat line after collecting stats
                                        break;
                                    }
                                    j++;
                                }
                                break;
                            }
                        }

                        // Find the item description (longer text after stats)
                        // Usually appears after the stat values
                        for (let i = 0; i < lines.length; i++) {
                            const line = lines[i];
                            // Match lines that contain ability/effect description
                            if (line.includes('deal') || line.includes('grant') || line.includes('increase') ||
                                line.includes('gain') || line.includes('reduce') || line.includes('gain') ||
                                line.includes('heal') || line.includes('summon')) {
                                if (line.length > 40) {
                                    description = line;
                                    break;
                                }
                            }
                        }

                        // Look for trait number (single digit that represents trait stars)
                        for (let i = 0; i < lines.length; i++) {
                            const line = lines[i];
                            // Look for isolated digits 1-5 (usually appears near stats)
                            if (/^[1-5]$/.test(line.trim())) {
                                traitNumber = line.trim();
                                break;
                            }
                        }

                        return {
                            name: itemName,
                            stats: statsData,
                            traitNumber: traitNumber,
                            description: description
                        };
                    }
                """)

                items_data.append(item_details)
                print(f"  ✓ {item_details['name']}")
                if item_details['stats']:
                    print(f"    Stats: {item_details['stats']}")
                if item_details['traitNumber']:
                    print(f"    Trait: {item_details['traitNumber']}")

            except Exception as e:
                print(f"  ✗ Error crawling {item_info['name']}: {e}")

        await browser.close()

        # Return structured data
        return {
            "timestamp": datetime.now().isoformat(),
            "source": base_url,
            "language": language,
            "total_items_found": len(items_list),
            "total_items_crawled": len(items_data),
            "items": items_data,
            "note": "Showing item names, stats (AP/AD, Armor/MR, Health), trait numbers, and descriptions"
        }
