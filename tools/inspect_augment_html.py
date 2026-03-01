#!/usr/bin/env python3
"""
Inspect the HTML structure of augments to find descriptions
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from playwright.async_api import async_playwright


async def inspect_html():
    """Inspect augment HTML structure."""

    base_url = "https://www.metatft.com/augments"

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        print("Navigating to augments page...")
        await page.goto(base_url, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(5000)

        # Switch to table view
        print("Switching to table view...")
        await page.evaluate("""
            () => {
                const tableDiv = Array.from(document.querySelectorAll('div'))
                    .find(div => div.innerText === 'Table' && div.className.includes('StatOptionChip'));
                if (tableDiv) tableDiv.click();
            }
        """)
        await page.wait_for_timeout(2000)

        # Get detailed HTML structure
        html_structure = await page.evaluate("""
            () => {
                // Look for the main content area
                const root = document.querySelector('#root');
                if (!root) return { error: 'No root element' };

                // Find augment-related elements
                const tables = document.querySelectorAll('table');
                const divs = document.querySelectorAll('div');

                // Look for divs that might contain augment info
                const augmentDivs = Array.from(divs).filter(div => {
                    const text = div.innerText || '';
                    return text.includes('Delayed Start') || text.includes('tier') && text.includes('type');
                });

                console.log('Found augment divs:', augmentDivs.length);

                // Check for any divs with role or aria attributes
                const rows = document.querySelectorAll('[role="row"], tr');

                // Get first few rows to understand structure
                const rowData = Array.from(rows).slice(0, 15).map((row, idx) => {
                    const cells = row.querySelectorAll('[role="cell"], td');
                    return {
                        index: idx,
                        cellCount: cells.length,
                        text: row.innerText?.substring(0, 100) || '',
                        cellTexts: Array.from(cells).map(c => c.innerText?.substring(0, 50) || '')
                    };
                });

                return {
                    tablesFound: tables.length,
                    rowsFound: rows.length,
                    sampleRows: rowData,
                    augmentDivsFound: augmentDivs.length
                };
            }
        """)

        print("\nHTML Structure Analysis:")
        print(f"Tables found: {html_structure.get('tablesFound', 0)}")
        print(f"Rows found: {html_structure.get('rowsFound', 0)}")
        print(f"Augment divs found: {html_structure.get('augmentDivsFound', 0)}")

        print("\nSample rows:")
        for row in html_structure.get('sampleRows', [])[:5]:
            print(f"\nRow {row['index']} ({row['cellCount']} cells):")
            print(f"  Text: {row['text']}")
            if row['cellTexts']:
                for i, cell in enumerate(row['cellTexts'][:5]):
                    if cell:
                        print(f"  Cell {i}: {cell}")

        # Try hovering over an augment to see if a tooltip appears
        print("\n\nTrying to trigger tooltips by hovering over augments...")
        tooltip_info = await page.evaluate("""
            () => {
                // Find the first augment name element
                const augmentElements = Array.from(document.querySelectorAll('*'))
                    .filter(el => el.innerText === 'Delayed Start' || el.innerText?.includes('Delayed Start'));

                if (augmentElements.length === 0) {
                    return { error: 'Could not find Delayed Start element' };
                }

                const element = augmentElements[0];
                console.log('Found element:', element.tagName, element.className);

                // Check for parent elements that might have tooltip data
                let current = element;
                const parents = [];
                for (let i = 0; i < 5; i++) {
                    if (!current) break;
                    parents.push({
                        tag: current.tagName,
                        class: current.className,
                        id: current.id,
                        text: current.innerText?.substring(0, 100) || '',
                        children: current.children.length
                    });
                    current = current.parentElement;
                }

                return { augmentElement: parents };
            }
        """)

        print("Element hierarchy for 'Delayed Start':")
        for parent in tooltip_info.get('augmentElement', []):
            print(f"  <{parent['tag']} class='{parent['class']}' id='{parent['id']}' children={parent['children']}>")
            if parent['text']:
                print(f"    Text: {parent['text']}")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(inspect_html())
