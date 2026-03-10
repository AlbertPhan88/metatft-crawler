#!/usr/bin/env python3
"""
TFT Augments Crawler - Extracts augment data from MetaTFT.com/augments
"""

import asyncio
import json
from datetime import datetime
from playwright.async_api import async_playwright
from typing import Dict, Any

from ..utils.browser import switch_language
from ..languages.loader import get_language_config


async def crawl_all_augments(language: str = "en", limit_augments: int = None) -> Dict[str, Any]:
    """
    Crawl MetaTFT.com/augments and extract data for augments.

    Args:
        language: Language code ('en' for English, 'vi' for Vietnamese, etc.)
        limit_augments: Limit crawling to N augments (None = crawl all). Useful for testing/demos.

    Returns:
        Dictionary containing timestamp and augment data
    """

    # Use the same base URL for all languages - language switching is done via selector
    base_url = "https://www.metatft.com/augments"

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

        # Switch language if needed
        if language == "vi":
            print("Switching to Vietnamese...")
            await switch_language(page, "vi")

        # Get language configuration
        lang_config = get_language_config(language)

        # Try switching to Table view (available on English, not on Vietnamese)
        print("Attempting to switch to Table view...")
        has_table = await page.evaluate("""
            () => {
                const tableDiv = Array.from(document.querySelectorAll('div'))
                    .find(div => div.innerText.trim() === 'Table' &&
                          div.className.includes('StatOptionChip'));
                if (tableDiv) { tableDiv.click(); return true; }
                return false;
            }
        """)
        await page.wait_for_timeout(2000)

        if has_table:
            print("Table view available - using table extraction")
            augments_data = await page.evaluate("""
                (langConfig) => {
                    const augments = [];
                    const lines = document.body.innerText.split('\\n');
                    let contentStartIdx = -1;
                    let contentEndIdx = lines.length;
                    const footerKeywords = langConfig.footer_keywords;

                    for (let i = 0; i < lines.length; i++) {
                        const line = lines[i].trim();
                        if ((line === 'Type' || line === 'Loại') && contentStartIdx === -1) {
                            contentStartIdx = i + 1;
                        }
                        if (contentStartIdx !== -1 && i > contentStartIdx + 50) {
                            const keywordMatches = footerKeywords.filter(kw => line.includes(kw));
                            if (keywordMatches.length > 0 && (line.length < 20 || keywordMatches.length > 1)) {
                                contentEndIdx = i;
                                break;
                            }
                        }
                    }

                    const tierPattern = /^[SABCD]$/;
                    const typeValues = new Set([
                        'Combat', 'Econ', 'Items', 'Scaling', 'Strategic', 'Traits',
                        'Attack', 'Fighter', 'Caster', 'Support', 'Tank',
                        'Void', 'Magic', 'Marksman', 'Zaun', 'Yordle', 'Duelist',
                        'Visionary', 'Knight', 'Assassin', 'Mage', 'Ranger'
                    ]);

                    if (contentStartIdx === -1) {
                        for (let i = 0; i < lines.length; i++) {
                            if (tierPattern.test(lines[i].trim())) {
                                contentStartIdx = i;
                                break;
                            }
                        }
                    }

                    for (let i = contentStartIdx; i < contentEndIdx; i++) {
                        const line = lines[i].trim();
                        if (!line || line === 'Augment' || line === 'Tier' || line === 'Type') continue;
                        if (tierPattern.test(line)) continue;
                        if (typeValues.has(line)) continue;

                        if (line.length > 1 && line.length < 100) {
                            let tier = null;
                            let type = null;
                            for (let j = i + 1; j < Math.min(i + 10, contentEndIdx); j++) {
                                const nextLine = lines[j].trim();
                                if (tierPattern.test(nextLine)) {
                                    tier = nextLine;
                                    for (let k = j + 1; k < Math.min(j + 5, contentEndIdx); k++) {
                                        const typeLine = lines[k].trim();
                                        if (typeLine && !tierPattern.test(typeLine) &&
                                            typeLine !== line && typeLine.length < 100) {
                                            type = typeLine;
                                            break;
                                        }
                                    }
                                    break;
                                }
                            }
                            if (tier && type) {
                                augments.push({ name: line, tier, type, description: '' });
                                i += 4;
                            }
                        }
                    }
                    return augments;
                }
            """, {
                'navigation_keywords': lang_config.navigation_keywords,
                'footer_keywords': lang_config.footer_keywords,
            })
        else:
            print("No Table view - using tier-list extraction")
            augments_data = await page.evaluate("""
                (langConfig) => {
                    const augments = [];
                    const lines = document.body.innerText.split('\\n').map(l => l.trim()).filter(l => l);
                    const tierPattern = /^[SABCD]$/;
                    const stagePattern = /^\\d+-\\d+$/;

                    // Footer/site content keywords to stop extraction
                    const stopKeywords = [
                        // Vietnamese site sections
                        'Tính Năng', 'Đội Hình Meta', 'Lịch Sử Đấu', 'Công Cụ',
                        'Tạo Đội Hình', 'Thư Viện VOD', 'Bảng Trả Đồ', 'Tải Ứng Dụng',
                        'Patreon', 'Mạng Xã Hội', 'Trình Khám Phá', 'Số Liệu Tướng',
                        'Phân Hạng Nâng Cấp', 'Thêm Tính Năng',
                        // English footer
                        'Privacy', 'Cookie', 'GitHub', 'Discord',
                        // Vietnamese footer
                        'Bảo Mật', 'Liên Hệ',
                    ];
                    // Also use footer keywords from lang config
                    const allStopKeywords = stopKeywords.concat(langConfig.footer_keywords || []);

                    // Find first stage selector to locate augment content area
                    let firstStageIdx = -1;
                    for (let i = 0; i < lines.length; i++) {
                        if (stagePattern.test(lines[i])) { firstStageIdx = i; break; }
                    }

                    // Find tier marker positions after stage selectors
                    const tierPositions = [];
                    for (let i = (firstStageIdx >= 0 ? firstStageIdx : 0); i < lines.length; i++) {
                        if (tierPattern.test(lines[i])) {
                            tierPositions.push({ index: i, tier: lines[i] });
                        }
                    }

                    // Extract augment names between consecutive tier markers
                    let stopped = false;
                    for (let t = 0; t < tierPositions.length && !stopped; t++) {
                        const tier = tierPositions[t].tier;
                        const startIdx = tierPositions[t].index + 1;
                        const endIdx = t + 1 < tierPositions.length
                            ? tierPositions[t + 1].index
                            : lines.length;

                        for (let i = startIdx; i < endIdx; i++) {
                            const line = lines[i];
                            if (!line || line.length <= 1 || stagePattern.test(line)) continue;

                            // Stop if we hit footer/site content
                            if (allStopKeywords.some(kw => line.includes(kw))) {
                                stopped = true;
                                break;
                            }

                            augments.push({ name: line, tier: tier, type: null, description: '' });
                        }
                    }
                    return augments;
                }
            """, {
                'footer_keywords': lang_config.footer_keywords,
            })

        # Apply limit before extracting descriptions to save time
        if limit_augments is not None:
            augments_data = augments_data[:limit_augments]
            print(f"Limited to {len(augments_data)} augments for demo")

        total_found = len(augments_data)
        print(f"Found {total_found} augments")

        # Now extract descriptions by hovering over each augment (sequential with 500ms wait)
        print(f"Extracting descriptions for {len(augments_data)} augments (500ms wait)...")
        for i, augment in enumerate(augments_data):
            try:
                if has_table:
                    elements = await page.query_selector_all(f"table tr >> text={augment['name']}")
                else:
                    # For list view, find elements with exact text match
                    all_elements = await page.query_selector_all(f"text={augment['name']}")
                    elements = []
                    for elem in all_elements:
                        text = await elem.inner_text()
                        if text.strip() == augment['name']:
                            elements.append(elem)
                    if not elements:
                        elements = all_elements[:1]

                if elements:
                    await elements[0].hover()
                    await page.wait_for_timeout(500)

                    description = await page.evaluate("""
                        (augmentName) => {
                            const tooltips = document.querySelectorAll(
                                '[role="tooltip"], [class*="MuiTooltip-tooltip"]'
                            );
                            for (let tooltip of tooltips) {
                                const text = tooltip.innerText || tooltip.textContent;
                                if (text && text.includes(augmentName)) {
                                    const descPart = text.replace(augmentName, '').trim();
                                    if (descPart.length > 0) return descPart;
                                }
                            }
                            return '';
                        }
                    """, augment['name'])

                    if description:
                        augment['description'] = description

                if (i + 1) % 50 == 0:
                    desc_so_far = sum(1 for a in augments_data[:i+1] if a.get('description'))
                    print(f"  Progress: {i + 1}/{len(augments_data)} ({desc_so_far} descriptions)")

            except Exception:
                pass

        desc_count = sum(1 for a in augments_data if a.get('description'))
        print(f"Descriptions extracted: {desc_count}/{len(augments_data)}")

        await browser.close()

        return {
            "timestamp": datetime.now().isoformat(),
            "source": base_url,
            "language": language,
            "total_augments_found": total_found,
            "total_augments_crawled": len(augments_data),
            "augments": augments_data,
        }


async def main(language: str = "en", limit_augments: int = None):
    """Main entry point for the crawler."""
    result = await crawl_all_augments(language=language, limit_augments=limit_augments)
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    import sys
    lang = sys.argv[1] if len(sys.argv) > 1 else "en"
    asyncio.run(main(language=lang))
