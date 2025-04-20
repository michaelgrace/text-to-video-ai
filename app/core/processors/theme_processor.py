from enum import Enum
from typing import List, Dict

class VideoTheme(Enum):
    NATURE = "nature"
    URBAN = "urban"
    PEOPLE = "people"
    ABSTRACT = "abstract"
    TECHNOLOGY = "technology"

class ThemeManager:
    def __init__(self):
        self.theme_keywords: Dict[VideoTheme, List[str]] = {
            VideoTheme.NATURE: ["nature", "wildlife", "forest", "ocean"],
            VideoTheme.URBAN: ["city", "street", "building", "urban"],
            VideoTheme.PEOPLE: ["people", "crowd", "person", "human"],
            VideoTheme.ABSTRACT: ["abstract", "pattern", "texture", "light"],
            VideoTheme.TECHNOLOGY: ["tech", "digital", "computer", "device"]
        }

    def filter_by_theme(self, query: str, theme: VideoTheme) -> str:
        theme_words = self.theme_keywords[theme]
        return f"{query} {' '.join(theme_words)}"
