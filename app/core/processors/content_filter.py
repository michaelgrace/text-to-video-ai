class ContentFilter:
    def __init__(self):
        self.negative_keywords = [
            "violent", "explicit", "graphic",
            "disturbing", "offensive", "inappropriate"
        ]
        self.replacement_terms = {
            "accident": "safe driving",
            "disaster": "nature scene",
            "emergency": "safety preparedness"
        }

    def filter_query(self, query: str) -> str:
        words = query.lower().split()
        filtered_words = [
            self.replacement_terms.get(word, word)
            for word in words
            if word not in self.negative_keywords
        ]
        return " ".join(filtered_words)

    def is_safe_content(self, query: str) -> bool:
        return not any(word in query.lower() for word in self.negative_keywords)
