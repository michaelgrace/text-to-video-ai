import os

directories = [
    # Core application directories
    'app/core/generators',
    'app/core/processors',
    'app/core/services',
    'app/models',
    'app/utils',
    'api',
    'web',
    'config',
    'config/data',
    'tests',
    'tests/unit',
    'tests/integration',
    
    # Cache directories
    'temp',
    'temp/pexels_cache',
    'temp/pexels_cache/videos',
    'temp/pexels_cache/metadata',
    'temp/theme_cache',
    'temp/content_cache',

    # Export directories
    'exports',
    'exports/audio',
    'exports/videos',
    'exports/captions', 
    'exports/logs/gpt_logs',
    'exports/logs/pexel_logs',
    'exports/logs/ffmpeg',
    'exports/photos'
]

for directory in directories:
    os.makedirs(directory, exist_ok=True)
    print(f"Created directory: {directory}")


