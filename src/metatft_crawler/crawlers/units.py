#!/usr/bin/env python3
"""
TFT Units Crawler - Extracts detailed data for each unit from MetaTFT.com/units
"""

import asyncio
import json
from datetime import datetime
from playwright.async_api import async_playwright
from typing import Dict, List, Any

from ..utils.browser import switch_language


async def crawl_all_units(language: str = "en") -> Dict[str, Any]:
    """
    Crawl MetaTFT.com/units and extract data for all units.

    Args:
        language: Language code ('en' for English, 'vi' for Vietnamese, etc.)

    Returns:
        Dictionary containing timestamp and all unit data
    """

    # Use the same base URL for all languages - language switching is done via selector
    base_url = "https://www.metatft.com/units"

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

        # Extract all units from the main units page
        print("Extracting all units and their links...")
        units_list = await page.evaluate("""
            () => {
                const units = [];
                const pageText = document.body.innerText;

                // Find all unit links on the page
                const allLinks = Array.from(document.querySelectorAll('a[href*="/units/"]'));
                const unitLinks = allLinks.filter(a => {
                    const href = a.getAttribute('href') || '';
                    return href.startsWith('/units/') && !href.endsWith('/units');
                });

                // Extract unit data from the table
                // English: Unit | Tier | Avg Place | Win Rate | Frequency
                // Vietnamese: Đơn vị | Rank | Hạng | Tỷ Lệ Thắng | Tần Suất
                const lines = pageText.split('\\n');
                const tierPattern = /^([SABCDF])\\s*$/;

                let i = 0;
                while (i < lines.length) {
                    const line = lines[i].trim();

                    // Look for tier indicators
                    if (tierPattern.test(line)) {
                        const tier = line;
                        // The unit name should be above or around this line
                        let unitName = null;

                        // Check previous lines for unit name
                        for (let j = i - 1; j >= Math.max(0, i - 5); j--) {
                            const prevLine = lines[j].trim();
                            if (prevLine && !tierPattern.test(prevLine) && prevLine.length < 40 && prevLine.length > 2) {
                                unitName = prevLine;
                                break;
                            }
                        }

                        // Check next lines for stats
                        if (i + 1 < lines.length) {
                            const statsLine = lines[i + 1].trim();
                            const statsMatch = statsLine.match(/([\\d.]+)\\s+([\\d.]+)\\s+([\\d,]+)\\s+([\\d.]+)/);

                            if (unitName && statsMatch) {
                                units.push({
                                    name: unitName,
                                    tier: tier,
                                    avg_placement: parseFloat(statsMatch[1]),
                                    win_rate_percent: parseFloat(statsMatch[2]),
                                    pick_count: parseInt(statsMatch[3].replace(/,/g, '')),
                                    frequency_percent: parseFloat(statsMatch[4])
                                });
                            }
                        }
                    }
                    i++;
                }

                // Also extract from unit links as fallback
                unitLinks.forEach(link => {
                    const unitName = link.textContent.trim();
                    if (unitName && unitName.length > 1 && unitName.length < 40) {
                        // Check if we already have this unit
                        if (!units.find(u => u.name === unitName)) {
                            units.push({
                                name: unitName,
                                tier: 'Unknown',
                                url: link.getAttribute('href')
                            });
                        }
                    }
                });

                return units.slice(0, 50); // Return top 50 units
            }
        """)

        print(f"Found {len(units_list)} units")

        # Crawl detail page for first few units as examples
        detailed_units = []
        for i, unit_data in enumerate(units_list[:10]):  # Limit to first 10 for speed
            unit_name = unit_data.get('name', '')
            print(f"  [{i+1}/10] Crawling {unit_name}...")

            try:
                # Create URL from unit name
                unit_path = unit_name.replace(' ', '').replace("'", '').replace('&', 'and')
                unit_url = f"https://www.metatft.com/units/{unit_path}"

                await page.goto(unit_url, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_timeout(1000)

                # Extract unit detail data
                unit_detail = await page.evaluate("""
                    () => {
                        const pageText = document.body.innerText;

                        // Find the "TFT Builds, Items and Stats" section
                        const contentStart = pageText.indexOf('TFT Builds, Items and Stats');
                        const relevantText = contentStart > 0 ? pageText.substring(contentStart, Math.min(contentStart + 4000, pageText.length)) : pageText;
                        const lines = relevantText.split('\\n').map(l => l.trim()).filter(l => l && l.length > 0);

                        // Known item names for better filtering
                        const itemNames = ['Rabadons', 'Rabadon', 'Void Staff', 'Guinsoo', "Archangel", "Nashor", "Morellonomicon", "Giant", "Thief", "Gloves", "Sword", "Spear", "Chain", "Bow", "Rod", "Crown"];

                        // Extract recommended items for best build
                        const recommendedBuild = [];
                        for (let i = 0; i < Math.min(100, lines.length); i++) {
                            const line = lines[i];
                            if (itemNames.some(item => line.includes(item))) {
                                recommendedBuild.push(line);
                                if (recommendedBuild.length >= 3) break;
                            }
                        }

                        // Extract positioning
                        let positioning = 'Unknown';
                        for (let i = 0; i < lines.length; i++) {
                            if (lines[i].includes('positioned')) {
                                // Get the row information
                                const match = lines[i].match(/(back|front|middle)[\\s\\w]*(row)?/i);
                                if (match) {
                                    positioning = match[0].trim();
                                    break;
                                }
                            }
                        }

                        // Extract unit traits from first 20 lines
                        const traits = [];
                        const allTraits = ['Magic', 'Marksman', 'Zaun', 'Zaunite', 'Yordle', 'Longshot', 'Duelist', 'Visionary', 'Knight', 'Assassin', 'Mage', 'Ranger', 'Support', 'Tank', 'Bruiser', 'Shurima', 'Noxus', 'Piltover', 'Demacia', 'Ionia', 'Shadow', 'Star'];

                        for (let i = 0; i < Math.min(10, lines.length); i++) {
                            for (const trait of allTraits) {
                                if (lines[i].includes(trait) && !traits.includes(trait)) {
                                    traits.push(trait);
                                }
                            }
                        }

                        // Extract stats - look for placement and pick rate
                        let avgPlacement = null;
                        let pickRate = null;

                        // Look for "Avg Place" followed by a number
                        const placementMatch = relevantText.match(/Avg Place[:\\s]+([\\d.]+)/i);
                        if (placementMatch) {
                            avgPlacement = parseFloat(placementMatch[1]);
                        }

                        // Look for "Pick Rate" followed by a number
                        const pickMatch = relevantText.match(/Pick Rate[:\\s]+([\\d.]+)/i);
                        if (pickMatch) {
                            pickRate = parseFloat(pickMatch[1]);
                        }

                        return {
                            recommended_build: recommendedBuild.slice(0, 3),
                            top_items: recommendedBuild.slice(0, 5),
                            positioning: positioning,
                            traits: [...new Set(traits)],
                            stats: {
                                avg_placement: avgPlacement,
                                pick_rate: pickRate
                            }
                        };
                    }
                """)

                detail_merged = {**unit_data, **unit_detail}
                detail_merged['url'] = unit_url
                detailed_units.append(detail_merged)

            except Exception as e:
                print(f"    Error: {str(e)[:100]}")
                detailed_units.append(unit_data)

        await browser.close()

        return {
            "timestamp": datetime.now().isoformat(),
            "source": "https://www.metatft.com/units",
            "total_units_found": len(units_list),
            "total_units_crawled": len(detailed_units),
            "units": detailed_units,
            "note": "Showing first 10 units with detailed crawling. Full list available on source page."
        }


async def main(language: str = "en"):
    """Main entry point for the crawler."""
    result = await crawl_all_units(language=language)
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    import sys
    lang = sys.argv[1] if len(sys.argv) > 1 else "en"
    asyncio.run(main(language=lang))
