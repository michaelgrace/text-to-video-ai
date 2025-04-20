import time
import os
import tempfile
import zipfile
import platform
import subprocess
from moviepy.editor import (AudioFileClip, CompositeVideoClip, CompositeAudioClip, ImageClip,
                            TextClip, VideoFileClip, ColorClip)
from moviepy.audio.fx.audio_loop import audio_loop
from moviepy.audio.fx.audio_normalize import audio_normalize
import requests
from config.settings import settings
from app.utils.logger_config import setup_logger

# Initialize logger
logger = setup_logger()

def download_file(url, filename):
    with open(filename, 'wb') as f:
        headers = {
            "User-Agent": settings.PEXELS_USER_AGENT
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

def check_gpu_support():
    hwaccel = settings.FFMPEG_HWACCEL
    hwaccel_device = settings.VAAPI_DEVICE
    try:
        if hwaccel and hwaccel_device and os.path.exists(hwaccel_device):
# Comment out GPU monitoring for now
            # subprocess.run(['vainfo'], check=True, capture_output=True)
            return True, hwaccel, hwaccel_device
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    return False, None, None

def get_output_media(audio_file, timed_captions, background_video_urls, video_server):
    OUTPUT_FILE_NAME = settings.DEFAULT_OUTPUT_FILENAME
    magick_path = get_program_path("magick")
    print(magick_path)
    if magick_path:
        os.environ['IMAGEMAGICK_BINARY'] = magick_path
    else:
        os.environ['IMAGEMAGICK_BINARY'] = '/usr/bin/convert'
    
    # Now using centralized settings for:
    # - GPU configuration
    # - Video codecs
    # - Caption styling
    # - File paths and cleanup

    # Configure GPU support using settings
    gpu_available, hwaccel, hwaccel_device = check_gpu_support()
    if gpu_available:
        print("GPU acceleration enabled")
        ffmpeg_params = [
            '-hwaccel', settings.FFMPEG_HWACCEL,
            '-hwaccel_device', settings.VAAPI_DEVICE,
            '-hwaccel_output_format', 'vaapi'
        ]
        codec = settings.VIDEO_CODEC['gpu']
    else:
        print("Using CPU encoding")
        ffmpeg_params = []
        codec = settings.VIDEO_CODEC['cpu']

    visual_clips = []
    for (t1, t2), video_url in background_video_urls:
        if video_url is None:
            # Create black background clip with settings
            black_bg = ColorClip(size=settings.VIDEO_SIZE, color=settings.VIDEO_BLACK_COLOR)
            black_bg = black_bg.set_duration(t2 - t1)
            black_bg = black_bg.set_start(t1)
            black_bg = black_bg.set_end(t2)
            visual_clips.append(black_bg)
        else:
            # Download and process video as before
            video_filename = tempfile.NamedTemporaryFile(delete=False).name
            download_file(video_url, video_filename)
            video_clip = VideoFileClip(video_filename)
            video_clip = video_clip.set_start(t1)
            video_clip = video_clip.set_end(t2)
            visual_clips.append(video_clip)
    
    audio_clips = []
    audio_file_clip = AudioFileClip(audio_file)
    audio_clips.append(audio_file_clip)

    for (t1, t2), text in timed_captions:
        text_clip = TextClip(
            txt=text, 
            fontsize=settings.CAPTION_FONT_SIZE,
            font=settings.CAPTION_FONT,
            color=settings.CAPTION_COLOR,
            stroke_width=settings.CAPTION_STROKE_WIDTH,
            stroke_color=settings.CAPTION_STROKE_COLOR,
            method="label"
        )
        text_clip = text_clip.set_start(t1)
        text_clip = text_clip.set_end(t2)
        text_clip = text_clip.set_position(["center", 800])
        visual_clips.append(text_clip)

    video = CompositeVideoClip(visual_clips)
    
    if audio_clips:
        audio = CompositeAudioClip(audio_clips)
        video.duration = audio.duration
        video.audio = audio

    try:
        video.write_videofile(
            "/app/" + settings.OUTPUT_FILE_NAME,  # Write directly to /app for Streamlit
            codec=settings.VIDEO_CODEC['gpu'] if gpu_available else settings.VIDEO_CODEC['cpu'],
            audio_codec=settings.AUDIO_CODEC,
            fps=settings.VIDEO_FPS,
            preset=settings.VIDEO_PRESET,
            ffmpeg_params=ffmpeg_params,
            threads=settings.FFMPEG_THREAD_COUNT
        )

        # Comment out GPU monitoring
        # final_gpu_usage = monitor_gpu_usage()
        # logger.info(f"Final GPU usage: {final_gpu_usage}")
        
        if gpu_available:
            logger.warning("GPU acceleration may not be working effectively")
            
    except Exception as e:
        logger.error(f"Error with GPU encoding: {e}")
        if codec != settings.VIDEO_CODEC['cpu']:
            print("Falling back to CPU encoding")
            video.write_videofile(
                "/app/" + settings.OUTPUT_FILE_NAME,  # Keep consistent path for fallback
                codec=settings.VIDEO_CODEC['cpu'],
                audio_codec=settings.AUDIO_CODEC,
                fps=settings.VIDEO_FPS,
                preset=settings.VIDEO_PRESET,
                threads=settings.FFMPEG_THREAD_COUNT
            )
    
    # Clean up downloaded files
    for (t1, t2), video_url in background_video_urls:
        video_filename = tempfile.NamedTemporaryFile(delete=False).name
        os.remove(video_filename)

    return "/app/" + settings.OUTPUT_FILE_NAME  # Return Streamlit-compatible path
