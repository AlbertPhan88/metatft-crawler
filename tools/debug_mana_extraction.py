#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright

async def debug():
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

                // Get context around ability name
                const startIdx = Math.max(0, abilityNameIndex - 1);
                const endIdx = Math.min(lines.length, abilityNameIndex + 5);
                const context = lines.slice(startIdx, endIdx);

                // Check for mana patterns
                const patterns = context.map(line => ({
                    line: line,
                    isSingleDigit: /^\\d+$/.test(line),
                    isSlashDigits: /^\\/\\d+$/.test(line),
                    isFullMana: /^\\d+\\/\\d+$/.test(line)
                }));

                return {
                    abilityTabIndex: abilityTabIndex,
                    abilityNameIndex: abilityNameIndex,
                    abilityName: abilityName,
                    contextLines: context,
                    patterns: patterns,
                    nextLine: abilityNameIndex + 1 < lines.length ? lines[abilityNameIndex + 1] : null,
                    followingLine: abilityNameIndex + 2 < lines.length ? lines[abilityNameIndex + 2] : null
                };
            }
        """)

        print("=== Mana Cost Extraction Debug ===\\n")
        print(f"Ability Name Index: {result['abilityNameIndex']}")
        print(f"Ability Name: {result['abilityName']}\\n")

        print("Context lines:")
        for i, (line, pattern) in enumerate(zip(result['contextLines'], result['patterns'])):
            print(f"  {i}: '{line}'")
            if pattern['isSingleDigit']:
                print(f"     ↳ SINGLE DIGIT")
            elif pattern['isSlashDigits']:
                print(f"     ↳ SLASH DIGITS")
            elif pattern['isFullMana']:
                print(f"     ↳ FULL MANA PATTERN")

        print(f"\\nNext line (index {result['abilityNameIndex']+1}): '{result['nextLine']}'")
        print(f"Following line (index {result['abilityNameIndex']+2}): '{result['followingLine']}'")

        await browser.close()

asyncio.run(debug())
