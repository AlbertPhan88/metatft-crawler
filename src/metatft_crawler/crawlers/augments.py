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

        # First, click on Table view to get structured data
        print("Switching to Table view...")
        await page.evaluate("""
            () => {
                const tableDiv = Array.from(document.querySelectorAll('div'))
                    .find(div => div.innerText === 'Table' && div.className.includes('StatOptionChip'));
                if (tableDiv) tableDiv.click();
            }
        """)
        await page.wait_for_timeout(2000)

        # First, extract basic augment data (name, tier, type)
        print("Extracting augment names, tiers, and types...")
        augments_data = await page.evaluate("""
            (langConfig) => {
                const augments = [];
                const pageText = document.body.innerText;

                // Split by newlines and handle tabs
                const lines = pageText.split('\\n');

                // Find the content boundaries
                // Look for the "Type" header to find where augments start
                let contentStartIdx = -1;
                let contentEndIdx = lines.length;

                // Use language-specific keywords from config
                const navKeywords = langConfig.navigation_keywords;
                const footerKeywords = langConfig.footer_keywords;

                for (let i = 0; i < lines.length; i++) {
                    const line = lines[i].trim();
                    // Start after we see the table headers (look for 'Type' in English or 'Loại' in Vietnamese, or 'Tier' marker)
                    if ((line === 'Type' || line === 'Loại' || line === 'Bậc') && contentStartIdx === -1) {
                        contentStartIdx = i + 1;
                    }
                    // Stop when we hit footer content (only after processing enough content)
                    // Look for lines that are ONLY footer keywords or multiple keywords together
                    if (contentStartIdx !== -1 && i > contentStartIdx + 50) {
                        const keywordMatches = footerKeywords.filter(kw => line.includes(kw));
                        // Only stop if line contains a footer keyword alone or multiple keywords
                        if (keywordMatches.length > 0 && (line.length < 20 || keywordMatches.length > 1)) {
                            contentEndIdx = i;
                            break;
                        }
                    }
                }

                // Extract augments from the main content area
                const tierPattern = /^[SABCD]$/;

                // Handle case where contentStartIdx was never set (no headers found)
                if (contentStartIdx === -1) {
                    // Vietnamese version - look for first tier marker
                    for (let i = 0; i < lines.length; i++) {
                        if (tierPattern.test(lines[i].trim())) {
                            contentStartIdx = i;
                            break;
                        }
                    }
                }

                for (let i = contentStartIdx; i < contentEndIdx; i++) {
                    const line = lines[i].trim();

                    // Skip empty lines and known patterns
                    if (!line || line === 'Augment' || line === 'Tier' || line === 'Type') {
                        continue;
                    }

                    // Skip tier markers
                    if (tierPattern.test(line)) {
                        continue;
                    }

                    // Check if this might be an augment name
                    if (line && line.length > 1 && line.length < 100) {
                        const augmentName = line;
                        let tier = null;
                        let type = null;

                        // Look ahead for tier
                        for (let j = i + 1; j < Math.min(i + 10, contentEndIdx); j++) {
                            const nextLine = lines[j].trim();

                            if (tierPattern.test(nextLine)) {
                                tier = nextLine;

                                // Look for type after tier
                                for (let k = j + 1; k < Math.min(j + 5, contentEndIdx); k++) {
                                    const typeLine = lines[k].trim();
                                    if (typeLine && !tierPattern.test(typeLine) && typeLine !== augmentName &&
                                        typeLine.length < 100) {
                                        type = typeLine;
                                        break;
                                    }
                                }
                                break;
                            }
                        }

                        if (tier && type) {
                            augments.push({
                                name: augmentName,
                                tier: tier,
                                type: type,
                                description: ''
                            });

                            // Skip ahead past this augment's properties
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

        # Now extract descriptions by hovering over each augment (sequential with 100ms wait)
        print(f"Extracting descriptions for {len(augments_data)} augments (100ms wait)...")
        for i, augment in enumerate(augments_data):
            try:
                # Find the element with this augment name and hover over it
                elements = await page.query_selector_all(f"text={augment['name']}")

                if elements:
                    elem = elements[0]
                    # Hover over the element using Playwright
                    await elem.hover()
                    # Wait for tooltip to appear (reduced from 500ms to 100ms)
                    await page.wait_for_timeout(100)

                    # Extract tooltip description
                    description = await page.evaluate(f"""
                        () => {{
                            const augmentName = {json.dumps(augment['name'])};

                            // Find tooltip elements
                            const tooltips = document.querySelectorAll('[role="tooltip"], [class*="MuiTooltip-tooltip"]');
                            for (let tooltip of tooltips) {{
                                const text = tooltip.innerText || tooltip.textContent;
                                if (text && text.includes(augmentName)) {{
                                    // Extract just the description part (after augment name)
                                    const descPart = text.replace(augmentName, '').trim();
                                    if (descPart.length > 0) {{
                                        return descPart;
                                    }}
                                }}
                            }}

                            return '';
                        }}
                    """)

                    if description:
                        augment['description'] = description

                if (i + 1) % 50 == 0:
                    print(f"  Extracted {i + 1}/{len(augments_data)} descriptions")

            except Exception as e:
                # If extraction fails, keep empty description
                pass

        # Print what we found
        print(f"Found {len(augments_data)} augments")

        # Apply limit if specified
        if limit_augments is not None:
            augments_data = augments_data[:limit_augments]
            print(f"Limited to {len(augments_data)} augments for demo")

        await browser.close()

        return {
            "timestamp": datetime.now().isoformat(),
            "source": "https://www.metatft.com/augments",
            "total_augments": len(augments_data),
            "augments": augments_data
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
