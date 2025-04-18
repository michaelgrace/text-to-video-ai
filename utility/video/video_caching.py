import os
import json
import hashlib
from pathlib import Path

class VideoCache:
    def __init__(self):
        self.cache_dir = Path("temp/pexels_cache")
        self.video_dir = self.cache_dir / "videos"
        self.metadata_dir = self.cache_dir / "metadata"
        self._ensure_dirs()

    def _ensure_dirs(self):
        self.video_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_key(self, query, orientation):
        query_hash = hashlib.md5(f"{query}:{orientation}".encode()).hexdigest()
        return query_hash

    def get_cached_video(self, query, orientation=True):
        cache_key = self._get_cache_key(query, orientation)
        metadata_file = self.metadata_dir / f"{cache_key}.json"
        if metadata_file.exists():
            with open(metadata_file) as f:
                return json.load(f)
        return None

    def cache_video(self, query, video_data, orientation=True):
        cache_key = self._get_cache_key(query, orientation)
        metadata_file = self.metadata_dir / f"{cache_key}.json"
        with open(metadata_file, 'w') as f:
            json.dump(video_data, f)
