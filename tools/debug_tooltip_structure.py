#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright

async def debug_tooltip():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.goto("https://www.metatft.com/units/BaronNashor", wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)

        # Get the exact structure of the tooltip/ability section
        result = await page.evaluate("""
            () => {
                // Find the ability section and get its structure with images
                const pageText = document.body.innerText;
                const lines = pageText.split('\\n');

                // Find where Damage: starts
                const abilityIndex = lines.findIndex(l => l.includes('Damage:'));

                // Get the tooltip calculation sections
                const tooltips = Array.from(document.querySelectorAll('tooltipcalculation'));

                const tooltipDetails = tooltips.map((tt, i) => {
                    const text = tt.textContent;
                    const html = tt.innerHTML;

                    // Get all images in this tooltip
                    const imgs = Array.from(tt.querySelectorAll('img[alt="AP"], img[alt="AD"]'));
                    const imgDetails = imgs.map((img, j) => ({
                        index: j,
                        alt: img.getAttribute('alt'),
                        // Get the text immediately after this image
                        nextContent: img.nextSibling?.textContent?.substring(0, 50) || '',
                        // Get the text immediately before this image
                        prevContent: img.previousSibling?.textContent?.substring(-50) || ''
                    }));

                    return {
                        tooltipIndex: i,
                        text: text.substring(0, 200),
                        imageCount: imgs.length,
                        images: imgDetails,
                        html: html.substring(0, 300)
                    };
                });

                return {
                    tooltips: tooltipDetails,
                    damageLineStart: abilityIndex,
                    relevantLines: lines.slice(Math.max(0, abilityIndex - 5), Math.min(lines.length, abilityIndex + 20))
                };
            }
        """)

        print("=== Tooltip Structures ===\\n")
        for tt in result['tooltips']:
            print(f"Tooltip {tt['tooltipIndex']}:")
            print(f"  Text: {tt['text'][:100]}...")
            print(f"  Images ({tt['imageCount']}):")
            for img in tt['images']:
                print(f"    {img['index']}: {img['alt']} (after: {img['nextContent'][:20]}...)")
            print()

        print("\\n=== Context Lines ===")
        for i, line in enumerate(result['relevantLines']):
            marker = " >> " if i == result['damageLineStart'] else "    "
            print(f"{marker}{line[:80]}")

        await browser.close()

asyncio.run(debug_tooltip())
