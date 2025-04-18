from pathlib import Path
import os

class Settings:
    PROJECT_ROOT = Path(__file__).parent.parent
    CACHE_DIR = PROJECT_ROOT / "temp/pexels_cache"
    OUTPUT_DIR = PROJECT_ROOT / "output"
    
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
    
    # Service configurations
    VOICE_PROVIDER = os.getenv("VOICE_PROVIDER", "kokoro")
    KOKORO_SERVICE_URL = os.getenv("KOKORO_SERVICE_URL")
    
    # Video generation settings
    MAX_VIDEO_DURATION = 30
    VIDEO_QUALITY = "1080p"
    
    class Config:
        case_sensitive = True

settings = Settings()
