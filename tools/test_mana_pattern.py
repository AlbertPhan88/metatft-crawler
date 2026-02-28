#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright

async def test():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.goto("https://www.metatft.com/units/BaronNashor", wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)

        result = await page.evaluate("""
            () => {
                const pageText = document.body.innerText;
                const lines = pageText.split('\\n').map(l => l.trim()).filter(l => l && l.length > 0);

                // Find ability name and mana
                let abilityNameIndex = -1;
                for (let i = 0; i < lines.length; i++) {
                    if (lines[i] === 'Wrath of the Void') {
                        abilityNameIndex = i;
                        break;
                    }
                }

                const nextLine = lines[abilityNameIndex + 1];
                const followingLine = lines[abilityNameIndex + 2];

                // Test patterns
                const test1 = /^\\d+$/.test(nextLine);
                const test2 = /^\\/\\d+$/.test(followingLine);

                return {
                    abilityNameIndex: abilityNameIndex,
                    nextLine: nextLine,
                    nextLineType: typeof nextLine,
                    followingLine: followingLine,
                    followingLineType: typeof followingLine,
                    test1Result: test1,  // Should match "0"
                    test2Result: test2,  // Should match "/50"
                    combined: (test1 && test2) ? (nextLine + followingLine) : "NO MATCH",
                    // Try different patterns
                    forwardSlashTest: /^\\//.test(followingLine),
                    digitAfterSlash: /\\/\\d+/.test(followingLine)
                };
            }
        """)

        print("=== Mana Pattern Test ===")
        for key, val in result.items():
            print(f"{key}: {val}")

        await browser.close()

asyncio.run(test())
