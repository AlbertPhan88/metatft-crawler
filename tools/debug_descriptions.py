#!/usr/bin/env python3
"""
Debug script to find augment descriptions on the page
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from playwright.async_api import async_playwright


async def debug_descriptions():
    """Debug augment descriptions."""

    base_url = "https://www.metatft.com/augments"

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        print(f"Navigating to {base_url}...")
        await page.goto(base_url, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(5000)

        # Get all the page content
        html_content = await page.content()

        # Look for augment data in the page
        print("\nSearching for augment data patterns...")

        # Check if there's JSON data embedded in the page
        if '"description"' in html_content or '"effect"' in html_content:
            print("✓ Found description/effect patterns in HTML")

        # Look for specific augment names and check for descriptions nearby
        page_text = await page.evaluate("() => document.body.innerText")
        lines = page_text.split('\n')

        print("\nLooking for pattern with 'Delayed Start' (first augment)...")
        for i, line in enumerate(lines):
            if 'Delayed Start' in line:
                print(f"Line {i}: {line}")
                print("Context (5 lines before and after):")
                for j in range(max(0, i-5), min(len(lines), i+6)):
                    print(f"  {j}: {lines[j]}")
                break

        # Try to extract augment cards/tooltips
        print("\nLooking for augment card elements...")
        card_info = await page.evaluate("""
            () => {
                // Look for augment containers with data attributes or specific classes
                const elements = [];

                // Try different selectors for augment cards
                const selectors = [
                    '[data-tooltip]',
                    '[title]',
                    '[class*="augment"]',
                    '[class*="card"]',
                    '[class*="description"]'
                ];

                for (const selector of selectors) {
                    const items = document.querySelectorAll(selector);
                    if (items.length > 0) {
                        elements.push({
                            selector: selector,
                            count: items.length,
                            examples: Array.from(items).slice(0, 2).map(el => ({
                                text: el.innerText || el.textContent,
                                title: el.getAttribute('title') || el.getAttribute('data-tooltip'),
                                class: el.className
                            }))
                        });
                    }
                }

                return elements;
            }
        """)

        print(f"Found {len(card_info)} selector patterns with elements")
        for info in card_info:
            print(f"\nSelector: {info['selector']} (found {info['count']} elements)")
            for ex in info['examples'][:1]:
                if ex['text']:
                    print(f"  Text: {ex['text'][:60]}...")
                if ex['title']:
                    print(f"  Title: {ex['title'][:60]}...")

        # Check if there's an info panel or tooltip area
        print("\nLooking for augment info/details panels...")
        info_check = await page.evaluate("""
            () => {
                const textContent = document.body.innerText;

                // Look for words that typically appear in descriptions
                const descKeywords = ['damage', 'mana', 'health', 'armor', 'effect', 'grants', 'units', 'gives'];
                const foundKeywords = [];

                for (const kw of descKeywords) {
                    if (textContent.toLowerCase().includes(kw)) {
                        foundKeywords.push(kw);
                    }
                }

                return foundKeywords;
            }
        """)

        print(f"Found description keywords: {info_check}")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(debug_descriptions())
