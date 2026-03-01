#!/usr/bin/env python3
"""Debug Tactician's Crown specifically"""

import asyncio
from playwright.async_api import async_playwright


async def check():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # Navigate from main items page like the crawler does
        print("Navigating to main items page...")
        await page.goto('https://www.metatft.com/items', timeout=60000)
        await page.wait_for_timeout(3000)

        # Get the URL for Tactician's Crown
        url = await page.evaluate("""
            () => {
                const links = Array.from(document.querySelectorAll('a[href*="/items/"]'));
                const itemLinks = links.filter(a => {
                    const href = a.getAttribute('href') || '';
                    return href.startsWith('/items/') && !href.endsWith('/items');
                });
                const tactician = itemLinks.find(a => a.innerText.includes("Tactician"));
                return tactician ? tactician.getAttribute('href') : null;
            }
        """)

        print(f"Tactician's Crown URL: {url}")

        if url:
            full_url = f"https://www.metatft.com{url}"
            print(f"Full URL: {full_url}\n")

            await page.goto(full_url, timeout=60000)
            await page.wait_for_timeout(2000)

            lines = await page.evaluate("""
                () => {
                    const pageText = document.body.innerText;
                    const allLines = pageText.split('\\n').map(l => l.trim()).filter(l => l);
                    return allLines;
                }
            """)

            print(f"Total lines: {len(lines)}\n")
            print("Full page content:")
            for i, line in enumerate(lines):
                print(f"{i:3d}: {line}")

        await browser.close()


asyncio.run(check())
