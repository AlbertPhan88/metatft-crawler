#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright

async def debug_damage():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.goto("https://www.metatft.com/units/BaronNashor", wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)

        # Get raw HTML of first few tooltipcalculation elements
        result = await page.evaluate("""
            () => {
                const tooltips = Array.from(document.querySelectorAll('tooltipcalculation')).slice(0, 3);

                return tooltips.map((tt, i) => ({
                    index: i,
                    html: tt.innerHTML.substring(0, 500),
                    textContent: tt.textContent.substring(0, 200),
                    children: Array.from(tt.childNodes).map(node => ({
                        type: node.nodeType === 3 ? 'text' : 'element',
                        tag: node.tagName || 'text',
                        text: (node.textContent || '').substring(0, 50)
                    }))
                }));
            }
        """)

        for item in result:
            print(f"\\n=== Tooltip {item['index']} ===")
            print(f"Text: {item['textContent']}")
            print(f"\\nHTML:\\n{item['html']}")
            print(f"\\nChildren ({len(item['children'])}):")
            for j, child in enumerate(item['children'][:10]):
                print(f"  {j}. {child['tag']:20s} | {child['text']}")

        await browser.close()

asyncio.run(debug_damage())
