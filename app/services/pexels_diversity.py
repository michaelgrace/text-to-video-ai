# NOTE: Run this once in your environment to download the tokenizer data:
# import nltk; nltk.download('punkt')

import re
from nltk.stem import PorterStemmer
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
    relax_filters=False,
    relax_negative_keywords=False,
    used_photo_ids=None,
    used_photographers=None
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

    # --- Fuzzy/Plural Matching: Use stemming for keywords and metadata ---
    stemmer = PorterStemmer()
    query_keywords = set(stemmer.stem(word.lower()) for word in re.findall(r'\w+', query_string))
    if theme:
        query_keywords.update(stemmer.stem(word.lower()) for word in re.findall(r'\w+', theme))
    if topic:
        query_keywords.update(stemmer.stem(word.lower()) for word in re.findall(r'\w+', topic))

    filtered_videos = []
    for video in videos:
        meta_fields = [
            str(video.get('url', '')).lower(),
            str(video.get('alt', '')).lower(),
            str(video.get('user', {}).get('name', '')).lower(),
            " ".join([str(tag).lower() for tag in video.get('tags', [])]),
        ]
        # Stem all words in metadata
        meta_words = set(stemmer.stem(word) for field in meta_fields for word in re.findall(r'\w+', field))
        if not query_keywords.intersection(meta_words):
            continue  # Skip if no fuzzy/plural keyword present
        if not relax_negative_keywords and any(contains_negative_keyword(field) for field in meta_fields):
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
                                "theme": theme,
                                "topic": topic,
                                "video_id": video["id"],
                                "selected_video_file": video_file
                            },
                            theme=theme,
                            topic=topic
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
                                "theme": theme,
                                "topic": topic,
                                "video_id": video["id"],
                                "selected_video_file": video_file
                            },
                            theme=theme,
                            topic=topic
                        )
                        used_video_ids.add(video['id'])
                        return video_file['link'], video['id'], False

    # If no unique video found, try relaxing filters (resolution, aspect ratio)
    if not relax_filters:
        return getBestVideoDiverse(
            query_string,
            orientation_landscape,
            used_video_ids=used_video_ids,
            video_name=video_name,
            theme=theme,
            topic=topic,
            aspect_ratio=aspect_ratio,
            relax_filters=True,
            relax_negative_keywords=relax_negative_keywords,
            used_photo_ids=used_photo_ids,
            used_photographers=used_photographers
        )

    # If still no video, try relaxing negative keywords filter
    if not relax_negative_keywords:
        return getBestVideoDiverse(
            query_string,
            orientation_landscape,
            used_video_ids=used_video_ids,
            video_name=video_name,
            theme=theme,
            topic=topic,
            aspect_ratio=aspect_ratio,
            relax_filters=True,
            relax_negative_keywords=True,
            used_photo_ids=used_photo_ids,
            used_photographers=used_photographers
        )

    # Fallback: Try to get a photo (with relaxed filters)
    if used_photo_ids is None:
        used_photo_ids = set()
    if used_photographers is None:
        used_photographers = set()
    photo_url = select_best_photo(
        query_string,
        orientation_landscape=orientation_landscape,
        theme=theme,
        aspect_ratio=aspect_ratio,
        used_photo_ids=used_photo_ids,
        used_photographers=used_photographers
    )
    if photo_url:
        log_response(
            LOG_TYPE_PEXEL,
            query_string,
            {
                "theme": theme,
                "topic": topic,
                "photo_fallback": True,
                "photo_url": photo_url
            },
            theme=theme,
            topic=topic
        )
        return photo_url, None, True

    # If still nothing, log and return the failed query string
    print(f"NO VIDEO or PHOTO found for this search query: '{search_query}'")
    log_response(
        LOG_TYPE_PEXEL,
        query_string,
        {
            "theme": theme,
            "topic": topic,
            "error": "No relevant video or photo found",
            "failed_query": search_query
        },
        theme=theme,
        topic=topic
    )
    return None, None, search_query

def select_best_photo(query_string, orientation_landscape=True, theme=None, aspect_ratio="landscape", used_photo_ids=None, used_photographers=None):
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

    # Remove used photos and photographers
    filtered_photos = [
        photo for photo in filtered_photos
        if photo['id'] not in used_photo_ids and photo['photographer'] not in used_photographers
    ]

    # Sort photos by relevance
    sorted_photos = sorted(filtered_photos, key=lambda x: x.get('avg_color', ''))

    if sorted_photos:
        best_photo = sorted_photos[0]
        used_photo_ids.add(best_photo['id'])
        used_photographers.add(best_photo['photographer'])
        return best_photo['src']['original']
    return None

def generate_video_url_diverse(
    timed_video_searches,
    video_server,
    theme=None,
    aspect_ratio="landscape",
    video_name=None,
    topic=None,
    render_mode="video"
):
    timed_video_urls = []
    # These must be reset for each new video!
    used_video_ids = set()
    used_photo_ids = set()
    used_photographers = set()
    if video_server == "pexel":
        for (t1, t2), search_terms in timed_video_searches:
            url = None
            is_photo = False
            failed_query = None
            # --- Extract the sentence fragment for this segment ---
            # Assume search_terms is a list of queries for this segment, and you want to log the fragment that led to the first query
            sentence_fragment = None
            if hasattr(search_terms, '__iter__') and len(search_terms) > 0:
                sentence_fragment = search_terms[0]  # Or use a mapping if available
            for query in search_terms:
                if render_mode == "video":
                    video_url, video_id, fallback = getBestVideoDiverse(
                        query,
                        orientation_landscape=(aspect_ratio == "landscape"),
                        used_video_ids=used_video_ids,
                        video_name=video_name,
                        theme=theme,
                        topic=topic,
                        aspect_ratio=aspect_ratio,
                        used_photo_ids=used_photo_ids,
                        used_photographers=used_photographers
                    )
                    if video_url and video_id:
                        used_video_ids.add(video_id)
                        url = video_url
                        is_photo = False
                        # --- Log with sentence fragment ---
                        log_response(
                            LOG_TYPE_PEXEL,
                            query,
                            {
                                "theme": theme,
                                "topic": topic,
                                "video_id": video_id,
                                "selected_video_file": None  # Already logged in getBestVideoDiverse, but you can add here if needed
                            },
                            title=video_name,
                            theme=theme,
                            topic=topic,
                            sentence=sentence_fragment
                        )
                        break
                elif render_mode == "photo":
                    photo_url = select_best_photo(
                        query,
                        orientation_landscape=(aspect_ratio == "landscape"),
                        theme=theme,
                        aspect_ratio=aspect_ratio,
                        used_photo_ids=used_photo_ids,
                        used_photographers=used_photographers
                    )
                    if photo_url:
                        log_response(
                            LOG_TYPE_PEXEL,
                            query,
                            {
                                "theme": theme,
                                "topic": topic,
                                "photo_fallback": True,
                                "photo_url": photo_url
                            },
                            title=video_name,
                            theme=theme,
                            topic=topic,
                            sentence=sentence_fragment
                        )
                        url = photo_url
                        is_photo = True
                        break
                else:
                    video_url, video_id, fallback = getBestVideoDiverse(
                        query,
                        orientation_landscape=(aspect_ratio == "landscape"),
                        used_video_ids=used_video_ids,
                        video_name=video_name,
                        theme=theme,
                        topic=topic,
                        aspect_ratio=aspect_ratio,
                        used_photo_ids=used_photo_ids,
                        used_photographers=used_photographers
                    )
                    if video_url:
                        if not fallback and video_id:
                            used_video_ids.add(video_id)
                        url = video_url
                        is_photo = (video_id is None and video_url is not None)
                        log_response(
                            LOG_TYPE_PEXEL,
                            query,
                            {
                                "theme": theme,
                                "topic": topic,
                                "video_id": video_id,
                                "selected_video_file": None
                            },
                            title=video_name,
                            theme=theme,
                            topic=topic,
                            sentence=sentence_fragment
                        )
                        break
                    elif fallback and isinstance(fallback, str):
                        failed_query = fallback
            if not url and failed_query:
                print(f"Failed to find relevant video or photo for query: '{failed_query}'")
            timed_video_urls.append([[t1, t2], url, is_photo if url else failed_query])
    # ...add stable_diffusion logic if needed...
    return timed_video_urls
