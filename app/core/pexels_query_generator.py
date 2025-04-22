import json
from pathlib import Path

def load_negative_keywords(json_path=None):
    # Default path to negative_keywords.json in schemas directory
    if json_path is None:
        json_path = Path(__file__).parent.parent / "schemas" / "negative_keywords.json"
    if Path(json_path).exists():
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict) and "negative_keywords" in data:
                return set(data["negative_keywords"])
            elif isinstance(data, list):
                return set(data)
    return set()

def build_pexels_query(theme, topic, negative_keywords=None):
    """
    Returns a query string for Pexels API, combining theme and topic,
    and appending negative keywords as exclusions.
    """
    if negative_keywords is None:
        negative_keywords = load_negative_keywords()
    # Build base query
    query = f"{theme.strip()} {topic.strip()}"
    # Append negative keywords as exclusions (e.g., -car -blood)
    if negative_keywords:
        query += " " + " ".join(f"-{kw}" for kw in negative_keywords)
    return query.strip()

# Example usage:
# theme = "wild animals"
# topic = "jaguar"
# query = build_pexels_query(theme, topic)
# print(query)
