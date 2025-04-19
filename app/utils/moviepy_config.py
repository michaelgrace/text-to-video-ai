import os
import subprocess
from config.settings import settings

# Configure MoviePy
import moviepy.config
moviepy.config.IMAGEMAGICK_BINARY = os.environ.get('IMAGEMAGICK_BINARY', 'convert')

# Configure FFmpeg for GPU acceleration if available
def check_vaapi_support():
    try:
        result = subprocess.run(['vainfo'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

# Set FFmpeg defaults based on hardware
if check_vaapi_support():
    moviepy.config.FFMPEG_BINARY = settings.FFMPEG_BINARY
    os.environ['FFMPEG_HWACCEL'] = 'vaapi'
    os.environ['FFMPEG_VAAPI_DEVICE'] = settings.VAAPI_DEVICE