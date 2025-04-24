import os 
import requests
import json
from app.utils.helpers import log_response, LOG_TYPE_PEXEL  # Updated from utility.utils
from app.utils.pg_cache import ensure_cache_table, get_cached_response, insert_cache  # <-- Add this import

PEXELS_API_KEY = os.environ.get('PEXELS_API_KEY')

# Load negative keywords from a JSON file (adjust path as needed)
NEGATIVE_KEYWORDS_PATH = os.path.join(os.path.dirname(__file__), "../schemas/negative_keywords.json")
with open(NEGATIVE_KEYWORDS_PATH, "r") as f:
    NEGATIVE_KEYWORDS = set(json.load(f)["negative_keywords"])  # <-- fix: load the list, not the whole dict

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
    used_vids=None,
    used_creators=None,
    used_locations=None,
    video_name=None,
    theme=None,
    topic=None,
    aspect_ratio=None
):
    if used_vids is None:
        used_vids = set()
    if used_creators is None:
        used_creators = set()
    if used_locations is None:
        used_locations = set()
    vids = search_videos(
        query_string,
        orientation_landscape,
        video_name=video_name,
        theme=theme,
        topic=topic,
        aspect_ratio=aspect_ratio
    )
    videos = vids.get('videos', [])

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

    # --- Diversity filter: skip used video IDs, creators, locations ---
    diverse_videos = []
    for video in filtered_videos:
        vid_id = video.get('id')
        creator_id = video.get('user', {}).get('id')
        location = video.get('location', None)
        if vid_id in used_vids:
            continue
        if creator_id and creator_id in used_creators:
            continue
        if location and location in used_locations:
            continue
        diverse_videos.append(video)
    # --- End diversity filter ---

    # --- Relevance scoring: prefer videos matching theme/topic/query ---
    def relevance_score(video):
        score = 0
        meta = (
            str(video.get('url', '')).lower() + " " +
            str(video.get('alt', '')).lower() + " " +
            str(video.get('user', {}).get('name', '')).lower() + " " +
            " ".join([str(tag).lower() for tag in video.get('tags', [])])
        )
        if theme and theme.lower() in meta:
            score += 2
        if topic and topic.lower() in meta:
            score += 2
        if query_string and query_string.lower() in meta:
            score += 1
        return score

    diverse_videos.sort(key=relevance_score, reverse=True)

    # --- Select the best unused, relevant video file ---
    for video in diverse_videos:
        for video_file in video.get('video_files', []):
            if orientation_landscape:
                if video_file.get('width') == 1920 and video_file.get('height') == 1080:
                    # Mark as used
                    used_vids.add(video.get('id'))
                    creator_id = video.get('user', {}).get('id')
                    if creator_id:
                        used_creators.add(creator_id)
                    location = video.get('location', None)
                    if location:
                        used_locations.add(location)
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
                if video_file.get('width') == 1080 and video_file.get('height') == 1920:
                    used_vids.add(video.get('id'))
                    creator_id = video.get('user', {}).get('id')
                    if creator_id:
                        used_creators.add(creator_id)
                    location = video.get('location', None)
                    if location:
                        used_locations.add(location)
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
    used_creators = set()
    used_locations = set()
    if video_server == "pexel":
        for (t1, t2), search_terms in timed_video_searches:
            url = None
            for query in search_terms:
                video_url = getBestVideo(
                    query,
                    orientation_landscape=(aspect_ratio == "landscape"),
                    used_vids=used_video_ids,
                    used_creators=used_creators,
                    used_locations=used_locations,
                    video_name=video_name,
                    theme=theme,
                    topic=topic,
                    aspect_ratio=aspect_ratio
                )
                if video_url:
                    url = video_url
                    break
            if not url:
                # Fallback: get a photo URL (implement getBestPhoto or similar)
                url = None  # Placeholder for fallback logic
                print(f"Fallback triggered: No video found for query '{query}'. Implement 'getBestPhoto' or alternative logic.")
            timed_video_urls.append([[t1, t2], url])
    elif video_server == "stable_diffusion":
        timed_video_urls = get_images_for_video(timed_video_searches)
    return timed_video_urls
