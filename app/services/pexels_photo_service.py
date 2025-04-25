import os
import requests
import re
import json
from nltk.stem import PorterStemmer
from app.utils.helpers import log_response, LOG_TYPE_PEXEL

# Load negative keywords from JSON
NEGATIVE_KEYWORDS_PATH = os.path.join(os.path.dirname(__file__), "../schemas/negative_keywords.json")
with open(NEGATIVE_KEYWORDS_PATH, "r") as f:
    NEGATIVE_KEYWORDS = set(json.load(f)["negative_keywords"])

PEXELS_API_KEY = os.environ.get('PEXELS_API_KEY')

def contains_negative_keyword(text):
    if not text:
        return False
    text_lower = text.lower()
    for neg in NEGATIVE_KEYWORDS:
        if neg.lower() in text_lower:
            return True
    return False

def search_photos(query_string, orientation_landscape=True, theme=None, aspect_ratio="landscape"):
    print(f"PEXELS PHOTO QUERY: {query_string}")
    url = "https://api.pexels.com/v1/search"
    headers = {
        "Authorization": PEXELS_API_KEY,
        "User-Agent": "Mozilla/5.0"
    }
    params = {
        "query": query_string,
        "orientation": "landscape" if orientation_landscape else "portrait",
        "per_page": 40  # Increase for more diversity
    }
    response = requests.get(url, headers=headers, params=params)
    json_data = response.json()
    # --- Add debug logging ---
    print(f"PEXELS PHOTO QUERY: {query_string}")
    for photo in json_data.get('photos', []):
        print(f"  Photo: {photo.get('id')} | Alt: {photo.get('alt')} | Photographer: {photo.get('photographer')} | URL: {photo['src'].get('original')}")
    return json_data

def select_best_photo(
    query_string,
    orientation_landscape=True,
    theme=None,
    topic=None,
    aspect_ratio="landscape",
    used_photo_ids=None,
    used_photographers=None,
    relax_filters=False,
    force_theme_only=False
):
    # Step 1: Build the query
    # --- Always prepend theme to the query for every segment ---
    if theme:
        search_query = f"{theme.strip()} {query_string.strip()}"
    else:
        search_query = query_string.strip()
    # If force_theme_only, ignore query_string and use only theme/topic
    if force_theme_only and (theme or topic):
        search_query = theme or topic

    photos_json = search_photos(search_query, orientation_landscape, theme, aspect_ratio)
    photos = photos_json.get('photos', [])

    # Fuzzy/Plural Matching: Use stemming for keywords and metadata
    stemmer = PorterStemmer()
    query_keywords = set()
    for term in search_query.split():
        query_keywords.update(stemmer.stem(word.lower()) for word in re.findall(r'\w+', term))

    if used_photo_ids is None:
        used_photo_ids = set()
    if used_photographers is None:
        used_photographers = set()

    # Negative keyword filter and diversity filter
    filtered_photos = []
    for photo in photos:
        meta_fields = [
            str(photo.get('url', '')).lower(),
            str(photo.get('alt', '')).lower(),
            str(photo.get('photographer', '')).lower(),
            " ".join([str(tag).lower() for tag in photo.get('tags', [])]) if 'tags' in photo else "",
        ]
        if any(contains_negative_keyword(field) for field in meta_fields):
            continue
        if photo['id'] in used_photo_ids:
            continue
        photographer = photo.get('photographer', '')
        if photographer and photographer in used_photographers:
            continue
        filtered_photos.append(photo)

    # Step 2: Require theme/topic in alt/tags/url for relevance
    def has_theme_or_topic(photo):
        meta = (
            str(photo.get('alt', '')).lower() + " " +
            str(photo.get('url', '')).lower() + " " +
            " ".join([str(tag).lower() for tag in photo.get('tags', [])])
        )
        if theme and theme.lower() in meta:
            return True
        if topic and topic.lower() in meta:
            return True
        return False

    # Filter for strict or relaxed requirements
    if orientation_landscape:
        filtered_photos = [
            photo for photo in filtered_photos
            if photo['width'] >= (1280 if relax_filters else 1920)
            and photo['height'] >= (720 if relax_filters else 1080)
            and abs(photo['width']/photo['height'] - 16/9) < (0.1 if relax_filters else 0.01)
        ]
    else:
        filtered_photos = [
            photo for photo in filtered_photos
            if photo['width'] >= (720 if relax_filters else 1080)
            and photo['height'] >= (1280 if relax_filters else 1920)
            and abs(photo['height']/photo['width'] - 16/9) < (0.1 if relax_filters else 0.01)
        ]

    # Step 4: Filter for photos that have theme/topic in metadata
    relevant_photos = [photo for photo in filtered_photos if has_theme_or_topic(photo)]

    # Prefer most relevant, unused, diverse photo
    if relevant_photos:
        photo = relevant_photos[0]
        used_photo_ids.add(photo['id'])
        photographer = photo.get('photographer', '')
        if photographer:
            used_photographers.add(photographer)
        log_response(
            LOG_TYPE_PEXEL,
            search_query,
            {
                "photo_id": photo['id'],
                "photo_url": photo['src'].get('landscape') or photo['src'].get('original'),
                "theme": theme,
                "topic": topic,
                "relaxed": relax_filters,
                "relevant": True
            }
        )
        if orientation_landscape:
            return photo['src'].get('landscape') or photo['src'].get('original')
        else:
            return photo['src'].get('portrait') or photo['src'].get('original')

    # Step 5: Fallback to theme/topic-only query if nothing found and not already forced
    if not relevant_photos and not force_theme_only:
        return select_best_photo(
            query_string,
            orientation_landscape,
            theme,
            topic,
            aspect_ratio,
            used_photo_ids=used_photo_ids,
            used_photographers=used_photographers,
            relax_filters=relax_filters,
            force_theme_only=True
        )

    # Step 6: If still nothing, relax filters and try again
    if not relevant_photos and not relax_filters:
        return select_best_photo(
            query_string,
            orientation_landscape,
            theme,
            topic,
            aspect_ratio,
            used_photo_ids=used_photo_ids,
            used_photographers=used_photographers,
            relax_filters=True,
            force_theme_only=force_theme_only
        )

    # Step 7: If still nothing, fallback to any photo (avoid black background)
    if not relevant_photos and filtered_photos:
        photo = filtered_photos[0]
        used_photo_ids.add(photo['id'])
        photographer = photo.get('photographer', '')
        if photographer:
            used_photographers.add(photographer)
        log_response(
            LOG_TYPE_PEXEL,
            search_query,
            {
                "photo_id": photo['id'],
                "photo_url": photo['src'].get('landscape') or photo['src'].get('original'),
                "theme": theme,
                "topic": topic,
                "relaxed": relax_filters,
                "relevant": False
            }
        )
        if orientation_landscape:
            return photo['src'].get('landscape') or photo['src'].get('original')
        else:
            return photo['src'].get('portrait') or photo['src'].get('original')

    # Log if nothing found
    log_response(
        LOG_TYPE_PEXEL,
        search_query,
        {
            "error": "No relevant photo found",
            "theme": theme,
            "topic": topic,
            "relaxed": relax_filters
        }
    )
    return None
