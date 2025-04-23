from app.services.pexels_service import search_videos, contains_negative_keyword
from app.services.pexels_photo_service import search_photos, select_best_photo
from app.utils.helpers import log_response, LOG_TYPE_PEXEL

def getBestVideoDiverse(
    query_string,
    orientation_landscape=True,
    used_video_ids=None,
    video_name=None,
    theme=None,
    topic=None,
    aspect_ratio=None,
    relax_filters=False
):
    if used_video_ids is None:
        used_video_ids = set()

    # Always combine theme and query_string for more relevant search
    if theme:
        search_query = f"{theme} {query_string}"
    else:
        search_query = query_string

    vids = search_videos(
        search_query,
        orientation_landscape,
        video_name=video_name,
        theme=theme,
        topic=topic,
        aspect_ratio=aspect_ratio
    )
    videos = vids.get('videos', [])

    # Negative keyword filter
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

    # Filter for strict or relaxed requirements
    if orientation_landscape:
        filtered_videos = [
            video for video in filtered_videos
            if (video['width'] >= (1280 if relax_filters else 1920))
            and (video['height'] >= (720 if relax_filters else 1080))
            and abs(video['width']/video['height'] - 16/9) < (0.1 if relax_filters else 0.01)
        ]
    else:
        filtered_videos = [
            video for video in filtered_videos
            if (video['width'] >= (720 if relax_filters else 1080))
            and (video['height'] >= (1280 if relax_filters else 1920))
            and abs(video['height']/video['width'] - 16/9) < (0.1 if relax_filters else 0.01)
        ]

    # Remove used videos
    filtered_videos = [v for v in filtered_videos if v['id'] not in used_video_ids]

    # Sort by duration closeness to 15 seconds
    sorted_videos = sorted(filtered_videos, key=lambda x: abs(15-int(x['duration'])))

    for video in sorted_videos:
        for video_file in video['video_files']:
            if orientation_landscape:
                if video_file['width'] == 1920 and video_file['height'] == 1080:
                    if video['id'] not in used_video_ids:
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
                        used_video_ids.add(video['id'])
                        return video_file['link'], video['id'], False
            else:
                if video_file['width'] == 1080 and video_file['height'] == 1920:
                    if video['id'] not in used_video_ids:
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
                        used_video_ids.add(video['id'])
                        return video_file['link'], video['id'], False

    # If no unique video found and not already relaxed, try relaxing filters
    if not relax_filters:
        return getBestVideoDiverse(
            query_string,
            orientation_landscape,
            used_video_ids=used_video_ids,
            video_name=video_name,
            theme=theme,
            topic=topic,
            aspect_ratio=aspect_ratio,
            relax_filters=True
        )

    # Fallback: Try to get a photo
    photo_url = select_best_photo(query_string, orientation_landscape, theme=theme, aspect_ratio=aspect_ratio)
    if photo_url:
        log_response(
            LOG_TYPE_PEXEL,
            query_string,
            {
                "photo_fallback": True,
                "photo_url": photo_url,
                "theme": theme,
                "topic": topic
            }
        )
        return photo_url, None, True

    print("NO VIDEO or PHOTO found for this round of search with query :", query_string)
    return None, None, False

def select_best_photo(query_string, orientation_landscape=True, theme=None, aspect_ratio="landscape"):
    # Always combine theme and query_string for more relevant search
    if theme:
        search_query = f"{theme} {query_string}"
    else:
        search_query = query_string

    photos_json = search_photos(search_query, orientation_landscape, theme, aspect_ratio)
    photos = photos_json.get('photos', [])

    # Filter photos based on orientation and aspect ratio
    if orientation_landscape:
        filtered_photos = [
            photo for photo in photos
            if photo['width'] >= 1920 and photo['height'] >= 1080
            and abs(photo['width']/photo['height'] - 16/9) < 0.01
        ]
    else:
        filtered_photos = [
            photo for photo in photos
            if photo['width'] >= 1080 and photo['height'] >= 1920
            and abs(photo['height']/photo['width'] - 16/9) < 0.01
        ]

    # Sort photos by relevance
    sorted_photos = sorted(filtered_photos, key=lambda x: x.get('avg_color', ''))

    if sorted_photos:
        return sorted_photos[0]['src']['original']
    return None

def generate_video_url_diverse(timed_video_searches, video_server, theme=None, aspect_ratio="landscape", video_name=None, topic=None):
    timed_video_urls = []
    used_video_ids = set()
    if video_server == "pexel":
        for (t1, t2), search_terms in timed_video_searches:
            url = None
            is_photo = False
            for query in search_terms:
                video_url, video_id, fallback_photo = getBestVideoDiverse(
                    query,
                    orientation_landscape=(aspect_ratio == "landscape"),
                    used_video_ids=used_video_ids,
                    video_name=video_name,
                    theme=theme,
                    topic=topic,
                    aspect_ratio=aspect_ratio
                )
                if video_url:
                    if not fallback_photo and video_id:
                        used_video_ids.add(video_id)
                    url = video_url
                    is_photo = fallback_photo
                    break
            timed_video_urls.append([[t1, t2], url, is_photo])
    # ...add stable_diffusion logic if needed...
    return timed_video_urls
