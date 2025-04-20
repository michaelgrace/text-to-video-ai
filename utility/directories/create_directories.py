import os

# Get the project root directory (where this script lives)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Create necessary directories for the application
directories = [
    'output',
    'exports/photos',
    'exports/videos',
    'exports/audio',
    'exports/captions',    
    'temp'
]

# Make all paths relative to project root
for directory in directories:
    full_path = os.path.join(PROJECT_ROOT, directory)
    os.makedirs(full_path, exist_ok=True)
    print(f"Created directory: {full_path}")

print(f"Directory structure created successfully in: {PROJECT_ROOT}")
