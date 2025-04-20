# Simple configuration for MoviePy in Docker
import os

# Get ImageMagick binary path from environment or use default
IMAGEMAGICK_BINARY = os.environ.get('IMAGEMAGICK_BINARY', 'convert')

# Configure MoviePy to use the specified ImageMagick binary
import moviepy.config
moviepy.config.IMAGEMAGICK_BINARY = IMAGEMAGICK_BINARY
