#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright

async def debug_mana():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.goto("https://www.metatft.com/units/BaronNashor", wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)

        # Find mana cost near ability name
        result = await page.evaluate("""
            () => {
                const pageText = document.body.innerText;
                const lines = pageText.split('\\n').map(l => l.trim()).filter(l => l);

                // Find "Ability" section
                const abilityIndex = lines.findIndex(l => l === 'Ability');

                if (abilityIndex === -1) return { error: 'No Ability section found' };

                // Get lines around ability name
                const context = lines.slice(abilityIndex, Math.min(abilityIndex + 10, lines.length));

                // Look for mana pattern (like "0/50" or "30/200")
                const manaPattern = /^(\\d+)\\/(\d+)$/;

                return {
                    abilityIndex: abilityIndex,
                    context: context,
                    lines: context.map((line, i) => ({
                        index: abilityIndex + i,
                        text: line,
                        isManaPattern: manaPattern.test(line),
                        manaMatch: line.match(manaPattern)
                    }))
                };
            }
        """)

        print("=== Ability Section with Mana Cost ===\\n")
        if 'error' in result:
            print(f"Error: {result['error']}")
        else:
            print(f"Ability starts at line {result['abilityIndex']}\\n")
            for line_info in result['lines']:
                marker = " >> MANA" if line_info['isManaPattern'] else ""
                print(f"{line_info['index']:3d}: {line_info['text']}{marker}")

        await browser.close()

asyncio.run(debug_mana())
