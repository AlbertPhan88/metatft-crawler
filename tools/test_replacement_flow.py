#!/usr/bin/env python3
import asyncio
import re
from playwright.async_api import async_playwright

async def test_flow():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.goto("https://www.metatft.com/units/BaronNashor", wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)

        # First, extract the ability_others and ability_description like the crawler does
        initial_data = await page.evaluate("""
            () => {
                const pageText = document.body.innerText;
                const lines = pageText.split('\\n').map(l => l.trim()).filter(l => l);

                let abilityIndex = -1;
                let unlockIndex = -1;
                let descriptionLines = [];
                let damageLines = [];
                let abilityName = '';
                let abilityDescription = '';
                let abilityOthers = '';
                let unlockCondition = '';

                // Find ability name
                for (let i = 0; i < lines.length; i++) {
                    if (lines[i] === 'Ability' && i + 1 < lines.length) {
                        abilityName = lines[i + 1];
                        abilityIndex = i;
                        break;
                    }
                }

                if (abilityIndex !== -1) {
                    let inDescription = true;

                    for (let i = abilityIndex + 2; i < lines.length; i++) {
                        const line = lines[i];

                        if (line === 'Mana' || line === 'Stats') {
                            break;
                        }

                        if (inDescription && unlockIndex === -1) {
                            if (line === 'Damage:' || line === 'Acid Damage:' ||
                                line === '+' || line === 'of' ||
                                line.match(/^\\d+[\\/\\d%]*\\s*$/) ||
                                line.match(/^[\\d\\(\\)\\/]*$/) ||
                                line.match(/\\(\\)\\s*$/) ||
                                line.match(/^%/)) {
                                damageLines.push(line);
                                continue;
                            }

                            if (line && line.length > 5 && line.length < 300) {
                                descriptionLines.push(line);
                            }
                        }

                        if (line === 'Unlock:' && unlockIndex === -1) {
                            unlockIndex = i;
                            break;
                        }
                    }

                    abilityDescription = descriptionLines.join(' ').trim();
                    abilityOthers = damageLines.join(' ').trim();
                }

                return {
                    ability_name: abilityName,
                    ability_description: abilityDescription,
                    ability_others: abilityOthers
                };
            }
        """)

        print("=== Extracted Data ===")
        print(f"Name: {initial_data['ability_name']}")
        print(f"\\nDescription ({len(initial_data['ability_description'])} chars):")
        print(f"  {initial_data['ability_description'][:200]}...")
        print(f"\\nOthers ({len(initial_data['ability_others'])} chars):")
        print(f"  {initial_data['ability_others']}")

        # Now extract the mapping
        damage_stats_mapping = await page.evaluate("""
            () => {
                const mapping = {};
                const damagePattern = /\\d+\\/\\d+\\/\\d+/;
                const walker = document.createTreeWalker(
                    document.body,
                    NodeFilter.SHOW_ELEMENT,
                    null
                );

                let node;
                const processed = new Set();

                while (node = walker.nextNode()) {
                    const text = node.textContent;
                    const match = text.match(damagePattern);

                    if (match) {
                        const damage = match[0];
                        if (!processed.has(damage)) {
                            const imgs = Array.from(node.querySelectorAll('img[alt="AP"], img[alt="AD"]'));
                            if (imgs.length > 0) {
                                const stats = imgs.map(img => img.getAttribute('alt'));
                                mapping[damage] = stats;
                                processed.add(damage);
                            }
                        }
                    }
                }

                return mapping;
            }
        """)

        print(f"\\n=== Mapping Extracted ===")
        for dmg, stats in damage_stats_mapping.items():
            print(f"  {dmg}: {stats}")

        # Now test the replacement
        def replace_with_stats(text):
            pattern = r'(\d+/\d+/\d+)\s*\(\)'

            def replacer(match):
                damage_val = match.group(1)
                if damage_val in damage_stats_mapping:
                    stats = damage_stats_mapping[damage_val]
                    stats_str = '/'.join(stats)
                    print(f"    Replacing {damage_val} with ({stats_str})")
                    return f'{damage_val} ({stats_str})'
                return match.group(0)

            return re.sub(pattern, replacer, text)

        print(f"\\n=== Testing Replacement ===")
        print(f"Original others:\n  {initial_data['ability_others']}")
        print(f"\\nReplacing...")
        result_others = replace_with_stats(initial_data['ability_others'])
        print(f"\\nResult others:\n  {result_others}")

        print(f"\\n\\nOriginal description:\n  {initial_data['ability_description'][:150]}...")
        print(f"\\nReplacing...")
        result_desc = replace_with_stats(initial_data['ability_description'])
        print(f"\\nResult description:\n  {result_desc[:150]}...")

        await browser.close()

asyncio.run(test_flow())
