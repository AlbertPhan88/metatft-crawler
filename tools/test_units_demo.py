#!/usr/bin/env python3
"""
Demo script for units crawler - crawls N units and saves demo output
Usage: python3 tools/test_units_demo.py <limit> [language]
Example: python3 tools/test_units_demo.py 10 en
"""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from metatft_crawler.crawlers.units import crawl_all_units


async def run_demo(limit_units: int = 10, language: str = "en"):
    """Run units crawler demo."""
    print("=" * 70)
    print(f"🚀 MetaTFT Units Crawler - Demo Mode ({limit_units} units)")
    print("=" * 70)
    print(f"\nCrawling {limit_units} units (language: {language})...\n")

    # Crawl units with limit
    result = await crawl_all_units(language=language, limit_units=limit_units)

    # Print summary
    print(f"\n{'=' * 70}")
    print("✅ Demo Crawl Complete!")
    print("=" * 70)
    print(f"  Units crawled: {result['total_units_crawled']}/{result['total_units_found']}")
    print(f"  Language: {language}")

    # Save to demo_output
    demo_output_dir = Path(__file__).parent.parent / "demo_output"
    demo_output_dir.mkdir(exist_ok=True)

    output_file = demo_output_dir / f"units_demo_{limit_units}.json"

    # Pretty print JSON
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    file_size = output_file.stat().st_size
    print(f"\n📂 Output Files:")
    print(f"  JSON: {output_file}")
    print(f"\n📊 File Size:")
    print(f"  JSON: {file_size:,} bytes")


if __name__ == "__main__":
    limit = 10
    language = "en"

    if len(sys.argv) > 1:
        try:
            limit = int(sys.argv[1])
        except ValueError:
            print(f"Invalid limit: {sys.argv[1]}")
            sys.exit(1)

    if len(sys.argv) > 2:
        language = sys.argv[2]

    asyncio.run(run_demo(limit, language))
