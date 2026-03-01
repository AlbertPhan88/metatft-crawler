#!/usr/bin/env python3
"""Debug Radiant Nashor's Tooth Vietnamese description"""

import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from playwright.async_api import async_playwright
from metatft_crawler.utils.browser import switch_language


async def check():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        print("Navigate to items page...")
        await page.goto('https://www.metatft.com/items', timeout=60000)
        await page.wait_for_timeout(3000)

        print("Switch to Vietnamese...")
        await switch_language(page, "vi")

        # Get Radiant Nashor's Tooth URL
        item_info = await page.evaluate("""
            () => {
                const links = Array.from(document.querySelectorAll('a[href*="/items/"]'));
                const itemLinks = links.filter(a => {
                    const href = a.getAttribute('href') || '';
                    return href.startsWith('/items/') && !href.endsWith('/items');
                });
                // Find item 3 - Radiant Nashor's Tooth equivalent
                if (itemLinks.length >= 3) {
                    return {
                        name: itemLinks[2].innerText.trim(),
                        url: itemLinks[2].getAttribute('href')
                    };
                }
                return null;
            }
        """)

        if item_info:
            print(f"\nItem: {item_info['name']}")
            print(f"URL: {item_info['url']}\n")

            # Navigate to the item page
            await page.goto(f"https://www.metatft.com{item_info['url']}", timeout=60000)
            await page.wait_for_timeout(2000)

            # Get all lines
            all_lines = await page.evaluate("""
                () => {
                    const pageText = document.body.innerText;
                    const lines = pageText.split('\\n').map(l => l.trim()).filter(l => l);
                    return lines;
                }
            """)

            print("Full page content (lines around Recipe section):")
            recipe_idx = -1
            for i, line in enumerate(all_lines):
                if 'Công Thức' in line:
                    recipe_idx = i
                    break

            if recipe_idx >= 0:
                print(f"\nRecipe found at line {recipe_idx}\n")
                for i in range(recipe_idx, min(recipe_idx + 15, len(all_lines))):
                    print(f"{i:3d}: {all_lines[i]}")

                print(f"\n\nLooking for Vietnamese keywords in lines {recipe_idx+1} to {min(recipe_idx+15, len(all_lines))}")
                for i in range(recipe_idx + 1, min(recipe_idx + 15, len(all_lines))):
                    line = all_lines[i]
                    keywords = ['Đòn đánh', 'Gây', 'Cộng', 'Nhận', 'Giảm', 'Chữa', 'Gọi', 'Gia tăng', 'Máu', 'Sức Mạnh']
                    found = [kw for kw in keywords if kw in line]
                    if found or len(line) > 25:
                        print(f"{i}: {line[:100]} | Keywords: {found}")

        await browser.close()


asyncio.run(check())
