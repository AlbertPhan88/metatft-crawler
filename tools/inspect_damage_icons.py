#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright

async def inspect_damage_icons():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.goto("https://www.metatft.com/units/BaronNashor", wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)

        # Look for the ability damage section and examine the HTML
        result = await page.evaluate("""
            () => {
                // Find all images in the page
                const allImages = Array.from(document.querySelectorAll('img'));

                // Find images that might be stat icons
                const statIcons = allImages.filter(img => {
                    const src = img.src || '';
                    const alt = img.alt || '';
                    const title = img.title || '';

                    // Look for common stat icon indicators
                    return src.includes('icon') || src.includes('stat') ||
                           alt.toLowerCase().includes('power') ||
                           alt.toLowerCase().includes('damage') ||
                           alt.toLowerCase().includes('ad') ||
                           alt.toLowerCase().includes('ap') ||
                           title.toLowerCase().includes('power') ||
                           title.toLowerCase().includes('damage');
                });

                return statIcons.map(img => ({
                    src: img.src,
                    alt: img.alt,
                    title: img.title,
                    className: img.className,
                    style: img.getAttribute('style')
                }));
            }
        """)

        print("Found stat icons:")
        for i, icon in enumerate(result):
            print(f"\\n{i+1}. Icon:")
            print(f"   Alt: {icon['alt']}")
            print(f"   Title: {icon['title']}")
            print(f"   Class: {icon['className']}")
            print(f"   Src: {icon['src']}")

        # Also check what's in the damage section HTML
        damage_html = await page.evaluate("""
            () => {
                // Find elements that contain "Damage:" text
                const allElements = Array.from(document.querySelectorAll('*'));
                const damageElements = allElements.filter(el =>
                    el.textContent.includes('Damage:') && el.textContent.length < 500
                );

                return damageElements.map(el => ({
                    tag: el.tagName,
                    text: el.textContent.substring(0, 200),
                    html: el.innerHTML.substring(0, 300)
                }));
            }
        """)

        print("\\n\\n=== Damage section HTML ===")
        for i, el in enumerate(damage_html[:3]):
            print(f"\\n{i+1}. {el['tag']}:")
            print(f"   Text: {el['text']}")
            print(f"   HTML: {el['html']}")

        await browser.close()

asyncio.run(inspect_damage_icons())
