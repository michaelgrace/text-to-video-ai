import os
import sys
import json
import tempfile
import mimetypes
from urllib.parse import urlparse

# Add the project directory to the path to ensure imports work correctly
# sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import our MoviePy config first to ensure proper initialization
# from utility.render.moviepy_config import *

import time
import zipfile
import platform
import subprocess
from moviepy import AudioFileClip, CompositeVideoClip, CompositeAudioClip, ImageClip, TextClip, VideoFileClip, ColorClip
import requests
from PIL import Image

def download_file(url, filename):
    with open(filename, 'wb') as f:
        headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        f.write(response.content)

def get_extension_from_url(url):
    path = urlparse(url).path
    ext = os.path.splitext(path)[1]
    if ext and ext.lower() in [".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"]:
        return ext
    return ".jpg"  # Default fallback

def search_program(program_name):
    try: 
        search_cmd = "where" if platform.system() == "Windows" else "which"
        return subprocess.check_output([search_cmd, program_name]).decode().strip()
    except subprocess.CalledProcessError:
        return None

def get_program_path(program_name):
    program_path = search_program(program_name)
    return program_path

def is_image_file(filename):
    # Simple check by extension
    return filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp'))

def pad_image_to_even(filename):
    """Pad image to even width and height if needed, overwrite the file."""
    img = Image.open(filename)
    w, h = img.size
    new_w = w + (w % 2)
    new_h = h + (h % 2)
    if (w, h) != (new_w, new_h):
        # Pad the image with black (or white if you prefer)
        new_img = Image.new(img.mode, (new_w, new_h), color=0)
        new_img.paste(img, (0, 0))
        new_img.save(filename)
        img.close()
        new_img.close()
    else:
        img.close()

def resize_and_pad_image(filename, target_width=1920, target_height=1080):
    """Resize and pad image to fit exactly target_width x target_height."""
    img = Image.open(filename)
    # Calculate new size preserving aspect ratio
    img_ratio = img.width / img.height
    target_ratio = target_width / target_height

    if img_ratio > target_ratio:
        # Image is wider than target: fit width, pad height
        new_width = target_width
        new_height = int(target_width / img_ratio)
    else:
        # Image is taller than target: fit height, pad width
        new_height = target_height
        new_width = int(target_height * img_ratio)

    img_resized = img.resize((new_width, new_height), Image.LANCZOS)
    # Create black background and paste resized image centered
    new_img = Image.new("RGB", (target_width, target_height), color=0)
    paste_x = (target_width - new_width) // 2
    paste_y = (target_height - new_height) // 2
    new_img.paste(img_resized, (paste_x, paste_y))
    new_img.save(filename)
    img.close()
    img_resized.close()
    new_img.close()

def load_caption_settings():
    config_path = os.path.join(os.path.dirname(__file__), "../config/global_settings.json")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            return config.get("captions", {})
    except Exception as e:
        print(f"Could not load caption settings: {e}")
        return {}

def get_output_media(audio_file_path, timed_captions, background_video_data, video_server, preset='ultrafast', aspect_ratio='landscape'):
    print("Rendering video...")
    try:
        """
        CPU-optimized preset options:
        - ultrafast: Fastest encoding, larger file size
        - superfast: Very fast encoding
        - veryfast: Good balance of speed/quality
        - medium: Better quality, slower encoding
        """
        OUTPUT_FILE_NAME = "rendered_video.mp4"
        magick_path = get_program_path("magick")
        print(magick_path)
        if magick_path:
            os.environ['IMAGEMAGICK_BINARY'] = magick_path
        else:
            os.environ['IMAGEMAGICK_BINARY'] = '/usr/bin/convert'
        
        # Set video dimensions based on aspect_ratio
        if aspect_ratio == "portrait":
            width, height = 1080, 1920
        elif aspect_ratio == "square":
            width, height = 1080, 1080
        else:
            width, height = 1920, 1080

        visual_clips = []
        for idx, entry in enumerate(background_video_data):
            # Support both [interval, url] and [interval, url, is_photo]
            if len(entry) == 3:
                (t1, t2), media_url, is_photo = entry
            else:
                (t1, t2), media_url = entry
                is_photo = False  # Default to video if not specified

            if media_url is None:
                print(f"NO MEDIA URL for segment {t1}-{t2}, using black background.")
                black_clip = ColorClip(size=(width, height), color=(0, 0, 0)).with_duration(t2 - t1)
                black_clip = black_clip.with_start(t1)
                black_clip = black_clip.with_end(t2)
                visual_clips.append(black_clip)
                print(f"Inserted black background for segment {t1}-{t2}")
                continue

            print(f"Attempting to download and process image: {media_url}")
            # Use correct file extension for image files
            ext = get_extension_from_url(media_url) if (is_photo or media_url.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'))) else ""
            media_filename = tempfile.NamedTemporaryFile(delete=False, suffix=ext).name
            download_file(media_url, media_filename)
            try:
                if is_photo or media_url.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp')):
                    print(f"Processing image for segment {t1}-{t2}: {media_url}")
                    resize_and_pad_image(media_filename, width, height)  # Use dynamic width/height
                    image_clip = ImageClip(media_filename).set_duration(t2 - t1)
                    image_clip = image_clip.with_start(t1)
                    image_clip = image_clip.with_end(t2)
                    visual_clips.append(image_clip)
                    print(f"Used image fallback for segment {t1}-{t2}: {media_url}")
                else:
                    # Handle as video
                    video_clip = VideoFileClip(media_filename)
                    video_clip = video_clip.with_start(t1)
                    video_clip = video_clip.with_end(t2)
                    visual_clips.append(video_clip)
            except Exception as exc:
                print(f"Failed to open media for segment {t1}-{t2}: {media_url}")
                print(f"Error: {exc}")
                continue
        
        audio_clips = []
        audio_file_clip = AudioFileClip(audio_file_path)
        audio_clips.append(audio_file_clip)
        moviepy_duration = audio_file_clip.duration

        # --- Use wave module for WAV files ---
        wave_duration = None
        try:
            import wave
            with wave.open(audio_file_path, 'rb') as wf:
                frames = wf.getnframes()
                rate = wf.getframerate()
                wave_duration = frames / float(rate)
                print(f"WAVE module audio duration: {wave_duration}")
        except Exception as e:
            print(f"Could not get wave audio duration: {e}")

        # --- Use ffprobe ---
        ffmpeg_duration = None
        try:
            import subprocess
            ffprobe_cmd = [
                "ffprobe", "-v", "error", "-show_entries",
                "format=duration", "-of",
                "default=noprint_wrappers=1:nokey=1", audio_file_path
            ]
            ffprobe_out = subprocess.check_output(ffprobe_cmd).decode().strip()
            ffmpeg_duration = float(ffprobe_out)
            print(f"FFmpeg-reported audio duration: {ffmpeg_duration}")
        except Exception as e:
            print(f"Could not get ffmpeg audio duration: {e}")

        # --- Use pydub ---
        pydub_duration = None
        try:
            from pydub import AudioSegment
            audio = AudioSegment.from_file(audio_file_path)
            pydub_duration = len(audio) / 1000.0
            print(f"Pydub audio duration: {pydub_duration}")
        except Exception as e:
            print(f"Could not get pydub audio duration: {e}")

        # --- Use audioread ---
        audioread_duration = None
        try:
            import audioread
            with audioread.audio_open(audio_file_path) as f:
                audioread_duration = f.duration
                print(f"Audioread audio duration: {audioread_duration}")
        except Exception as e:
            print(f"Could not get audioread audio duration: {e}")

        # --- Use mutagen ---
        mutagen_duration = None
        try:
            from mutagen import File as MutagenFile
            mfile = MutagenFile(audio_file_path)
            if mfile is not None and mfile.info is not None:
                mutagen_duration = mfile.info.length
                print(f"Mutagen audio duration: {mutagen_duration}")
        except Exception as e:
            print(f"Could not get mutagen audio duration: {e}")

        # --- Use the maximum duration ---
        durations = [
            moviepy_duration, wave_duration, ffmpeg_duration,
            pydub_duration, audioread_duration, mutagen_duration
        ]
        durations = [d for d in durations if d]
        if durations:
            audio_duration = max(durations)
            print(f"Using max audio duration: {audio_duration}")
        else:
            audio_duration = moviepy_duration
            print(f"Falling back to MoviePy audio duration: {audio_duration}")

        # --- Ensure last caption extends to audio end ---
        if timed_captions and audio_duration:
            last_start, last_end = timed_captions[-1][0]
            if audio_duration - last_end > 0.1:
                print(f"Extending last caption from {last_end} to {audio_duration}")
                timed_captions[-1] = ((last_start, audio_duration), timed_captions[-1][1])

        caption_settings = load_caption_settings()
        # Default settings
        font = caption_settings.get("font", "DejaVuSans-Bold")
        fontsize = caption_settings.get("fontsize", 80)
        fontcolor = caption_settings.get("fontcolor", "yellow")
        stroke_color = caption_settings.get("stroke_color", "black")
        stroke_width = caption_settings.get("stroke_width", 3)
        caption_position = caption_settings.get("caption_position", ["center", "bottom"])
        caption_margin = caption_settings.get("caption_margin", 80)
        # Portrait overrides
        if aspect_ratio == "portrait":
            fontsize = 75
            caption_margin = 140
            caption_position = ["center", "bottom"]
            text_max_width = 864  # Fixed width for wrapping
        else:
            text_max_width = width

        # After visual_clips are created, get video height for caption positioning
        video_height = height  # Use dynamic height for caption positioning

        for (t1, t2), text in timed_captions:
            # Ensure no caption ends after audio
            t2 = min(t2, audio_file_clip.duration)
            text_clip = TextClip(
                text=text,
                font_size=fontsize,
                color=fontcolor,
                font=font,
                stroke_width=stroke_width,
                stroke_color=stroke_color,
                method="caption",  # <-- Use 'caption' for wrapping and margin
                size=(text_max_width, None)  # Fixed width, allow wrapping
            )
            # Position logic
            if caption_position == ["center", "center"]:
                text_clip = text_clip.with_position("center")
            elif caption_position == ["center", "bottom"]:
                if aspect_ratio == "portrait":
                    # Align top of caption to top of bottom third
                    text_clip = text_clip.with_position(
                        lambda txt: (
                            (width - text_clip.w) // 2,
                            int(video_height * 2 / 3)
                        )
                    )
                else:
                    # Place at bottom with margin and horizontal centering
                    text_clip = text_clip.with_position(
                        lambda txt: (
                            (width - text_clip.w) // 2,
                            video_height - text_clip.h - caption_margin
                        )
                    )
            else:
                text_clip = text_clip.with_position("center")
            text_clip = text_clip.with_start(t1)
            text_clip = text_clip.with_end(t2)
            visual_clips.append(text_clip)

        # --- Set video duration to audio duration plus a small buffer ---
        buffer = 0.5  # seconds, to ensure no cutoff
        final_duration = audio_duration + buffer

        video = CompositeVideoClip(visual_clips)
        if audio_clips:
            audio = CompositeAudioClip(audio_clips)
            video = video.with_duration(final_duration)
            video.audio = audio

        # CPU-optimized encoding configuration
        threads = os.environ.get('FFMPEG_THREADS', '8')
        video.write_videofile(
            OUTPUT_FILE_NAME,
            codec='libx264',  # CPU encoder
            audio_codec='aac',
            fps=25,
            preset=preset,
            ffmpeg_params=[
                '-threads', threads,
                '-preset', 'ultrafast',
                '-crf', '28',  # Lower quality but faster encoding
                '-pix_fmt', 'yuv420p',
                '-movflags', '+faststart',
                '-max_muxing_queue_size', '1024'
            ]
        )

        # --- FFmpeg log handling ---
        ffmpeg_log_src = "/app/tmp/ffmpeg_report.log"
        ffmpeg_log_dir = "exports/logs/ffmpeg"
        if os.path.exists(ffmpeg_log_src):
            os.makedirs(ffmpeg_log_dir, exist_ok=True)
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            log_dest = os.path.join(ffmpeg_log_dir, f"ffmpeg_{timestamp}.log")
            try:
                os.rename(ffmpeg_log_src, log_dest)
                print(f"FFmpeg log saved to {log_dest}")
            except Exception as e:
                print(f"Failed to move FFmpeg log: {e}")

        # Clean up downloaded files
        for (t1, t2), media_url in background_video_data:
            media_filename = tempfile.NamedTemporaryFile(delete=False).name
            os.remove(media_filename)

        return OUTPUT_FILE_NAME
    except Exception as e:
        print(f"Error rendering video: {e}")
        raise
