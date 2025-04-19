import os 
import requests
import time
from tenacity import retry, stop_after_attempt, wait_exponential
from app.utils.helpers import log_response, LOG_TYPE_PEXEL
from config.settings import settings
from functools import lru_cache

PEXELS_API_KEY = settings.PEXELS_API_KEY

@retry(stop=stop_after_attempt(settings.MAX_SEARCH_ATTEMPTS), 
      wait=wait_exponential(multiplier=1, min=settings.SEARCH_BACKOFF_MIN, max=settings.SEARCH_BACKOFF_MAX))
def search_videos_with_retry(query_string, orientation_landscape=True):
    try:
        response = search_videos(query_string, orientation_landscape)
        if 'videos' not in response or not response['videos']:
            raise Exception("No videos found")
        return response
    except Exception as e:
        print(f"Error searching videos: {e}")
        raise

@lru_cache(maxsize=128)
def search_videos(query_string, orientation_landscape=True):
    url = settings.PEXELS_SEARCH_URL
    headers = {
        "Authorization": PEXELS_API_KEY,
        "User-Agent": settings.PEXELS_USER_AGENT,
    }
    params = {
        "query": query_string,
        "orientation": "landscape" if orientation_landscape else "portrait",
        "per_page": settings.PEXELS_PER_PAGE
    }

    response = requests.get(url, headers=headers, params=params)
    json_data = response.json()
    log_response(LOG_TYPE_PEXEL, query_string, response.json())
   
    return json_data

def getBestVideo(query_string, orientation_landscape=True, used_vids=[], attempt=0):
    while attempt < settings.MAX_RETRIES:
        try:
            vids = search_videos_with_retry(query_string, orientation_landscape)
            videos = vids['videos']
            
            if not videos:
                attempt += 1
                continue
                
            if orientation_landscape:
                filtered_videos = [video for video in videos 
                    if video['width'] >= settings.VIDEO_LANDSCAPE_WIDTH and 
                    video['height'] >= settings.VIDEO_LANDSCAPE_HEIGHT and 
                    abs(video['width']/video['height'] - settings.ASPECT_RATIO) < 0.01]  # More forgiving ratio check
            else:
                filtered_videos = [video for video in videos 
                    if video['width'] >= settings.VIDEO_PORTRAIT_WIDTH and 
                    video['height'] >= settings.VIDEO_PORTRAIT_HEIGHT and 
                    abs(video['height']/video['width'] - settings.ASPECT_RATIO) < 0.01]
            
            if not filtered_videos and attempt < settings.MAX_RETRIES:
                attempt += 1
                continue
                
            sorted_videos = sorted(filtered_videos, key=lambda x: abs(settings.VIDEO_TARGET_DURATION - int(x['duration'])))
            
            for video in sorted_videos:
                for video_file in video['video_files']:
                    if orientation_landscape:
                        if video_file['width'] == settings.VIDEO_LANDSCAPE_WIDTH and video_file['height'] == settings.VIDEO_LANDSCAPE_HEIGHT:
                            if not (video_file['link'].split('.hd')[0] in used_vids):
                                return video_file['link']
                    else:
                        if video_file['width'] == settings.VIDEO_PORTRAIT_WIDTH and video_file['height'] == settings.VIDEO_PORTRAIT_HEIGHT:
                            if not (video_file['link'].split('.hd')[0] in used_vids):
                                return video_file['link']
        except Exception as e:
            if attempt >= settings.MAX_RETRIES - 1:
                print(f"Failed to get video after {settings.MAX_RETRIES} attempts: {e}")
                return None
            attempt += 1
            time.sleep(2 ** attempt)  # Exponential backoff
            
    print("NO LINKS found for this round of search with query :", query_string)
    return None

def get_alternative_terms(search_term):
    """Generate alternative search terms when original fails"""
    alternatives = []
    
    # Remove specific words using settings
    term = search_term.lower()
    for word, replacement in settings.WORD_REPLACEMENTS.items():
        if word in term:
            alternatives.append(term.replace(word, replacement).strip())
            
    # Use generic alternatives from settings
    for key, values in settings.GENERIC_ALTERNATIVES.items():
        if key in term.lower():
            alternatives.extend(values)
    
    return alternatives

def generate_video_url(timed_video_searches, video_server):
    if video_server != "pexel":
        return get_images_for_video(timed_video_searches)
        
    timed_video_urls = []
    used_links = []
    
    for (t1, t2), search_terms in timed_video_searches:
        url = None
        # Try original search terms
        for query in search_terms:
            url = getBestVideo(query, orientation_landscape=True, used_vids=used_links)
            if url:
                used_links.append(url.split('.hd')[0])
                break
                
        # If no video found, try alternative terms
        if not url:
            for query in search_terms:
                alternative_terms = get_alternative_terms(query)
                for alt_term in alternative_terms:
                    url = getBestVideo(alt_term, orientation_landscape=True, used_vids=used_links)
                    if url:
                        used_links.append(url.split('.hd')[0])
                        print(f"Found alternative video for '{query}' using '{alt_term}'")
                        break
                if url:
                    break
                    
        timed_video_urls.append([[t1, t2], url])
    
    return timed_video_urls
