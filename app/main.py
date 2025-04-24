from fastapi import FastAPI
from app.services.openai_service import generate_script
from app.services.kokoro_service import kokoro_client
from app.core.audio_generator import generate_audio
from app.core.caption_generator import generate_timed_captions
from app.services.pexels_service import generate_video_url
from app.services.pexels_diversity import generate_video_url_diverse
from app.core.render import get_output_media
from app.core.search_generator import getVideoSearchQueriesTimed, merge_empty_intervals

import asyncio

app = FastAPI()

@app.post("/generate-video")
async def generate_video(topic: str):
    SAMPLE_FILE_NAME = "audio_tts.wav"
    VIDEO_SERVER = "pexel"

    response = generate_script(topic)
    print("script: {}".format(response))

    await generate_audio(response, SAMPLE_FILE_NAME)

    timed_captions = generate_timed_captions(SAMPLE_FILE_NAME)
    print(timed_captions)

    search_terms = getVideoSearchQueriesTimed(response, timed_captions)
    print(search_terms)

    background_video_urls = None
    if search_terms is not None:
        background_video_urls = generate_video_url_diverse(
            search_terms,
            VIDEO_SERVER
            # add theme, aspect_ratio, video_name, topic if needed
        )
        print(background_video_urls)
    else:
        print("No background video")

    # Only keep [interval, url] for merge_empty_intervals
    background_video_urls_for_merge = None
    if background_video_urls is not None:
        background_video_urls_for_merge = [
            [interval, url] for interval, url, _ in background_video_urls
        ]

    background_video_urls_merged = merge_empty_intervals(background_video_urls_for_merge)

    if background_video_urls_merged is not None:
        video = get_output_media(SAMPLE_FILE_NAME, timed_captions, background_video_urls_merged, VIDEO_SERVER)
        print(video)
        return {"status": "success", "video": video}
    else:
        print("No video")
        return {"status": "failure", "message": "No video generated"}