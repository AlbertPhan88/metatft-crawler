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

                        // Extract stats from HTML alt text (most accurate)
                        // Look for stat bonus images with alt text like "AD Bonus: +20%"
                        const statImages = Array.from(document.querySelectorAll('img[alt*="Bonus"]'));
                        if (statImages.length > 0) {
                            statImages.forEach(img => {
                                const alt = img.getAttribute('alt') || '';
                                // Parse alt text like "AD Bonus: +20%" or "AS Bonus: +20"
                                const match = alt.match(/^([A-Za-z\\s]+?)\\s*Bonus:\\s*([+\\-]?[0-9.%]+)/);
                                if (match) {
                                    const statType = match[1].trim(); // "AD", "AS", "Health", etc
                                    const statValue = match[2];       // "+20%", "+20", etc
                                    statsData[statType] = statValue;
                                }
                            });
                        }

                        // Fallback: If no HTML images found, parse from text
                        if (Object.keys(statsData).length === 0) {
                            for (let i = 0; i < lines.length; i++) {
                                if (lines[i] === 'Recipe') {
                                    // Next lines might contain stat values or recipe info
                                    let j = i + 1;
                                    let statIndex = 0;
                                    const statNames = ['AP/AD', 'Armor/MR', 'Health'];

                                    // Skip past recipe indicator (like "Cannot be Crafted" or "+")
                                    while (j < lines.length && (lines[j] === '+' || lines[j].includes('Crafted'))) {
                                        j++;
                                    }

                                    // Now try to collect stat values, but stop at meta stat labels
                                    while (j < lines.length && statIndex < 3) {
                                        const line = lines[j];

                                        // Stop if we hit meta stat labels
                                        if (line.includes('Avg Place') || line.includes('Pick Rate') ||
                                            line.includes('Last 7 Days') || line.includes('Place Change') ||
                                            line.includes('Play Rate') || line.includes('Win Rate') ||
                                            line.includes('Best Item') || line.includes('Performance')) {
                                            break;
                                        }

                                        // Collect stat values (they look like "+20%", "+20", "+300")
                                        if (line.match(/^[+\\-][0-9.%]+$/) && !line.includes('Place')) {
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
                        }

                        // Find the item description (ability/effect text, NOT meta stats)
                        // Look for text that describes what the item does
                        // Priority: Look near Recipe section, find action verbs
                        for (let i = 0; i < lines.length; i++) {
                            if (lines[i] === 'Recipe') {
                                // Look ahead from Recipe for description
                                for (let j = i + 1; j < Math.min(i + 15, lines.length); j++) {
                                    const line = lines[j];
                                    // Skip stat lines and craft indicators
                                    if (line.match(/^[+\\-][0-9.%]+$/) || line === '+' || line.includes('Crafted')) {
                                        continue;
                                    }
                                    // Skip common meta/stats labels
                                    if (line.includes('Stats on how') || line.includes('Avg Place') ||
                                        line.includes('Pick Rate') || line.includes('Best Item') ||
                                        line.includes('Trait') || line.includes('Rate') || line === '1') {
                                        continue;
                                    }
                                    // Check if this looks like an ability description
                                    const hasActionKeyword = line.includes('deal') || line.includes('grant') ||
                                        line.includes('gain') || line.includes('reduce') || line.includes('heal') ||
                                        line.includes('summon') || line.includes('restore') || line.includes('apply') ||
                                        line.includes('trigger') || line.includes('convert') || line.includes('double') ||
                                        line.includes('each') || line.includes('takes') || line.includes('shield') ||
                                        line.includes('absorb') || line.includes('max team') || line.includes('chance') ||
                                        line.includes('regenerate') || line.includes('execute') || line.includes('become') ||
                                        line.includes('untargetable') || line.includes('invulnerable') || line.includes('burn') ||
                                        line.includes('wound') || line.includes('stacking') || line.includes('bonus') ||
                                        line.includes('critical') || line.includes('Attack') || line.includes('Health');

                                    if (hasActionKeyword && line.length > 25) {
                                        description = line;
                                        break;
                                    }
                                }
                                break;
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
