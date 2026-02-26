"""
CSV export utilities for MetaTFT crawlers
"""

import csv
from typing import Dict, List, Any


def _flatten_list(items: Any, separator: str = ",") -> str:
    """Convert a list to a comma-separated string."""
    if not items:
        return ""
    if isinstance(items, list):
        return separator.join(str(item) for item in items)
    return str(items)


def units_to_csv(units_data: Dict[str, Any]) -> List[List[str]]:
    """
    Convert units JSON data to CSV format.

    Args:
        units_data: Dictionary containing 'units' key with list of unit objects

    Returns:
        List of rows where first row is headers, subsequent rows are data
    """

    headers = [
        "name",
        "tier",
        "url",
        "avg_placement",
        "win_rate_percent",
        "pick_count",
        "frequency_percent",
        "recommended_build",
        "top_items",
        "positioning",
        "traits",
        "stats_avg_placement",
        "stats_pick_rate",
    ]

    rows = [headers]

    units = units_data.get("units", [])
    for unit in units:
        row = [
            unit.get("name", ""),
            unit.get("tier", ""),
            unit.get("url", ""),
            str(unit.get("avg_placement", "")),
            str(unit.get("win_rate_percent", "")),
            str(unit.get("pick_count", "")),
            str(unit.get("frequency_percent", "")),
            _flatten_list(unit.get("recommended_build", [])),
            _flatten_list(unit.get("top_items", [])),
            unit.get("positioning", ""),
            _flatten_list(unit.get("traits", [])),
            str(unit.get("stats", {}).get("avg_placement", "")),
            str(unit.get("stats", {}).get("pick_rate", "")),
        ]
        rows.append(row)

    return rows
