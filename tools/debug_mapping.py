#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright

async def debug_mapping():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.goto("https://www.metatft.com/units/BaronNashor", wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)

        # Test the exact mapping extraction logic
        damage_stats_mapping = await page.evaluate("""
            () => {
                const mapping = {};

                // Look for elements with damage patterns and images
                const damagePattern = /\\d+\\/\\d+\\/\\d+/;
                const walker = document.createTreeWalker(
                    document.body,
                    NodeFilter.SHOW_ELEMENT,
                    null
                );

                let node;
                const processed = new Set();
                const allResults = [];

                while (node = walker.nextNode()) {
                    const text = node.textContent;
                    const match = text.match(damagePattern);

                    if (match) {
                        const damage = match[0];
                        // Only process each unique damage value once
                        if (!processed.has(damage)) {
                            const imgs = Array.from(node.querySelectorAll('img[alt="AP"], img[alt="AD"]'));
                            if (imgs.length > 0) {
                                const stats = imgs.map(img => img.getAttribute('alt'));
                                mapping[damage] = stats;
                                processed.add(damage);
                                allResults.push({
                                    damage: damage,
                                    stats: stats,
                                    tag: node.tagName
                                });
                            }
                        }
                    }
                }

                return {
                    mapping: mapping,
                    allResults: allResults.slice(0, 20)
                };
            }
        """)

        print("=== Extracted Mapping ===")
        print(f"Mapping: {damage_stats_mapping['mapping']}")
        print(f"\\nDetailed Results:")
        for result in damage_stats_mapping['allResults']:
            print(f"  {result['damage']} ({result['tag']}): {result['stats']}")

        # Now test if the pattern matching works
        test_text = "dealing 280/420/20500 () physical damage. Then deal 112/189/10250 () damage."
        import re

        mapping = damage_stats_mapping['mapping']
        pattern = r'(\d+/\d+/\d+)\s*\(\)'

        def replacer(match):
            damage_val = match.group(1)
            print(f"Found damage {damage_val}")
            if damage_val in mapping:
                stats = mapping[damage_val]
                stats_str = '/'.join(stats)
                result = f'{damage_val} ({stats_str})'
                print(f"  Replacing with {result}")
                return result
            print(f"  No mapping found")
            return match.group(0)

        result = re.sub(pattern, replacer, test_text)
        print(f"\\nOriginal: {test_text}")
        print(f"Result:   {result}")

        await browser.close()

asyncio.run(debug_mapping())
