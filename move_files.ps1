# First create backup of files
Copy-Item -Path "utility" -Destination "utility_backup" -Recurse

# Move files to new structure
$moves = @{
    "utility/script/script_generator.py" = "app/services/openai_service.py"
    "utility/audio/audio_generator.py" = "app/services/edge_tts_service.py"
    "utility/video/background_video_generator.py" = "app/services/pexels_service.py"
    "utility/video/video_search_query_generator.py" = "app/core/search_generator.py"
    "utility/captions/timed_captions_generator.py" = "app/core/caption_generator.py"
    "utility/render/render_engine.py" = "app/core/render.py"
    "utility/utils.py" = "app/utils/helpers.py"
}

foreach ($source in $moves.Keys) {
    $destination = $moves[$source]
    Copy-Item -Path $source -Destination $destination -Force
    Write-Host "Moved $source to $destination"
}

Write-Host "Files moved. Please verify the new structure before deleting utility_backup/"
