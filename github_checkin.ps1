# Stage all changes
git add .

# Show status for review
git status

# Commit with a detailed message
git commit -m @"
v0.8.2: Unified Real-Time Log Window, Backend Stage Prints, and Log Download

- Streamlit UI now features a single, continuously updated log window (monospaced, 550px, auto-scroll) for all backend output, including status, stage, errors, and progress (except %).
- Separate Streamlit progress bar and status alert for each pipeline stage.
- Log window is cleared for each new video generation and remains visible after completion.
- All backend pipeline steps now print clear stage/status messages and errors for comprehensive log feedback.
- Log is saved as formatted JSON (with metadata: timestamps, stage, line) to exports/logs/video_generation/ using the video title as filename (enumerated if duplicate).
- Download log button is always available after a run, regardless of video generation success.
- No duplicate log windows: only one log window is rendered and updated in place.
- Backend and UI changes follow project guidelines: no deletion of existing code, minimal disruption, and clear separation of new logic.
- NOTE: Caption text and selected video per caption are not yet displayed in the UI; this will be addressed in a future UX update.

"@

# Tag the commit
git tag v0.8.2

# Push commit and tag to origin main
git push origin main
git push origin v0.8.2

# Show the commit hash for reference
git rev-parse HEAD
