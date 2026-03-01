#!/usr/bin/env python3
"""
Debug stats extraction during actual crawl
"""

import asyncio
import sys
import os
from playwright.async_api import async_playwright

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.metatft_crawler.utils.browser import switch_language
from src.metatft_crawler.languages.loader import get_language_config


async def debug_crawl_stats():
    """Debug stats extraction on a single unit during crawl."""

    lang_config = get_language_config("vi")

    print("=" * 100)
    print("DEBUG: Stats Extraction During Crawl")
    print("=" * 100)
    print(f"\nLanguage Config:")
    print(f"  health: {lang_config.health}")
    print(f"  mana: {lang_config.mana}")
    print(f"  attack_damage: {lang_config.attack_damage}")
    print(f"  ability_power: {lang_config.ability_power}")
    print(f"  armor: {lang_config.armor}")
    print(f"  magic_resist: {lang_config.magic_resist}")

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # Navigate to a unit
        print("\nNavigating to Baron Nashor (Vietnamese)...")
        await page.goto("https://www.metatft.com/units/BaronNashor", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(2000)

        # Switch to Vietnamese
        await switch_language(page, "vi")
        await page.wait_for_timeout(2000)

        # Try to click Stats button
        print("\nLooking for Stats button...")
        stats_button = await page.query_selector("button:has-text('Stats')")
        if not stats_button:
            # Try Vietnamese label
            buttons = await page.query_selector_all("button")
            for btn in buttons:
                text = await btn.text_content()
                print(f"  Found button: {text}")
                if text and ("Stats" in text or "Số Liệu" in text):
                    stats_button = btn
                    print(f"  ✅ Found Stats button: {text}")
                    break

        if stats_button:
            print("Clicking Stats button...")
            await stats_button.click()
            await page.wait_for_timeout(1000)

            # Extract using the same JavaScript as the crawl
            print("\n" + "=" * 100)
            print("Extracting stats using crawl JavaScript")
            print("=" * 100)

            base_stats = await page.evaluate("""
                (langConfig) => {
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

                    console.log("DEBUG: Looking for stat labels:");
                    console.log("  health:", langConfig.health);
                    console.log("  mana:", langConfig.mana);
                    console.log("  attack_damage:", langConfig.attack_damage);
                    console.log("  ability_power:", langConfig.ability_power);
                    console.log("  armor:", langConfig.armor);
                    console.log("  magic_resist:", langConfig.magic_resist);

                    console.log("DEBUG: Total lines on page:", lines.length);

                    // Look for stat labels and their values (language-aware)
                    for (let i = 0; i < lines.length; i++) {
                        const line = lines[i];

                        // Health: "3000/5400/9720" format
                        if (line === langConfig.health && i + 1 < lines.length) {
                            console.log(`DEBUG: Found health at line ${i}: "${line}"`);
                            stats.health = lines[i + 1];
                        }
                        // Mana
                        if (line === langConfig.mana && i + 1 < lines.length) {
                            console.log(`DEBUG: Found mana at line ${i}: "${line}"`);
                            stats.mana = lines[i + 1];
                        }
                        // Attack Damage
                        if (line.includes(langConfig.attack_damage) && i + 1 < lines.length) {
                            console.log(`DEBUG: Found attack_damage at line ${i}: "${line}"`);
                            stats.attack_damage = lines[i + 1];
                        }
                        // Ability Power
                        if (line === langConfig.ability_power && i + 1 < lines.length) {
                            console.log(`DEBUG: Found ability_power at line ${i}: "${line}"`);
                            stats.ability_power = lines[i + 1];
                        }
                        // Armor
                        if (line === langConfig.armor && i + 1 < lines.length) {
                            console.log(`DEBUG: Found armor at line ${i}: "${line}"`);
                            stats.armor = lines[i + 1];
                        }
                        // Magic Resist
                        if (line.includes(langConfig.magic_resist) && i + 1 < lines.length) {
                            console.log(`DEBUG: Found magic_resist at line ${i}: "${line}"`);
                            stats.magic_resist = lines[i + 1];
                        }
                    }

                    return stats;
                }
            """, {
                'health': lang_config.health,
                'mana': lang_config.mana,
                'attack_damage': lang_config.attack_damage,
                'ability_power': lang_config.ability_power,
                'armor': lang_config.armor,
                'magic_resist': lang_config.magic_resist,
                'attack_speed': lang_config.attack_speed,
                'crit_chance': lang_config.crit_chance,
                'crit_damage': lang_config.crit_damage,
                'range': lang_config.range,
            })

            print("\n" + "=" * 100)
            print("Results:")
            print("=" * 100)
            print(f"  health: {base_stats.get('health')}")
            print(f"  mana: {base_stats.get('mana')}")
            print(f"  attack_damage: {base_stats.get('attack_damage')}")
            print(f"  ability_power: {base_stats.get('ability_power')}")
            print(f"  armor: {base_stats.get('armor')}")
            print(f"  magic_resist: {base_stats.get('magic_resist')}")

        else:
            print("❌ Stats button not found!")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(debug_crawl_stats())
