import os 
import requests
import time
from tenacity import retry, stop_after_attempt, wait_exponential
from app.utils.helpers import log_response, LOG_TYPE_PEXEL

PEXELS_API_KEY = os.environ.get('PEXELS_API_KEY')

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def search_videos_with_retry(query_string, orientation_landscape=True):
    try:
        response = search_videos(query_string, orientation_landscape)
        if 'videos' not in response or not response['videos']:
            raise Exception("No videos found")
        return response
    except Exception as e:
        print(f"Error searching videos: {e}")
        raise

def search_videos(query_string, orientation_landscape=True):
    url = "https://api.pexels.com/videos/search"
    headers = {
        "Authorization": PEXELS_API_KEY,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    params = {
        "query": query_string,
        "orientation": "landscape" if orientation_landscape else "portrait",
        "per_page": 15
    }

    response = requests.get(url, headers=headers, params=params)
    json_data = response.json()
    log_response(LOG_TYPE_PEXEL, query_string, response.json())
   
    return json_data

def getBestVideo(query_string, orientation_landscape=True, used_vids=[], attempt=0):
    max_attempts = 3
    while attempt < max_attempts:
        try:
            vids = search_videos_with_retry(query_string, orientation_landscape)
            videos = vids['videos']
            
            if not videos:
                attempt += 1
                continue
                
            if orientation_landscape:
                filtered_videos = [video for video in videos if video['width'] >= 1920 and video['height'] >= 1080 and video['width']/video['height'] == 16/9]
            else:
                filtered_videos = [video for video in videos if video['width'] >= 1080 and video['height'] >= 1920 and video['height']/video['width'] == 16/9]
            
            if not filtered_videos and attempt < max_attempts:
                attempt += 1
                continue
                
            sorted_videos = sorted(filtered_videos, key=lambda x: abs(15-int(x['duration'])))
            
            for video in sorted_videos:
                for video_file in video['video_files']:
                    if orientation_landscape:
                        if video_file['width'] == 1920 and video_file['height'] == 1080:
                            if not (video_file['link'].split('.hd')[0] in used_vids):
                                return video_file['link']
                    else:
                        if video_file['width'] == 1080 and video_file['height'] == 1920:
                            if not (video_file['link'].split('.hd')[0] in used_vids):
                                return video_file['link']
        except Exception as e:
            if attempt >= max_attempts - 1:
                print(f"Failed to get video after {max_attempts} attempts: {e}")
                return None
            attempt += 1
            time.sleep(2 ** attempt)  # Exponential backoff
            
    print("NO LINKS found for this round of search with query :", query_string)
    return None

def get_alternative_terms(search_term):
    """Generate alternative search terms when original fails"""
    alternatives = []
    
    # Remove specific words
    term = search_term.lower()
    if 'the' in term:
        alternatives.append(term.replace('the', '').strip())
    
    # Add generic equivalents
    if 'person' in term:
        alternatives.extend(['people outdoors', 'human activity'])
    elif 'animal' in term:
        alternatives.extend(['wildlife', 'nature'])
    elif 'building' in term:
        alternatives.extend(['architecture', 'city view'])
        
    # Add broader category
    if 'night' in term:
        alternatives.append('evening scene')
    if 'water' in term:
        alternatives.append('ocean waves')
    
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
