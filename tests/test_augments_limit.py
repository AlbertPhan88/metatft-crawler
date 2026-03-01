#!/usr/bin/env python3
"""
Test for augments crawler with limit parameter
"""

import asyncio
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from metatft_crawler.crawlers.augments import crawl_all_augments


async def test_augments_limit_10():
    """Test crawling exactly 10 augments"""
    print("Testing augments crawler with limit_augments=10...")

    result = await crawl_all_augments(language="en", limit_augments=10)

    # Validate result structure
    assert "timestamp" in result, "Missing timestamp"
    assert "source" in result, "Missing source"
    assert "total_augments" in result, "Missing total_augments"
    assert "augments" in result, "Missing augments list"

    # Validate augment count
    assert result["total_augments"] == 10, f"Expected 10 augments, got {result['total_augments']}"
    assert len(result["augments"]) == 10, f"Expected 10 items in list, got {len(result['augments'])}"

    # Validate augment structure
    for aug in result["augments"]:
        assert "name" in aug, "Augment missing name"
        assert "tier" in aug, "Augment missing tier"
        assert "type" in aug, "Augment missing type"
        assert "description" in aug, "Augment missing description"
        assert aug["tier"] in ["S", "A", "B", "C", "D"], f"Invalid tier: {aug['tier']}"
        assert len(aug["name"]) > 0, "Augment name is empty"

    print(f"✓ Test passed! Retrieved {result['total_augments']} augments")
    print(f"\nDemo output (10 augments):")
    print(json.dumps(result, indent=2))

    return result


async def test_augments_all():
    """Test crawling all augments (no limit)"""
    print("Testing augments crawler without limit...")

    result = await crawl_all_augments(language="en", limit_augments=None)

    assert result["total_augments"] > 10, "Should find more than 10 augments when no limit"
    print(f"✓ Test passed! Retrieved {result['total_augments']} augments")

    return result


async def main():
    """Run all tests"""
    print("=" * 60)
    print("Running Augments Crawler Tests")
    print("=" * 60)
    print()

    try:
        # Test with limit
        result_limit = await test_augments_limit_10()
        print()
        print("=" * 60)
        print()

        # Test without limit
        result_all = await test_augments_all()
        print()
        print("=" * 60)
        print("All tests passed!")

    except AssertionError as e:
        print(f"✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
