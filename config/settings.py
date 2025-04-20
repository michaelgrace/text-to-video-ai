from pathlib import Path
import os

class Settings:
    PROJECT_ROOT = Path(__file__).parent.parent
    CACHE_DIR = PROJECT_ROOT / "temp/pexels_cache"
    OUTPUT_DIR = PROJECT_ROOT / "exports"

    OUTPUT_FILE_NAME = "rendered_video.mp4"
    
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
    ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
    TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
    
    # Voice Services
    VOICE_PROVIDER = os.getenv("VOICE_PROVIDER", "kokoro")
    KOKORO_SERVICE_URL = os.getenv("KOKORO_SERVICE_URL", "http://kokoro_service:8880")
    ELEVENLABS_SERVICE_URL = os.getenv("ELEVENLABS_SERVICE_URL", "https://api.elevenlabs.io/v1")
    TIKTOK_SERVICE_URL = os.getenv("TIKTOK_SERVICE_URL", "https://tiktok-tts.weilnet.workers.dev/api/generation")
    
    # Kokoro Service settings
    KOKORO_TIMEOUT = 30  # seconds
    
    # Debug Settings
    DEBUG_MODE = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
    CLEAN_TEMP_FILES = not bool(os.getenv('PRESERVE_TEMP', 'false').lower() == 'true')
       
    # Video generation settings
    MAX_VIDEO_DURATION = 30
    VIDEO_QUALITY = "1080p"
    
    # Audio settings
    DEFAULT_AUDIO_FILENAME = "audio_tts.wav"
    DEFAULT_VOICE = "af_heart"
    DEFAULT_VOICE_SPEED = 0.8
    
    # Video settings
    VIDEO_SERVER = "pexel"
    FALLBACK_VOICE = "en-AU-WilliamNeural"
    MIN_VIDEO_WIDTH = 1920
    MIN_VIDEO_HEIGHT = 1080
    ASPECT_RATIO = 16/9
    VIDEOS_PER_PAGE = 15
    MAX_RETRIES = 3
    
    # Cache settings
    CACHE_DURATION_DAYS = 1
    MAX_HISTORY_VIDEOS = 50
    
    # API settings - Standard Pexels URLs (no need for env vars)
    PEXELS_SEARCH_URL = "https://api.pexels.com/videos/search"
    PEXELS_PHOTO_URL = "https://api.pexels.com/v1/search"
    PEXELS_PHOTO_CURATED_URL = "https://api.pexels.com/v1/curated"
    PEXELS_VIDEO_CURATED_URL = "https://api.pexels.com/videos/curated"
    PEXELS_PER_PAGE = 15
    PEXELS_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    # Photo output configuration
    PHOTO_OUTPUT_DIR = "./exports/photos"
    
    # Video search settings
    MAX_SEARCH_ATTEMPTS = 3
    SEARCH_BACKOFF_MIN = 4
    SEARCH_BACKOFF_MAX = 10
    
    # Video file formats
    DEFAULT_VIDEO_FORMAT = "mp4"
    DEFAULT_AUDIO_FORMAT = "mp3"
    DEFAULT_OUTPUT_FILENAME = "rendered_video.mp4"
    
    # Log file settings
    LOG_ROTATION = "500 MB"
    LOG_RETENTION = "10 days"
    DEBUG_LOG_FILE = "exports/logs/debug.log"
    
    # Script Generation
    GPT_MODEL = "gpt-4-turbo"
    
    # Video Search
    VIDEO_ORIENTATION_LANDSCAPE = True
    VIDEO_DURATION_TARGET = 15  # Target video duration in seconds
    VIDEO_FILE_FORMAT = "mp4"
    
    # API Settings
    API_RETRY_ATTEMPTS = 3
    API_BACKOFF_FACTOR = 2
    
    # Cache settings (for video searching)
    CACHE_EXPIRY_DAYS = 1
    CACHE_MAX_ENTRIES = 1000
    
    # File Management
    CLEAN_TEMP_FILES = not bool(os.getenv('PRESERVE_TEMP', 'false').lower() == 'true')
    
    # MoviePy settings
    FFMPEG_BINARY = "ffmpeg"
    VAAPI_DEVICE = "/dev/dri/renderD128"
    
    # Script Generation (from script_generator.py)
    MAX_SCRIPT_LENGTH = 140  # words
    MAX_VIDEO_LENGTH = 50  # seconds
        
    # Search configuration (from video_generator.py)
    VIDEO_MIN_WIDTH = 1920
    VIDEO_MIN_HEIGHT = 1080
    TARGET_DURATION = 15
    SEARCH_RETRY_DELAY = 2
    
    # Alternative search (from video_generator.py)
    GENERIC_ALTERNATIVES = {
        "person": ["people outdoors", "human activity"],
        "animal": ["wildlife", "nature"],
        "building": ["architecture", "city view"],
        "night": ["evening scene"],
        "water": ["ocean waves"]
    }
    
    # Image processing
    IMAGEMAGICK_BINARY = os.getenv('IMAGEMAGICK_BINARY', '/usr/bin/convert')
    
    # Video Search Filters
    VIDEO_LANDSCAPE_WIDTH = 1920
    VIDEO_LANDSCAPE_HEIGHT = 1080
    VIDEO_PORTRAIT_WIDTH = 1080
    VIDEO_PORTRAIT_HEIGHT = 1920
    VIDEO_TARGET_DURATION = 15
    
    # Error handling
    MAX_RETRIES = 3
    RETRY_BACKOFF_MIN = 4
    RETRY_BACKOFF_MAX = 10
    
    # Process control
    SEARCH_BATCH_SIZE = 15
    EXPONENTIAL_BACKOFF_BASE = 2
    
    # File paths
    FFMPEG_LOG_PATH = "exports/logs/ffmpeg/ffmpeg_report.log"
    SEARCH_HISTORY_PATH = "temp/pexels_cache/usage_history.json"
    
    # Resource settings
    CPU_THREAD_COUNT = 8
    FFMPEG_THREAD_COUNT = 8
    
    IMAGEMAGICK_BINARY = os.getenv('IMAGEMAGICK_BINARY', '/usr/bin/convert')
    
    # GPT API Configuration
    GPT_MODEL = "gpt-4-turbo"
    GPT_FALLBACK_MODEL = "gpt-3.5-turbo"
    GPT_TEMPERATURE = 0.7
    GPT_MAX_TOKENS = 1000
    
    # Progress tracking
    PROGRESS_STAGES = {
        "script": {
            "name": "🤖 Generating script...",
            "weight": 25
        },
        "audio": {
            "name": "🎵 Creating audio...",
            "weight": 25
        },
        "captions": {
            "name": "📝 Generating captions...",
            "weight": 25
        },
        "video": {
            "name": "🎬 Processing video...",
            "weight": 25
        }
    }
    
    # Backup settings
    BACKUP_RETENTION_DAYS = 7
    BACKUP_DIR = "backup"
    
    # Search alternatives (improve video search results)
    WORD_REPLACEMENTS = {
        "the": "",
        "a": "",
        "an": ""
    }
    
    # Default paths
    LOG_PATHS = {
        "GPT": "exports/logs/gpt_logs",
        "PEXEL": "exports/logs/pexel_logs",
        "FFMPEG": "exports/logs/ffmpeg"
    }
    
    # Caption settings
    MAX_CAPTION_CHARS = 25 # Renamed from SUBTITLE_MAX_CHARS
    DEFAULT_CAPTION_SIZE = 15  # Default size if not specified
    
    # Whisper model settings
    WHISPER_MODEL_SIZE = "base"
    WHISPER_FP16_ENABLED = False
    WHISPER_VERBOSE = False    
    
    # File naming patterns
    GPT_LOG_FILENAME_PATTERN = "{}_gpt3.txt"
    PEXEL_LOG_FILENAME_PATTERN = "{}_pexel.txt"
    DATE_FORMAT = "%Y%m%d_%H%M%S"
    
    # Video URL parsing
    VIDEO_URL_SPLIT_PATTERN = ".hd"
    
    # Regex patterns
    WORD_CLEANING_PATTERN = r'[^\w\s\-_"\'\']'
    SENTENCE_SPLIT_PATTERN = r'(?<=[.!?]) +'
    
    # Cache settings
    CACHE_FILE_EXTENSION = "json"
    MD5_ENCODING = "utf-8"
    
    # Video rendering settings
    FADE_DURATION = 0.5
    CAPTION_FONT_SIZE = 40
    CAPTION_FONT = "Arial"
    CAPTION_COLOR = 'white'
    CAPTION_STROKE_COLOR = 'black'
    CAPTION_STROKE_WIDTH = 2
    
    # Video Encoding Settings
    VIDEO_FPS = 25
    VIDEO_PRESET = "veryfast" # Preset for encoding speed
    VIDEO_CODEC = {
        "cpu": "libx264",
        "gpu": "h264_vaapi"
    }
    AUDIO_CODEC = "aac"
    VIDEO_BLACK_COLOR = (0, 0, 0)
    VIDEO_SIZE = (1920, 1080)
    
    # Error messages
    ERROR_MESSAGES = {
        "API_KEYS_MISSING": "Please provide both API keys",
        "VIDEO_NOT_FOUND": "Video file not found. Check the console output for details.",
        "NO_VIDEOS_FOUND": "No videos found, using black background",
        "PEXEL_FAILURE": "Pexel retrieval failure: {}. Using black background."
    }
    
    # Video Background Fallback
    USE_BLACK_BACKGROUND = True
    BLACK_BACKGROUND_DURATION = None  # Will be set from last caption time
    
    # File processing
    FILENAME_SEPARATOR = "-"
    ALLOWED_FILENAME_CHARS = "alphanumeric-"
    
    # Voice Settings
    VOICE_PROVIDERS = ["kokoro", "elevenlabs", "tiktok"]
    VOICE_FALLBACK_ORDER = ["kokoro", "edge-tts"]
    
    # Response Processing
    JSON_PARSE_RETRIES = 2
    
    # System Messages
    GENERATING_MESSAGE = "Generating your video... This might take a while."
    SUCCESS_MESSAGE = "Video generated successfully!"
    
    # Voice Synthesis Settings
    TTS_RESPONSE_FORMAT = "mp3"
    TTS_DEFAULT_PROVIDER = "kokoro"
    
    # Script Generation Prompts
    SCRIPT_EXAMPLE = """Weird facts you don't know:
        - Bananas are berries, but strawberries aren't.
        - A single cloud can weigh over a million pounds.
        - There's a species of jellyfish that is biologically immortal."""
    
    # Directory Structure
    CORE_DIRECTORIES = [
        'app/core/generators',
        'app/core/processors',
        'app/core/services',
        'app/models',
        'app/utils',
        'api',
        'web',
        'config',
        'config/data',
        'tests',
        'tests/unit',
        'tests/integration'
    ]
    
    # Kokoro Voice Settings
    KOKORO_VOICES_FILE = "config/data/kokoro_voices.json"
    KOKORO_DEFAULT_VOICES = ["af_heart"]
    
    # Content Management
    CONTENT_EXPIRY_DAYS = 7
    CONTENT_BATCH_SIZE = 15
    
    # Image Generation Defaults
    IMAGE_QUALITY = "high"
    IMAGE_WIDTH = 1920
    IMAGE_HEIGHT = 1080
    
    # Content Safety
    UNSAFE_CONTENT_THRESHOLD = 0.8
    CONTENT_FILTER_STRICT = True
    
    # Application Paths
    CONFIG_PATH = PROJECT_ROOT / "config" / "data"
    TEMP_CLEANUP_ENABLED = True
    TEMP_CLEANUP_AGE = 24  # hours
    
    # Hardware Acceleration
    GPU_ENABLED = True
    GPU_MEMORY_FRACTION = 0.8
    CUDA_VISIBLE_DEVICES = "0"
    
    # Application Metadata
    APP_NAME = "Text-To-Video AI"
    APP_VERSION = "0.5.0"
    APP_ICON = "🎬"
    APP_DESCRIPTION = "Generate video from text using AI"
    
    # FFmpeg hardware acceleration
    FFMPEG_HWACCEL = os.getenv('FFMPEG_HWACCEL', 'vaapi')
    FFMPEG_PARAMS = {
        'gpu': ['-hwaccel', 'vaapi', '-hwaccel_output_format', 'vaapi'],
        'cpu': []
    }
    
    # HTTP Headers
    HTTP_HEADERS = {
        "User-Agent": PEXELS_USER_AGENT
    }
    
    # Caption position
    CAPTION_POSITION = ["center", 800]  # [x, y] coordinates
    
    # Application Defaults
    DEFAULT_TOPIC = "Tell me an interesting fact"
    
    class Config:
        case_sensitive = True

settings = Settings()
