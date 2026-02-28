#!/usr/bin/env python3
"""
Test script to extract item data from a specific item page
Usage: python test_item_extraction.py
"""

import asyncio
import json
from playwright.async_api import async_playwright


async def extract_item_data():
    """Extract item data from MetaTFT item page."""
    item_url = "https://www.metatft.com/items/TFT_Item_Artifact_TitanicHydra"

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        print(f"Navigating to {item_url}...")
        try:
            await page.goto(item_url, wait_until="domcontentloaded", timeout=60000)
        except Exception as e:
            print(f"Navigation timeout: {e}")
            await browser.close()
            return None

        print("Waiting for page to render...")
        await page.wait_for_timeout(3000)

        # Extract item data using JavaScript
        item_data = await page.evaluate("""
            () => {
                const pageText = document.body.innerText;
                const lines = pageText.split('\\n').map(l => l.trim()).filter(l => l);

                // Find item name - "Titanic Hydra TFT Item Stats" -> extract "Titanic Hydra"
                let itemName = null;
                let statsData = {};
                let traitNumber = null;
                let description = null;

                // Find the item name from the header that mentions "TFT Item Stats"
                for (let i = 0; i < lines.length; i++) {
                    if (lines[i].includes('TFT Item Stats')) {
                        itemName = lines[i].replace(/\\s*TFT Item Stats\\s*/i, '').trim();
                        break;
                    }
                }

                // Find Recipe section and extract stats
                // The pattern seems to be: "Recipe" followed by stat values like "+20%", "+20", "+300"
                for (let i = 0; i < lines.length; i++) {
                    if (lines[i] === 'Recipe') {
                        // Next line might be "Cannot be Crafted" or stat info
                        let j = i + 1;
                        let statIndex = 0;
                        const statNames = ['AP/AD', 'Armor/MR', 'Health'];

                        while (j < lines.length && statIndex < 3) {
                            const line = lines[j];
                            // Collect stat values (they look like "+20%", "+20", "+300")
                            if (line.match(/^[+\\-][0-9.%]+$/)) {
                                if (statIndex < statNames.length) {
                                    statsData[statNames[statIndex]] = line;
                                    statIndex++;
                                }
                            } else if (line && !line.match(/^[+\\-][0-9.%]+$/) && statIndex > 0) {
                                // We hit a non-stat line after collecting stats
                                break;
                            }
                            j++;
                        }
                        break;
                    }
                }

                // Find the item description (longer text after stats)
                // Usually appears after the stat values
                for (let i = 0; i < lines.length; i++) {
                    const line = lines[i];
                    // Match lines that contain ability/effect description
                    if (line.includes('deal') || line.includes('grant') || line.includes('increase') ||
                        line.includes('gain') || line.includes('reduce')) {
                        if (line.length > 40) {
                            description = line;
                            break;
                        }
                    }
                }

                // Look for trait number (single digit that represents trait stars)
                for (let i = 0; i < lines.length; i++) {
                    const line = lines[i];
                    // Look for isolated digits 1-5 (usually appears near stats)
                    if (/^[1-5]$/.test(line.trim())) {
                        traitNumber = line.trim();
                        break;
                    }
                }

                return {
                    itemName: itemName,
                    stats: statsData,
                    traitNumber: traitNumber,
                    description: description,
                    rawLines: lines.slice(0, 50)  // First 50 lines for debugging
                };
            }
        """)

        print("\n" + "="*70)
        print("EXTRACTED DATA:")
        print("="*70)
        print(json.dumps(item_data, indent=2, ensure_ascii=False))

        await browser.close()
        return item_data


if __name__ == "__main__":
    result = asyncio.run(extract_item_data())
    if result:
        print("\n✅ Extraction complete")
    else:
        print("\n❌ Extraction failed")
