#!/usr/bin/env python3
"""
TFT Augments Crawler - Extracts augment data from MetaTFT.com/augments
"""

import asyncio
import json
from datetime import datetime
from playwright.async_api import async_playwright
from typing import Dict, Any

from ..utils.browser import switch_language


async def crawl_all_augments(language: str = "en") -> Dict[str, Any]:
    """
    Crawl MetaTFT.com/augments and extract data for all augments.

    Args:
        language: Language code ('en' for English, 'vi' for Vietnamese, etc.)

    Returns:
        Dictionary containing timestamp and augment data
    """

    # Use the same base URL for all languages - language switching is done via selector
    base_url = "https://www.metatft.com/augments"

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        print(f"Navigating to {base_url} (Language: {language})...")
        try:
            await page.goto(base_url, wait_until="domcontentloaded", timeout=60000)
        except Exception as e:
            print(f"Navigation timeout: {e}")

        print("Waiting for page to fully render...")
        await page.wait_for_timeout(5000)

        # Switch language if needed
        if language == "vi":
            print("Switching to Vietnamese...")
            await switch_language(page, "vi")

        # First, click on Table view to get structured data
        print("Switching to Table view...")
        await page.evaluate("""
            () => {
                const tableDiv = Array.from(document.querySelectorAll('div'))
                    .find(div => div.innerText === 'Table' && div.className.includes('StatOptionChip'));
                if (tableDiv) tableDiv.click();
            }
        """)
        await page.wait_for_timeout(2000)

        # Extract all augments from the page
        print("Extracting augment data from page...")
        augments_data = await page.evaluate("""
            () => {
                const augments = [];
                const pageText = document.body.innerText;

                // Split by newlines and handle tabs
                const lines = pageText.split('\\n');

                let i = 0;
                while (i < lines.length) {
                    const line = lines[i].trim();

                    // Skip empty lines and header lines
                    if (!line || line.includes('Select View') || line === 'Augment' || line === 'Tier' || line === 'Type') {
                        i++;
                        continue;
                    }

                    // Look for augment name (usually followed by tier)
                    // Tier pattern: single letters S, A, B, C, D
                    const tierPattern = /^[SABCD]$/;

                    // Check if this might be an augment name
                    if (line && !tierPattern.test(line) && line.length > 1 && line.length < 100) {
                        const augmentName = line;
                        let tier = null;
                        let type = null;

                        // Look ahead for tier
                        for (let j = i + 1; j < Math.min(i + 5, lines.length); j++) {
                            const nextLine = lines[j].trim();

                            if (tierPattern.test(nextLine)) {
                                tier = nextLine;

                                // Look for type after tier
                                for (let k = j + 1; k < Math.min(j + 5, lines.length); k++) {
                                    const typeLine = lines[k].trim();
                                    if (typeLine && !tierPattern.test(typeLine) && typeLine !== augmentName) {
                                        type = typeLine;
                                        break;
                                    }
                                }
                                break;
                            }
                        }

                        if (tier && type) {
                            augments.push({
                                name: augmentName,
                                tier: tier,
                                type: type,
                                description: ''
                            });

                            // Skip to next augment
                            i += 5;
                            continue;
                        }
                    }

                    i++;
                }

                return augments;
            }
        """)

        # Print what we found
        print(f"Found {len(augments_data)} augments")

        await browser.close()

        return {
            "timestamp": datetime.now().isoformat(),
            "source": "https://www.metatft.com/augments",
            "total_augments": len(augments_data),
            "augments": augments_data
        }


async def main(language: str = "en"):
    """Main entry point for the crawler."""
    result = await crawl_all_augments(language=language)
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    import sys
    lang = sys.argv[1] if len(sys.argv) > 1 else "en"
    asyncio.run(main(language=lang))
