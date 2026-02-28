#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright

async def test_stat_extraction():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.goto("https://www.metatft.com/units/BaronNashor", wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)

        stat_abbreviations = await page.evaluate("""
            () => {
                // Get all img elements with AD/AP alt text within damage sections
                const allDamageImgs = Array.from(document.querySelectorAll('tooltipcalculation img'));

                console.log('Total imgs in tooltipcalculation:', allDamageImgs.length);

                allDamageImgs.forEach((img, i) => {
                    console.log(`IMG ${i}: alt="${img.getAttribute('alt')}", src="${img.src}"`);
                });

                const stats = allDamageImgs
                    .filter(img => img.getAttribute('alt') === 'AP' || img.getAttribute('alt') === 'AD')
                    .map(img => img.getAttribute('alt'));

                console.log('Filtered stats:', stats);

                return stats;
            }
        """)

        print("Stat abbreviations returned:", stat_abbreviations)

        await browser.close()

asyncio.run(test_stat_extraction())
