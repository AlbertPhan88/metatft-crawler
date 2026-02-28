#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright

async def inspect_damage():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.goto("https://www.metatft.com/units/BaronNashor", wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)

        text = await page.evaluate("() => document.body.innerText")
        lines = text.split('\n')

        # Find Passive/Active and show everything until Unlock
        print("=== Ability Section (Passive -> Unlock) ===\n")
        in_ability = False
        for i, line in enumerate(lines):
            if 'Passive:' in line or 'Active:' in line:
                in_ability = True

            if in_ability:
                print(f"{i:3d}: {line}")

                if 'Unlock:' in line:
                    # Show a few more lines
                    for j in range(i+1, min(i+4, len(lines))):
                        print(f"{j:3d}: {lines[j]}")
                    break

        await browser.close()

asyncio.run(inspect_damage())
