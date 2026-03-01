#!/usr/bin/env python3
"""
Investigate alternative ways to get augment descriptions without hovering
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from playwright.async_api import async_playwright


async def investigate():
    """Investigate augment data extraction methods."""

    base_url = "https://www.metatft.com/augments"

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        print("Navigating to augments page...")
        await page.goto(base_url, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(5000)

        # Switch to Table view
        await page.evaluate("""
            () => {
                const tableDiv = Array.from(document.querySelectorAll('div'))
                    .find(div => div.innerText === 'Table' && div.className.includes('StatOptionChip'));
                if (tableDiv) tableDiv.click();
            }
        """)
        await page.wait_for_timeout(2000)

        # Investigate different data sources
        investigation = await page.evaluate("""
            () => {
                const results = {};

                // 1. Check if tooltip content is already in DOM (hidden)
                results.hiddenTooltips = [];
                const allDivs = document.querySelectorAll('div[role="tooltip"], [class*="MuiTooltip"]');
                allDivs.forEach(div => {
                    if (div.innerText && div.innerText.includes('Delayed Start')) {
                        results.hiddenTooltips.push({
                            visible: div.offsetParent !== null,
                            text: div.innerText.substring(0, 100)
                        });
                    }
                });

                // 2. Check data attributes on augment rows
                results.dataAttributes = [];
                const rows = document.querySelectorAll('tr');
                if (rows.length > 0) {
                    const firstRow = rows[1]; // Skip header
                    if (firstRow) {
                        const attrs = {};
                        for (let attr of firstRow.attributes) {
                            attrs[attr.name] = attr.value.substring(0, 50);
                        }
                        results.dataAttributes = attrs;
                    }
                }

                // 3. Check for aria-label or title attributes
                results.augmentElements = [];
                const augmentCells = document.querySelectorAll('[role="cell"], td');
                augmentCells.forEach((cell, idx) => {
                    if (idx < 20 && cell.innerText.includes('Start')) {
                        results.augmentElements.push({
                            text: cell.innerText.substring(0, 50),
                            ariaLabel: cell.getAttribute('aria-label'),
                            title: cell.getAttribute('title'),
                            dataTooltip: cell.getAttribute('data-tooltip'),
                            innerHTML: cell.innerHTML.substring(0, 100)
                        });
                    }
                });

                // 4. Check for REST API calls in the page
                results.apiInfo = {
                    hasGraphQL: !!window.__APOLLO_CLIENT__,
                    hasRedux: !!window.__REDUX_DEVTOOLS_EXTENSION__
                };

                // 5. Look for inline script data
                results.scriptData = [];
                const scripts = document.querySelectorAll('script[type="application/json"]');
                scripts.forEach((script, idx) => {
                    if (idx < 3) {
                        try {
                            const data = JSON.parse(script.textContent);
                            results.scriptData.push({
                                size: script.textContent.length,
                                hasAugments: script.textContent.includes('augment') || script.textContent.includes('Delayed'),
                                keys: Object.keys(data).slice(0, 5)
                            });
                        } catch (e) {
                            // Not JSON
                        }
                    }
                });

                // 6. Check if descriptions are in data attributes when hovering
                results.hoverBehavior = "Need to test";

                return results;
            }
        """)

        print("\n" + "="*70)
        print("INVESTIGATION RESULTS")
        print("="*70)

        print("\n1. HIDDEN TOOLTIPS IN DOM:")
        if investigation['hiddenTooltips']:
            print(f"   ✓ Found {len(investigation['hiddenTooltips'])} tooltips already in DOM")
            for tt in investigation['hiddenTooltips'][:2]:
                print(f"     Visible: {tt['visible']}")
                print(f"     Text: {tt['text'][:80]}...")
        else:
            print("   ✗ No pre-loaded tooltips found")

        print("\n2. DATA ATTRIBUTES ON ROWS:")
        if investigation['dataAttributes']:
            print(f"   Found attributes: {list(investigation['dataAttributes'].keys())}")
            for key, val in list(investigation['dataAttributes'].items())[:3]:
                print(f"     {key}: {val}")
        else:
            print("   ✗ No data attributes found")

        print("\n3. AUGMENT ELEMENT INSPECTION:")
        if investigation['augmentElements']:
            print(f"   Found {len(investigation['augmentElements'])} augment elements")
            for elem in investigation['augmentElements'][:2]:
                if elem['ariaLabel']:
                    print(f"     ✓ aria-label: {elem['ariaLabel'][:80]}")
                if elem['title']:
                    print(f"     ✓ title: {elem['title'][:80]}")
                if elem['dataTooltip']:
                    print(f"     ✓ data-tooltip: {elem['dataTooltip'][:80]}")
        else:
            print("   ✗ No augment elements found")

        print("\n4. STATE MANAGEMENT:")
        print(f"   GraphQL: {investigation['apiInfo']['hasGraphQL']}")
        print(f"   Redux: {investigation['apiInfo']['hasRedux']}")

        print("\n5. INLINE JSON DATA:")
        if investigation['scriptData']:
            print(f"   Found {len(investigation['scriptData'])} <script> tags")
            for script in investigation['scriptData']:
                print(f"     Size: {script['size']} bytes")
                print(f"     Has augment data: {script['hasAugments']}")
                print(f"     Keys: {script['keys']}")
        else:
            print("   ✗ No inline JSON found")

        # Test alternative: Click instead of hover
        print("\n6. TESTING CLICK BEHAVIOR:")
        click_result = await page.evaluate("""
            () => {
                // Find first augment
                const cells = document.querySelectorAll('td');
                let found = false;
                for (let cell of cells) {
                    if (cell.innerText.includes('Delayed Start')) {
                        // Check if clicking triggers tooltip
                        const parent = cell.closest('tr');
                        if (parent) {
                            parent.click();
                            return {
                                clicked: true,
                                parentClass: parent.className
                            };
                        }
                    }
                }
                return { clicked: false };
            }
        """)

        if click_result['clicked']:
            await page.wait_for_timeout(500)
            desc = await page.evaluate("() => document.querySelector('[role=tooltip]')?.innerText || 'No tooltip'")
            print(f"   Click result: {desc[:80]}...")
        else:
            print("   ✗ Click didn't trigger tooltip")

        # Network inspection
        print("\n7. CHECKING IF DATA IS LOADED UPFRONT:")
        page_content = await page.content()
        print(f"   Page HTML size: {len(page_content)} bytes")
        print(f"   Contains 'Delayed Start': {'Delayed Start' in page_content}")
        print(f"   Contains augment descriptions: {'Sell your board' in page_content}")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(investigate())
