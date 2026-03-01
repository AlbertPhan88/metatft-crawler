"""
English language configuration for MetaTFT Crawler.
"""

from .base import LanguageConfig


class EnglishConfig(LanguageConfig):
    """English language-specific strings and patterns."""

    def __init__(self):
        # Comps page stats labels
        self.avg_place = "Avg Place"
        self.pick_rate = "Pick Rate"
        self.win_rate = "Win Rate"
        self.top_4_rate = "Top 4 Rate"

        # Units page tab labels
        self.ability_label = "Ability"
        self.stats_label = "Stats"

        # Unit base stats labels (shown in Stats tab)
        self.health = "Health"
        self.mana = "Mana"
        self.attack_damage = "Attack Damage"
        self.ability_power = "Ability Power"
        self.armor = "Armor"
        self.magic_resist = "Magic Resist"
        self.attack_speed = "Attack Speed"
        self.crit_chance = "Crit Chance"
        self.crit_damage = "Crit Damage"
        self.range = "Range"

        # Ability description markers
        self.passive_marker = "Passive:"
        self.active_marker = "Active:"
        self.unlock_marker = "Unlock:"

        # List of known traits
        self.traits = [
            "Attack",
            "Fighter",
            "Void",
            "Riftscourge",
            "Magic",
            "Marksman",
            "Zaun",
            "Zaunite",
            "Yordle",
            "Longshot",
            "Duelist",
            "Visionary",
            "Knight",
            "Assassin",
            "Mage",
            "Ranger",
            "Support",
            "Tank",
            "Bruiser",
            "Shurima",
            "Noxus",
            "Piltover",
            "Demacia",
            "Ionia",
            "Shadow",
            "Star",
            "Caretaker",
            "Chemtech",
            "Corrupt",
            "Enforcer",
        ]

        # Unit types
        self.unit_types = ["Attack", "Fighter", "Caster", "Support", "Tank"]

        # Items page labels
        self.tft_item_stats = "TFT Item Stats"
        self.item_stats_labels = []  # English doesn't need alternate labels

        # Unit page build/items labels
        self.top_items_label = "Top Items"
        self.recommended_builds_label = "Recommended Builds"

        # Augments page keywords
        self.navigation_keywords = [
            "MetaTFT",
            "Comps",
            "Units",
            "Items",
            "Traits",
            "Download",
            "Advertise",
            "Terms",
        ]

        self.footer_keywords = [
            "Privacy",
            "Cookies",
            "Sitemap",
            "Contact",
            "GitHub",
            "Twitter",
            "Discord",
            "Advertise With Us",
        ]
