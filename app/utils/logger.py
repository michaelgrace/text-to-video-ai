from loguru import logger
import sys
import os
from config.settings import settings

def setup_logger():
    # Remove default logger
    logger.remove()
    
    # Debug level based on environment
    log_level = "DEBUG" if os.getenv('DEBUG_MODE') == 'true' else "INFO"
    
    # Console output
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=log_level
    )
    
    # File output for debugging
    if log_level == "DEBUG":
        logger.add(
            settings.DEBUG_LOG_FILE,
            rotation=settings.LOG_ROTATION,
            retention=settings.LOG_RETENTION,
            level="DEBUG"
        )

    return logger
