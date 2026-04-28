# MetaTFT Crawler

A Python web scraper that extracts competitive Teamfight Tactics (TFT) meta data from [MetaTFT.com](https://www.metatft.com/) using Playwright (headless Chromium).

## Features

- **6 crawlers**: comps, comp-details, units, items, augments, traits
- **Detailed comp data**: units + items, level variations, augments, leveling guide, carousel priority, counters & VODs
- **Multi-language**: English (`en`) and Vietnamese (`vi`)
- **JSON output**: structured files ready for integration
- **One-command update**: `scripts/update_meta.sh` runs all crawlers and pushes to GitHub

## Pre-crawled data

Latest season data is in [`output/`](./output/):

| File | Contents |
|---|---|
| `output/comps.json` | 56 comps with stats and units |
| `output/comp_details.json` | Full detail per comp (items, boards, augments, leveling) |
| `output/units.json` | 63 units with stats, abilities, recommended builds |
| `output/items.json` | 178 items with stats |
| `output/augments.json` | 265 augments with descriptions |
| `output/traits.json` | 34 traits with descriptions |

## Installation

Requires Python 3.8+ and no system pip needed.

```bash
git clone https://github.com/AlbertPhan88/metatft-crawler.git
cd metatft-crawler
python3 -m venv .venv
.venv/bin/pip install -e .
.venv/bin/playwright install chromium
```

## Updating meta data

Run all crawlers and push to GitHub in one command:

```bash
bash scripts/update_meta.sh
```

Output files in `output/` have no date suffix so each run overwrites the previous version.

## Manual usage

```bash
# Activate venv (or prefix commands with .venv/bin/)
source .venv/bin/activate

# All crawlers support: -l en|vi, -o <file>, -f json, -n <limit>
metatft-crawler comps        -f json -o output/comps.json
metatft-crawler comp-details -f json -o output/comp_details.json
metatft-crawler units        -f json -o output/units.json
metatft-crawler items        -f json -o output/items.json
metatft-crawler augments     -f json -o output/augments.json
metatft-crawler traits       -f json -o output/traits.json

# Vietnamese output
metatft-crawler comps -l vi -f json -o output/comps_vi.json

# Limit for quick testing
metatft-crawler comp-details -n 3 -f json
```

## Output format

All crawlers return a top-level object with `timestamp`, `source`, `language`, `total_<entity>_found`, `total_<entity>_crawled`, and a list of entities.

### comps.json

```json
{
  "comps": [
    {
      "name": "Voyager Viktor",
      "tier": "S",
      "playstyle": "lvl 7",
      "difficulty": "Medium",
      "stats": {
        "avg_placement": 3.9,
        "pick_rate": 0.5,
        "win_rate": "12.6%",
        "top_4_rate": "62.4%"
      },
      "units": [
        { "name": "Viktor", "items": ["Drone Uplink", "Jeweled Gauntlet", "Rabadon's Deathcap"], "is_three_star": true },
        { "name": "Illaoi", "items": ["Bramble Vest", "Gargoyle Stoneplate", "Warmog's Armor"], "is_three_star": true }
      ]
    }
  ]
}
```

### comp_details.json

Extends comps with per-comp detail sections:

```json
{
  "comps": [
    {
      "name": "Voyager Viktor",
      "tier": "S",
      "playstyle": "lvl 7",
      "difficulty": "Medium",
      "stats": { "avg_place": 3.9, "pick_rate": 0.5, "win_rate": "12.6%", "top_4_rate": "62.4%" },
      "units": [
        { "name": "Viktor", "items": ["Drone Uplink", "Jeweled Gauntlet"], "is_three_star": true }
      ],
      "early_game_boards": [
        { "units": ["Lissandra", "Meepsie", "Mordekaiser", "Pyke", "Viktor"], "round_win_rate": "73.8%" }
      ],
      "level_variations": [
        { "level": "Lvl 7", "percentage": "24.7%", "comps": [["Viktor", "Illaoi", "Nami"]] }
      ],
      "positioning": ["Pyke", "Mordekaiser", "Illaoi", "Rhaast", "Meepsie", "Viktor", "Lissandra", "Nami"],
      "leveling_guide": [
        { "level": "Lvl 5", "timing": "3-1", "gold": null },
        { "level": "Lvl 7", "timing": "3-6", "gold": 38.7 }
      ],
      "augments": ["Firesale", "Exiles I", "Electrocharge I", "Good For Something I"],
      "carousel_priority": [
        { "component": "Needlessly Large Rod", "count": 3 }
      ],
      "counters_and_vods": {
        "synergies": [{ "name": "Vanguard Teemo", "similarity": "62%", "avg_place_delta": "-0.3" }],
        "counters": [{ "name": "Primordian Bel'Veth", "similarity": "58%", "avg_place_delta": "+0.4" }]
      }
    }
  ]
}
```

## Architecture

```
metatft-crawler/
├── scripts/
│   └── update_meta.sh      # One-command: crawl all + push to GitHub
├── output/                 # Latest crawled JSON files (committed to repo)
├── src/metatft_crawler/
│   ├── cli.py              # Argument parsing, dispatches to crawlers
│   ├── crawlers/
│   │   ├── comps.py        # /comps listing via CSS selectors
│   │   ├── comp_details.py # /comps with click-expand per comp
│   │   ├── units.py        # /units + per-unit detail pages
│   │   ├── items.py        # /items + per-item detail pages
│   │   ├── augments.py     # /augments tier list
│   │   └── traits.py       # /traits + per-trait detail pages
│   ├── languages/
│   │   ├── base.py         # LanguageConfig abstract base class
│   │   ├── en.py           # English labels
│   │   ├── vi.py           # Vietnamese labels
│   │   └── loader.py       # get_language_config(lang)
│   └── utils/
│       ├── browser.py      # switch_language() helper
│       └── csv_export.py   # CSV export for units
└── tests/
```

## How it works

1. Launches a headless Chromium browser via Playwright
2. Navigates to the target page and waits for JS rendering
3. Scrolls to trigger lazy-loaded content
4. Optionally switches language via the site's language selector
5. Runs `page.evaluate()` JS snippets to extract data from the DOM
6. Returns structured JSON

All extraction logic lives in `page.evaluate()` — Python only orchestrates navigation. Language-specific labels from `languages/en.py` or `languages/vi.py` are passed into the JS as a config dict.

## Dependencies

- [playwright](https://playwright.dev/python/) >= 1.40.0

## Disclaimer

For educational and research purposes. Respect MetaTFT.com's terms of service and avoid excessive requests.
