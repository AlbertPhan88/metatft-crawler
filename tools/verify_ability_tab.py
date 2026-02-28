#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright

async def verify():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.goto("https://www.metatft.com/units/BaronNashor", wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)

        result = await page.evaluate("""
            () => {
                const pageText = document.body.innerText;
                const lines = pageText.split('\\n').map(l => l.trim()).filter(l => l && l.length > 0);

                // Find "Ability" and "Stats"
                let abilityTabIndex = -1;
                for (let i = 0; i < Math.min(100, lines.length); i++) {
                    if (lines[i] === 'Ability' && lines[i+1] === 'Stats') {
                        abilityTabIndex = i;
                        break;
                    }
                }

                // Find ability name
                let abilityName = null;
                let abilityNameIndex = -1;
                for (let i = abilityTabIndex + 1; i < Math.min(abilityTabIndex + 5, lines.length); i++) {
                    const line = lines[i];
                    if (line && !line.match(/^\\d/) && line !== 'Key' && line !== 'Stats' && line.length < 100) {
                        abilityName = line;
                        abilityNameIndex = i;
                        break;
                    }
                }

                // Get context
                const contextStart = Math.max(0, abilityTabIndex - 1);
                const contextEnd = Math.min(lines.length, abilityNameIndex + 5);
                const context = lines.slice(contextStart, contextEnd);

                return {
                    abilityTabIndex: abilityTabIndex,
                    abilityNameIndex: abilityNameIndex,
                    abilityName: abilityName,
                    context: context.map((line, i) => ({
                        index: contextStart + i,
                        line: line
                    }))
                };
            }
        """)

        print("=== Ability Tab & Name Finding ===\\n")
        print(f"Ability Tab Index: {result['abilityTabIndex']}")
        print(f"Ability Name Index: {result['abilityNameIndex']}")
        print(f"Ability Name: {result['abilityName']}\\n")

        print("Context:")
        for item in result['context']:
            marker = " << ABILITY TAB" if item['index'] == result['abilityTabIndex'] else ""
            marker += " << ABILITY NAME" if item['index'] == result['abilityNameIndex'] else ""
            print(f"  {item['index']:3d}: {item['line']}{marker}")

        await browser.close()

asyncio.run(verify())
