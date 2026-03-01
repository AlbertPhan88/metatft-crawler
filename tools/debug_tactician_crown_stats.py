#!/usr/bin/env python3
"""Debug Tactician's Crown stats extraction"""

import asyncio
from playwright.async_api import async_playwright


async def check():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        print("Getting Tactician's Crown page...")
        await page.goto('https://www.metatft.com/items', timeout=60000)
        await page.wait_for_timeout(3000)

        # Get the URL
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

        if url:
            full_url = f"https://www.metatft.com{url}"
            print(f"URL: {full_url}\n")

            await page.goto(full_url, timeout=60000)
            await page.wait_for_timeout(2000)

            # Check for stat images
            stat_images = await page.evaluate("""
                () => {
                    const images = Array.from(document.querySelectorAll('img[alt*="Bonus"]'));
                    return images.map(img => ({
                        alt: img.getAttribute('alt'),
                        src: img.getAttribute('src')
                    }));
                }
            """)

            print(f"Stat images found: {len(stat_images)}")
            for img in stat_images:
                print(f"  - Alt: {img['alt']}")

            # Also check ALL images with alt text
            all_images = await page.evaluate("""
                () => {
                    const images = Array.from(document.querySelectorAll('img[alt]'));
                    return images.map(img => img.getAttribute('alt'));
                }
            """)

            print(f"\nAll images with alt text ({len(all_images)}):")
            for i, alt in enumerate(all_images[:30]):
                print(f"  {i}: {alt}")

            # Check Recipe section
            recipe_text = await page.evaluate("""
                () => {
                    const pageText = document.body.innerText;
                    const lines = pageText.split('\\n').map(l => l.trim()).filter(l => l);
                    const idx = lines.findIndex(l => l === 'Recipe');
                    if (idx >= 0) {
                        return lines.slice(idx, idx + 10);
                    }
                    return [];
                }
            """)

            print("\nRecipe section:")
            for i, line in enumerate(recipe_text):
                print(f"  {i}: {line}")

        await browser.close()


asyncio.run(check())
