#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright

async def debug_html():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.goto("https://www.metatft.com/units/BaronNashor", wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)

        # Get the exact HTML of all tooltip sections
        result = await page.evaluate("""
            () => {
                const tooltips = Array.from(document.querySelectorAll('tooltipcalculation'));

                return tooltips.map((tt, i) => {
                    // Get the HTML content
                    let html = tt.innerHTML;

                    // Extract all text and image nodes in order
                    const nodes = [];
                    const walker = document.createTreeWalker(
                        tt,
                        NodeFilter.SHOW_ALL,
                        null
                    );

                    let node;
                    while (node = walker.nextNode()) {
                        if (node.nodeType === Node.TEXT_NODE && node.textContent.trim()) {
                            nodes.push({
                                type: 'text',
                                content: node.textContent.trim().substring(0, 50)
                            });
                        } else if (node.nodeType === Node.ELEMENT_NODE && node.tagName === 'IMG') {
                            nodes.push({
                                type: 'image',
                                alt: node.getAttribute('alt')
                            });
                        }
                    }

                    return {
                        index: i,
                        text: tt.textContent.substring(0, 150),
                        nodes: nodes,
                        html: html.substring(0, 500)
                    };
                });
            }
        """)

        print("=== Full Tooltip HTML Analysis ===\\n")
        for tt in result:
            print(f"Tooltip {tt['index']}:")
            print(f"  Full text: {tt['text']}")
            print(f"  Node sequence:")
            for node in tt['nodes'][:15]:
                if node['type'] == 'text':
                    print(f"    TEXT: {node['content']}")
                else:
                    print(f"    IMG:  {node['alt']}")
            print(f"  HTML: {tt['html'][:200]}...")
            print()

        await browser.close()

asyncio.run(debug_html())
