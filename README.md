# MetaTFT Crawler

A deterministic Python web scraper that extracts competitive Teamfight Tactics (TFT) meta data from [MetaTFT.com](https://www.metatft.com/). This tool is **fully deterministic** and does not involve any LLM components.

## Features

- **Comps Crawler**: Extract detailed information about TFT compositions including win rates, pick rates, placement statistics, unit compositions, and item builds
- **Units Crawler**: Extract detailed data for each champion including recommended builds, top items, positioning, traits, and placement statistics
- **Multi-language Support**: Vietnamese (vi) and English (en)
- **JSON Output**: Structured JSON output for easy integration with other tools
- **File Export**: Save results to JSON files or output to stdout

## Installation

### Prerequisites

- Python 3.8 or higher
- pip

### From Source

```bash
git clone https://github.com/albertphan/metatft-crawler.git
cd metatft-crawler
pip install -e .
```

This will:
1. Install the package in development mode
2. Install all required dependencies
3. Register the `metatft-crawler` command

### Manual Installation

```bash
pip install -r requirements.txt
```

## Usage

### Command Line Interface

```bash
# Crawl comps in English
python -m metatft_crawler comps

# Crawl comps in Vietnamese
python -m metatft_crawler comps -l vi

# Crawl units in English
python -m metatft_crawler units

# Crawl units in Vietnamese and save to file
python -m metatft_crawler units -l vi -o units.json

# Save comps data to file
python -m metatft_crawler comps -o comps.json

# Enable verbose output
python -m metatft_crawler comps -v

# Show help
python -m metatft_crawler --help
```

### Using as a Python Module

```python
import asyncio
from metatft_crawler import crawl_tft_meta, crawl_all_units

# Crawl comps
result = asyncio.run(crawl_tft_meta(language="en"))
print(result)

# Crawl units
result = asyncio.run(crawl_all_units(language="vi"))
print(result)
```

## Output Format

### Comps Crawler Output

```json
{
  "timestamp": "2026-02-26T12:34:56.789123",
  "source": "https://www.metatft.com/comps",
  "total_comps": 5,
  "comps": [
    {
      "name": "Noxus Ambessa",
      "rawText": "...",
      "stats": {
        "avg_placement": 3.91,
        "pick_rate": 0.28,
        "win_rate": 16.1,
        "top_4_rate": 61.5
      },
      "units": [
        {
          "name": "Swain",
          "rarity": "unknown",
          "stars": 1,
          "items": []
        }
      ]
    }
  ]
}
```

### Units Crawler Output

```json
{
  "timestamp": "2026-02-26T12:34:56.789123",
  "source": "https://www.metatft.com/units",
  "total_units_found": 50,
  "total_units_crawled": 10,
  "units": [
    {
      "name": "Ziggs",
      "tier": "S",
      "avg_placement": 3.27,
      "win_rate_percent": 58.0,
      "pick_count": 12345,
      "frequency_percent": 45.2,
      "url": "https://www.metatft.com/units/Ziggs",
      "recommended_build": ["Item1", "Item2", "Item3"],
      "top_items": ["Item1", "Item2", "Item3", "Item4", "Item5"],
      "positioning": "back row",
      "traits": ["Magic", "Marksman"],
      "stats": {
        "avg_placement": 3.27,
        "pick_rate": 0.58
      }
    }
  ],
  "note": "Showing first 10 units with detailed crawling. Full list available on source page."
}
```

## Language Support

### English (en)
The crawler extracts English labels:
- `Avg Place` - Average Placement
- `Pick Rate` - Pick Rate percentage
- `Win Rate` - Win Rate percentage
- `Top 4 Rate` - Top 4 placement rate

### Vietnamese (vi)
The crawler extracts Vietnamese labels:
- `Hạng TB` - Average Placement
- `Tỷ Lệ Chọn` - Pick Rate
- `Tỷ Lệ Thắng` - Win Rate
- `Tỷ Lệ Top 4` - Top 4 Rate

## How It Works

The crawler uses **Playwright** to:

1. Launch a Chromium browser instance
2. Navigate to MetaTFT.com
3. Wait for page rendering
4. Switch language if needed by clicking the language selector and choosing the target language
5. Extract data using JavaScript evaluation
6. Parse structured data from page content
7. Return JSON results

## Architecture

```
src/metatft_crawler/
├── __init__.py           # Package initialization
├── cli.py               # Command-line interface
├── crawlers/
│   ├── __init__.py
│   ├── comps.py        # Comps crawler logic
│   └── units.py        # Units crawler logic
└── utils/
    ├── __init__.py
    └── browser.py      # Shared browser utilities (language switching)
```

## Technical Details

### Browser Automation
- Uses Playwright's async API for non-blocking operations
- Launches Chromium headless browser
- Implements timeout handling for reliable scraping

### Language Switching
The crawler intelligently switches languages by:
1. Clicking the `.LanguageSelectContainer` element
2. Finding the language option with the target language code
3. Clicking the option and waiting for the page to update
4. Resuming data extraction after language change

### Data Extraction
- Uses JavaScript evaluation on page content
- Implements pattern matching for both English and Vietnamese labels
- Filters noise and validates data before returning
- Limits results to top items (comps limited to 20, units limited to 50)

## Dependencies

- **playwright** (>=1.40.0) - Browser automation and web scraping

The crawler requires Playwright browsers to be installed. After installing the package, you may need to run:

```bash
playwright install chromium
```

## Troubleshooting

### Browser installation issues
```bash
# Install Chromium browser
python -m playwright install chromium
```

### Timeout errors
The crawler includes reasonable timeouts (60s for navigation, 5s for rendering). If you experience timeouts:
- Ensure stable internet connection
- MetaTFT.com may be under heavy load
- Try again later

### Language switching not working
- The `.LanguageSelectContainer` element might have changed
- Verify the website structure hasn't changed
- Check browser console for JavaScript errors

## Contributing

Contributions are welcome! Areas for improvement:
- Add more robust error handling
- Implement caching to reduce load
- Add support for additional languages
- Optimize extraction patterns
- Add more unit detail extraction (abilities, synergies)

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Disclaimer

This tool is for educational and research purposes. Ensure you comply with MetaTFT.com's terms of service and robots.txt before using this crawler. Respect rate limits and avoid excessive requests.

## Related Resources

- [MetaTFT.com](https://www.metatft.com/) - The source website
- [Teamfight Tactics](https://teamfighttactics.leagueoflegends.com/) - Official TFT game
- [Playwright](https://playwright.dev/) - Browser automation framework
