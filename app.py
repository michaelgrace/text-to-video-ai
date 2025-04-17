from openai import OpenAI
import os
import edge_tts
import json
import asyncio
import whisper_timestamped as whisper
from utility.script.script_generator import generate_script
from utility.audio.audio_generator import generate_audio
from utility.captions.timed_captions_generator import generate_timed_captions
from utility.video.background_video_generator import generate_video_url
from utility.render.render_engine import get_output_media
from utility.video.video_search_query_generator import getVideoSearchQueriesTimed, merge_empty_intervals
import argparse
from utility.logger_config import setup_logger

# Initialize logger
logger = setup_logger()

if __name__ == "__main__":
    logger.debug("Starting video generation process")
    parser = argparse.ArgumentParser(description="Generate a video from a topic.")
    parser.add_argument("topic", type=str, help="The topic for the video")

    args = parser.parse_args()
    SAMPLE_TOPIC = args.topic
    SAMPLE_FILE_NAME = "audio_tts.wav"
    VIDEO_SERVER = "pexel"

    response = generate_script(SAMPLE_TOPIC)
    logger.debug(f"Generated script: {response}")
    print("script: {}".format(response))

    asyncio.run(generate_audio(response, SAMPLE_FILE_NAME))
    logger.debug(f"Generated audio file: {SAMPLE_FILE_NAME}")

    timed_captions = generate_timed_captions(SAMPLE_FILE_NAME)
    logger.debug(f"Generated captions: {timed_captions}")
    print(timed_captions)
	
    search_terms = getVideoSearchQueriesTimed(response, timed_captions)
    logger.debug(f"Generated search terms: {search_terms}")
    print(search_terms)
	
    background_video_urls = None
    if search_terms is not None:
        try:
            background_video_urls = generate_video_url(search_terms, VIDEO_SERVER)
            if not background_video_urls or all(url[1] is None for url in background_video_urls):
                raise Exception("Failed to retrieve any videos from Pexels")
            print(background_video_urls)
        except Exception as e:
            print(f"Pexel retrieval failure: {str(e)}. Please try your query again.")
            # return
    else:
        print("No background video")
        logger.debug("No background video")

    background_video_urls = merge_empty_intervals(background_video_urls)

    if background_video_urls is not None:
        video = get_output_media(SAMPLE_FILE_NAME, timed_captions, background_video_urls, VIDEO_SERVER)
        print(video)
        logger.debug(f"Generated video: {video}")
    else:
        print("No video")
        logger.debug("No video")
