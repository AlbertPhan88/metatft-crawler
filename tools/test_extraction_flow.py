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

                let abilityTabIndex = -1;
                for (let i = 0; i < Math.min(100, lines.length); i++) {
                    if (lines[i] === 'Ability' && lines[i+1] === 'Stats') {
                        abilityTabIndex = i;
                        break;
                    }
                }

                let abilityName = null;
                let abilityNameIndex = -1;

                // Debug: check all lines in search range
                const searchLines = [];
                for (let i = abilityTabIndex + 1; i < Math.min(abilityTabIndex + 5, lines.length); i++) {
                    const line = lines[i];
                    const startsWithDigit = line.match(/^\\d/);
                    const isKey = line === 'Key';
                    const isStats = line === 'Stats';
                    const isLongLine = line.length >= 100;

                    searchLines.push({
                        i: i,
                        line: line,
                        startsWithDigit: !!startsWithDigit,
                        isKey: isKey,
                        isStats: isStats,
                        isLongLine: isLongLine,
                        matchesCondition: !startsWithDigit && !isKey && !isStats && !isLongLine
                    });

                    if (line && !line.match(/^\\d/) && line !== 'Key' && line !== 'Stats' && line.length < 100) {
                        abilityName = line;
                        abilityNameIndex = i;
                        break;
                    }
                }

                let abilityMana = '';
                if (abilityNameIndex > 0 && abilityNameIndex + 2 < lines.length) {
                    const l1 = lines[abilityNameIndex + 1];
                    const l2 = lines[abilityNameIndex + 2];

                    if (l1 && /^\\d+$/.test(l1)) {
                        abilityMana = l1;
                        if (l2 && /^\\/\\d+$/.test(l2)) {
                            abilityMana += l2;
                        }
                    } else if (l1 && /^\\d+\\/\\d+$/.test(l1)) {
                        abilityMana = l1;
                    }
                }

                return {
                    abilityTabIndex: abilityTabIndex,
                    abilityName: abilityName,
                    abilityNameIndex: abilityNameIndex,
                    searchLines: searchLines,
                    manaExtraction: {
                        l1: abilityNameIndex + 1 < lines.length ? lines[abilityNameIndex + 1] : 'OUT_OF_BOUNDS',
                        l2: abilityNameIndex + 2 < lines.length ? lines[abilityNameIndex + 2] : 'OUT_OF_BOUNDS',
                        abilityMana: abilityMana
                    }
                };
            }
        """)

        print("=== Extraction Flow Debug ===\\n")
        print(f"Ability Tab Index: {result['abilityTabIndex']}")
        print(f"Ability Name: {result['abilityName']}")
        print(f"Ability Name Index: {result['abilityNameIndex']}\\n")

        print("Search Lines:")
        for sl in result['searchLines']:
            marker = " << MATCH" if sl['matchesCondition'] else ""
            print(f"  {sl['i']}: '{sl['line'][:40]}' | starts={sl['startsWithDigit']}, Key={sl['isKey']}, Stats={sl['isStats']}, Long={sl['isLongLine']}{marker}")

        print(f"\\nMana Extraction:")
        for k, v in result['manaExtraction'].items():
            print(f"  {k}: '{v}'")

        await browser.close()

asyncio.run(test())
