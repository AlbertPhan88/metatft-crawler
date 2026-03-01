#!/usr/bin/env python3
"""
Compare units crawling in English vs Vietnamese to find gaps.
Tests with 10 units and compares the outputs side-by-side.
"""

import asyncio
import json
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.metatft_crawler import crawl_all_units


async def compare_languages():
    """Crawl 10 units in both languages and compare outputs."""

    print("=" * 80)
    print("LANGUAGE COMPARISON TEST - 10 Units (English vs Vietnamese)")
    print("=" * 80)

    # Crawl in English
    print("\n[1/2] Crawling 10 units in English...")
    en_result = await crawl_all_units(language="en", limit_units=10)
    en_units = en_result.get("units", [])
    print(f"✓ Crawled {len(en_units)} English units")

    # Crawl in Vietnamese
    print("\n[2/2] Crawling 10 units in Vietnamese...")
    vi_result = await crawl_all_units(language="vi", limit_units=10)
    vi_units = vi_result.get("units", [])
    print(f"✓ Crawled {len(vi_units)} Vietnamese units")

    # Save results for inspection
    with open("/tmp/en_units.json", "w") as f:
        json.dump(en_units, f, indent=2, ensure_ascii=False)
    with open("/tmp/vi_units.json", "w") as f:
        json.dump(vi_units, f, indent=2, ensure_ascii=False)
    print(f"\n✓ Saved outputs to /tmp/en_units.json and /tmp/vi_units.json")

    # Compare structures
    print("\n" + "=" * 80)
    print("COMPARISON ANALYSIS")
    print("=" * 80)

    if len(en_units) == 0 or len(vi_units) == 0:
        print("⚠️  No units crawled - cannot compare")
        return

    # Get first unit from each
    en_first = en_units[0] if en_units else {}
    vi_first = vi_units[0] if vi_units else {}

    print(f"\nFirst English unit: {en_first.get('name', 'Unknown')}")
    print(f"First Vietnamese unit: {vi_first.get('name', 'Unknown')}")

    # Compare structure
    en_keys = set(en_first.keys()) if en_first else set()
    vi_keys = set(vi_first.keys()) if vi_first else set()

    print(f"\n📊 English unit keys ({len(en_keys)}): {sorted(en_keys)}")
    print(f"📊 Vietnamese unit keys ({len(vi_keys)}): {sorted(vi_keys)}")

    # Find differences
    missing_in_vi = en_keys - vi_keys
    missing_in_en = vi_keys - en_keys

    if missing_in_vi:
        print(f"\n⚠️  MISSING IN VIETNAMESE: {missing_in_vi}")
    if missing_in_en:
        print(f"\n⚠️  MISSING IN ENGLISH: {missing_in_en}")

    if not missing_in_vi and not missing_in_en:
        print(f"\n✅ Structure is identical between languages")

    # Deep comparison - check field values
    print("\n" + "=" * 80)
    print("FIELD VALUE COMPARISON (First Unit)")
    print("=" * 80)

    all_keys = en_keys | vi_keys
    gaps = []

    for key in sorted(all_keys):
        en_value = en_first.get(key)
        vi_value = vi_first.get(key)

        # Special handling for nested objects and lists
        if isinstance(en_value, (dict, list)) or isinstance(vi_value, (dict, list)):
            if en_value and not vi_value:
                print(f"\n❌ {key}: Present in EN but MISSING in VI")
                print(f"   EN: {type(en_value).__name__}")
                print(f"   VI: {type(vi_value).__name__}")
                gaps.append((key, "missing_in_vi", en_value, vi_value))
            elif vi_value and not en_value:
                print(f"\n❌ {key}: Present in VI but MISSING in EN")
                print(f"   EN: {type(en_value).__name__}")
                print(f"   VI: {type(vi_value).__name__}")
                gaps.append((key, "missing_in_en", en_value, vi_value))
            elif not en_value and not vi_value:
                print(f"\n✅ {key}: Both empty (OK)")
            elif isinstance(en_value, dict) and isinstance(vi_value, dict):
                # Check nested dict keys
                en_dict_keys = set(en_value.keys())
                vi_dict_keys = set(vi_value.keys())
                if en_dict_keys != vi_dict_keys:
                    print(f"\n⚠️  {key} (dict): Key mismatch")
                    print(f"   EN keys: {sorted(en_dict_keys)}")
                    print(f"   VI keys: {sorted(vi_dict_keys)}")
                    if en_dict_keys - vi_dict_keys:
                        print(f"   Missing in VI: {en_dict_keys - vi_dict_keys}")
                        gaps.append((key, "dict_keys_mismatch", en_value, vi_value))
                    if vi_dict_keys - en_dict_keys:
                        print(f"   Missing in EN: {vi_dict_keys - en_dict_keys}")
                else:
                    print(f"\n✅ {key} (dict): Keys match")
            elif isinstance(en_value, list) and isinstance(vi_value, list):
                print(f"\n✅ {key} (list): EN={len(en_value)}, VI={len(vi_value)}")
                if len(en_value) != len(vi_value):
                    print(f"   ⚠️  Length mismatch!")
                    gaps.append((key, "list_length_mismatch", en_value, vi_value))
        else:
            # String/number comparison
            if en_value == vi_value:
                print(f"\n✅ {key}: {en_value}")
            elif en_value and vi_value:
                print(f"\n⚠️  {key}: Different values (expected for translations)")
                print(f"   EN: {en_value}")
                print(f"   VI: {vi_value}")
            elif en_value and not vi_value:
                print(f"\n❌ {key}: Has value in EN but EMPTY in VI")
                print(f"   EN: {en_value}")
                print(f"   VI: {vi_value}")
                gaps.append((key, "empty_in_vi", en_value, vi_value))
            else:
                print(f"\n❌ {key}: Has value in VI but EMPTY in EN")
                print(f"   EN: {en_value}")
                print(f"   VI: {vi_value}")
                gaps.append((key, "empty_in_en", en_value, vi_value))

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"\nTotal units crawled (English): {len(en_units)}")
    print(f"Total units crawled (Vietnamese): {len(vi_units)}")
    print(f"Total gaps found: {len(gaps)}")

    if gaps:
        print(f"\n🔴 GAPS DETECTED:")
        for key, gap_type, en_val, vi_val in gaps:
            print(f"\n  • {key} ({gap_type})")
            if gap_type == "empty_in_vi":
                print(f"    EN has: {en_val}")
                print(f"    VI has: {vi_val}")
            elif gap_type == "missing_in_vi":
                print(f"    Field is missing in Vietnamese output")
            elif gap_type == "dict_keys_mismatch":
                en_keys = set(en_val.keys()) if isinstance(en_val, dict) else set()
                vi_keys = set(vi_val.keys()) if isinstance(vi_val, dict) else set()
                print(f"    EN dict keys: {sorted(en_keys)}")
                print(f"    VI dict keys: {sorted(vi_keys)}")
    else:
        print(f"\n✅ NO GAPS FOUND - Both languages produce identical structures!")

    return gaps


if __name__ == "__main__":
    gaps = asyncio.run(compare_languages())
    sys.exit(0 if not gaps else 1)
