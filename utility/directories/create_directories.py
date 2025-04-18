import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

directories = [
    # Core application directories
    'app/core/generators',
    'app/core/processors',
    'app/core/services',
    'app/models',
    'app/utils',
    
    # API and web interface
    'api',
    'web',
    
    # Configuration
    'config',
    'config/data',  # Add this line
    
    # Testing
    'tests',
    'tests/unit',
    'tests/integration',
    
    # Output directories
    'output/audio',
    'output/videos',
    'output/captions',
    'output/logs/gpt_logs',
    'output/logs/pexel_logs',
    'output/logs/app_logs',
    
    # Cache directories
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
