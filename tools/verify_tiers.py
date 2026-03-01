#!/usr/bin/env python3
"""
Verify tier extraction by looking at the raw page text
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from playwright.async_api import async_playwright


async def verify_tiers():
    """Verify tier extraction."""

    base_url = "https://www.metatft.com/augments"

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        print(f"Navigating to {base_url}...")
        await page.goto(base_url, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(5000)

        # Click on Table view
        print("Clicking on Table view...")
        await page.evaluate("""
            () => {
                const tableDiv = Array.from(document.querySelectorAll('div'))
                    .find(div => div.innerText === 'Table' && div.className.includes('StatOptionChip'));
                if (tableDiv) tableDiv.click();
            }
        """)
        await page.wait_for_timeout(3000)

        # Get the page content
        text_content = await page.evaluate("() => document.body.innerText")
        lines = text_content.split('\n')

        # Count tier sections
        print("\nSearching for tier sections...")
        tier_section_indices = []

        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped in ['S', 'A', 'B', 'C', 'D']:
                print(f"Line {i}: Found tier {stripped}")
                tier_section_indices.append((i, stripped))

        print(f"\nFound {len(tier_section_indices)} tier markers")

        # For each tier, count augments
        print("\nCounting augments per tier:")
        for idx, (line_num, tier) in enumerate(tier_section_indices):
            # Find the next tier marker or end of file
            if idx + 1 < len(tier_section_indices):
                next_tier_line = tier_section_indices[idx + 1][0]
            else:
                next_tier_line = len(lines)

            # Count non-empty lines in this tier section that look like augment names
            tier_lines = []
            for i in range(line_num + 1, next_tier_line):
                line_text = lines[i].strip()
                # Skip empty lines and known patterns
                if (line_text and
                    line_text not in ['Augment', 'Tier', 'Type', 'Select View:'] and
                    not line_text.startswith('Tier') and
                    len(line_text) > 1 and
                    len(line_text) < 100):
                    tier_lines.append(line_text)

            print(f"\nTier {tier}: {len(tier_lines)} augments")
            if len(tier_lines) <= 5:
                for line in tier_lines[:5]:
                    print(f"  - {line}")
            else:
                print(f"  First 3: {tier_lines[:3]}")
                print(f"  Last 2: {tier_lines[-2:]}")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(verify_tiers())
