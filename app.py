from openai import OpenAI
import os
import json
import asyncio
import whisper_timestamped as whisper

# Keep original working imports
# from utility.script.script_generator import generate_script
# from utility.audio.audio_generator import generate_audio
# from utility.captions.timed_captions_generator import generate_timed_captions
# from utility.video.background_video_generator import generate_video_url
# from utility.render.render_engine import get_output_media
# from utility.video.video_search_query_generator import getVideoSearchQueriesTimed, merge_empty_intervals

# New imports commented until all files are moved
from app.services.openai_service import generate_script
from app.core.audio_generator import generate_audio
from app.core.caption_generator import generate_timed_captions
from app.services.pexels_service import generate_video_url
from app.core.render import get_output_media
from app.core.search_generator import getVideoSearchQueriesTimed, merge_empty_intervals
from app.services.kokoro_service import kokoro_client

import argparse

# CLI entry point for direct video generation
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a video from a topic.")
    parser.add_argument("topic", type=str, help="The topic for the video")

    args = parser.parse_args()
    SAMPLE_TOPIC = args.topic
    SAMPLE_FILE_NAME = "audio_tts.wav"
    VIDEO_SERVER = "pexel"

    response = generate_script(SAMPLE_TOPIC)
    print("script: {}".format(response))

    try:
        audio_response = asyncio.run(kokoro_client.create_speech(
            text=response,
            voice="af_heart"  # Default voice
        ))
        with open(SAMPLE_FILE_NAME, "wb") as f:
            f.write(audio_response)
    except Exception as e:
        print(f"Error generating audio: {e}")
        exit()

    timed_captions = generate_timed_captions(SAMPLE_FILE_NAME)
    print(timed_captions)

    search_terms = getVideoSearchQueriesTimed(response, timed_captions)
    print(search_terms)

    background_video_urls = None
    if search_terms is not None:
        background_video_urls = generate_video_url(search_terms, VIDEO_SERVER)
        print(background_video_urls)
    else:
        print("No background video")

    background_video_urls = merge_empty_intervals(background_video_urls)

    if background_video_urls is not None:
        video = get_output_media(SAMPLE_FILE_NAME, timed_captions, background_video_urls, VIDEO_SERVER)
        print(video)
    else:
        print("No video")
