from openai import OpenAI
import os
import edge_tts
import json
import asyncio
import whisper_timestamped as whisper

from app.services.kokoro_service import kokoro_client
from app.services.openai_service import generate_script
from app.core.audio_generator import generate_audio
from app.core.caption_generator import generate_timed_captions
from app.services.pexels_service import generate_video_url
from app.core.render import get_output_media
from app.core.search_generator import getVideoSearchQueriesTimed, merge_empty_intervals

import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a video from a topic or custom script.")
    parser.add_argument("input_text", type=str, help="The topic or custom script for the video")
    parser.add_argument("--theme", type=str, required=True, help="Theme for the video")
    parser.add_argument("--aspect-ratio", type=str, default="landscape", choices=["landscape", "portrait", "square"], help="Aspect ratio for the video")
    parser.add_argument("--title", type=str, required=True, help="Title (video name)")
    parser.add_argument("--custom-script", action="store_true", help="Use input as custom script (bypass OpenAI)")

    args = parser.parse_args()
    SAMPLE_FILE_NAME = "audio_tts.wav"
    VIDEO_SERVER = "pexel"

    print("video_title:", args.title)

    if args.custom_script:
        response = args.input_text
    else:
        response = generate_script(args.theme, args.input_text)
    print("script: {}".format(response))

    asyncio.run(generate_audio(response, SAMPLE_FILE_NAME))

    timed_captions = generate_timed_captions(SAMPLE_FILE_NAME)
    print(timed_captions)

    search_terms = getVideoSearchQueriesTimed(response, timed_captions)
    print("search_terms:", search_terms)
    print("theme:", args.theme)
    print("input_text:", args.input_text)

    background_video_urls = None
    if search_terms is not None:
        background_video_urls = generate_video_url(
            search_terms,
            VIDEO_SERVER,
            theme=args.theme,
            aspect_ratio=args.aspect_ratio,
            video_name=args.title,
            topic=args.input_text
        )
        print("background_video_urls:", background_video_urls)
    else:
        print("No background video")
        print("Failed search_terms:", search_terms)
        print("Query context - theme:", args.theme, "input_text:", args.input_text)

    if background_video_urls is not None:
        background_video_urls_merged = merge_empty_intervals(background_video_urls)
        if background_video_urls_merged is not None:
            video = get_output_media(SAMPLE_FILE_NAME, timed_captions, background_video_urls_merged, VIDEO_SERVER)
            print(video)
        else:
            print("merge_empty_intervals returned None. Failed background_video_urls:", background_video_urls)
            print("Query context - theme:", args.theme, "input_text:", args.input_text, "search_terms:", search_terms)
    else:
        print("background_video_urls is None. Failed search_terms:", search_terms)
        print("Query context - theme:", args.theme, "input_text:", args.input_text)
