#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright

async def debug_all():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.goto("https://www.metatft.com/units/BaronNashor", wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)

        result = await page.evaluate("""
            () => {
                const tooltips = Array.from(document.querySelectorAll('tooltipcalculation'));

                return tooltips.map((tt, i) => {
                    const text = tt.textContent.trim();
                    const imgs = tt.querySelectorAll('img');
                    const imgAlts = Array.from(imgs).map(img => img.getAttribute('alt'));

                    return {
                        index: i,
                        text: text.substring(0, 150),
                        hasImages: imgs.length > 0,
                        imageAlts: imgAlts.filter(alt => alt === 'AP' || alt === 'AD'),
                        html: tt.innerHTML.substring(0, 300)
                    };
                });
            }
        """)

        for item in result[:15]:
            print(f"{item['index']:2d}. Text: {item['text']}")
            if item['imageAlts']:
                print(f"    Stats: {item['imageAlts']}")
            print()

        await browser.close()

asyncio.run(debug_all())
