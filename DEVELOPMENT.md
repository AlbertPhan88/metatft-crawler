# Development Guide - MetaTFT Crawler

## Quick Start

```bash
cd /home/albertphan/Projects/metatft-crawler

# Install dependencies
pip install -e .
playwright install chromium

# Run demo
python3 tools/test_crawl_demo.py

# View output
jq '.units[0]' demo_output/units_demo_10.json
```

## Project Structure

```
src/metatft_crawler/
├── __init__.py                 # Package exports
├── cli.py                      # Command-line interface
├── crawlers/
│   ├── comps.py               # Comps crawler
│   └── units.py               # Units crawler (MAIN FILE)
└── utils/
    ├── browser.py             # Browser utilities
    ├── csv_export.py          # CSV formatting
    └── __init__.py            # Utils exports

tools/
├── test_crawl_demo.py          # Run 10-unit demo
├── debug_tooltip_structure.py  # Inspect HTML structure
├── debug_exact_html.py         # DOM inspection
├── debug_mapping.py            # Test mapping extraction
├── debug_full_tooltip_html.py  # Node sequence inspection
├── test_contextual_mapping.py  # Verify scalelevel mappings
└── check_ziggs.py              # Unit-specific debugging

demo_output/
├── units_demo_10.json          # JSON output (10 units)
└── units_demo_10.csv           # CSV output (10 units)
```

## Debugging Workflow

### Problem: Empty Damage Stats Mapping

**Symptom:** `damage_stats_mapping = {}`

**Quick Fix:** Check extraction timing
```python
# ✅ Correct location (lines 309-370)
# Inside JavaScript evaluation, BEFORE Stats tab click

# ❌ Wrong location (would be after line 387)
# AFTER clicking Stats tab (DOM changed)
```

### Problem: Wrong Stat Scaling

**Symptom:** `30/45/500 (AP/AD/AP)` instead of context-specific

**Debug Steps:**
```bash
# 1. Run contextual mapping test
python3 tools/test_contextual_mapping.py

# 2. Check if scalelevels are extracted
# Should show separate AP/AD for each scalelevel entry

# 3. Verify prioritization in units.py
# Scalelevels should be processed FIRST (lines 320-336)
```

### Problem: Inline Labels Not Showing

**Symptom:** `Damage: 30/45/500` instead of `Damage: AP 30/45/500`

**Check:**
```bash
# Verify first tooltip has images
python3 tools/debug_tooltip_structure.py

# Should show: Tooltip 0: ... Images (1): ['AP']
```

**Fix:** Ensure `is_others_field=True` when calling `replace_with_stats()`

## Testing Guide

### Unit Testing (Manual)

```bash
# Test single unit extraction
python3 -c "
import asyncio
from playwright.async_api import async_playwright

async def test():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto('https://www.metatft.com/units/BaronNashor')
        await page.wait_for_timeout(2000)
        # Test extraction here
        await browser.close()

asyncio.run(test())
"
```

### Integration Testing

```bash
# Run demo and check output
python3 tools/test_crawl_demo.py

# Verify Baron Nashor output
jq '.units[0].ability' demo_output/units_demo_10.json

# Should show:
# - description: "...280/420/20500 (AD/AP)..."
# - others: "Damage: AP 30/45/500 Damage: 280/420/20500 250/375/20000 (AD) + 30/45/500 (AP)..."
```

### Visual Inspection Tools

```bash
# 1. Check JSON structure
jq '.units[] | {name, others: .ability.others}' demo_output/units_demo_10.json

# 2. Pretty print first unit
jq '.units[0]' demo_output/units_demo_10.json | less

# 3. Check CSV export
head -20 demo_output/units_demo_10.csv
```

## Git Workflow

### Creating Changes

```bash
# 1. Make changes in worktree
git checkout -b your-feature-branch

# 2. Test thoroughly
python3 tools/test_crawl_demo.py

# 3. Commit with clear message
git add src/metatft_crawler/crawlers/units.py
git commit -m "Describe the change clearly"

# 4. Verify history
git log --oneline -5
```

### Merging to Main

```bash
# 1. Switch to main
git checkout main

# 2. Merge your branch
git merge your-feature-branch

# 3. Push to GitHub
git push origin main
```

## Common Modifications

### Adding New Damage Extraction

**Location:** `src/metatft_crawler/crawlers/units.py` (lines 245-307)

```python
// In JavaScript, modify damage line patterns:
if (line === 'Damage:' || line === 'Acid Damage:' ||
    line === 'New Label:') {  // Add here
    damageLines.push(line);
}
```

### Changing Stat Abbreviations

**Location:** `src/metatft_crawler/crawlers/units.py` (lines 330, 363)

```python
// Change from:
const imgs = Array.from(node.querySelectorAll('img[alt="AP"], img[alt="AD"]'));

// To support new stats:
const imgs = Array.from(node.querySelectorAll('img[alt="AP"], img[alt="AD"], img[alt="MR"]'));
```

### Modifying Replacement Rules

**Location:** `src/metatft_crawler/crawlers/units.py` (lines 486-492)

```python
def replacer(match):
    damage_val = match.group(1)
    if damage_val in damage_stats_mapping:
        stats = damage_stats_mapping[damage_val]
        # Modify formatting here
        stats_str = '/'.join(stats)  # Change separator if needed
        return f'{damage_val} ({stats_str})'
    return match.group(0)
```

## Performance Optimization

### Current Metrics
- Per unit: 2.3 seconds average
- 10 units: 23 seconds
- 50 units: 115 seconds

### Optimization Opportunities

1. **Parallel Crawling:**
   ```python
   # Use asyncio.gather() for concurrent unit extraction
   tasks = [extract_unit(url) for url in unit_urls]
   results = await asyncio.gather(*tasks, return_exceptions=True)
   ```

2. **Caching:**
   ```python
   # Cache DOM structures to avoid re-extraction
   unit_cache = {}
   if unit_name in unit_cache:
       return unit_cache[unit_name]
   ```

3. **Lazy Loading:**
   ```python
   # Only extract fields that are requested
   # Skip heavy extractions if not needed
   ```

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Browser hangs | Page doesn't fully load | Increase `wait_for_timeout()` |
| Empty ability fields | Text extraction fails | Check DOM selector in JavaScript |
| Stats missing | Mapping not extracted | Verify extraction timing (BEFORE Stats tab) |
| Wrong context | Using global mapping | Prioritize scalelevel elements |
| Demo fails | Missing playwright | Run `playwright install chromium` |

## File Modification Checklist

Before making changes:
- [ ] Understand current implementation
- [ ] Run existing tests
- [ ] Make targeted changes only
- [ ] Test with demo
- [ ] Verify output format
- [ ] Commit with clear message
- [ ] Update IMPLEMENTATION_NOTES.md if needed

## Related Documentation

- `IMPLEMENTATION_NOTES.md` - Technical implementation details
- `README.md` - User-facing documentation
- `src/metatft_crawler/crawlers/units.py` - Source code (inline comments)
