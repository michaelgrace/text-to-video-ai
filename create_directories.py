import os

# Create necessary directories for the application
directories = [
    'output',
    'output/photos',
    'output/videos',
    'output/audio',
    'temp',
    'utility/render',  # This already exists based on your changes
]

for directory in directories:
    os.makedirs(directory, exist_ok=True)
    print(f"Created directory: {directory}")

print("Directory structure created successfully.")
