"""
Vietnamese language configuration for MetaTFT Crawler.
"""

from .base import LanguageConfig


class VietnameseConfig(LanguageConfig):
    """Vietnamese language-specific strings and patterns."""

    def __init__(self):
        # Comps page stats labels
        self.avg_place = "Hạng TB"
        self.pick_rate = "Tỷ Lệ Chọn"
        self.win_rate = "Tỷ Lệ Thắng"
        self.top_4_rate = "Tỷ Lệ Top 4"

        # Units page tab labels (Vietnamese translations)
        self.ability_label = "Kỹ Năng"  # Vietnamese for "Ability"
        self.stats_label = "Số Liệu"  # Vietnamese for "Stats"

        # Unit base stats labels (shown in Stats tab)
        self.health = "Máu"  # Vietnamese for "Health"
        self.mana = "Mana"  # Stays English on Vietnamese page
        self.attack_damage = "Sát thương tấn công"  # Vietnamese for "Attack Damage"
        self.ability_power = "Sát thương kỹ năng"  # Vietnamese for "Ability Power"
        self.armor = "Giáp"  # Vietnamese for "Armor"
        self.magic_resist = "Kháng phép"  # Vietnamese for "Magic Resist"
        self.attack_speed = "Attack Speed"  # May be same or translated
        self.crit_chance = "Crit Chance"  # May be same or translated
        self.crit_damage = "Crit Damage"  # May be same or translated
        self.range = "Range"  # May be same or translated

        # Ability description markers (Vietnamese translations)
        self.passive_marker = "Nội Tại:"  # Vietnamese for "Passive:"
        self.active_marker = "Kích Hoạt:"  # Vietnamese for "Active:"
        self.unlock_marker = "Unlock:"  # Stays same in Vietnamese

        # List of known traits (English names game-internal, plus Vietnamese equivalents for page matching)
        # When traits are shown on Vietnamese pages, they appear in Vietnamese
        self.traits = [
            # English versions (game terms)
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
            # Vietnamese versions (as shown on Vietnamese page)
            "Vật Lý",  # Attack
            "Đấu Sĩ",  # Fighter
            "Hư Không",  # Void
            "Tai Ương",  # Riftscourge
            "Phép Thuật",  # Magic
            "Xạ Thủ",  # Marksman
            "Zaun",  # Same
            "Người Zaun",  # Zaunite
            "Tí Hon",  # Yordle
            "Bắn Xa",  # Longshot
            "Thoái Ích Chủ",  # Duelist
            "Tiên Tri",  # Visionary
            "Hiệp Sĩ",  # Knight
            "Sát Thủ",  # Assassin
            "Pháp Sư",  # Mage
            "Cung Thủ",  # Ranger
            "Hỗ Trợ",  # Support
            "Quân Áo",  # Tank
            "Rú Thổ",  # Bruiser
            "Shurima",  # Same
            "Noxus",  # Same
            "Piltover",  # Same
            "Demacia",  # Same
            "Ionia",  # Same
            "Bóng Tối",  # Shadow
            "Sao",  # Star
            "Người Chăm Sóc",  # Caretaker
            "Hóa Học",  # Chemtech
            "Bị Thối",  # Corrupt
            "Cảnh Sát",  # Enforcer
        ]

        # Unit types (both English and Vietnamese to support page matching)
        self.unit_types = [
            # English versions (game terms)
            "Attack", "Fighter", "Caster", "Support", "Tank", "Marksman", "Oracle",
            # Vietnamese versions (as shown on Vietnamese page)
            "Đấu Sĩ",      # Fighter
            "Vật Lý",      # Attack
            "Pháp Sư",     # Mage/Caster
            "Hỗ Trợ",      # Support
            "Quân Áo",     # Tank
            "Xạ Thủ",      # Marksman
            "Viễn Kích",   # Longshot (also appears as unit type)
            "Thuật Sư",    # Oracle
        ]

        # Items page labels
        self.tft_item_stats = "Số Liệu Trang Bị"
        self.item_stats_labels = ["Số Liệu Trang Bị", "Thống kê"]

        # Unit page build/items labels (Vietnamese translations)
        self.top_items_label = "Trang Bị Hàng Đầu"  # Vietnamese for "Top Items"
        self.recommended_builds_label = "Lối Chơi Đề Xuất"  # Vietnamese for "Recommended Builds"

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
            # English footer keywords (for English pages)
            "Privacy",
            "Cookies",
            "Sitemap",
            "Contact",
            "GitHub",
            "Twitter",
            "Discord",
            "Advertise With Us",
            # Vietnamese footer keywords (for Vietnamese pages)
            "Bảo Mật",
            "Cookie",
            "Liên Hệ",
            "Sơ Đồ",
        ]

        # Traits page keywords
        self.traits_back_link = "Quay về"  # Vietnamese for "Back to Traits"
        self.traits_meta_stat_keywords = [
            # English keywords (for English pages)
            "Avg Place",
            "Pick Rate",
            "Placements",
            "Stats",
            "1st",
            "2nd",
            "3rd",
            "Download",
            # Vietnamese keywords (for Vietnamese pages)
            "Hạng TB",
            "Tỷ Lệ",
            "Thống kê",
            "Tải Xuống",
            "Tộc/Hệ",  # Traits section header in Vietnamese
        ]
