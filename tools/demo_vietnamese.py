#!/usr/bin/env python3
"""
Demo: Crawl 10 units in Vietnamese and display results
Saves output to demo_output folder
"""

import asyncio
import json
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.metatft_crawler import crawl_all_units


def ensure_demo_output_dir():
    """Create demo_output directory if it doesn't exist."""
    demo_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "demo_output")
    os.makedirs(demo_dir, exist_ok=True)
    return demo_dir


async def demo_vietnamese():
    """Crawl 10 units in Vietnamese and display formatted results."""

    print("=" * 100)
    print("MetaTFT CRAWLER - DEMO TIẾNG VIỆT (Vietnamese Demo)")
    print("=" * 100)
    print("\n🌍 Crawling 10 units in Vietnamese from metatft.com/units...")
    print("-" * 100)

    # Crawl 10 units in Vietnamese
    result = await crawl_all_units(language="vi", limit_units=10)
    units = result.get("units", [])

    print(f"\n✅ Successfully crawled {len(units)} units!\n")

    # Display each unit
    for i, unit in enumerate(units, 1):
        print(f"\n{'='*100}")
        print(f"Unit #{i}: {unit['name']}")
        print("=" * 100)

        # Basic info
        print(f"\n📊 Basic Information:")
        print(f"  • Cost (Giá):          {unit.get('cost', 'N/A')}")
        print(f"  • Type (Loại):         {unit.get('type', 'N/A')}")
        print(f"  • Traits (Đặc Tính):   {', '.join(unit.get('traits', []))}")

        # Ability info
        ability = unit.get("ability", {})
        if ability:
            print(f"\n🎯 Ability (Kỹ Năng):")
            print(f"  • Name (Tên):          {ability.get('name', 'N/A')}")
            if ability.get("mana"):
                print(f"  • Mana Cost (Chi Phí): {ability.get('mana', 'N/A')}")
            if ability.get("description"):
                desc = ability.get("description", "")[:150]
                print(f"  • Description (Mô Tả): {desc}...")

        # Stats
        stats = unit.get("stats", {})
        if stats:
            print(f"\n⚔️  Base Stats (Chỉ Số Cơ Bản):")
            stat_display = []
            if stats.get("health"):
                stat_display.append(f"HP: {stats.get('health')}")
            if stats.get("attack_damage"):
                stat_display.append(f"AD: {stats.get('attack_damage')}")
            if stats.get("ability_power"):
                stat_display.append(f"AP: {stats.get('ability_power')}")
            if stats.get("armor"):
                stat_display.append(f"Armor: {stats.get('armor')}")
            if stats.get("magic_resist"):
                stat_display.append(f"MR: {stats.get('magic_resist')}")

            for stat in stat_display:
                print(f"  • {stat}")

        # Items
        top_items = unit.get("top_items", [])
        if top_items:
            print(f"\n🎁 Top Items (Trang Bị Hàng Đầu):")
            for j, item in enumerate(top_items, 1):
                print(f"  {j}. {item}")

        # Recommended Builds
        builds = unit.get("recommended_builds", [])
        if builds:
            print(f"\n🛠️  Recommended Builds (Bản Dựng Được Khuyến Nghị):")
            for j, build in enumerate(builds, 1):
                if isinstance(build, list):
                    build_str = " + ".join(build)
                else:
                    build_str = str(build)
                print(f"  {j}. {build_str}")

        print()

    # Summary statistics
    print("\n" + "=" * 100)
    print("📈 SUMMARY STATISTICS (THỐNG KÊ TỔNG HỢP)")
    print("=" * 100)

    total_traits = sum(len(u.get("traits", [])) for u in units)
    total_items = sum(len(u.get("top_items", [])) for u in units)
    total_builds = sum(len(u.get("recommended_builds", [])) for u in units)

    print(f"\n  • Total Units Crawled: {len(units)}")
    print(f"  • Total Traits Found: {total_traits}")
    print(f"  • Total Top Items: {total_items}")
    print(f"  • Total Recommended Builds: {total_builds}")
    print(f"  • Average Top Items per Unit: {total_items / len(units):.1f}")

    # Cost distribution
    cost_distribution = {}
    for unit in units:
        cost = unit.get("cost")
        if cost:
            cost_distribution[cost] = cost_distribution.get(cost, 0) + 1

    if cost_distribution:
        print(f"\n  Cost Distribution (Phân Bố Giá):")
        for cost in sorted(cost_distribution.keys()):
            count = cost_distribution[cost]
            bar = "█" * count
            print(f"    Cost {cost}: {bar} ({count} units)")

    print("\n" + "=" * 100)
    print("✅ DEMO COMPLETE! (HOÀN THÀNH!)")
    print("=" * 100 + "\n")


if __name__ == "__main__":
    # Ensure demo_output directory exists
    demo_dir = ensure_demo_output_dir()

    # Open file for output
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(demo_dir, f"demo_vietnamese_{timestamp}.txt")

    # Redirect stdout to both console and file
    import io

    class Tee:
        def __init__(self, *files):
            self.files = files

        def write(self, data):
            for f in self.files:
                f.write(data)
                f.flush()

        def flush(self):
            for f in self.files:
                f.flush()

    with open(output_file, 'w', encoding='utf-8') as f:
        sys.stdout = Tee(sys.stdout, f)
        asyncio.run(demo_vietnamese())

    # Restore stdout
    sys.stdout = sys.__stdout__

    # Also save JSON data
    result = asyncio.run(crawl_all_units(language="vi", limit_units=10))
    json_file = os.path.join(demo_dir, f"demo_vietnamese_units_{timestamp}.json")
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(result.get("units", []), f, indent=2, ensure_ascii=False)

    print(f"\n✅ Demo outputs saved to demo_output folder:")
    print(f"  📄 Text report: {output_file}")
    print(f"  📊 JSON data:   {json_file}")
