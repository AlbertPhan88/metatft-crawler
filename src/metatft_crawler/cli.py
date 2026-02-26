#!/usr/bin/env python3
"""
CLI interface for MetaTFT Crawler
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Optional

from .crawlers.comps import crawl_tft_meta
from .crawlers.units import crawl_all_units


def print_help():
    """Print help message."""
    help_text = """
MetaTFT Crawler - Extract competitive TFT meta data

Usage:
  python -m metatft_crawler comps [OPTIONS]     Crawl comps from MetaTFT.com
  python -m metatft_crawler units [OPTIONS]     Crawl units from MetaTFT.com
  python -m metatft_crawler --help              Show this help message

Options:
  -l, --language LANG     Target language (en, vi) [default: en]
  -o, --output FILE       Output JSON file path [default: stdout]
  -v, --verbose           Enable verbose output
  -h, --help             Show this help message

Examples:
  # Crawl English comps data
  python -m metatft_crawler comps

  # Crawl Vietnamese units data and save to file
  python -m metatft_crawler units -l vi -o units.json

  # Crawl comps with verbose output
  python -m metatft_crawler comps -v
"""
    print(help_text)


async def run_comps(language: str = "en", output: Optional[str] = None, verbose: bool = False):
    """Run comps crawler."""
    if verbose:
        print(f"[INFO] Starting comps crawler (language={language})")

    result = await crawl_tft_meta(language=language)

    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        if verbose:
            print(f"[INFO] Results saved to {output_path}")
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))

    return result


async def run_units(language: str = "en", output: Optional[str] = None, verbose: bool = False):
    """Run units crawler."""
    if verbose:
        print(f"[INFO] Starting units crawler (language={language})")

    result = await crawl_all_units(language=language)

    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        if verbose:
            print(f"[INFO] Results saved to {output_path}")
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))

    return result


def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        print_help()
        sys.exit(1)

    command = sys.argv[1].lower()
    language = "en"
    output = None
    verbose = False

    # Parse arguments
    i = 2
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg in ['-h', '--help']:
            print_help()
            sys.exit(0)
        elif arg in ['-l', '--language']:
            if i + 1 < len(sys.argv):
                language = sys.argv[i + 1]
                i += 2
            else:
                print("Error: --language requires a value")
                sys.exit(1)
        elif arg in ['-o', '--output']:
            if i + 1 < len(sys.argv):
                output = sys.argv[i + 1]
                i += 2
            else:
                print("Error: --output requires a value")
                sys.exit(1)
        elif arg in ['-v', '--verbose']:
            verbose = True
            i += 1
        else:
            print(f"Error: Unknown option {arg}")
            sys.exit(1)

    # Run command
    if command == 'comps':
        asyncio.run(run_comps(language=language, output=output, verbose=verbose))
    elif command == 'units':
        asyncio.run(run_units(language=language, output=output, verbose=verbose))
    else:
        print(f"Error: Unknown command '{command}'")
        print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
