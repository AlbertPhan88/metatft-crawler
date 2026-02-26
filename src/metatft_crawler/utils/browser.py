"""
Browser utility functions for Playwright automation
"""


async def switch_language(page, target_lang: str) -> bool:
    """
    Switch website language by clicking language selector and choosing target language.

    Args:
        page: Playwright page object
        target_lang: Target language code (e.g., 'vi' for Vietnamese)

    Returns:
        True if successful, False otherwise
    """
    try:
        # Click language selector
        selector = await page.query_selector('.LanguageSelectContainer')
        if selector:
            await selector.click()
            await page.wait_for_timeout(1500)

            # Find and click the target language option
            options = await page.query_selector_all('[role="option"]')
            for option in options:
                text = await option.text_content()
                if text and text.strip() == target_lang:
                    await option.click()
                    await page.wait_for_timeout(3000)
                    print(f"✓ Switched to {target_lang}")
                    return True

            print(f"✗ Could not find {target_lang} option")
            return False
        else:
            print("✗ Language selector not found")
            return False
    except Exception as e:
        print(f"✗ Error switching language: {e}")
        return False
