#!/usr/bin/env python3
"""
TFT Traits Crawler - Extracts trait data from MetaTFT.com/traits
"""

import asyncio
import json
from datetime import datetime
from playwright.async_api import async_playwright
from typing import Dict, List, Any

from ..utils.browser import switch_language
from ..languages.loader import get_language_config


async def crawl_all_traits(language: str = "en", limit_traits: int = None) -> Dict[str, Any]:
    """
    Crawl MetaTFT.com/traits and extract data for traits.

    Args:
        language: Language code ('en' for English, 'vi' for Vietnamese, etc.)
        limit_traits: Limit crawling to N traits (None = crawl all). Useful for testing.

    Returns:
        Dictionary containing timestamp and trait data
    """

    # Use the same base URL for all languages - language switching is done via selector
    base_url = "https://www.metatft.com/traits"

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

        # Extract all trait links from the main traits page
        print("Extracting all traits and their links...")
        traits_list = await page.evaluate("""
            () => {
                const traits = [];

                // Find all trait links on the page
                const allLinks = Array.from(document.querySelectorAll('a[href*="/traits/"]'));
                const traitLinks = allLinks.filter(a => {
                    const href = a.getAttribute('href') || '';
                    return href.startsWith('/traits/') && !href.endsWith('/traits');
                });

                // Extract trait data from the links
                const uniqueTraits = new Set();
                traitLinks.forEach(link => {
                    const href = link.getAttribute('href');
                    const traitName = link.innerText.trim();

                    if (traitName && !uniqueTraits.has(traitName)) {
                        uniqueTraits.add(traitName);
                        traits.push({
                            name: traitName,
                            url: href
                        });
                    }
                });

                return traits;
            }
        """)

        print(f"Found {len(traits_list)} traits")

        # Limit traits if specified
        if limit_traits:
            traits_list = traits_list[:limit_traits]
            print(f"Limited to {len(traits_list)} traits")

        # Crawl detailed data for each trait
        traits_data = []
        for i, trait_info in enumerate(traits_list, 1):
            print(f"\n[{i}/{len(traits_list)}] Crawling {trait_info['name']}...")
            try:
                trait_url = f"https://www.metatft.com{trait_info['url']}"
                await page.goto(trait_url, wait_until="domcontentloaded", timeout=60000)
                await page.wait_for_timeout(2000)

                # Extract trait details
                trait_details = await page.evaluate("""
                    (langConfig) => {
                        const pageText = document.body.innerText;
                        const lines = pageText.split('\\n').map(l => l.trim()).filter(l => l);

                        let traitName = null;
                        let description = null;

                        // Strategy 1: Find the back link (language-specific from config)
                        let contentStartIdx = -1;
                        for (let i = 0; i < lines.length; i++) {
                            if (lines[i].includes(langConfig.traits_back_link)) {
                                contentStartIdx = i + 1;
                                break;
                            }
                        }

                        // If we found the back link, the next non-empty line should be the trait name
                        if (contentStartIdx > 0 && contentStartIdx < lines.length) {
                            traitName = lines[contentStartIdx];
                        }

                        // Strategy 2: If not found, look for short lines (likely trait names) followed by longer description
                        if (!traitName) {
                            for (let i = 5; i < lines.length && i < 50; i++) {
                                const line = lines[i];
                                const nextLine = i + 1 < lines.length ? lines[i + 1] : '';

                                // Trait names are typically short (20-40 chars) and followed by longer descriptions
                                // Skip lines that match known meta stat keywords
                                let isMetaStat = langConfig.traits_meta_stat_keywords.some(kw => line.includes(kw));

                                if (line.length > 5 && line.length < 60 && !isMetaStat &&
                                    nextLine.length > 50) {
                                    traitName = line;
                                    contentStartIdx = i;
                                    break;
                                }
                            }
                        }

                        // Strategy 3: Fallback to h2 or h3 headings
                        if (!traitName) {
                            const heading = document.querySelector('h2, h3');
                            if (heading) {
                                traitName = heading.innerText.trim();
                            }
                        }

                        // Extract trait description - look for ability text
                        // It should be right after the trait name
                        let descriptionLines = [];
                        let startIdx = contentStartIdx > 0 ? contentStartIdx + 1 : 0;

                        for (let i = startIdx; i < lines.length; i++) {
                            const line = lines[i];

                            // Stop at known metadata sections (use language-specific keywords)
                            let isMetaStat = langConfig.traits_meta_stat_keywords.some(kw => line.includes(kw));
                            if (isMetaStat || line.match(/^\\d+,\\d+$/) || (line.match(/^\\d+$/) && line.length < 3)) {
                                // We've hit stats, stop collecting
                                break;
                            }

                            // Skip short placeholder lines
                            if (line.length < 5) {
                                continue;
                            }

                            // Skip long content summaries that look like page intro text
                            if (line.length > 100) {
                                continue;
                            }

                            // Collect ability description text (but skip generic stat labels)
                            if (line.length > 10 && !line.includes('Stats on how')) {
                                descriptionLines.push(line);
                            }

                            // Stop after we have collected ability description (usually 2-5 lines max)
                            if (descriptionLines.length >= 5) {
                                break;
                            }
                        }

                        if (descriptionLines.length > 0) {
                            description = descriptionLines.join('\\n');
                        }

                        return {
                            name: traitName,
                            description: description
                        };
                    }
                """, {
                    'traits_back_link': lang_config.traits_back_link,
                    'traits_meta_stat_keywords': lang_config.traits_meta_stat_keywords,
                })

                traits_data.append(trait_details)
                print(f"  ✓ {trait_details['name']}")
                if trait_details['description']:
                    # Print first 80 chars of description
                    desc_preview = trait_details['description'].replace('\\n', ' ')[:80]
                    print(f"    Description: {desc_preview}...")

            except Exception as e:
                print(f"  ✗ Error crawling {trait_info['name']}: {e}")

        await browser.close()

        # Return structured data
        return {
            "timestamp": datetime.now().isoformat(),
            "source": base_url,
            "language": language,
            "total_traits_found": len(traits_list),
            "total_traits_crawled": len(traits_data),
            "traits": traits_data
        }


async def main(language: str = "en", limit_traits: int = None):
    """Main entry point for the crawler."""
    result = await crawl_all_traits(language=language, limit_traits=limit_traits)
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    import sys
    lang = sys.argv[1] if len(sys.argv) > 1 else "en"
    asyncio.run(main(language=lang))
