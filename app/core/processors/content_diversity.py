from collections import defaultdict
import json
from pathlib import Path

class ContentDiversity:
    def __init__(self):
        self.used_videos = defaultdict(int)
        self.usage_limit = 3
        self.usage_file = Path("temp/content_cache/used_videos.json")
        self._load_usage()

    def _load_usage(self):
        if self.usage_file.exists():
            with open(self.usage_file) as f:
                self.used_videos = defaultdict(int, json.load(f))

    def _save_usage(self):
        self.usage_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.usage_file, 'w') as f:
            json.dump(dict(self.used_videos), f)

    def can_use_video(self, video_id: str) -> bool:
        return self.used_videos[video_id] < self.usage_limit

    def record_usage(self, video_id: str):
        self.used_videos[video_id] += 1
        self._save_usage()

    def get_usage_count(self, video_id: str) -> int:
        return self.used_videos[video_id]
