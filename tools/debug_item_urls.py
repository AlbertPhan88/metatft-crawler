#!/usr/bin/env python3
"""Check actual item URLs from main items page"""

import asyncio
from playwright.async_api import async_playwright


async def check_urls():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        print("Getting item URLs from main items page...")
        await page.goto('https://www.metatft.com/items', timeout=60000)
        await page.wait_for_timeout(3000)

        items = await page.evaluate("""
            () => {
                const items = [];
                const links = Array.from(document.querySelectorAll('a[href*="/items/"]'));
                const itemLinks = links.filter(a => {
                    const href = a.getAttribute('href') || '';
                    return href.startsWith('/items/') && !href.endsWith('/items');
                });

                itemLinks.slice(0, 10).forEach(link => {
                    items.push({
                        name: link.innerText.trim(),
                        url: link.getAttribute('href')
                    });
                });

                return items;
            }
        """)

        print("\nFirst 10 items with their URLs:")
        for i, item in enumerate(items, 1):
            print(f"{i}. {item['name']:<30s} -> {item['url']}")

        # Now test one of them
        if items:
            test_item = items[0]
            print(f"\n{'='*70}")
            print(f"Testing: {test_item['name']}")
            print(f"Full URL: https://www.metatft.com{test_item['url']}")
            print('='*70)

            await page.goto(f"https://www.metatft.com{test_item['url']}", timeout=60000)
            await page.wait_for_timeout(2000)

            lines = await page.evaluate("""
                () => {
                    const pageText = document.body.innerText;
                    const allLines = pageText.split('\\n').map(l => l.trim()).filter(l => l);
                    return allLines.slice(25, 50);
                }
            """)

            print("\nPage lines 25-50:")
            for i, line in enumerate(lines, 25):
                print(f"{i:3d}: {line}")

        await browser.close()


asyncio.run(check_urls())
