#!/usr/bin/env python3
"""
Inspect augments page structure with more detail
"""

import asyncio
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from playwright.async_api import async_playwright


async def inspect_augments():
    """Inspect the augments page structure."""

    base_url = "https://www.metatft.com/augments"

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        print(f"Navigating to {base_url}...")
        await page.goto(base_url, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(5000)

        # Get all augment data from the page structure
        augments_data = await page.evaluate("""
            () => {
                const pageText = document.body.innerText;
                const lines = pageText.split('\\n').filter(l => l.trim());

                // Find tier section headers (S, A, B, C, D)
                const tiers = [];
                const tierPattern = /^[SABCD]$/;

                for (let i = 0; i < lines.length; i++) {
                    if (tierPattern.test(lines[i].trim())) {
                        const tier = lines[i].trim();
                        const augmentsInTier = [];

                        // Collect augments in this tier until next tier
                        for (let j = i + 1; j < lines.length; j++) {
                            const line = lines[j].trim();
                            if (tierPattern.test(line)) {
                                break; // Next tier
                            }
                            if (line && line.length > 1 && line.length < 50) {
                                augmentsInTier.push(line);
                            }
                        }

                        tiers.push({ tier: tier, augments: augmentsInTier });
                    }
                }

                return { tiers: tiers, pageLength: pageText.length };
            }
        """)

        print(f"\nTotal tiers found: {len(augments_data['tiers'])}")
        for tierData in augments_data['tiers']:
            print(f"\nTier {tierData['tier']}: {len(tierData['augments'])} augments")
            print(f"  Augments: {tierData['augments'][:5]}")  # Show first 5

        # Now let's try to switch to table view
        print("\n\nTrying to switch to Table view...")

        # Get all buttons and their text
        buttons = await page.evaluate("""
            () => {
                const buttons = Array.from(document.querySelectorAll('button'));
                return buttons.map(b => ({ text: b.innerText, html: b.outerHTML.substring(0, 100) }));
            }
        """)

        print(f"Found {len(buttons)} buttons:")
        for btn in buttons[:10]:
            print(f"  - {btn['text']}")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(inspect_augments())
