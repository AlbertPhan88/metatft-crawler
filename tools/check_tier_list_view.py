#!/usr/bin/env python3
"""
Check if tier list view has augment descriptions
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from playwright.async_api import async_playwright


async def check_tier_list():
    """Check tier list view for descriptions."""

    base_url = "https://www.metatft.com/augments"

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        print("Navigating to augments page...")
        await page.goto(base_url, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(5000)

        # Get the default view (should be Tier List)
        print("Getting tier list view (default)...")
        page_text = await page.evaluate("() => document.body.innerText")

        lines = page_text.split('\n')

        print("\nSearching for 'Delayed Start' and surrounding context in Tier List view...")
        for i, line in enumerate(lines):
            if 'Delayed Start' in line:
                print(f"\nFound at line {i}:")
                print("Context (10 lines before and after):")
                for j in range(max(0, i-10), min(len(lines), i+11)):
                    marker = ">>>" if j == i else "   "
                    print(f"{marker} {j}: {lines[j]}")
                break

        # Try clicking on the "Tier List" view to see if descriptions appear
        print("\n\nChecking if 'Tier List' view has descriptions...")
        tier_list_check = await page.evaluate("""
            () => {
                const text = document.body.innerText;
                // Look for description-like text after augment names
                const lines = text.split('\\n');
                const result = [];

                for (let i = 0; i < lines.length; i++) {
                    if (lines[i].includes('Delayed Start')) {
                        // Check next 10 lines for description patterns
                        for (let j = i + 1; j < Math.min(i + 15, lines.length); j++) {
                            const line = lines[j].trim();
                            if (line.length > 20 && !line.match(/^[SABCD]$/) &&
                                line.length < 200 && !line.includes('Exiles')) {
                                result.push({
                                    position: j - i,
                                    text: line
                                });
                            }
                        }
                        break;
                    }
                }

                return result;
            }
        """)

        print(f"Found {len(tier_list_check)} potential description lines:")
        for item in tier_list_check:
            print(f"  +{item['position']}: {item['text'][:100]}")

        # Try hovering over an augment name to trigger tooltip
        print("\n\nTrying to hover over first augment to see if tooltip appears...")

        # Find an augment element and hover
        await page.hover('text="Delayed Start"')
        await page.wait_for_timeout(2000)

        # Check if a tooltip or details panel appeared
        tooltip_text = await page.evaluate("""
            () => {
                // Look for tooltip or description elements
                const tooltips = document.querySelectorAll('[role="tooltip"], .tooltip, [class*="tooltip"], [class*="description"], [class*="info"]');
                const results = [];

                for (let tooltip of tooltips) {
                    const text = tooltip.innerText || tooltip.textContent;
                    if (text && text.trim().length > 0) {
                        results.push({
                            class: tooltip.className,
                            text: text.substring(0, 200)
                        });
                    }
                }

                // Also check for any visible descriptions near the augment
                const delayedStartElements = Array.from(document.querySelectorAll('*'))
                    .filter(el => el.innerText === 'Delayed Start');

                if (delayedStartElements.length > 0) {
                    const elem = delayedStartElements[0];
                    const parent = elem.closest('[class*="card"], [class*="item"], div[role="button"], tr, [role="row"]');
                    if (parent) {
                        results.push({
                            class: 'parent_container',
                            text: parent.innerText?.substring(0, 300) || ''
                        });
                    }
                }

                return results;
            }
        """)

        print(f"Found {len(tooltip_text)} tooltip/description elements:")
        for item in tooltip_text:
            print(f"  [{item['class']}]: {item['text']}")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(check_tier_list())
