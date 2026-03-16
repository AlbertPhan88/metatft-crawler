#!/usr/bin/env python3
"""TFT Comp Detail Crawler - Extracts detailed comp data from MetaTFT.com/comps."""

import asyncio
import json
from datetime import datetime
from playwright.async_api import async_playwright, Page
from typing import Dict, Any, List

from ..utils.browser import switch_language
from ..languages.loader import get_language_config


async def crawl_comp_details(
    language: str = "vi",
    limit_comps: int = None,
) -> Dict[str, Any]:
    """Crawl MetaTFT.com/comps and extract detailed data for each comp.

    Extracts: units with items, early game boards, positioning, augments,
    leveling guide, carousel priority, and counters/VODs.

    Args:
        language: Language code ('en' or 'vi').
        limit_comps: Limit to N comps (None = all).

    Returns:
        Dictionary with timestamp, source, and detailed comp data.
    """
    base_url = "https://www.metatft.com/comps"
    lang_config = get_language_config(language)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        print(f"Navigating to {base_url} (Language: {language})...")
        try:
            await page.goto(base_url, wait_until="domcontentloaded", timeout=60000)
        except Exception as e:
            print(f"Navigation timeout: {e}")

        print("Waiting for page to fully render...")
        await page.wait_for_timeout(5000)

        if language == "vi":
            print("Switching to Vietnamese...")
            await switch_language(page, "vi")
            await page.wait_for_timeout(2000)

        # Scroll down to load all comps
        print("Scrolling to load all comps...")
        for _ in range(15):
            await page.evaluate("window.scrollBy(0, 1000)")
            await page.wait_for_timeout(400)
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(500)

        # Extract comp list (name, tier, basic info)
        print("Extracting comp list...")
        comp_list = await _extract_comp_list(page, lang_config)
        total_found = len(comp_list)
        print(f"Found {total_found} comps")

        if limit_comps is not None:
            comp_list = comp_list[:limit_comps]
            print(f"Limited to {len(comp_list)} comps")

        # Extract details for each comp
        detailed_comps = []
        for i, comp in enumerate(comp_list):
            print(f"\n[{i+1}/{len(comp_list)}] Expanding {comp['name']}...")
            try:
                detail = await _extract_comp_detail(page, comp, lang_config)
                detailed_comps.append(detail)
                print(f"  ✓ {comp['name']} - {len(detail.get('units', []))} units, "
                      f"{len(detail.get('augments', []))} augments, "
                      f"{len(detail.get('early_game_boards', []))} boards")
            except Exception as e:
                print(f"  ✗ Failed: {e}")
                detailed_comps.append(comp)

        await browser.close()

        return {
            "timestamp": datetime.now().isoformat(),
            "source": base_url,
            "language": language,
            "total_comps_found": total_found,
            "total_comps_crawled": len(detailed_comps),
            "comps": detailed_comps,
        }


async def _extract_comp_list(page: Page, lang_config) -> List[Dict]:
    """Extract the list of comps with basic info from the listing page."""
    return await page.evaluate("""
        (langConfig) => {
            const comps = [];
            const lines = document.body.innerText.split('\\n').map(l => l.trim()).filter(l => l);
            const tierPattern = /^[SABCD]$/;

            // Find comp entries: tier marker followed by comp name
            for (let i = 0; i < lines.length; i++) {
                if (tierPattern.test(lines[i]) && i + 1 < lines.length) {
                    const nextLine = lines[i + 1];
                    // Comp names are like "Warwick Zaun", "Malzahar Targon", etc.
                    if (nextLine.length > 3 && nextLine.length < 60 &&
                        !nextLine.includes(langConfig.avg_place) &&
                        !nextLine.includes(langConfig.pick_rate) &&
                        !nextLine.match(/^\\d/) &&
                        !['Cơ Bản', 'Dễ', 'Trung Bình', 'Khó', 'Basic', 'Easy', 'Medium', 'Hard',
                          'Fast 8', 'Fast 9', 'Cấp 6', 'Cấp 7', 'Cấp 8', 'Cấp 9', 'Cấp 10'].includes(nextLine)) {
                        comps.push({
                            name: nextLine,
                            tier: lines[i],
                            index: i
                        });
                    }
                }
            }

            return comps;
        }
    """, {
        'avg_place': lang_config.avg_place,
        'pick_rate': lang_config.pick_rate,
    })


async def _extract_comp_detail(
    page: Page, comp: Dict, lang_config
) -> Dict[str, Any]:
    """Click on a comp to expand it and extract all detail sections."""
    comp_name = comp['name']

    # Scroll comp into view and click to expand it
    clicked = await page.evaluate("""
        (compName) => {
            const elements = document.querySelectorAll('div, span, a');
            for (const el of elements) {
                const text = el.innerText ? el.innerText.trim() : '';
                if (text === compName && el.offsetHeight > 0 && el.offsetHeight < 60) {
                    el.scrollIntoView({ behavior: 'instant', block: 'start' });
                    el.click();
                    return true;
                }
            }
            return false;
        }
    """, comp_name)

    if not clicked:
        return comp

    await page.wait_for_timeout(2000)

    # Scroll down to trigger lazy loading of augments/leveling sections
    await page.evaluate("window.scrollBy(0, 600)")
    await page.wait_for_timeout(1000)

    # Extract all detail data
    detail = await page.evaluate("""
        (params) => {
            const compName = params.compName;
            const lc = params.langConfig;
            const lines = document.body.innerText.split('\\n').map(l => l.trim()).filter(l => l);

            // Find the comp's section
            let compIdx = -1;
            for (let i = 0; i < lines.length; i++) {
                if (lines[i] === compName) { compIdx = i; break; }
            }
            if (compIdx === -1) return { name: compName, error: 'not found' };

            // Find section end (next tier + comp name)
            const tierPattern = /^[SABCD]$/;
            let endIdx = lines.length;
            for (let i = compIdx + 10; i < lines.length; i++) {
                if (tierPattern.test(lines[i]) && i + 1 < lines.length) {
                    const next = lines[i + 1];
                    if (next.length > 3 && next.length < 60 && next !== compName &&
                        !next.match(/^\\d/) &&
                        !['Cơ Bản','Dễ','Trung Bình','Khó','Basic','Easy','Medium','Hard',
                          'Fast 8','Fast 9','Cấp 6','Cấp 7','Cấp 8','Cấp 9','Cấp 10'].includes(next)) {
                        endIdx = i;
                        break;
                    }
                }
            }

            const section = lines.slice(compIdx, endIdx);

            // Extract playstyle and difficulty (lines after comp name)
            let playstyle = '';
            let difficulty = '';
            const playstyles = ['Cơ Bản', 'Basic', 'Fast 8', 'Fast 9', 'Cấp 6', 'Cấp 7', 'Cấp 8', 'Cấp 9', 'Cấp 10'];
            const difficulties = ['Dễ', 'Trung Bình', 'Khó', 'Easy', 'Medium', 'Hard'];
            for (let i = 1; i < Math.min(5, section.length); i++) {
                if (playstyles.includes(section[i])) playstyle = section[i];
                if (difficulties.includes(section[i])) difficulty = section[i];
            }

            // Extract stats (value comes AFTER label)
            let stats = {};
            for (let i = 0; i < section.length; i++) {
                if (section[i] === lc.avg_place || section[i] === 'Hạng TB' || section[i] === 'Avg Place') {
                    if (i + 1 < section.length) stats.avg_place = parseFloat(section[i + 1]) || section[i + 1];
                }
                if (section[i] === lc.pick_rate || section[i] === 'Tỷ Lệ Chọn' || section[i] === 'Pick Rate') {
                    if (i + 1 < section.length) stats.pick_rate = parseFloat(section[i + 1]) || section[i + 1];
                }
                if (section[i] === lc.win_rate || section[i] === 'Tỷ Lệ Thắng' || section[i] === 'Win Rate') {
                    if (i + 1 < section.length) stats.win_rate = section[i + 1];
                }
                if (section[i] === lc.top_4_rate || section[i] === 'Tỷ Lệ Top 4' || section[i] === 'Top 4 Rate') {
                    if (i + 1 < section.length) stats.top_4_rate = section[i + 1];
                }
            }

            // Extract early game boards
            let earlyGameBoards = [];
            for (let i = 0; i < section.length; i++) {
                if (section[i] === lc.comp_round_win_rate) {
                    // Look backwards for units and win rate %
                    let winRate = '';
                    let units = [];
                    // The win rate % is just before this label
                    if (i > 0 && section[i - 1].includes('%')) {
                        // Units are above the win rate, going back until we hit a level label or non-unit text
                        for (let j = i - 2; j >= 0; j--) {
                            const line = section[j];
                            if (line.includes('%') || line.match(/^\\d+\\.\\d+$/) ||
                                line.startsWith('Cấp') || line === lc.comp_early_game ||
                                line === lc.comp_round_win_rate || line === 'Tùy Chỉnh') break;
                            units.unshift(line);
                        }
                    }
                    if (i > 0) winRate = section[i - 1];
                    if (units.length > 0) {
                        earlyGameBoards.push({
                            units: units,
                            round_win_rate: winRate
                        });
                    }
                }
            }

            // Extract positioning (after "Bài Trí Đội Hình" / "Team Positioning")
            let positioning = [];
            for (let i = 0; i < section.length; i++) {
                if (section[i] === lc.comp_positioning || section[i].includes(lc.comp_positioning)) {
                    for (let j = i + 1; j < section.length; j++) {
                        const line = section[j];
                        if (line === lc.comp_augments || line === lc.comp_leveling ||
                            line === lc.comp_carousel || line === 'More' || line.startsWith('Lên Cấp')) break;
                        if (line.length > 1 && line.length < 40 && !line.match(/^\\d/)) {
                            positioning.push(line);
                        }
                    }
                    break;
                }
            }

            // Extract leveling guide (after "Lên Cấp" / "Leveling")
            let levelingGuide = [];
            for (let i = 0; i < section.length; i++) {
                if (section[i].startsWith(lc.comp_leveling) || section[i].startsWith('Lên Cấp')) {
                    let j = i + 1;
                    while (j < section.length) {
                        const line = section[j];
                        if (line === lc.comp_carousel || line.includes('Ưu Tiên') || line.includes('Carousel')) break;
                        if (line.startsWith('Cấp') || line.startsWith('Level')) {
                            const level = line;
                            const timing = (j + 1 < section.length) ? section[j + 1] : null;
                            let gold = null;
                            if (j + 2 < section.length && section[j + 2].match(/^\\d+\\.?\\d*$/)) {
                                gold = parseFloat(section[j + 2]);
                                j += 3;
                            } else {
                                j += 2;
                            }
                            levelingGuide.push({ level, timing, gold });
                        } else {
                            j++;
                        }
                    }
                    break;
                }
            }

            // Extract carousel priority counts
            let carouselPriority = [];
            for (let i = 0; i < section.length; i++) {
                if (section[i].includes(lc.comp_carousel) || section[i].includes('Ưu Tiên Vòng Đi Chợ')) {
                    for (let j = i + 1; j < section.length; j++) {
                        const line = section[j];
                        if (line.match(/^x\\d+$/)) {
                            carouselPriority.push(parseInt(line.substring(1)));
                        } else if (tierPattern.test(line) || line.length > 20) {
                            break;
                        }
                    }
                    break;
                }
            }

            return {
                name: compName,
                tier: params.tier,
                playstyle,
                difficulty,
                stats,
                early_game_boards: earlyGameBoards,
                positioning,
                leveling_guide: levelingGuide,
                carousel_priority_counts: carouselPriority,
            };
        }
    """, {
        'compName': comp_name,
        'tier': comp.get('tier', ''),
        'langConfig': {
            'avg_place': lang_config.avg_place,
            'pick_rate': lang_config.pick_rate,
            'win_rate': lang_config.win_rate,
            'top_4_rate': lang_config.top_4_rate,
            'comp_options_tab': lang_config.comp_options_tab,
            'comp_counters_tab': lang_config.comp_counters_tab,
            'comp_early_game': lang_config.comp_early_game,
            'comp_positioning': lang_config.comp_positioning,
            'comp_augments': lang_config.comp_augments,
            'comp_leveling': lang_config.comp_leveling,
            'comp_carousel': lang_config.comp_carousel,
            'comp_round_win_rate': lang_config.comp_round_win_rate,
        },
    })

    # Extract items per unit from HTML img alt attributes
    # Pass positioning list to filter to only this comp's units
    positioning = detail.get('positioning', [])
    units_with_items = await _extract_units_with_items(page, comp_name, positioning)
    detail['units'] = units_with_items

    # Extract per-level comp variations by clicking MUI Tab buttons
    level_variations = await _extract_level_variations(page, lang_config)
    detail['level_variations'] = level_variations

    # Extract augments from img alt attributes
    augments = await _extract_augments(page, lang_config)
    detail['augments'] = augments

    # Extract carousel component names from img alt
    carousel_components = await _extract_carousel_components(page, lang_config)
    detail['carousel_priority'] = []
    for idx, component in enumerate(carousel_components):
        count = detail['carousel_priority_counts'][idx] if idx < len(detail.get('carousel_priority_counts', [])) else None
        detail['carousel_priority'].append({'component': component, 'count': count})
    if 'carousel_priority_counts' in detail:
        del detail['carousel_priority_counts']

    # Click on Counters & Vods tab
    counters_vods = await _extract_counters_vods(page, lang_config)
    detail['counters_and_vods'] = counters_vods

    # Collapse the comp by clicking again
    await page.evaluate("""
        (compName) => {
            const elements = document.querySelectorAll('div, span, a');
            for (const el of elements) {
                const text = el.innerText ? el.innerText.trim() : '';
                if (text === compName && el.offsetHeight > 0 && el.offsetHeight < 60) {
                    el.click();
                    return true;
                }
            }
            return false;
        }
    """, comp_name)
    await page.wait_for_timeout(1000)

    return detail


async def _extract_level_variations(page: Page, lang_config) -> List[Dict]:
    """Extract comp variations for each level tab (Cấp 7/8/9/10).

    Each level tab shows multiple comp compositions (rows of unit icons).
    Units may have a 3-star indicator. No items are shown in level variations.
    """
    variations = []

    # Get all level tab buttons
    tabs = await page.evaluate("""
        () => {
            const buttons = document.querySelectorAll('button[class*="MuiTab"]');
            return Array.from(buttons)
                .filter(b => b.offsetHeight > 0 && b.innerText.trim().startsWith('Cấp'))
                .map(b => {
                    const text = b.innerText.trim();
                    const parts = text.split('\\n');
                    return {
                        label: parts[0],
                        percentage: parts.length > 1 ? parts[1] : null
                    };
                });
        }
    """)

    for tab in tabs:
        await page.evaluate("""
            (label) => {
                const buttons = document.querySelectorAll('button[class*="MuiTab"]');
                for (const btn of buttons) {
                    if (btn.innerText.trim().startsWith(label) && btn.offsetHeight > 0) {
                        btn.click(); return;
                    }
                }
            }
        """, tab['label'])
        await page.wait_for_timeout(1500)

        # Extract comp variation rows from Unit_Wrapper groups
        # Group by Y position, skip the main comp row (first row) and other comps below
        comps = await page.evaluate("""
            () => {
                const wrappers = document.querySelectorAll('div[class*="Unit_Wrapper"]');
                const units = [];

                for (const wrapper of wrappers) {
                    const rect = wrapper.getBoundingClientRect();
                    if (rect.height === 0) continue;

                    const imgs = wrapper.querySelectorAll('img');
                    const alts = Array.from(imgs).map(i => (i.alt || '').trim());

                    const unitName = alts.find(a =>
                        a.length > 1 && !a.includes('Unlockable') &&
                        !a.includes('Three Star') && !a.includes('Tướng 3 Sao') &&
                        a !== 'Teambuilder' && !a.includes('Copy') && !a.includes('Open In'));
                    const isThreeStar = alts.some(a =>
                        a.includes('Three Star') || a.includes('Tướng 3 Sao'));

                    if (unitName) {
                        units.push({
                            name: unitName,
                            top: Math.round(rect.top),
                            is_three_star: isThreeStar
                        });
                    }
                }

                // Group by Y position (40px tolerance)
                const rows = {};
                for (const u of units) {
                    const key = Math.round(u.top / 40) * 40;
                    if (!rows[key]) rows[key] = [];
                    rows[key].push(u);
                }

                // Sort rows by Y, skip first row (main comp) and rows that belong to other comps
                const sortedKeys = Object.keys(rows).map(Number).sort((a, b) => a - b);
                if (sortedKeys.length < 2) return [];

                const mainRowY = sortedKeys[0];
                const mainRowSize = rows[mainRowY].length;

                // Find where other comps start (look for "Bài Trí Đội Hình" label position)
                const posLabel = Array.from(document.querySelectorAll('*')).find(
                    el => el.innerText && el.innerText.trim() === 'Bài Trí Đội Hình' && el.offsetHeight > 0
                );
                const posTop = posLabel ? posLabel.getBoundingClientRect().top : 99999;

                // Variation rows are between main comp row and the next full-page comp
                // Stop when we see a row with mostly different units (another comp)
                const mainUnits = new Set(rows[mainRowY].map(u => u.name));
                const compVariations = [];
                for (const key of sortedKeys) {
                    if (key <= mainRowY) continue;  // skip main comp row
                    const row = rows[key];
                    // Check if this row shares units with the main comp
                    const sharedUnits = row.filter(u => mainUnits.has(u.name)).length;
                    const shareRatio = row.length > 0 ? sharedUnits / row.length : 0;
                    // If less than 30% shared, this is a different comp - stop
                    if (shareRatio < 0.3) break;
                    if (row.length >= 3) {
                        compVariations.push(
                            row.map(u => ({
                                name: u.name,
                                is_three_star: u.is_three_star
                            }))
                        );
                    }
                }

                return compVariations;
            }
        """)

        variations.append({
            'level': tab['label'],
            'percentage': tab['percentage'],
            'comps': comps,
        })

    # Click back to "Đầu Trận" tab
    await page.evaluate("""
        () => {
            const buttons = document.querySelectorAll('button[class*="MuiTab"]');
            for (const btn of buttons) {
                if (btn.innerText.trim().startsWith('Đầu Trận') || btn.innerText.trim().startsWith('Early')) {
                    btn.click(); return;
                }
            }
        }
    """)
    await page.wait_for_timeout(500)

    return variations


async def _extract_units_with_items(
    page: Page, comp_name: str, positioning: List[str]
) -> List[Dict]:
    """Extract units and their recommended items from HTML img alt attributes.

    Uses the positioning list to identify which units belong to this comp.
    """
    return await page.evaluate("""
        (params) => {
            const compUnits = params.positioning;
            const results = [];
            const seen = new Set();

            // Scan all Unit_Wrapper divs on the page
            const wrappers = document.querySelectorAll('div[class*="Unit_Wrapper"]');

            for (const wrapper of wrappers) {
                const imgs = wrapper.querySelectorAll('img');
                const alts = Array.from(imgs).map(i => (i.alt || '').trim()).filter(a => a.length > 1);
                const isThreeStar = alts.some(a =>
                    a.includes('Three Star') || a.includes('Tướng 3 Sao'));
                const filtered = alts.filter(a =>
                    !a.includes('Unlockable') && !a.includes('Three Star') &&
                    !a.includes('Tướng 3 Sao') &&
                    a !== 'Teambuilder' && !a.includes('Copy') && !a.includes('Open In'));

                if (filtered.length >= 2) {
                    const unitName = filtered[0];
                    const itemNames = filtered.slice(1);

                    if (compUnits.includes(unitName) && !seen.has(unitName) && itemNames.length > 0) {
                        seen.add(unitName);
                        results.push({ name: unitName, items: itemNames, is_three_star: isThreeStar });
                    }
                }
            }

            // Add units from positioning that had no items
            for (const unitName of compUnits) {
                if (!seen.has(unitName)) {
                    results.push({ name: unitName, items: [], is_three_star: false });
                }
            }

            return results;
        }
    """, {'positioning': positioning})


async def _extract_augments(page: Page, lang_config) -> List[str]:
    """Extract augment names from img alt near the augments section."""
    return await page.evaluate("""
        (label) => {
            const allElements = document.querySelectorAll('*');
            for (const el of allElements) {
                const text = el.innerText ? el.innerText.trim() : '';
                if (text === label && el.offsetHeight > 0) {
                    // Look in parent for augment images
                    let container = el.parentElement;
                    for (let depth = 0; depth < 3; depth++) {
                        if (!container) break;
                        const imgs = container.querySelectorAll('img');
                        const augNames = Array.from(imgs)
                            .map(img => img.alt)
                            .filter(a => a && a.length > 2 && !a.includes('Unlockable'));
                        if (augNames.length >= 2) return augNames;
                        container = container.parentElement;
                    }
                }
            }
            return [];
        }
    """, lang_config.comp_augments)


async def _extract_carousel_components(page: Page, lang_config) -> List[str]:
    """Extract carousel priority component item names from img alt."""
    return await page.evaluate("""
        (label) => {
            // Find the exact label element (small text, not a large container)
            const allElements = document.querySelectorAll('*');
            for (const el of allElements) {
                const text = el.innerText ? el.innerText.trim() : '';
                if (text === label && el.offsetHeight > 0 && el.offsetHeight < 40) {
                    // Go up to parent that contains component images
                    let container = el.parentElement;
                    for (let depth = 0; depth < 3; depth++) {
                        if (!container) break;
                        const imgs = container.querySelectorAll('img');
                        const names = Array.from(imgs)
                            .map(img => (img.alt || '').trim())
                            .filter(a => a.length > 1);
                        if (names.length >= 3 && names.length <= 15) return names;
                        container = container.parentElement;
                    }
                }
            }
            return [];
        }
    """, lang_config.comp_carousel)


async def _extract_counters_vods(page: Page, lang_config) -> Dict:
    """Click the Counters & Vods tab and extract synergy/counter data."""
    # Click the tab using anchor (nav-link) inside the LI
    await page.evaluate("""
        (label) => {
            const links = document.querySelectorAll('a');
            for (const el of links) {
                const text = el.innerText ? el.innerText.trim() : '';
                if (text === label && el.offsetHeight > 0) {
                    el.click();
                    return true;
                }
            }
            return false;
        }
    """, lang_config.comp_counters_tab)
    await page.wait_for_timeout(1500)

    # Extract synergy and counter comps
    # Structure: "Hiệu Quả Với" (good with) + "Bất Lợi Trước" (weak against)
    # Each entry: comp name + similarity% + avg place delta
    result = await page.evaluate("""
        () => {
            const lines = document.body.innerText.split('\\n').map(l => l.trim()).filter(l => l);
            const synergies = [];
            const counters = [];

            let section = null;  // 'synergy' or 'counter'

            for (let i = 0; i < lines.length; i++) {
                const line = lines[i];

                if (line === 'Hiệu Quả Với' || line === 'Good With') {
                    section = 'synergy';
                    continue;
                }
                if (line === 'Bất Lợi Trước' || line === 'Weak Against') {
                    section = 'counter';
                    continue;
                }

                if (!section) continue;

                // Stop at VODs section or next major section
                if (line === 'Phát Sóng Twitch Gần Đây' || line === 'Recent Twitch Streams' ||
                    line === 'Xem thêm' || line === 'See More' ||
                    line.includes('Tùy Chọn') || line.includes('Tướng & Trang Bị') ||
                    line.includes('Tộc/Hệ')) break;

                // Skip labels
                if (line === 'Độ Tương Đồng' || line === 'Similarity' ||
                    line === 'Hạng TB' || line === 'Avg Place') continue;
                // Skip percentages and deltas (they're parsed via lookahead)
                if (line.endsWith('%') || line.match(/^[+-][0-9.]+$/)) continue;
                // Skip pure numbers
                if (line.match(/^[0-9.]+$/)) continue;

                // Remaining lines are comp names
                if (line.length > 3) {
                    const entry = { name: line };

                    // Look ahead for similarity% and avg_place delta
                    for (let j = i + 1; j < Math.min(i + 5, lines.length); j++) {
                        if (lines[j].endsWith('%') && !entry.similarity) {
                            entry.similarity = lines[j];
                        }
                        if ((lines[j].startsWith('+') || lines[j].startsWith('-')) &&
                            lines[j].match(/^[+-][0-9.]+$/) && !entry.avg_place_delta) {
                            entry.avg_place_delta = lines[j];
                        }
                    }

                    if (section === 'synergy') synergies.push(entry);
                    else if (section === 'counter') counters.push(entry);
                }
            }

            return { synergies, counters };
        }
    """)

    # Switch back to first tab
    await page.evaluate("""
        (label) => {
            const links = document.querySelectorAll('a');
            for (const el of links) {
                const text = el.innerText ? el.innerText.trim() : '';
                if (text === label && el.offsetHeight > 0) {
                    el.click();
                    return true;
                }
            }
            return false;
        }
    """, lang_config.comp_options_tab)
    await page.wait_for_timeout(500)

    return result
