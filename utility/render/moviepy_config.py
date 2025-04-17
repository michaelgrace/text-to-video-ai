# Simple configuration for MoviePy in Docker
import os
import subprocess

# Get ImageMagick binary path from environment or use default
IMAGEMAGICK_BINARY = os.environ.get('IMAGEMAGICK_BINARY', 'convert')

# Configure MoviePy to use the specified ImageMagick binary
import moviepy.config
moviepy.config.IMAGEMAGICK_BINARY = IMAGEMAGICK_BINARY

# Configure FFmpeg for GPU acceleration if available
def check_vaapi_support():
    try:
        result = subprocess.run(['vainfo'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

# Set FFmpeg defaults based on hardware
if check_vaapi_support():
    moviepy.config.FFMPEG_BINARY = 'ffmpeg'
    os.environ['FFMPEG_HWACCEL'] = 'vaapi'
    os.environ['FFMPEG_VAAPI_DEVICE'] = '/dev/dri/renderD128'
