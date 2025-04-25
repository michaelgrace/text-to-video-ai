# Stage all changes
git add .

# Show status for review
git status

# Commit with a detailed message
git commit -m @"
v0.8.3: Improved Photo/Video Relevance, Logging, and Robustness

- Streamlit UI: Rendering mode (video/photo/hybrid) selection and pipeline wiring.
- Photo fallback: Black background for missing assets, robust error handling.
- Image processing: All images resized/padded to fit video frame, correct file extension for MoviePy/Pillow.
- Unified caption styling: Font, color, border, and position via global settings.
- Photo selection: Fuzzy/plural keyword matching, theme/topic/query combination, diversity filter, relaxed fallback.
- Logging: All Pexels photo/video selections, fallbacks, and errors now logged for debugging.
- Bug fixes: Odd image dimensions, unknown file extension, OpenAI JSON, merge logic.
- Docker/requirements: Updated for NLTK, Pillow, MoviePy, and GPU/CPU optimizations.
- Caching: Video API results cached in Postgres; photo caching pending.
- Code and log verticalization utilities added.

Pending Issues:
- Photo relevance still not satisfactory for some topics (e.g., "standard poodle").
- Photo diversity limited; repeated or generic images for some queries.
- Hybrid mode not fully implemented.
- No negative keyword filtering for photos.
- No logging of actual Pexels API queries for photos.
- No advanced photo relevance scoring.
- No photo API caching yet.
"

- RESTORE tag v0.8.3 -> ce347ba616e46d654f739fcc8c159778dcbf775a

# Tag the commit
git tag v0.8.3

# Push commit and tag to origin main
git push origin main
git push origin v0.8.3

# Show the commit hash for reference
git rev-parse HEAD
