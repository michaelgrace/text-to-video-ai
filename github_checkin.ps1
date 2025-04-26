# PowerShell script for safe GitHub check-in (v0.8.6)

Write-Host "=== Text-To-Video-AI GitHub Check-in Script v0.8.6 ==="
Write-Host "Please ensure you have a local backup of your project before proceeding."
$backup = Read-Host "Have you created a backup? (y/n)"
if ($backup -ne "y") {
    Write-Host "Please create a backup before running this script."
    exit 1
}

git add .
git status

git commit -m @"
v0.8.9 - Portrait caption alignment (top of bottom third), font/wrapping tuning, maxCaptionSize for portrait, MoviePy 2.x compatibility, config and CLI/Streamlit integration

- Portrait video rendering: Caption alignment improved—captions now align to the top of the bottom third of the video in portrait mode for better mobile readability.
- Caption font size and wrapping further tuned for portrait mode.
- maxCaptionSize is set to 20 for portrait mode in caption generation.
- MoviePy 2.x compatibility maintained throughout the pipeline.
- CLI and Streamlit integration: aspect ratio and render mode are passed through the pipeline.
- No unrelated code was refactored or deleted; all changes are focused on video rendering, caption styling, audio sync, and configuration.

PENDING/OPEN:
- Further user feedback and testing for portrait caption appearance and wrapping.
- Additional review of caption splitting and edge cases for long sentences.
"@

git tag v0.8.6
git push origin main
git push origin v0.8.6
git rev-parse HEAD
