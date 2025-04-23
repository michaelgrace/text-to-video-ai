import os
import sys

# Add the project directory to the path to ensure imports work correctly
# sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import our MoviePy config first to ensure proper initialization
# from utility.render.moviepy_config import *

import time
import tempfile
import zipfile
import platform
import subprocess
from moviepy.editor import (AudioFileClip, CompositeVideoClip, CompositeAudioClip, ImageClip,
                            TextClip, VideoFileClip)
from moviepy.audio.fx.audio_loop import audio_loop
from moviepy.audio.fx.audio_normalize import audio_normalize
import requests

def download_file(url, filename):
    with open(filename, 'wb') as f:
        headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        f.write(response.content)

def search_program(program_name):
    try: 
        search_cmd = "where" if platform.system() == "Windows" else "which"
        return subprocess.check_output([search_cmd, program_name]).decode().strip()
    except subprocess.CalledProcessError:
        return None

def get_program_path(program_name):
    program_path = search_program(program_name)
    return program_path

def get_output_media(audio_file_path, timed_captions, background_video_data, video_server, preset='ultrafast'):
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
    
    visual_clips = []
    for (t1, t2), video_url in background_video_data:
        # Download the video file
        video_filename = tempfile.NamedTemporaryFile(delete=False).name
        download_file(video_url, video_filename)
        
        # Create VideoFileClip from the downloaded file
        video_clip = VideoFileClip(video_filename)
        video_clip = video_clip.set_start(t1)
        video_clip = video_clip.set_end(t2)
        visual_clips.append(video_clip)
    
    audio_clips = []
    audio_file_clip = AudioFileClip(audio_file_path)
    audio_clips.append(audio_file_clip)

    # --- Fix: Ensure last video segment covers full audio duration ---
    audio_duration = audio_file_clip.duration
    if visual_clips:
        last_clip = visual_clips[-1]
        if last_clip.end < audio_duration:
            # Extend the last video segment to match audio duration
            last_clip = last_clip.set_end(audio_duration)
            visual_clips[-1] = last_clip
    # ---------------------------------------------------------------

    # TODO: UI for font control
    for (t1, t2), text in timed_captions:
        text_clip = TextClip(txt=text, fontsize=130, color="yellow", stroke_width=3, stroke_color="black", method="label")
        text_clip = text_clip.set_start(t1)
        text_clip = text_clip.set_end(t2)
        text_clip = text_clip.set_position(["center", 800])
        visual_clips.append(text_clip)

    video = CompositeVideoClip(visual_clips)
    
    if audio_clips:
        audio = CompositeAudioClip(audio_clips)
        video.duration = audio.duration
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
    
    # Clean up downloaded files
    for (t1, t2), video_url in background_video_data:
        video_filename = tempfile.NamedTemporaryFile(delete=False).name
        os.remove(video_filename)

    return OUTPUT_FILE_NAME
