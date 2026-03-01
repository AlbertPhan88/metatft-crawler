# Language Configuration - Gaps Found & Fixes Applied

**Date:** March 1, 2026
**Status:** ✅ COMPLETE - All gaps fixed and tested

## Testing Overview

Tested crawling 10 units in both English and Vietnamese to identify and fix any gaps in the language configuration system.

### Test Results

**Initial Test:** ❌ 5 GAPS DETECTED
- ❌ cost: Empty in Vietnamese
- ❌ type: Empty in Vietnamese
- ❌ traits: Empty list in Vietnamese
- ❌ top_items: Missing in Vietnamese
- ❌ recommended_builds: Missing in Vietnamese

**Final Test:** ✅ NO GAPS - Both languages produce identical structures!

---

## Gaps Found & Fixed

### Gap 1: Unit Tabs (Ability/Stats)
**Issue:** Vietnamese page shows "Kỹ Năng" and "Số Liệu" instead of "Ability" and "Stats"

**Root Cause:** Vietnamese config used English labels instead of Vietnamese translations

**Fix Applied:**
```python
# Before (Vietnamese config)
self.ability_label = "Ability"
self.stats_label = "Stats"

# After (Vietnamese config)
self.ability_label = "Kỹ Năng"      # Vietnamese for "Ability"
self.stats_label = "Số Liệu"        # Vietnamese for "Stats"
```

**Commit:** Updated `src/metatft_crawler/languages/vi.py`

---

### Gap 2: Ability Description Markers
**Issue:** Vietnamese page shows "Nội Tại:" and "Kích Hoạt:" instead of "Passive:" and "Active:"

**Root Cause:** Vietnamese config used English markers instead of Vietnamese translations

**Fix Applied:**
```python
# Before (Vietnamese config)
self.passive_marker = "Passive:"
self.active_marker = "Active:"

# After (Vietnamese config)
self.passive_marker = "Nội Tại:"       # Vietnamese for "Passive:"
self.active_marker = "Kích Hoạt:"      # Vietnamese for "Active:"
```

**Commit:** Updated `src/metatft_crawler/languages/vi.py`

---

### Gap 3: Unit Type Detection
**Issue:** Type extraction failed because Vietnamese page shows "Đấu Sĩ Vật Lý" not "Attack Fighter"

**Root Cause:** Type detection uses keyword matching. Vietnamese type names are different from English.

**Fix Applied:**
```python
# Before (Vietnamese config)
self.unit_types = ["Attack", "Fighter", "Caster", "Support", "Tank"]

# After (Vietnamese config)
self.unit_types = [
    # English versions
    "Attack", "Fighter", "Caster", "Support", "Tank",
    # Vietnamese versions (as shown on Vietnamese page)
    "Đấu Sĩ", "Vật Lý", "Pháp Sư", "Hỗ Trợ", "Quân Áo",
]
```

**Commit:** Updated `src/metatft_crawler/languages/vi.py`

---

### Gap 4: Trait Name Detection
**Issue:** Trait extraction failed because Vietnamese page shows Vietnamese trait names

**Root Cause:** Trait detection uses exact name matching. Vietnamese trait names are different.

**Fix Applied:**
```python
# Before (Vietnamese config)
self.traits = [30 English trait names only]

# After (Vietnamese config)
self.traits = [
    # 30 English trait names (game terms)
    "Attack", "Fighter", "Void", ... "Enforcer",
    # Vietnamese trait name equivalents (as shown on Vietnamese page)
    "Vật Lý", "Đấu Sĩ", "Hư Không", "Tai Ương", ... (30 more)
]
```

**Commit:** Updated `src/metatft_crawler/languages/vi.py`

---

### Gap 5: Top Items Label
**Issue:** Top Items section not found in Vietnamese

**Root Cause:** Used wrong Vietnamese label - initially thought it was "Top Items" (English)

**Fix Applied:**
```python
# Before (Vietnamese config)
self.top_items_label = "Top Items"

# After (Vietnamese config)
self.top_items_label = "Trang Bị Hàng Đầu"  # Vietnamese for "Top Items"
```

**Commit:** Updated `src/metatft_crawler/languages/vi.py`

---

### Gap 6: Recommended Builds Label
**Issue:** Recommended Builds section had wrong extraction for Vietnamese

**Root Cause:** Vietnamese uses "Lối Chơi Đề Xuất" instead of "Recommended Builds"

**Fix Applied:**
```python
# Before (Vietnamese config)
self.recommended_builds_label = "Recommended Builds"

# After (Vietnamese config)
self.recommended_builds_label = "Lối Chơi Đề Xuất"  # Vietnamese for "Recommended Builds"
```

**Also added English labels to match in all extraction code:**
```python
# English config (updated)
self.top_items_label = "Top Items"
self.recommended_builds_label = "Recommended Builds"
```

**Commit:** Updated `src/metatft_crawler/languages/{en,vi}.py` and extraction logic

---

### Gap 7: Vietnamese Text Parsing
**Issue:** Items extracted from Vietnamese text were incomplete or corrupted

**Root Cause:** Vietnamese text structure differs from English
- Vietnamese uses "là" (is/are) as separator
- Vietnamese uses "và" (and) instead of commas
- Vietnamese sentences have different structure

**Fix Applied:**
```javascript
// Top Items extraction (Before)
if (itemsStr.includes(' are ')) {
    itemsStr = itemsStr.split(' are ')[1];
}
let itemList = itemsStr.split(/,|\s+and\s+/);

// Top Items extraction (After)
if (itemsStr.includes(' are ')) {
    itemsStr = itemsStr.split(' are ')[1];
} else if (itemsStr.includes(' là ')) {        // NEW: Vietnamese support
    itemsStr = itemsStr.split(' là ')[1];
}
let itemList = itemsStr.split(/,|\s+and\s+|\s+và\s+/);  // NEW: Support "và"
```

**Recommended Builds extraction fix:**
```javascript
// Before
if (itemsStr.includes(' recommend ')) {
    itemsStr = itemsStr.split(' recommend ')[1].split(' as ')[0];
}

// After - Support Vietnamese "đề xuất" keyword
if (itemsStr.includes(' recommend ')) {
    itemsStr = itemsStr.split(' recommend ')[1].split(' as ')[0];
} else if (itemsStr.includes(' đề xuất ')) {
    // Vietnamese: "Chúng tôi đề xuất ... là ..."
    itemsStr = itemsStr.split(' đề xuất ')[1].split(' là ')[0];
}
```

**Commit:** Updated `src/metatft_crawler/crawlers/units.py`

---

## Verification

### Test Data
- Crawled 10 units in English: ✅ All fields extracted correctly
- Crawled 10 units in Vietnamese: ✅ All fields extracted correctly
- Comparison: ✅ Identical structure and content (languages translated appropriately)

### Sample Output - Baron Nashor
```
ENGLISH:
  cost: 7
  type: Attack Fighter
  traits: ['Void', 'Riftscourge']
  top_items: ['Bloodthirster', "Sterak's Gage", 'Deathblade', 'Infinity Edge', 'Edge of Night']
  recommended_builds: [['Bloodthirster', 'Infinity Edge', "Sterak's Gage"]]

VIETNAMESE:
  cost: 7
  type: Đấu Sĩ Vật Lý
  traits: ['Hư Không', 'Tai Ương']
  top_items: ['Huyết Kiếm', 'Móng Vuốt Sterak', 'Kiếm Tử Thần', 'Vô Cực Kiếm', 'Áo Choàng Bóng Tối']
  recommended_builds: [['Huyết Kiếm', 'Vô Cực Kiếm', 'Móng Vuốt Sterak']]
```

✅ All items are translated correctly!

---

## Files Modified

1. **`src/metatft_crawler/languages/vi.py`**
   - Updated ability_label to "Kỹ Năng"
   - Updated stats_label to "Số Liệu"
   - Updated passive_marker to "Nội Tại:"
   - Updated active_marker to "Kích Hoạt:"
   - Added Vietnamese unit_types
   - Added Vietnamese trait names
   - Updated top_items_label to "Trang Bị Hàng Đầu"
   - Updated recommended_builds_label to "Lối Chơi Đề Xuất"

2. **`src/metatft_crawler/languages/en.py`**
   - Added top_items_label = "Top Items"
   - Added recommended_builds_label = "Recommended Builds"

3. **`src/metatft_crawler/crawlers/units.py`**
   - Updated top items extraction to handle Vietnamese "là" separator
   - Updated item list parsing to handle Vietnamese "và" (and)
   - Updated recommended builds detection to recognize Vietnamese "đề xuất"
   - Updated builds item extraction to handle Vietnamese text structure

---

## Key Learnings

1. **Language Labels Are Context-Specific**
   - Not all page labels are obvious - needed to inspect actual Vietnamese page
   - Page structures can differ between languages even on same website

2. **Text Structure Varies by Language**
   - Vietnamese uses different separators and word order
   - Need language-specific parsing rules for text extraction

3. **Trait/Type Names Are User-Facing**
   - English internal names ≠ Vietnamese display names
   - Need both versions in config for pattern matching

4. **Test Early and Often**
   - Testing with actual language outputs caught issues quickly
   - Comparison testing between languages is essential

---

## Summary

✅ Language configuration system is now fully working for both English and Vietnamese
✅ All identified gaps have been fixed and tested
✅ Text extraction handles Vietnamese-specific language patterns
✅ No breaking changes to English extraction
✅ System is ready for production
