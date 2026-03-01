#!/usr/bin/env python3
"""
Debug description extraction for units with and without descriptions
"""

import asyncio
import sys
import os
from playwright.async_api import async_playwright

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.metatft_crawler.utils.browser import switch_language
from src.metatft_crawler.languages.loader import get_language_config


async def debug_unit(unit_name, unit_url):
    """Debug a specific unit's description extraction."""

    lang_config = get_language_config("vi")

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.goto(unit_url, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(2000)

        await switch_language(page, "vi")
        await page.wait_for_timeout(2000)

        # Click Stats button
        buttons = await page.query_selector_all("button")
        for btn in buttons:
            text = await btn.text_content()
            if text and ('Stats' in text or text.strip() == lang_config.stats_label):
                await btn.click()
                await page.wait_for_timeout(1000)
                break

        # Get the page text and extract description
        page_text = await page.evaluate("document.body.innerText")
        lines = page_text.split('\n')

        print(f"\n{'='*100}")
        print(f"Unit: {unit_name}")
        print(f"{'='*100}")

        # Get initial data like the crawler does
        initial_data = await page.evaluate("""
            (langConfig) => {
                const pageText = document.body.innerText;
                const lines = pageText.split('\\n').map(l => l.trim()).filter(l => l && l.length > 0);

                let abilityDescription = '';
                let abilityMana = '';
                let abilityName = null;
                let abilityTabIndex = -1;
                let abilityNameIndex = -1;

                // Find ability tab
                for (let i = 0; i < Math.min(100, lines.length); i++) {
                    if (lines[i] === langConfig.ability_label && lines[i+1] === langConfig.stats_label) {
                        abilityTabIndex = i;
                        break;
                    }
                }

                if (abilityTabIndex > 0) {
                    // Get ability name
                    for (let i = abilityTabIndex + 1; i < Math.min(abilityTabIndex + 5, lines.length); i++) {
                        const line = lines[i];
                        if (line && !line.match(/^\\d/) && line !== 'Key' && line !== 'Stats' && line.length < 100) {
                            abilityName = line;
                            abilityNameIndex = i;
                            break;
                        }
                    }

                    // Get mana
                    try {
                        const manaContainer = document.querySelector('.UnitAbilityMana');
                        if (manaContainer) {
                            const manaText = manaContainer.innerText;
                            const nums = manaText.match(/\\d+/g);
                            if (nums && nums.length >= 2) {
                                abilityMana = nums[0] + '/' + nums[1];
                            }
                        }
                    } catch (e) {
                    }

                    // Extract description
                    let descriptionLines = [];
                    let inDescription = false;
                    let manaFoundIndex = -1;

                    // Find where mana ends
                    for (let i = abilityTabIndex + 1; i < lines.length; i++) {
                        if (lines[i] && lines[i].match(/^\\d+$/) && i + 1 < lines.length && lines[i + 1] === '/') {
                            manaFoundIndex = i + 2;
                            break;
                        }
                    }

                    for (let i = abilityTabIndex + 1; i < lines.length; i++) {
                        const line = lines[i];

                        // Check for Passive/Active markers
                        const passiveMarker = langConfig.passive_marker;
                        const activeMarker = langConfig.active_marker;
                        if ((line.startsWith(passiveMarker) || line.startsWith(activeMarker)) && !inDescription) {
                            inDescription = true;
                            const markers = new RegExp(`^(${passiveMarker}|${activeMarker})\\\\s*`);
                            const textAfterLabel = line.replace(markers, '');
                            if (textAfterLabel && textAfterLabel.length > 3) {
                                descriptionLines.push(textAfterLabel);
                            }
                            continue;
                        }

                        // Also start description after mana
                        if (!inDescription && manaFoundIndex !== -1 && i >= manaFoundIndex) {
                            if (line && line.length > 5 && line.length < 300 &&
                                !line.match(/^\\d/) && !line.match(/^[\\/\\(\\)]*$/) &&
                                line !== langConfig.unlock_marker) {
                                inDescription = true;
                                console.log(`Starting description at line ${i}: ${line}`);
                                descriptionLines.push(line);
                                continue;
                            }
                        }

                        // Collect lines in description
                        if (inDescription && line === langConfig.unlock_marker) {
                            break;
                        }

                        if (inDescription && line && line.length > 5 && line.length < 300) {
                            descriptionLines.push(line);
                        }
                    }

                    abilityDescription = descriptionLines.join(' ');
                }

                return {
                    abilityName: abilityName,
                    abilityMana: abilityMana,
                    abilityDescription: abilityDescription,
                    abilityTabIndex: abilityTabIndex,
                    abilityNameIndex: abilityNameIndex
                };
            }
        """, {
            'ability_label': lang_config.ability_label,
            'stats_label': lang_config.stats_label,
            'passive_marker': lang_config.passive_marker,
            'active_marker': lang_config.active_marker,
            'unlock_marker': lang_config.unlock_marker,
        })

        print(f"\nExtraction Results:")
        print(f"  abilityTabIndex: {initial_data['abilityTabIndex']}")
        print(f"  abilityName: {initial_data['abilityName']}")
        print(f"  abilityMana: {initial_data['abilityMana']}")
        print(f"  abilityDescription length: {len(initial_data.get('abilityDescription', ''))}")
        print(f"  abilityDescription: {initial_data.get('abilityDescription', '')[:200]}")

        await browser.close()


async def main():
    units = [
        ("Renekton (NO desc)", "https://www.metatft.com/units/Renekton"),
        ("Baron Nashor (HAS desc)", "https://www.metatft.com/units/BaronNashor"),
    ]

    for name, url in units:
        await debug_unit(name, url)


if __name__ == "__main__":
    asyncio.run(main())
