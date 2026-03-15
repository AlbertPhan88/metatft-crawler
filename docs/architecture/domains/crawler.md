# Domain Model: Crawler

## Overview

The Crawler domain handles extraction of TFT meta data from MetaTFT.com using browser automation (Playwright).

## Class Diagram

```mermaid
classDiagram
    class crawler {
        +crawl_all(language, limit) dict
    }

    class comps_crawler {
        +crawl_tft_meta(language) dict
        -_extract_comp_data(page, lang_config) list
    }

    class units_crawler {
        +crawl_all_units(language, limit_units) dict
        -_extract_unit_list(page) list
        -_extract_unit_detail(page, unit_url, lang_config) dict
    }

    class items_crawler {
        +crawl_all_items(language, limit_items) dict
        -_extract_item_list(page) list
        -_extract_item_detail(page, item_url, lang_config) dict
    }

    class augments_crawler {
        +crawl_all_augments(language, limit_augments) dict
        -_extract_from_table(page, lang_config) list
        -_extract_from_tier_list(page) list
        -_extract_descriptions(page, augments, has_table) None
    }

    class traits_crawler {
        +crawl_all_traits(language, limit_traits) dict
        -_extract_trait_list(page) list
        -_extract_trait_detail(page, trait_url) dict
    }

    class comp_detail_crawler {
        +crawl_comp_details(language, limit_comps) dict
        -_extract_comp_list(page) list
        -_expand_comp(page, comp_element) None
        -_extract_units_with_items(page) list
        -_extract_early_game_boards(page) list
        -_extract_positioning(page) list
        -_extract_augments(page) list
        -_extract_leveling_guide(page) list
        -_extract_carousel_priority(page) list
        -_extract_counters_vods(page) dict
    }

    class language_config {
        <<abstract>>
        +avg_place str
        +pick_rate str
        +win_rate str
        +traits list~str~
        +unit_types list~str~
        +footer_keywords list~str~
        +navigation_keywords list~str~
        +comp_options_tab str
        +comp_counters_tab str
        +comp_early_game str
        +comp_positioning str
        +comp_augments str
        +comp_leveling str
        +comp_carousel str
        +comp_round_win_rate str
    }

    class english_config {
    }

    class vietnamese_config {
    }

    class language_loader {
        +get_language_config(lang) language_config
        +get_supported_languages() list~str~
        -_cache dict
    }

    class browser_utils {
        +switch_language(page, target_lang) None
    }

    class csv_export {
        +units_to_csv(units_data) str
    }

    class cli {
        +main() None
        -run_comps(language, output, verbose) None
        -run_units(language, output, verbose) None
        -run_items(language, output, verbose) None
        -run_augments(language, output, verbose) None
        -run_traits(language, output, verbose) None
    }

    crawler <|-- comps_crawler
    crawler <|-- units_crawler
    crawler <|-- items_crawler
    crawler <|-- augments_crawler
    crawler <|-- traits_crawler
    crawler <|-- comp_detail_crawler

    language_config <|-- english_config
    language_config <|-- vietnamese_config

    language_loader --> language_config : creates/caches

    comps_crawler --> language_loader : uses
    units_crawler --> language_loader : uses
    items_crawler --> language_loader : uses
    augments_crawler --> language_loader : uses
    traits_crawler --> language_loader : uses
    comp_detail_crawler --> language_loader : uses

    comps_crawler --> browser_utils : uses
    units_crawler --> browser_utils : uses
    items_crawler --> browser_utils : uses
    augments_crawler --> browser_utils : uses
    traits_crawler --> browser_utils : uses
    comp_detail_crawler --> browser_utils : uses

    cli --> comps_crawler : invokes
    cli --> units_crawler : invokes
    cli --> items_crawler : invokes
    cli --> augments_crawler : invokes
    cli --> traits_crawler : invokes
    cli --> comp_detail_crawler : invokes
    cli --> csv_export : uses
```

## Entity Descriptions

### Crawlers

| Entity | Responsibility | Data Extracted |
|--------|---------------|----------------|
| `comps_crawler` | Extract team compositions | Comp names, units, items, win/pick/top4 rates |
| `units_crawler` | Extract unit details | Stats, abilities, builds, items, traits, positioning |
| `items_crawler` | Extract item details | Name, stats (AD/AP/AS/etc.), trait number, description |
| `augments_crawler` | Extract augment details | Name, tier (S/A/B/C/D), type, description |
| `traits_crawler` | Extract trait details | Name, ability description |
| `comp_detail_crawler` | Extract detailed comp data | Units with items, early game boards, positioning, augments, leveling guide, carousel priority, counters/VODs |

### Language System

| Entity | Responsibility |
|--------|---------------|
| `language_config` | Abstract base defining 30+ language-specific attributes |
| `english_config` | English labels, keywords, traits |
| `vietnamese_config` | Vietnamese labels + English fallbacks for page matching |
| `language_loader` | Factory with caching, case-insensitive lookup |

### Utilities

| Entity | Responsibility |
|--------|---------------|
| `browser_utils` | Playwright language switching via DOM selector |
| `csv_export` | Convert unit JSON data to CSV format |
| `cli` | Command-line interface with argparse |

## Standard Output Format

All crawlers return:

```json
{
  "timestamp": "ISO-8601",
  "source": "https://www.metatft.com/{endpoint}",
  "language": "en|vi",
  "total_{type}_found": N,
  "total_{type}_crawled": N,
  "{type}": [...]
}
```

## Business Rules

| ID | Rule | Applies To |
|----|------|-----------|
| BR-01 | Never hardcode language strings in crawler code | All crawlers |
| BR-02 | All crawlers must support `language` and `limit` parameters | All crawlers |
| BR-03 | Language config must be passed to JavaScript via `page.evaluate()` | All crawlers |
| BR-04 | Adding a new language requires only a new config file + loader update | Language system |
| BR-05 | Crawlers must handle page structure differences between languages | All crawlers |
| BR-06 | Description extraction must achieve >95% success rate | Items, augments, traits |
