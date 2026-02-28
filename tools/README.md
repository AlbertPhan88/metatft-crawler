# MetaTFT Crawler - Tools & Debug Scripts

This folder contains utility scripts for testing, debugging, and exploring the MetaTFT crawler.

## Testing Tools

### `test_crawl_demo.py`
Main testing script for crawling a limited number of units.

**Usage:**
```bash
# From project root
python tools/test_crawl_demo.py [units_count] [language]

# Examples
python tools/test_crawl_demo.py 1 en      # Crawl 1 unit in English
python tools/test_crawl_demo.py 5 vi      # Crawl 5 units in Vietnamese
python tools/test_crawl_demo.py 50 en     # Crawl all 50 units
```

**Output:**
- Generates demo JSON and CSV files in `demo_output/` folder
- Shows progress and summary statistics

## Inspection/Debug Scripts

These scripts examine the page structure and help debug extraction issues.

### `inspect_damage_icons.py`
Inspects the damage section HTML and extracts stat icons (AP/AD).

**Purpose:** Understand the page structure for damage info extraction

### `inspect_damage_section.py`
Examines the ability damage section and its surrounding HTML structure.

**Purpose:** Debug damage section parsing

### `test_stat_extraction.py`
Tests extraction of stat abbreviations (AP/AD) from page images.

**Purpose:** Verify that stat icons are being correctly identified

### `inspect_baron_detail.py`
Detailed inspection of Baron Nashor's page structure.

**Purpose:** Explore page layout for a specific unit

### `check_top_items.py`
Checks the Top Items and Recommended Builds sections.

**Purpose:** Verify item extraction logic

### `debug_extraction.py`
General debugging script for extraction logic.

**Purpose:** Test and debug various extraction patterns

## Running Scripts

All scripts can be run from the project root:

```bash
python tools/test_crawl_demo.py
python tools/inspect_damage_icons.py
# etc.
```

Or from within the tools folder:

```bash
cd tools
python test_crawl_demo.py
```

## Adding New Tools

When creating new inspection/debug scripts:

1. Save them in this `tools/` folder
2. Use relative paths to reference the `src/` folder (go up one level: `Path(__file__).parent.parent`)
3. Add documentation in this README
4. Update .gitignore if needed (tools are typically tracked in git)
