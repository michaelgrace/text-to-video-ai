# PowerShell script for safe GitHub check-in (v0.8.5)

Write-Host "=== Text-To-Video-AI GitHub Check-in Script v0.8.5 ==="
Write-Host "Please ensure you have a local backup of your project before proceeding."
$backup = Read-Host "Have you created a backup? (y/n)"
if ($backup -ne "y") {
    Write-Host "Please create a backup before running this script."
    exit 1
}

git add .
git status

git commit -m @"
v0.8.5: Audio/Video/Caption Sync, Whisper Alignment, Logging, and Echo Investigation

- Video duration now set to max(audio, captions) to prevent premature cutoff.
- Captions are extended to audio duration only if Whisper misses the end.
- Added robust caption JSON logging for traceability and debugging.
- Validated that TTS audio, captions, and video are now aligned for most cases.
- Echo/repeat last word issue documented for further review.
- No changes to Docker config, file locations, or UI logic.
"@

git tag v0.8.5
git push origin main
git push origin v0.8.5
git rev-parse HEAD
