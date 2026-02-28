# MetaTFT Crawler - Implementation Notes

## Stat Scaling Feature (Feb 28, 2026)

### Overview
Enhanced the units crawler to display stat scaling information (AD/AP) for damage values in ability descriptions and damage breakdowns.

**Status:** ✅ COMPLETED
**Commits:** e28d6c9, 37cfbb0, f02e4ae

### Example Output
**Baron Nashor:**
```json
{
  "ability": {
    "description": "...dealing 280/420/20500 (AD/AP) physical damage... deal 112/189/10250 (AD/AP) physical damage.",
    "others": "Damage: AP 30/45/500 Damage: 280/420/20500 250/375/20000 (AD) + 30/45/500 (AP) Acid Damage: 112/189/10250..."
  }
}
```

### Implementation Details

#### File: `src/metatft_crawler/crawlers/units.py`

**JavaScript Extraction Block (lines 309-370):**
- Extracts `damageStatsMapping` while on ability tab (BEFORE clicking Stats)
- Prioritizes DOM elements in order:
  1. `SCALELEVEL` elements - most context-specific
  2. First `TOOLTIPCALCULATION` - for inline labels
  3. Generic DOM traversal - fallback

```javascript
// Key extraction strategy:
// 1. Extract from scalelevel elements (context-specific)
// 2. Use first tooltip for inline stat label (AP label only)
// 3. Fallback to generic damage pattern search
```

**Python Replacement Logic (lines 478-507):**
- Function: `replace_with_stats(text, is_others_field=False)`
- For `ability_others`: Adds inline stat labels (e.g., "Damage: AP 30/45/500")
- For `ability_description`: Applies standard () → (STAT) replacement
- Regex pattern: `r'(\d+/\d+/\d+)\s*\(\)'`

```python
def replace_with_stats(text, is_others_field=False):
    # If ability_others, check for inline label in first damage
    if is_others_field:
        # Pattern: "Damage:" followed by damage value
        # If value has single stat, insert inline (e.g., "Damage: AP 30/45/500")

    # Replace all () placeholders with stats from mapping
    pattern = r'(\d+/\d+/\d+)\s*\(\)'
    # ... replacement logic
```

#### Key DOM Elements

| Element | Purpose | Info |
|---------|---------|------|
| `TOOLTIPCALCULATION` | Damage line header | First one has inline stat image |
| `SCALELEVEL` | Damage breakdown | Most specific stat info (AD-only or AP-only) |
| `TOOLTIPCALCULATIONDETAIL` | Breakdown section | Contains multiple damage components |

#### Extraction Timing

**Critical:** Must extract mapping DURING initial_data extraction:
```python
# ✅ CORRECT: Extract while on ability tab
const damageStatsMapping = {};
// ... extraction logic ...
return {
    ability_others: abilityOthers,
    damage_stats_mapping: damageStatsMapping
};

# ❌ WRONG: Extract AFTER clicking Stats tab
// DOM has changed, images not visible, mapping returns {}
```

### Common Issues & Solutions

#### Issue 1: Mapping Returns Empty `{}`
**Symptom:** `damage_stats_mapping = {}` in Python
**Cause:** Extraction happens after clicking Stats tab (DOM structure changes)
**Solution:** Extract mapping BEFORE clicking Stats (lines 309-370, before line 387)

#### Issue 2: Wrong Stat Associations
**Symptom:** `30/45/500 (AP/AD/AP)` shows all stats instead of context-specific
**Cause:** Using only first DOM occurrence, not context-specific scalelevels
**Solution:** Prioritize SCALELEVEL elements which isolate single damage values with their specific stats

**Example:**
- First `30/45/500` in tooltip[0] = AP only → "Damage: AP 30/45/500"
- Same `30/45/500` in scalelevel[4] = AP only → "(AP)"
- But `30/45/500` in tooltipDetail = AD/AP → "(AD/AP)"

#### Issue 3: Multiple Occurrences of Same Damage Value
**Cause:** Damage values like `30/45/500` appear in multiple contexts
**Solution:** Use context-aware mapping from scalelevels for breakdown values

### Testing Tools

Located in `/tools/` directory:

```bash
# Run 10-unit demo
python3 tools/test_crawl_demo.py

# Debug tooltip structure
python3 tools/debug_tooltip_structure.py

# Check contextual mapping
python3 tools/test_contextual_mapping.py

# Unit-specific debugging
python3 tools/check_ziggs.py
```

### Data Flow

```
Page Load → Extract Ability Tab Data
    ↓
    ├─ Extract ability text (description, damage breakdown)
    ├─ Extract scalelevel stat mappings (context-specific)
    ├─ Extract first tooltip stat labels
    └─ Store damage_stats_mapping in initial_data
    ↓
Click Stats Tab → Extract Base Stats
    ↓
Post-Process Ability Fields
    ├─ Replace () in ability_description with stats
    └─ Replace () in ability_others with stats
        (with inline labels for first tooltip)
```

### Regex Patterns Used

```python
# Find damage value with empty parens
r'(\d+/\d+/\d+)\s*\(\)'

# Find "Damage:" followed by damage value
r'(Damage:)\s+(\d+/\d+/\d+)(?=\s|$)'
```

### Expected Output Formats

#### Baron Nashor (with breakdown)
```
ability.others: "Damage: AP 30/45/500 Damage: 280/420/20500 250/375/20000 (AD) + 30/45/500 (AP) Acid Damage: 112/189/10250..."
```

#### Ziggs (magic damage)
```
ability.others: "40/65/500 100% + 40/65/500 (AP) 70/105/3000 (AP) 550/875/7000 (AP)"
```

#### Mel (pure AP)
```
ability.others: "65/100/150 (AP) 1000/1500/10000 (AP) 400/600/10000 (AP)"
```

### Performance Notes

- Average extraction time per unit: 2.3 seconds
- 10 units: ~23 seconds total
- 50 units: ~115 seconds (~2 minutes)
- Bottleneck: Page load and screenshot rendering (Playwright)

### Future Improvements

1. **Caching:** Cache DOM extraction results per unit type
2. **Parallelization:** Extract multiple units simultaneously
3. **Error Handling:** Add retry logic for failed extractions
4. **Validation:** Verify stat mappings match expected format
5. **Multi-language:** Ensure works with Vietnamese stat labels

### Related Files

- `src/metatft_crawler/crawlers/units.py` - Main implementation
- `src/metatft_crawler/utils/csv_export.py` - CSV formatting
- `tools/test_crawl_demo.py` - Demo script
- `README.md` - User-facing documentation
