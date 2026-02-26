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


async def crawl_tft_meta(language: str = "en") -> Dict[str, Any]:
    """
    Crawl MetaTFT.com/comps and extract all comp, unit, and item data.

    Args:
        language: Language code ('en' for English, 'vi' for Vietnamese, etc.)

    Returns:
        Dictionary containing timestamp and all extracted comp data
    """

    # Use the same base URL for all languages - language switching is done via selector
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

        # Switch language if needed
        if language == "vi":
            print("Switching to Vietnamese...")
            await switch_language(page, "vi")

        # Extract comp data from the page
        print("Extracting comp data from page...")
        comps_data = await page.evaluate("""
            () => {
                const comps = [];

                // Get all text content and parse it
                const pageText = document.body.innerText;

                // Find comp sections - they seem to have a pattern of:
                // CompName
                // Champions list
                // Stats (Avg Place, Pick Rate, Win Rate, Top 4 Rate)

                // Use more sophisticated parsing
                const root = document.querySelector('#root');
                if (!root) return [];

                // Try to find all elements that might contain comp info
                const allElements = root.querySelectorAll('div, section');
                const compDataPoints = [];

                allElements.forEach(el => {
                    const text = el.innerText || '';

                    // Look for pattern: unit names and stats together
                    // English: "Avg Place", "Pick Rate", "Win Rate", "Top 4 Rate"
                    // Vietnamese: "Hạng TB", "Tỷ Lệ Chọn", "Tỷ Lệ Thắng", "Tỷ Lệ Top 4"
                    const hasPlacementEnglish = text.includes('Avg Place');
                    const hasPlacementVietnamese = text.includes('Hạng TB');
                    const hasPickRateEnglish = text.includes('Pick Rate');
                    const hasPickRateVietnamese = text.includes('Tỷ Lệ Chọn');

                    if ((hasPlacementEnglish || hasPlacementVietnamese) && (hasPickRateEnglish || hasPickRateVietnamese)) {
                        const lines = text.split('\\n').filter(l => l.trim());

                        // Extract stats - support both English and Vietnamese patterns
                        const avgPlaceMatch = text.match(/(Avg Place|Hạng TB)\\s*([\\d.]+)/) || text.match(/([\\d.]+)(?=.*Hạng)/);
                        const pickRateMatch = text.match(/(Pick Rate|Tỷ Lệ Chọn)\\s*([\\d.]+)/);
                        const winRateMatch = text.match(/(Win Rate|Tỷ Lệ Thắng)\\s*([\\d.%]+)/);
                        const top4Match = text.match(/(Top 4 Rate|Tỷ Lệ Top 4)\\s*([\\d.]+)/);

                        // Unit names are actual TFT champion names
                        // They typically appear between tier/difficulty and "Avg Place"
                        const units = [];
                        let compName = 'Unknown';

                        // Known champion names for better filtering
                        const knownChamps = ['Swain', 'Ambessa', 'Mel', 'Draven', 'Fiddlesticks', 'Kindred', 'Darius', 'Sion', 'Briar',
                                           'Aphelios', 'Neeko', 'Bard', 'Nidalee', 'Taric', 'Kalista', 'Thresh', 'Braum', 'Ornn', 'Seraphine', 'Gwen', 'Yorick', 'Veigar', 'Kennen', 'Fizz', 'Ziggs', 'Poppy', 'Teemo', 'Rumble'];

                        // Find all units
                        lines.forEach(line => {
                            const trimmed = line.trim();
                            // Check if this line is a known champion
                            if (knownChamps.includes(trimmed)) {
                                units.push({
                                    name: trimmed,
                                    rarity: 'unknown',
                                    stars: 1,
                                    items: []
                                });
                            }
                            // Look for comp name pattern like "Noxus Ambessa"
                            // Usually a trait name + champion name
                            else if (!compName.includes('Unknown') && trimmed.includes(' ') && trimmed.length > 5 && trimmed.length < 30 &&
                                    !trimmed.includes('Avg') && !trimmed.includes('Pick') && !trimmed.includes('Win') && !trimmed.includes('Top') &&
                                    !trimmed.match(/^\\d+/) && !trimmed.match(/^[ABC]$/) && !trimmed.match(/^[IVXLCDM]+$/)) {
                                // This might be the comp name if we haven't found it yet
                                if (compName === 'Unknown') {
                                    compName = trimmed;
                                }
                            }
                        });

                        // If we didn't find comp name from pattern, try to construct from first unit
                        if (compName === 'Unknown' && units.length > 0) {
                            // Try to find a multi-word entry before units started
                            for (let i = 0; i < lines.length; i++) {
                                const line = lines[i].trim();
                                if (line.length > 5 && line.length < 30 && !knownChamps.includes(line) &&
                                    !line.match(/^[\\d]$/) && !line.match(/^[ABC]$/) &&
                                    !line.includes('Avg') && !line.includes('Pick') && !line.includes('Win')) {
                                    compName = line;
                                    break;
                                }
                            }
                        }

                        compDataPoints.push({
                            name: compName,
                            rawText: text.substring(0, 150),
                            stats: {
                                avg_placement: avgPlaceMatch ? parseFloat(avgPlaceMatch[avgPlaceMatch.length - 1]) : null,
                                pick_rate: pickRateMatch ? parseFloat(pickRateMatch[pickRateMatch.length - 1]) : null,
                                win_rate: winRateMatch ? parseFloat(winRateMatch[winRateMatch.length - 1]) : null,
                                top_4_rate: top4Match ? parseFloat(top4Match[top4Match.length - 1]) : null,
                            },
                            units: units
                        });
                    }
                });

                // Filter and clean up comps
                const seen = new Set();
                const validComps = [];

                compDataPoints.forEach(comp => {
                    // Filter out noise entries
                    // A valid comp should:
                    // 1. Have a meaningful name (not just single letters or UI text)
                    // 2. Have actual units
                    // 3. Have stats

                    const hasNoiseKeywords = ['Download', 'Want To Win', 'Top TFT', 'MetaTFT', 'Last Updated', 'a few seconds'];
                    const isNoise = hasNoiseKeywords.some(kw => comp.name.includes(kw));
                    const isShortName = comp.name.length <= 2 && comp.name.match(/^[0-9]$/);
                    const hasValidUnits = comp.units.length >= 7; // TFT comps have at least 7-9 units
                    const hasStats = comp.stats.avg_placement !== null;

                    // Also filter out nav items
                    const navItems = ['Comps', 'Stats', 'Players', 'Tools', 'Info', 'Team Builder', 'EN', 'Sort', 'Situational', 'Platinum', 'Ranked'];
                    const isNav = navItems.some(item => comp.name === item);

                    if (!isNoise && !isShortName && hasValidUnits && hasStats && !isNav && !seen.has(comp.name)) {
                        seen.add(comp.name);
                        validComps.push(comp);
                    }
                });

                return validComps.slice(0, 20); // Limit to top 20 comps
            }
        """)

        # Print what we found
        print(f"Found {len(comps_data)} comps")

        await browser.close()

        return {
            "timestamp": datetime.now().isoformat(),
            "source": "https://www.metatft.com/comps",
            "total_comps": len(comps_data),
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
