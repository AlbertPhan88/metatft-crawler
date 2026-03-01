#!/usr/bin/env python3
"""Debug script to extract correct stat labels from HTML alt text"""

import asyncio
from playwright.async_api import async_playwright


async def check():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        print("Navigating to Titanic Hydra item page...")
        await page.goto('https://www.metatft.com/items/TFT_Item_Artifact_TitanicHydra', timeout=60000)
        await page.wait_for_timeout(3000)

        # Extract stat labels from HTML
        stats = await page.evaluate("""
            () => {
                const stats = [];

                // Look for stat images and their alt text
                const statImages = document.querySelectorAll('img[alt*="Bonus"], img[alt="AD"], img[alt="AP"], img[alt="Armor"], img[alt="MR"], img[alt="AS"]');

                console.log('Found ' + statImages.length + ' stat images');

                statImages.forEach((img, i) => {
                    const alt = img.getAttribute('alt');
                    // Find the next text node or sibling that contains the value
                    let value = null;

                    // Try to find value in parent's text content
                    let parent = img.parentElement;
                    if (parent) {
                        const text = parent.innerText || parent.textContent;
                        // Extract numbers with % or just numbers
                        const match = text.match(/([+\\-]?[0-9.%]+)/);
                        if (match) {
                            value = match[1];
                        }
                    }

                    stats.push({
                        index: i,
                        alt: alt,
                        value: value,
                        parentText: parent ? parent.innerText : null
                    });
                });

                return stats;
            }
        """)

        print("\nExtracted stats:")
        for stat in stats:
            print(f"  [{stat['index']}] Alt: '{stat['alt']}' | Value: '{stat['value']}'")
            if stat['parentText']:
                print(f"       Parent text: {stat['parentText'][:100]}")

        # Also check the Recipe section text
        print("\n\nRecipe section content:")
        recipe_content = await page.evaluate("""
            () => {
                const pageText = document.body.innerText;
                const lines = pageText.split('\\n').map(l => l.trim()).filter(l => l);

                // Find Recipe and next 15 lines
                const recipeIdx = lines.findIndex(l => l === 'Recipe');
                if (recipeIdx >= 0) {
                    return lines.slice(recipeIdx, recipeIdx + 15);
                }
                return [];
            }
        """)

        for i, line in enumerate(recipe_content):
            print(f"  {i}: {line}")

        await browser.close()


asyncio.run(check())
