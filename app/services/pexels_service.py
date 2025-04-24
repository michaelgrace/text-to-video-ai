import os 
import requests
import json
from app.utils.helpers import log_response, LOG_TYPE_PEXEL  # Updated from utility.utils
from app.utils.pg_cache import ensure_cache_table, get_cached_response, insert_cache  # <-- Add this import

PEXELS_API_KEY = os.environ.get('PEXELS_API_KEY')

# Load negative keywords from a JSON file (adjust path as needed)
NEGATIVE_KEYWORDS_PATH = os.path.join(os.path.dirname(__file__), "../schemas/negative_keywords.json")
with open(NEGATIVE_KEYWORDS_PATH, "r") as f:
    NEGATIVE_KEYWORDS = set(json.load(f))

def contains_negative_keyword(text):
    if not text:
        return False
    text_lower = text.lower()
    # Check for whole word matches and substrings
    for neg in NEGATIVE_KEYWORDS:
        if neg.lower() in text_lower:
            return True
    return False

def search_videos(query_string, orientation_landscape=True, video_name=None, theme=None, topic=None, aspect_ratio=None):
    print(f"Searching for Pexels videos... Query: {query_string}")
    try:
        # Combine theme and query_string for more relevant search
        if theme and theme.lower() not in query_string.lower():
            search_query = f"{theme} {query_string}"
        else:
            search_query = query_string

        url = "https://api.pexels.com/videos/search"
        headers = {
            "Authorization": PEXELS_API_KEY,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        params = {
            "query": search_query,
            "orientation": "landscape" if orientation_landscape else "portrait",
            "per_page": 15
        }

        # Minimal cache integration
        ensure_cache_table()
        cached = get_cached_response(video_name, theme, topic, aspect_ratio, query_string)
        if cached:
            return cached

        response = requests.get(url, headers=headers, params=params)
        json_data = response.json()
        insert_cache(video_name, theme, topic, aspect_ratio, query_string, json_data)
        return json_data
    except Exception as e:
        print(f"Error searching Pexels videos: {e}")
        return {}

def getBestVideo(
    query_string,
    orientation_landscape=True,
    used_vids=[],
    video_name=None,
    theme=None,
    topic=None,
    aspect_ratio=None
):
    vids = search_videos(
        query_string,
        orientation_landscape,
        video_name=video_name,
        theme=theme,
        topic=topic,
        aspect_ratio=aspect_ratio
    )
    videos = vids['videos']

    # --- Negative keyword filter ---
    filtered_videos = []
    for video in videos:
        meta_fields = [
            str(video.get('url', '')).lower(),
            str(video.get('alt', '')).lower(),
            str(video.get('user', {}).get('name', '')).lower(),
            " ".join([str(tag).lower() for tag in video.get('tags', [])]),
        ]
        if any(contains_negative_keyword(field) for field in meta_fields):
            continue
        filtered_videos.append(video)
    # --- End negative keyword filter ---

    # Filter and extract videos with width and height as 1920x1080 for landscape or 1080x1920 for portrait
    if orientation_landscape:
        filtered_videos = [video for video in filtered_videos if video['width'] >= 1920 and video['height'] >= 1080 and video['width']/video['height'] == 16/9]
    else:
        filtered_videos = [video for video in filtered_videos if video['width'] >= 1080 and video['height'] >= 1920 and video['height']/video['width'] == 16/9]
    # Sort the filtered videos by duration in ascending order
    sorted_videos = sorted(filtered_videos, key=lambda x: abs(15-int(x['duration'])))
    # Extract the top 3 videos' URLs
    for video in sorted_videos:
        for video_file in video['video_files']:
            if orientation_landscape:
                if video_file['width'] == 1920 and video_file['height'] == 1080:
                    if not (video_file['link'].split('.hd')[0] in used_vids):
                        # Log only the selected video file and metadata
                        log_response(
                            LOG_TYPE_PEXEL,
                            query_string,
                            {
                                "video_id": video["id"],
                                "selected_video_file": video_file,
                                "theme": theme,
                                "topic": topic
                            }
                        )
                        return video_file['link']
            else:
                if video_file['width'] == 1080 and video_file['height'] == 1920:
                    if not (video_file['link'].split('.hd')[0] in used_vids):
                        log_response(
                            LOG_TYPE_PEXEL,
                            query_string,
                            {
                                "video_id": video["id"],
                                "selected_video_file": video_file,
                                "theme": theme,
                                "topic": topic
                            }
                        )
                        return video_file['link']
    print("NO LINKS found for this round of search with query :", query_string)
    return None

def generate_video_url(timed_video_searches, video_server, theme=None, aspect_ratio="landscape", video_name=None, topic=None):
    timed_video_urls = []
    used_video_ids = set()
    if video_server == "pexel":
        for (t1, t2), search_terms in timed_video_searches:
            url = None
            for query in search_terms:
                video_url = getBestVideo(
                    query,
                    orientation_landscape=(aspect_ratio == "landscape"),
                    used_vids=used_video_ids,
                    video_name=video_name,
                    theme=theme,
                    topic=topic,
                    aspect_ratio=aspect_ratio
                )
                if video_url:
                    # Extract video ID from URL or metadata and add to used_video_ids
                    # (Assume you can get video_id from the selected video in getBestVideo)
                    # used_video_ids.add(video_id)
                    url = video_url
                    break
            if not url:
                # Fallback: get a photo URL (implement getBestPhoto or similar)
                url = getBestPhoto(query, theme=theme, aspect_ratio=aspect_ratio)
            timed_video_urls.append([[t1, t2], url])
    elif video_server == "stable_diffusion":
        timed_video_urls = get_images_for_video(timed_video_searches)
    return timed_video_urls
