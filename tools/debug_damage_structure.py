#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright

async def debug_structure():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.goto("https://www.metatft.com/units/BaronNashor", wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)

        # Extract detailed info about damage values and their associated images
        result = await page.evaluate("""
            () => {
                // Find the section with ability description
                const pageText = document.body.innerText;
                const lines = pageText.split('\\n');

                // Look for text that contains damage numbers with patterns like "280/420/20500"
                const damagePattern = /\\d+\\/\\d+\\/\\d+/g;
                const damageMatches = [];

                lines.forEach((line, i) => {
                    const matches = line.match(damagePattern);
                    if (matches) {
                        damageMatches.push({
                            lineNum: i,
                            line: line,
                            damages: matches
                        });
                    }
                });

                // Now let's find the HTML sections with images and see how they relate
                // Look for text nodes containing damage numbers, then check for adjacent images

                // Get all elements that might contain damage info
                const bodyText = document.body.innerText;
                const allImgs = Array.from(document.querySelectorAll('img[alt="AP"], img[alt="AD"]'));

                // For each damage match in text, find which images follow it nearby
                const damageWithImages = [];

                lines.forEach((line, i) => {
                    const matches = Array.from(line.matchAll(/(\\d+\\/\\d+\\/\\d+)/g));
                    if (matches.length > 0) {
                        // This line has damage values
                        // Try to find nearby images by looking at the DOM

                        // Find the text node in the DOM
                        const walker = document.createTreeWalker(
                            document.body,
                            NodeFilter.SHOW_TEXT,
                            null
                        );

                        let node;
                        while (node = walker.nextNode()) {
                            if (node.textContent.includes(line.substring(0, 30))) {
                                // Found the text node, now look for images around it
                                let parent = node.parentElement;
                                let imgCount = 0;
                                let images = [];

                                // Check siblings and nearby elements
                                const parentClone = parent ? parent.cloneNode(true) : null;
                                if (parentClone) {
                                    const imgs = parentClone.querySelectorAll('img[alt="AP"], img[alt="AD"]');
                                    imgCount = imgs.length;
                                    images = Array.from(imgs).map(img => ({
                                        alt: img.getAttribute('alt'),
                                        src: img.getAttribute('src')
                                    }));
                                }

                                if (imgCount > 0) {
                                    damageWithImages.push({
                                        line: line.substring(0, 100),
                                        damages: matches.map(m => m[1]),
                                        imageCount: imgCount,
                                        images: images
                                    });
                                    break;
                                }
                            }
                        }
                    }
                });

                return {
                    totalDamageLines: damageMatches.length,
                    damageLines: damageMatches.slice(0, 5),
                    damageWithImages: damageWithImages,
                    totalImages: allImgs.length,
                    images: allImgs.slice(0, 10).map(img => ({
                        alt: img.getAttribute('alt'),
                        src: img.getAttribute('src')
                    }))
                };
            }
        """)

        print("=== Damage Values Analysis ===")
        print(f"Total lines with damage values: {result['totalDamageLines']}")
        print(f"\\nFirst few damage lines:")
        for item in result['damageLines'][:5]:
            print(f"  Line {item['lineNum']}: {item['line']}")
            print(f"    Damages: {item['damages']}")

        print(f"\\n=== Damages with Images ===")
        print(f"Total: {len(result['damageWithImages'])}")
        for item in result['damageWithImages']:
            print(f"  {item['line']}")
            print(f"    Damages: {item['damages']}")
            print(f"    Images ({item['imageCount']}): {[img['alt'] for img in item['images']]}")

        print(f"\\n=== All Images on Page ===")
        print(f"Total images: {result['totalImages']}")
        for img in result['images']:
            print(f"  {img['alt']}: {img['src']}")

        await browser.close()

asyncio.run(debug_structure())
