#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright

async def debug_exact():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.goto("https://www.metatft.com/units/BaronNashor", wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)

        # Get the exact HTML structure around damage values
        result = await page.evaluate("""
            () => {
                // Find elements that contain damage patterns and images
                const walker = document.createTreeWalker(
                    document.body,
                    NodeFilter.SHOW_ELEMENT,
                    null
                );

                const damageVals = ['280/420/20500', '112/189/10250', '250/375/20000', '30/45/500'];
                const results = [];

                let node;
                while (node = walker.nextNode()) {
                    const html = node.innerHTML;
                    const text = node.textContent;

                    // Check if this element or nearby contains damage values
                    for (const damage of damageVals) {
                        if (text.includes(damage)) {
                            // Found element with damage value
                            // Get images in this element
                            const imgs = Array.from(node.querySelectorAll('img[alt="AP"], img[alt="AD"]'));

                            if (imgs.length > 0) {
                                results.push({
                                    damage: damage,
                                    tag: node.tagName,
                                    textSnippet: text.substring(0, 150),
                                    imageCount: imgs.length,
                                    images: imgs.map((img, i) => ({
                                        index: i,
                                        alt: img.getAttribute('alt'),
                                        nextSibling: img.nextSibling?.textContent?.substring(0, 20) || 'none'
                                    })),
                                    htmlSnippet: html.substring(0, 300)
                                });
                                break;
                            }
                        }
                    }
                }

                return results;
            }
        """)

        print("=== Damage Values with Images in DOM ===\\n")
        for item in result:
            print(f"Damage: {item['damage']}")
            print(f"  Tag: {item['tag']}")
            print(f"  Text: {item['textSnippet'][:80]}...")
            print(f"  Images ({item['imageCount']}): {[img['alt'] for img in item['images']]}")
            print(f"  HTML: {item['htmlSnippet'][:100]}...")
            print()

        await browser.close()

asyncio.run(debug_exact())
