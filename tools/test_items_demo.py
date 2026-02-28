#!/usr/bin/env python3
"""
Test script to crawl and export limited items (demo/testing purposes)
Usage: python test_items_demo.py [items_count] [language]
Example: python test_items_demo.py 5 en
"""

import asyncio
import json
import sys
from pathlib import Path

# Add src to path (go up one level to project root)
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from metatft_crawler.crawlers.items import crawl_all_items


async def crawl_demo(items_count: int = 5, language: str = "en"):
    """
    Crawl items and limit output to specified count for demo/testing.

    Args:
        items_count: Number of items to include in demo output
        language: Language code ('en' or 'vi')

    Returns:
        Tuple of (json_file_path, result_dict)
    """
    print(f"\n{'='*70}")
    print(f"🚀 MetaTFT Items Crawler - Demo Mode ({items_count} items)")
    print(f"{'='*70}\n")

    try:
        # Run the crawler with limit
        print(f"Crawling {items_count} items (language: {language})...\n")
        result = await crawl_all_items(language=language, limit_items=items_count)

        # Create output directory (in project root)
        output_dir = Path(__file__).parent.parent / "demo_output"
        output_dir.mkdir(exist_ok=True)

        # Generate JSON file
        json_file = output_dir / f"items_demo_{items_count}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        # Print summary
        print(f"\n{'='*70}")
        print(f"✅ Demo Crawl Complete!")
        print(f"{'='*70}")
        print(f"  Items crawled: {result['total_items_crawled']}/{result['total_items_found']}")
        print(f"  Language: {language}")
        print(f"\n📂 Output Files:")
        print(f"  JSON: {json_file}")
        print(f"\n📊 File Size:")
        print(f"  JSON: {json_file.stat().st_size:,} bytes")
        print(f"\n📋 Items Crawled:")
        for i, item in enumerate(result['items'], 1):
            print(f"  {i:2d}. {item['name']:<30s}", end="")
            if item.get('traitNumber'):
                print(f" | Trait: {item['traitNumber']}", end="")
            if item.get('stats'):
                stats_str = ', '.join([f"{k}: {v}" for k, v in item['stats'].items()])
                print(f" | Stats: {stats_str}", end="")
            print()
            if item.get('description'):
                desc = item['description'][:60] + "..." if len(item['description']) > 60 else item['description']
                print(f"      Description: {desc}")

        print(f"{'='*70}\n")

        return json_file, result

    except Exception as e:
        print(f"\n❌ Error during crawl: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def main():
    """Main entry point."""
    # Parse arguments
    items_count = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    language = sys.argv[2].lower() if len(sys.argv) > 2 else "en"

    # Validate inputs
    if items_count < 1:
        print("Error: items_count must be >= 1")
        sys.exit(1)

    if language not in ["en", "vi"]:
        print("Error: language must be 'en' or 'vi'")
        sys.exit(1)

    # Run crawler
    json_file, result = asyncio.run(crawl_demo(items_count, language))

    if json_file and result:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
