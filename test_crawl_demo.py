#!/usr/bin/env python3
"""
Test script to crawl and export limited units (demo/testing purposes)
Usage: python test_crawl_demo.py [units_count] [language]
Example: python test_crawl_demo.py 10 en
"""

import asyncio
import json
import csv
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from metatft_crawler.crawlers.units import crawl_all_units
from metatft_crawler.utils.csv_export import units_to_csv


async def crawl_demo(units_count: int = 10, language: str = "en"):
    """
    Crawl units and limit output to specified count for demo/testing.

    Args:
        units_count: Number of units to include in demo output
        language: Language code ('en' or 'vi')

    Returns:
        Tuple of (json_file_path, csv_file_path, result_dict)
    """
    print(f"\n{'='*70}")
    print(f"🚀 MetaTFT Units Crawler - Demo Mode ({units_count} units)")
    print(f"{'='*70}\n")

    try:
        # Run the crawler with limit
        print(f"Crawling {units_count} units (language: {language})...\n")
        result = await crawl_all_units(language=language, limit_units=units_count)

        # Result already limited by crawler
        demo_result = {
            **result,
            "note": f"Demo: {units_count} units crawled with enhanced data extraction"
        }

        # Create output directory
        output_dir = Path(__file__).parent / "demo_output"
        output_dir.mkdir(exist_ok=True)

        # Generate JSON file
        json_file = output_dir / f"units_demo_{units_count}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(demo_result, f, indent=2, ensure_ascii=False)

        # Generate CSV file
        csv_file = output_dir / f"units_demo_{units_count}.csv"
        rows = units_to_csv(demo_result)
        with open(csv_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(rows)

        # Print summary
        print(f"\n{'='*70}")
        print(f"✅ Demo Crawl Complete!")
        print(f"{'='*70}")
        print(f"  Units crawled: {demo_result['total_units_crawled']}/{result['total_units_found']}")
        print(f"  Language: {language}")
        print(f"\n📂 Output Files:")
        print(f"  JSON: {json_file}")
        print(f"  CSV:  {csv_file}")
        print(f"\n📊 File Sizes:")
        print(f"  JSON: {json_file.stat().st_size:,} bytes")
        print(f"  CSV:  {csv_file.stat().st_size:,} bytes")
        print(f"\n📋 Units Crawled:")
        for i, unit in enumerate(demo_result['units'], 1):
            print(f"  {i:2d}. {unit['name']:<25s} | Tier: {unit.get('tier', 'Unknown'):<7s} | Traits: {', '.join(unit.get('traits', []))}")
        print(f"{'='*70}\n")

        return json_file, csv_file, demo_result

    except Exception as e:
        print(f"\n❌ Error during crawl: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None


def main():
    """Main entry point."""
    # Parse arguments
    units_count = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    language = sys.argv[2].lower() if len(sys.argv) > 2 else "en"

    # Validate inputs
    if units_count < 1:
        print("Error: units_count must be >= 1")
        sys.exit(1)

    if language not in ["en", "vi"]:
        print("Error: language must be 'en' or 'vi'")
        sys.exit(1)

    # Run crawler
    json_file, csv_file, result = asyncio.run(crawl_demo(units_count, language))

    if json_file and csv_file:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
