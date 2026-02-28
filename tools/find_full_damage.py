#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright

async def find_damage():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.goto("https://www.metatft.com/units/BaronNashor", wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)

        # Find where the "250/375/20000 ()" text is
        result = await page.evaluate("""
            () => {
                const pageText = document.body.innerText;

                // Find the section with our damage text
                const lines = pageText.split('\\n');
                let results = [];

                lines.forEach((line, i) => {
                    if (line.includes('250/375/20000')) {
                        results.push({
                            lineNum: i,
                            text: line.trim()
                        });
                    }
                });

                // Also search by looking for all img elements with AP/AD
                const allAPs = Array.from(document.querySelectorAll('img[alt="AP"]'));
                const allADs = Array.from(document.querySelectorAll('img[alt="AD"]'));

                return {
                    damageLines: results,
                    totalAPImages: allAPs.length,
                    totalADImages: allADs.length,
                    firstAPParent: allAPs[0]?.parentElement?.className || 'N/A',
                    pageHasDamageMultiplier: pageText.includes('% of'),
                    sectionWithDamage: lines.slice(40, 60).join('\\n')
                };
            }
        """)

        print("Damage line with 250/375/20000:")
        for item in result['damageLines']:
            print(f"  Line {item['lineNum']}: {item['text']}")

        print(f"\\nTotal AP images on page: {result['totalAPImages']}")
        print(f"Total AD images on page: {result['totalADImages']}")
        print(f"\\nFirst AP parent class: {result['firstAPParent']}")
        print(f"Page has damage multiplier: {result['pageHasDamageMultiplier']}")

        print(f"\\n=== Lines 40-60 ===")
        print(result['sectionWithDamage'])

        await browser.close()

asyncio.run(find_damage())
