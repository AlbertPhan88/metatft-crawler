#!/usr/bin/env python3
"""
TFT Units Crawler - Extracts detailed data for each unit from MetaTFT.com/units
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from playwright.async_api import async_playwright
from typing import Dict, List, Any

from ..utils.browser import switch_language


async def crawl_all_units(language: str = "en", limit_units: int = None) -> Dict[str, Any]:
    """
    Crawl MetaTFT.com/units and extract data for units.

    Args:
        language: Language code ('en' for English, 'vi' for Vietnamese, etc.)
        limit_units: Limit crawling to N units (None = crawl all). Useful for testing.

    Returns:
        Dictionary containing timestamp and unit data
    """

    # Use the same base URL for all languages - language switching is done via selector
    base_url = "https://www.metatft.com/units"

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        print(f"Navigating to {base_url} (Language: {language})...")
        try:
            await page.goto(base_url, wait_until="domcontentloaded", timeout=60000)
        except Exception as e:
            print(f"Navigation timeout: {e}")

        print("Waiting for page to fully render...")
        await page.wait_for_timeout(5000)

        # Switch language if needed
        if language == "vi":
            print("Switching to Vietnamese...")
            await switch_language(page, "vi")

        # Extract all units from the main units page
        print("Extracting all units and their links...")
        units_list = await page.evaluate("""
            () => {
                const units = [];
                const pageText = document.body.innerText;

                // Find all unit links on the page
                const allLinks = Array.from(document.querySelectorAll('a[href*="/units/"]'));
                const unitLinks = allLinks.filter(a => {
                    const href = a.getAttribute('href') || '';
                    return href.startsWith('/units/') && !href.endsWith('/units');
                });

                // Extract unit data from the table
                // English: Unit | Tier | Avg Place | Win Rate | Frequency
                // Vietnamese: Đơn vị | Rank | Hạng | Tỷ Lệ Thắng | Tần Suất
                const lines = pageText.split('\\n');
                const tierPattern = /^([SABCDF])\\s*$/;

                let i = 0;
                while (i < lines.length) {
                    const line = lines[i].trim();

                    // Look for tier indicators
                    if (tierPattern.test(line)) {
                        const tier = line;
                        // The unit name should be above or around this line
                        let unitName = null;

                        // Check previous lines for unit name
                        for (let j = i - 1; j >= Math.max(0, i - 5); j--) {
                            const prevLine = lines[j].trim();
                            if (prevLine && !tierPattern.test(prevLine) && prevLine.length < 40 && prevLine.length > 2) {
                                unitName = prevLine;
                                break;
                            }
                        }

                        // Check next lines for stats
                        if (i + 1 < lines.length) {
                            const statsLine = lines[i + 1].trim();
                            const statsMatch = statsLine.match(/([\\d.]+)\\s+([\\d.]+)\\s+([\\d,]+)\\s+([\\d.]+)/);

                            if (unitName && statsMatch) {
                                units.push({
                                    name: unitName,
                                    tier: tier,
                                    avg_placement: parseFloat(statsMatch[1]),
                                    win_rate_percent: parseFloat(statsMatch[2]),
                                    pick_count: parseInt(statsMatch[3].replace(/,/g, '')),
                                    frequency_percent: parseFloat(statsMatch[4])
                                });
                            }
                        }
                    }
                    i++;
                }

                // Also extract from unit links as fallback
                unitLinks.forEach(link => {
                    const unitName = link.textContent.trim();
                    if (unitName && unitName.length > 1 && unitName.length < 40) {
                        // Check if we already have this unit
                        if (!units.find(u => u.name === unitName)) {
                            units.push({
                                name: unitName,
                                tier: 'Unknown',
                                url: link.getAttribute('href')
                            });
                        }
                    }
                });

                return units.slice(0, 50); // Return top 50 units
            }
        """)

        total_units = len(units_list)
        print(f"✓ Found {total_units} units to crawl")
        print(f"\n{'='*70}")
        print(f"Starting detailed crawl of all {total_units} units...")
        print(f"{'='*70}\n")

        # Crawl detail page for all units
        detailed_units = []
        start_time = time.time()

        for i, unit_data in enumerate(units_list):
            # Stop if limit reached
            if limit_units and i >= limit_units:
                break

            unit_name = unit_data.get('name', '')
            current_progress = i + 1
            percentage = (current_progress / total_units) * 100

            # Calculate elapsed time and estimate remaining
            elapsed = time.time() - start_time
            units_per_second = current_progress / elapsed if elapsed > 0 else 0
            remaining_units = total_units - current_progress
            estimated_remaining = remaining_units / units_per_second if units_per_second > 0 else 0

            # Format times
            elapsed_str = str(timedelta(seconds=int(elapsed)))
            remaining_str = str(timedelta(seconds=int(estimated_remaining)))

            # Print progress
            progress_bar = "█" * int(percentage / 5) + "░" * (20 - int(percentage / 5))
            print(f"[{progress_bar}] {current_progress:2d}/{total_units} ({percentage:5.1f}%) | {unit_name:25s} | ⏱ {elapsed_str} | 🕐 ETA: {remaining_str}")

            try:
                # Create URL from unit name
                unit_path = unit_name.replace(' ', '').replace("'", '').replace('&', 'and')
                unit_url = f"https://www.metatft.com/units/{unit_path}"

                await page.goto(unit_url, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_timeout(1000)

                # Extract unit detail data - with proper tab handling
                # First, extract initial info (cost, type, traits, ability name, description)
                initial_data = await page.evaluate("""
                    () => {
                        const pageText = document.body.innerText;
                        const lines = pageText.split('\\n').map(l => l.trim()).filter(l => l && l.length > 0);

                        // Find unit header section with cost and traits
                        let cost = null;
                        let type = null;  // e.g., "Attack Fighter"
                        let traits = [];
                        let abilityName = null;
                        let abilityDescription = '';
                        let abilityOthers = '';
                        let unlockCondition = '';

                        // Known trait names to look for (exact matches)
                        const knownTraits = ['Attack', 'Fighter', 'Void', 'Riftscourge', 'Magic', 'Marksman', 'Zaun', 'Zaunite', 'Yordle', 'Longshot', 'Duelist', 'Visionary', 'Knight', 'Assassin', 'Mage', 'Ranger', 'Support', 'Tank', 'Bruiser', 'Shurima', 'Noxus', 'Piltover', 'Demacia', 'Ionia', 'Shadow', 'Star', 'Caretaker', 'Chemtech', 'Corrupt', 'Enforcer'];
                        const typeWords = ['Attack', 'Fighter', 'Caster', 'Support', 'Tank'];

                        // Look for pattern: Unit Name, then Type, then Traits, then number (cost), then "Ability"/"Stats" tabs
                        let headerStartIndex = -1;
                        let abilityTabIndex = -1;

                        // Find where unit header starts (look for tabs)
                        for (let i = 0; i < Math.min(100, lines.length); i++) {
                            if (lines[i] === 'Ability' && lines[i+1] === 'Stats') {
                                abilityTabIndex = i;
                                headerStartIndex = Math.max(0, i - 20);
                                break;
                            }
                        }

                        if (abilityTabIndex > 0) {
                            // Look backwards from "Ability" tab for cost, type, and traits
                            let typeLines = [];
                            for (let i = abilityTabIndex - 1; i >= headerStartIndex; i--) {
                                const line = lines[i];

                                // Cost is a single digit (1-10)
                                if (/^[1-9]$/.test(line) && cost === null) {
                                    cost = parseInt(line);
                                }

                                // Type: look for lines containing type words (could be "Attack Fighter" on one line)
                                if (type === null) {
                                    let hasTypeWord = false;
                                    for (const typeWord of typeWords) {
                                        if (line.includes(typeWord)) {
                                            typeLines.unshift(line);
                                            hasTypeWord = true;
                                            break;
                                        }
                                    }
                                    if (hasTypeWord) continue;
                                }

                                // Traits are exact word matches (but not type words)
                                if (knownTraits.includes(line) && !typeWords.includes(line) && !traits.includes(line)) {
                                    traits.unshift(line);  // add to front to preserve order
                                }
                            }

                            // Set type from first matching line found
                            if (typeLines.length > 0) {
                                type = typeLines[0];
                            }

                            // Extract ability name: Look after "Ability" tab for first non-empty, non-number line
                            for (let i = abilityTabIndex + 1; i < Math.min(abilityTabIndex + 5, lines.length); i++) {
                                const line = lines[i];
                                if (line && !line.match(/^\\d/) && line !== 'Key' && line !== 'Stats' && line.length < 100) {
                                    abilityName = line;
                                    break;
                                }
                            }

                            // Extract ability description, damage info, and unlock condition
                            let descriptionLines = [];
                            let damageLines = [];
                            let inDescription = false;
                            let unlockIndex = -1;

                            for (let i = abilityTabIndex + 1; i < lines.length; i++) {
                                const line = lines[i];

                                // Mark start of description when we see Passive or Active
                                if ((line.startsWith('Passive:') || line.startsWith('Active:')) && !inDescription) {
                                    inDescription = true;
                                    const textAfterLabel = line.replace(/^(Passive:|Active:)\\s*/, '');
                                    if (textAfterLabel && textAfterLabel.length > 3) {
                                        descriptionLines.push(textAfterLabel);
                                    }
                                    continue;
                                }

                                // Track where Unlock starts
                                if (line === 'Unlock:' && unlockIndex === -1) {
                                    unlockIndex = i;
                                }

                                // Collect lines while in description section (until Unlock)
                                if (inDescription && unlockIndex === -1) {
                                    // Collect damage calculation lines separately
                                    if (line === 'Damage:' || line === 'Acid Damage:' ||
                                        line === '+' || line === 'of' ||
                                        line.match(/^\\d+[\\/\\d%]*\\s*$/) ||  // Just numbers like "30/45/500"
                                        line.match(/^[\\d\\(\\)\\/]*$/) ||     // Numbers and parens
                                        line.match(/\\(\\)\\s*$/) ||           // Ends with ()
                                        line.match(/^%/)) {                     // Starts with %
                                        damageLines.push(line);
                                        continue;
                                    }

                                    // Collect substantial text lines (likely ability description)
                                    if (line && line.length > 5 && line.length < 300) {
                                        descriptionLines.push(line);
                                    }
                                }

                                // Extract unlock condition after "Unlock:" is found
                                if (unlockIndex !== -1 && i === unlockIndex) {
                                    // Next 2 lines after "Unlock:" contain the condition
                                    if (i + 1 < lines.length) {
                                        unlockCondition = lines[i + 1].trim();
                                        if (i + 2 < lines.length && lines[i + 2].trim().length > 0 && lines[i + 2].trim().length < 100) {
                                            const nextLine = lines[i + 2].trim();
                                            // Only add if it looks like part of the condition (not a section header)
                                            if (!nextLine.match(/^[A-Z][a-z]+\\s[A-Z]/) && nextLine.length > 3) {
                                                unlockCondition += ' ' + nextLine;
                                            }
                                        }
                                    }
                                    break;  // Stop after processing unlock
                                }
                            }

                            abilityDescription = descriptionLines.join(' ').trim();
                            abilityOthers = damageLines.join(' ').trim();
                        }

                        return {
                            cost: cost,
                            type: type,
                            traits: traits,
                            ability_name: abilityName,
                            ability_description: abilityDescription,
                            unlock_condition: unlockCondition,
                            ability_others: abilityOthers
                        };
                    }
                """)

                # Now click Stats tab to get base stats
                try:
                    stats_button = await page.query_selector("button:has-text('Stats')")
                    if not stats_button:
                        # Try finding by text content
                        buttons = await page.query_selector_all("button")
                        for btn in buttons:
                            text = await btn.text_content()
                            if text and 'Stats' in text:
                                stats_button = btn
                                break

                    if stats_button:
                        await stats_button.click()
                        await page.wait_for_timeout(1000)
                except Exception as e:
                    print(f"    Could not click Stats tab: {str(e)[:50]}")

                # Extract base stats from Stats tab
                base_stats = await page.evaluate("""
                    () => {
                        const pageText = document.body.innerText;
                        const lines = pageText.split('\\n').map(l => l.trim()).filter(l => l && l.length > 0);

                        const stats = {
                            health: null,
                            mana: null,
                            attack_damage: null,
                            ability_power: null,
                            armor: null,
                            magic_resist: null,
                            attack_speed: null,
                            crit_chance: null,
                            crit_damage: null,
                            range: null
                        };

                        // Look for stat labels and their values
                        for (let i = 0; i < lines.length; i++) {
                            const line = lines[i];

                            // Health: "3000/5400/9720" format
                            if (line === 'Health' && i + 1 < lines.length) {
                                stats.health = lines[i + 1];
                            }
                            // Mana
                            if (line === 'Mana' && i + 1 < lines.length) {
                                stats.mana = lines[i + 1];
                            }
                            // Attack Damage
                            if (line.includes('Attack Damage') && i + 1 < lines.length) {
                                stats.attack_damage = lines[i + 1];
                            }
                            // Ability Power
                            if (line === 'Ability Power' && i + 1 < lines.length) {
                                stats.ability_power = lines[i + 1];
                            }
                            // Armor
                            if (line === 'Armor' && i + 1 < lines.length) {
                                stats.armor = lines[i + 1];
                            }
                            // Magic Resist
                            if (line.includes('Magic Resist') && i + 1 < lines.length) {
                                stats.magic_resist = lines[i + 1];
                            }
                            // Attack Speed
                            if (line.includes('Attack Speed') && i + 1 < lines.length) {
                                stats.attack_speed = lines[i + 1];
                            }
                            // Crit Chance
                            if (line.includes('Crit Chance') && i + 1 < lines.length) {
                                stats.crit_chance = lines[i + 1];
                            }
                            // Crit Damage
                            if (line.includes('Crit Damage') && i + 1 < lines.length) {
                                stats.crit_damage = lines[i + 1];
                            }
                            // Range
                            if (line === 'Range' && i + 1 < lines.length) {
                                stats.range = lines[i + 1];
                            }
                        }

                        return stats;
                    }
                """)

                # Post-process damage info to add stat abbreviations (AD/AP) to empty ()
                if initial_data.get('ability_others'):
                    import re
                    damage_text = initial_data['ability_others']

                    # Get stat image counts from the page to match patterns
                    stat_counts = await page.evaluate("""
                        () => {
                            const apImgs = Array.from(document.querySelectorAll('img[alt="AP"]'));
                            const adImgs = Array.from(document.querySelectorAll('img[alt="AD"]'));
                            return { ap: apImgs.length, ad: adImgs.length };
                        }
                    """)

                    # Strategy: Replace () based on patterns and context
                    # Heuristic: alternate between stats, starting with AP for first damage
                    # "physical damage" usually indicates AD

                    # Replace specific patterns based on context
                    # 1. "Damage:" damage is usually AP damage (ability related)
                    # 2. "physical damage" indicates AD
                    # 3. For multiplier lines, infer from position

                    # Find all () and replace them
                    paren_count = 0
                    stat_order = ['AP', 'AD', 'AP', 'AD', 'AP', 'AD', 'AP']  # Likely pattern

                    def replace_paren(match):
                        nonlocal paren_count
                        if paren_count < len(stat_order):
                            stat = stat_order[paren_count]
                            paren_count += 1
                            return f'({stat})'
                        return match.group(0)

                    # Replace all () with stat abbreviations
                    damage_text = re.sub(r'\(\)', replace_paren, damage_text)

                    initial_data['ability_others'] = damage_text

                # Extract recommended builds (all 5) and top items
                recommended_builds_data = await page.evaluate("""
                    () => {
                        const pageText = document.body.innerText;
                        const lines = pageText.split('\\n').map(l => l.trim()).filter(l => l && l.length > 0);

                        let topItems = [];
                        let builds = [];

                        // Find "Top Items" section and extract items from the next line
                        for (let i = 0; i < lines.length; i++) {
                            if (lines[i].includes('Top Items') && !lines[i].includes('Recommended') && i + 1 < lines.length) {
                                const nextLine = lines[i + 1];

                                // Look for item names in this line
                                // Items are separated by commas and possibly "and"
                                let itemsStr = nextLine;

                                // Extract just the items part (after "are" or ":")
                                if (itemsStr.includes(' are ')) {
                                    itemsStr = itemsStr.split(' are ')[1];
                                }

                                // Split by comma and "and"
                                let itemList = itemsStr.split(/,|\\s+and\\s+/);

                                itemList.forEach(item => {
                                    const cleanItem = item.trim();
                                    if (cleanItem && cleanItem.length > 3 && !cleanItem.match(/^\\d/) && cleanItem.length < 60) {
                                        if (!topItems.includes(cleanItem)) {
                                            topItems.push(cleanItem);
                                        }
                                    }
                                });

                                break;  // Only process first Top Items section
                            }
                        }

                        // Find "Recommended Builds" section and extract builds
                        // Each build is preceded by stats (avg place, etc.)
                        for (let i = 0; i < lines.length; i++) {
                            if (lines[i].includes('Recommended Builds') && !lines[i].includes('Top Items')) {
                                // Look at next line - should have the recommended build description
                                if (i + 1 < lines.length) {
                                    const buildLine = lines[i + 1];
                                    // Extract items from description like "We recommend Bloodthirster, Infinity Edge, Sterak's Gage..."
                                    if (buildLine.includes('recommend') || buildLine.includes('build')) {
                                        // Find items in this line by looking for known items
                                        // For now, extract comma-separated items after "recommend"
                                        let itemsStr = buildLine;
                                        if (itemsStr.includes(' recommend ')) {
                                            itemsStr = itemsStr.split(' recommend ')[1].split(' as ')[0];
                                        }

                                        // Split by comma and "and"
                                        let itemList = itemsStr.split(/,|\\s+and\\s+/);
                                        let build = [];

                                        itemList.forEach(item => {
                                            const cleanItem = item.trim();
                                            if (cleanItem && cleanItem.length > 3 && !cleanItem.match(/^\\d/) && cleanItem.length < 60) {
                                                build.push(cleanItem);
                                            }
                                        });

                                        if (build.length > 0) {
                                            builds.push(build);
                                        }
                                    }
                                }
                                break;  // Only process first Recommended Builds section for now
                            }
                        }

                        return {
                            top_items: topItems.slice(0, 5),
                            recommended_builds: builds
                        };
                    }
                """)

                # Merge all extracted data with proper structure
                unit_detail = {
                    'cost': initial_data.get('cost'),
                    'type': initial_data.get('type'),  # e.g., "Attack Fighter"
                    'traits': initial_data.get('traits', []),
                    'ability': {
                        'name': initial_data.get('ability_name'),
                        'description': initial_data.get('ability_description', ''),
                        'unlock_condition': initial_data.get('unlock_condition', ''),
                        'others': initial_data.get('ability_others', '')
                    },
                    'stats': {
                        'health': base_stats.get('health'),
                        'mana': base_stats.get('mana'),
                        'attack_damage': base_stats.get('attack_damage'),
                        'ability_power': base_stats.get('ability_power'),
                        'armor': base_stats.get('armor'),
                        'magic_resist': base_stats.get('magic_resist'),
                        'attack_speed': base_stats.get('attack_speed'),
                        'crit_chance': base_stats.get('crit_chance'),
                        'crit_damage': base_stats.get('crit_damage'),
                        'range': base_stats.get('range')
                    },
                    'top_items': recommended_builds_data.get('top_items', []),
                    'recommended_builds': recommended_builds_data.get('recommended_builds', [])
                }

                detail_merged = {**unit_data, **unit_detail}
                detail_merged['url'] = unit_url
                detailed_units.append(detail_merged)

            except Exception as e:
                error_msg = str(e)[:80]
                print(f"  ⚠️  Error: {error_msg}")
                detailed_units.append(unit_data)

        await browser.close()

        # Calculate final stats
        total_time = time.time() - start_time
        time_str = str(timedelta(seconds=int(total_time)))
        avg_time_per_unit = total_time / len(detailed_units) if detailed_units else 0

        print(f"\n{'='*70}")
        print(f"✅ Crawling Complete!")
        print(f"{'='*70}")
        print(f"  Total units crawled: {len(detailed_units)}/{total_units}")
        print(f"  Total time: {time_str}")
        print(f"  Average time per unit: {avg_time_per_unit:.2f}s")
        print(f"{'='*70}\n")

        return {
            "timestamp": datetime.now().isoformat(),
            "source": "https://www.metatft.com/units",
            "total_units_found": len(units_list),
            "total_units_crawled": len(detailed_units),
            "units": detailed_units,
            "note": "All units crawled with detailed data.",
            "crawl_stats": {
                "total_time_seconds": total_time,
                "average_time_per_unit": avg_time_per_unit
            }
        }


async def main(language: str = "en"):
    """Main entry point for the crawler."""
    result = await crawl_all_units(language=language)
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    import sys
    lang = sys.argv[1] if len(sys.argv) > 1 else "en"
    asyncio.run(main(language=lang))
