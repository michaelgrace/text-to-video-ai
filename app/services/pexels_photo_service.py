import os
import requests
import re
from nltk.stem import PorterStemmer
from app.utils.helpers import log_response, LOG_TYPE_PEXEL

PEXELS_API_KEY = os.environ.get('PEXELS_API_KEY')

def search_photos(query_string, orientation_landscape=True, theme=None, aspect_ratio="landscape"):
    url = "https://api.pexels.com/v1/search"
    headers = {
        "Authorization": PEXELS_API_KEY,
        "User-Agent": "Mozilla/5.0"
    }
    params = {
        "query": query_string,
        "orientation": "landscape" if orientation_landscape else "portrait",
        "per_page": 15
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()

def select_best_photo(
    query_string,
    orientation_landscape=True,
    theme=None,
    topic=None,
    aspect_ratio="landscape",
    used_photo_ids=None,
    relax_filters=False
):
    # Always combine theme and query_string for more relevant search
    if theme:
        search_query = f"{theme} {query_string}"
    else:
        search_query = query_string

    photos_json = search_photos(search_query, orientation_landscape, theme, aspect_ratio)
    photos = photos_json.get('photos', [])

    # --- Fuzzy/Plural Matching: Use stemming for keywords and metadata ---
    stemmer = PorterStemmer()
    query_keywords = set(stemmer.stem(word.lower()) for word in re.findall(r'\w+', query_string))
    if theme:
        query_keywords.update(stemmer.stem(word.lower()) for word in re.findall(r'\w+', theme))
    if topic:
        query_keywords.update(stemmer.stem(word.lower()) for word in re.findall(r'\w+', topic))

    # Diversity: avoid duplicates
    if used_photo_ids is None:
        used_photo_ids = set()

    # Filter photos based on orientation, aspect ratio, and relevance
    if orientation_landscape:
        filtered_photos = [
            photo for photo in photos
            if photo['width'] >= (1280 if relax_filters else 1920)
            and photo['height'] >= (720 if relax_filters else 1080)
            and abs(photo['width']/photo['height'] - 16/9) < (0.1 if relax_filters else 0.01)
            and photo['id'] not in used_photo_ids
        ]
    else:
        filtered_photos = [
            photo for photo in photos
            if photo['width'] >= (720 if relax_filters else 1080)
            and photo['height'] >= (1280 if relax_filters else 1920)
            and abs(photo['height']/photo['width'] - 16/9) < (0.1 if relax_filters else 0.01)
            and photo['id'] not in used_photo_ids
        ]

    # Score and filter for relevance using fuzzy/plural matching
    relevant_photos = []
    for photo in filtered_photos:
        meta_fields = [
            str(photo.get('url', '')).lower(),
            str(photo.get('alt', '')).lower(),
            str(photo.get('photographer', '')).lower(),
            " ".join([str(tag).lower() for tag in photo.get('tags', [])]) if 'tags' in photo else "",
        ]
        meta_words = set(stemmer.stem(word) for field in meta_fields for word in re.findall(r'\w+', field))
        if query_keywords.intersection(meta_words):
            relevant_photos.append(photo)

    # Prefer most relevant, unused photo
    if relevant_photos:
        photo = relevant_photos[0]
        used_photo_ids.add(photo['id'])
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

    # If no relevant, unused photo, relax filters and try again
    if not relax_filters:
        return select_best_photo(
            query_string,
            orientation_landscape,
            theme,
            topic,
            aspect_ratio,
            used_photo_ids=used_photo_ids,
            relax_filters=True
        )

    # Fallback: return any unused filtered photo
    for photo in filtered_photos:
        if photo['id'] not in used_photo_ids:
            used_photo_ids.add(photo['id'])
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

    # Fallback: return any photo
    for photo in photos:
        if photo['id'] not in used_photo_ids:
            used_photo_ids.add(photo['id'])
            log_response(
                LOG_TYPE_PEXEL,
                search_query,
                {
                    "photo_id": photo['id'],
                    "photo_url": photo['src'].get('original'),
                    "theme": theme,
                    "topic": topic,
                    "relaxed": relax_filters,
                    "relevant": False
                }
            )
            return photo['src'].get('original')
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
