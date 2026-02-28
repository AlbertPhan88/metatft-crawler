#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright

async def check():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.goto("https://www.metatft.com/units/Ziggs", wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)

        result = await page.evaluate("""
            () => {
                const tooltips = Array.from(document.querySelectorAll('tooltipcalculation, scalelevel, tooltipcalculationdetail'));

                return tooltips.map((tt, i) => {
                    const text = tt.textContent.trim();
                    const imgs = Array.from(tt.querySelectorAll('img[alt="AP"], img[alt="AD"]'));
                    const stats = imgs.map(img => img.getAttribute('alt'));

                    return {
                        index: i,
                        tag: tt.tagName,
                        text: text.substring(0, 80),
                        stats: stats
                    };
                });
            }
        """)

        print("=== Ziggs Tooltip Structure ===")
        for item in result:
            print(f"{item['index']}. {item['tag']}: {item['text']}")
            if item['stats']:
                print(f"   Images: {item['stats']}")

        await browser.close()

asyncio.run(check())
