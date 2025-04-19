from loguru import logger
import sys
from config.settings import settings

def setup_logger():
    """Configure and return a logger instance"""
    # Remove default handler
    logger.remove()
    
    # Add console handler
    logger.add(sys.stderr, level="INFO")
    
    # Add file handler for debug logs
    logger.add(
        settings.DEBUG_LOG_FILE,
        rotation=settings.LOG_ROTATION,
        retention=settings.LOG_RETENTION,
        level="DEBUG"
    )
    
    return logger
