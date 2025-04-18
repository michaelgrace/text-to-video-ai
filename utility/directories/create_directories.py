import os

# Get the project root directory (where this script lives)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Create necessary directories for the application
directories = [
    'output',
    'output/photos',
    'output/videos',
    'output/audio',
    'output/captions',    
    'output/logs',
    'output/logs/gpt_logs',
    'output/logs/pexel_logs',
    'output/whisper',
    'output/whisper/audio',
    'output/whisper/captions',
    'output/ffmpeg',
    'output/ffmpeg/audio',
    'output/ffmpeg/videos', 
    'temp',
    'temp/pexels_cache',
    'temp/pexels_cache/videos',
    'temp/pexels_cache/metadata',
    'temp/theme_cache',
    'temp/content_cache'
]

# Make all paths relative to project root
for directory in directories:
    full_path = os.path.join(PROJECT_ROOT, directory)
    os.makedirs(full_path, exist_ok=True)
    print(f"Created directory: {full_path}")

print(f"Directory structure created successfully in: {PROJECT_ROOT}")
