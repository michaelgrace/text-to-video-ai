from openai import OpenAI
import os
import edge_tts
import json
import asyncio
import whisper_timestamped as whisper
import tempfile

from app.services.kokoro_service import kokoro_client
from app.services.openai_service import generate_script
from app.core.audio_generator import generate_audio
from app.core.caption_generator import generate_timed_captions, get_audio_duration
from app.services.pexels_diversity import generate_video_url_diverse
from app.core.render import get_output_media
from app.core.search_generator import getVideoSearchQueriesTimed, merge_empty_intervals

import argparse
from datetime import datetime

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a video from a topic or custom script.")
    parser.add_argument("input_text", type=str, nargs="?", help="The topic or custom script for the video")
    parser.add_argument("--theme", type=str, required=True, help="Theme for the video")
    parser.add_argument("--aspect-ratio", type=str, default="landscape", choices=["landscape", "portrait", "square"], help="Aspect ratio for the video")
    parser.add_argument("--title", type=str, required=True, help="Title (video name)")
    parser.add_argument("--custom-script", action="store_true", help="Use input as custom script (bypass OpenAI)")
    parser.add_argument("--render-mode", type=str, default="video", choices=["video", "photo", "hybrid (both)"], help="Rendering mode: video, photo, or hybrid (both)")
    parser.add_argument("--audio-file", type=str, help="Path to user-uploaded audio file (bypass TTS)")
    parser.add_argument("--disable-captions", action="store_true", help="Do not render captions on the video")
    parser.add_argument("--disable-audio", action="store_true", help="Do not add audio to the rendered video")
    parser.add_argument("--soundtrack-file", type=str, help="Optional background soundtrack audio file")
    parser.add_argument("--soundtrack-volume", type=float, default=0.4, help="Soundtrack volume (0.0-1.0, default 0.1)")
    # Add max-seconds and max-words arguments
    parser.add_argument("--max-seconds", type=int, default=30, help="Maximum duration for the script in seconds")
    parser.add_argument("--max-words", type=int, default=50, help="Maximum number of words for the script")
    args = parser.parse_args()
    SAMPLE_FILE_NAME = os.path.join(tempfile.gettempdir(), "audio_tts.wav")  # Use absolute path in Docker/Linux
    VIDEO_SERVER = "pexel"

    print("video_title:", args.title)

    if args.audio_file:
        # User uploaded audio, skip script and TTS
        print("Using uploaded audio file:", args.audio_file)
        SAMPLE_FILE_NAME = args.audio_file
        # For search/captions, need a script text. Use a placeholder or empty string.
        response = ""
    else:
        if args.custom_script:
            print("Generating script (custom)...")
            response = args.input_text
        else:
            print("Generating script with OpenAI...")
            response = generate_script(
                args.theme,
                args.input_text,
                max_seconds=args.max_seconds,
                max_words=args.max_words
            )
        print("script:", response)

        print("Generating audio...")
        asyncio.run(generate_audio(response, SAMPLE_FILE_NAME))

    print("Generating captions...")
    timed_captions = generate_timed_captions(SAMPLE_FILE_NAME, aspect_ratio=args.aspect_ratio)
    print("timed_captions:", json.dumps(timed_captions))  # Print as JSON
    if not timed_captions:
        print("WARNING: No captions were generated!")

    # --- DEBUG: Print audio duration and last caption end ---
    audio_duration = get_audio_duration(SAMPLE_FILE_NAME)
    print("AUDIO FILE DURATION:", audio_duration)
    if timed_captions:
        print("LAST CAPTION END:", timed_captions[-1][0][1])

    # --- Save captions as JSON ---
    captions_dir = "exports/logs/captions"
    os.makedirs(captions_dir, exist_ok=True)
    safe_title = "".join(c for c in args.title if c.isalnum() or c in (' ', '_', '-')).rstrip().replace(" ", "_")
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    captions_path = os.path.join(captions_dir, f"{timestamp}-{safe_title}.json")
    captions_log = {
        "title": args.title,
        "audio_file": SAMPLE_FILE_NAME,
        "audio_duration": audio_duration,
        "captions": timed_captions
    }
    with open(captions_path, "w", encoding="utf-8") as f:
        json.dump(captions_log, f, indent=2)
    print(f"Saved captions log: {captions_path}")

    print("Generating search terms...")
    # For search_terms, if response is empty (audio upload), you may want to use captions as context
    if not response and timed_captions:
        # Use all captions as a single string for search context
        response = " ".join([c[1] for c in timed_captions])
    search_terms = getVideoSearchQueriesTimed(response, timed_captions)
    print("search_terms:", json.dumps(search_terms))  # Print as JSON
    print("theme:", args.theme)
    print("input_text:", args.input_text)

    background_video_urls = None
    if search_terms is not None:
        print("Generating background video URLs...")
        background_video_urls = generate_video_url_diverse(
            search_terms,
            VIDEO_SERVER,
            theme=args.theme,
            aspect_ratio=args.aspect_ratio,
            video_name=args.title,
            topic=args.input_text,
            render_mode=args.render_mode  # <-- pass render mode
        )
        print("background_video_urls:", json.dumps(background_video_urls))  # Print as JSON
    else:
        print("No background video")
        print("Failed search_terms:", search_terms)
        print("Query context - theme:", args.theme, "input_text:", args.input_text)

    if background_video_urls is not None:
        # Only keep [interval, url] for merge_empty_intervals
        background_video_urls_for_merge = [
            [interval, url] for interval, url, _ in background_video_urls
        ]
        print("Merging empty intervals in background video URLs...")
        background_video_urls_merged = merge_empty_intervals(background_video_urls_for_merge)
        if background_video_urls_merged is not None:
            print("Rendering video...")
            # --- Prepare kwargs for soundtrack ---
            render_kwargs = dict(
                preset='ultrafast',
                aspect_ratio=args.aspect_ratio,
                disable_captions=getattr(args, "disable_captions", False),
                disable_audio=getattr(args, "disable_audio", False)
            )
            if getattr(args, "soundtrack_file", None):
                print(f"Soundtrack file received: {args.soundtrack_file}")
                render_kwargs["soundtrack_file"] = "/app/audio_soundtrack_uploaded.wav"
                render_kwargs["soundtrack_volume"] = args.soundtrack_volume
            # video = get_output_media(
            #     SAMPLE_FILE_NAME,
            #     timed_captions,
            #     background_video_urls_merged,
            #     VIDEO_SERVER,
            #     preset='ultrafast',
            #     aspect_ratio=args.aspect_ratio,  # <-- pass aspect ratio
            #     disable_captions=getattr(args, "disable_captions", False),  # <-- pass flag
            #     disable_audio=getattr(args, "disable_audio", False)         # <-- pass flag
            # )
            video = get_output_media(
                SAMPLE_FILE_NAME,
                timed_captions,
                background_video_urls_merged,
                VIDEO_SERVER,
                preset='ultrafast',
                aspect_ratio=args.aspect_ratio,
                disable_captions=getattr(args, "disable_captions", False),
                disable_audio=getattr(args, "disable_audio", False),
                soundtrack_file=render_kwargs.get("soundtrack_file"),
                soundtrack_volume=render_kwargs.get("soundtrack_volume")
            )
            print("video:", video)
        else:
            print("merge_empty_intervals returned None. Failed background_video_urls:", json.dumps(background_video_urls))
            print("Query context - theme:", args.theme, "input_text:", args.input_text, "search_terms:", json.dumps(search_terms))
    else:
        print("background_video_urls is None. Failed search_terms:", json.dumps(search_terms))
        print("Query context - theme:", args.theme, "input_text:", args.input_text)
