#!/usr/bin/env python3
"""
Check for null/empty fields in crawled units JSON
"""

import json
import sys
import os
from pathlib import Path

# Find the latest demo_vietnamese_units JSON file
demo_dir = Path("/home/albertphan/Projects/metatft-crawler/demo_output")
json_files = sorted(demo_dir.glob("demo_vietnamese_units_*.json"), reverse=True)

if not json_files:
    print("No Vietnamese demo output files found")
    sys.exit(1)

latest_json = json_files[0]
print(f"Analyzing: {latest_json.name}\n")

with open(latest_json) as f:
    data = json.load(f)

print("=" * 100)
print("CHECKING FOR NULL/EMPTY FIELDS IN VIETNAMESE UNITS")
print("=" * 100)

null_counts = {
    'cost': 0,
    'type': 0,
    'traits': 0,
    'ability_name': 0,
    'ability_description': 0,
    'ability_mana': 0,
    'health': 0,
    'attack_damage': 0,
    'armor': 0,
}

for i, unit in enumerate(data, 1):
    issues = []

    if not unit.get('cost'):
        issues.append('cost=None')
        null_counts['cost'] += 1

    if not unit.get('type'):
        issues.append('type=None')
        null_counts['type'] += 1

    if not unit.get('traits') or len(unit.get('traits', [])) == 0:
        issues.append('traits=[]')
        null_counts['traits'] += 1

    ability = unit.get('ability', {})
    if not ability.get('name'):
        issues.append('ability.name=None')
        null_counts['ability_name'] += 1

    if not ability.get('description') or ability.get('description') == '':
        issues.append('ability.description=""')
        null_counts['ability_description'] += 1

    if not ability.get('mana') or ability.get('mana') == '':
        issues.append('ability.mana=""')
        null_counts['ability_mana'] += 1

    stats = unit.get('stats', {})
    if not stats.get('health'):
        issues.append('stats.health=None')
        null_counts['health'] += 1

    if not stats.get('attack_damage'):
        issues.append('stats.attack_damage=None')
        null_counts['attack_damage'] += 1

    if not stats.get('armor'):
        issues.append('stats.armor=None')
        null_counts['armor'] += 1

    if issues:
        print(f"\nUnit {i}: {unit['name']}")
        for issue in issues:
            print(f"  ❌ {issue}")

print("\n" + "=" * 100)
print("SUMMARY")
print("=" * 100)
total_issues = sum(null_counts.values())
if total_issues == 0:
    print("✅ NO NULL/EMPTY FIELDS FOUND!")
else:
    print(f"Total null/empty fields: {total_issues}")
    for field, count in null_counts.items():
        if count > 0:
            print(f"  {field}: {count} units")

print(f"\n✅ All base stats extracted: {sum(1 for u in data if u.get('stats', {}).get('health'))}/{len(data)} units")
