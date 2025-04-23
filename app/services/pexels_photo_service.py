import os
import requests

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

def select_best_photo(query_string, orientation_landscape=True, theme=None, aspect_ratio="landscape"):
    photos_json = search_photos(query_string, orientation_landscape, theme, aspect_ratio)
    photos = photos_json.get('photos', [])
    # Prefer largest landscape/portrait photo
    for photo in photos:
        if orientation_landscape:
            if photo['width'] >= 1280 and photo['height'] >= 720:
                return photo['src'].get('landscape') or photo['src'].get('original')
        else:
            if photo['width'] >= 720 and photo['height'] >= 1280:
                return photo['src'].get('portrait') or photo['src'].get('original')
    # Fallback: return any photo
    if photos:
        return photos[0]['src'].get('original')
    return None
