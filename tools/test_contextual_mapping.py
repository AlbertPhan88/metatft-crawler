#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright

async def test_mapping():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.goto("https://www.metatft.com/units/BaronNashor", wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)

        result = await page.evaluate("""
            () => {
                const damageStatsMapping = {};
                const contextualDamageStats = {};

                // Extract from specific tooltip elements
                const tooltips = Array.from(document.querySelectorAll('tooltipcalculation, scalelevel, tooltipcalculationdetail'));
                tooltips.forEach((tt, i) => {
                    const text = tt.textContent.trim();
                    // Find all damage values in this element
                    const damageMatches = Array.from(text.matchAll(/(\\d+\\/\\d+\\/\\d+)/g));

                    damageMatches.forEach((match, j) => {
                        const damageVal = match[1];
                        const imgs = Array.from(tt.querySelectorAll('img[alt="AP"], img[alt="AD"]'));
                        const stats = imgs.length > 0 ? imgs.map(img => img.getAttribute('alt')) : [];

                        // Create context key
                        const contextKey = `${damageVal}_${i}_${j}`;

                        if (stats.length > 0) {
                            contextualDamageStats[contextKey] = {
                                damage: damageVal,
                                stats: stats,
                                element: tt.tagName,
                                text: text.substring(0, 60)
                            };

                            // Store first occurrence in main mapping
                            if (!damageStatsMapping[damageVal]) {
                                damageStatsMapping[damageVal] = stats;
                            }
                        }
                    });
                });

                return {
                    mapping: damageStatsMapping,
                    contextual: contextualDamageStats
                };
            }
        """)

        print("=== Main Damage Stats Mapping ===")
        for dmg, stats in result['mapping'].items():
            print(f"  {dmg}: {stats}")

        print("\\n=== Contextual Details ===")
        for ctx, info in list(result['contextual'].items())[:15]:
            print(f"  {ctx}: {info['stats']} in {info['element']}")

        await browser.close()

asyncio.run(test_mapping())
