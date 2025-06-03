"""
Logging configuration for the application.
"""
import logging
import sys
from typing import Dict, Any
from loguru import logger
from app.core.config import settings


def setup_logging() -> None:
    """Configure logging for the application."""
    
    # Remove default logger
    logger.remove()
    
    # Configure log format
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )
    
    # Add console handler
    logger.add(
        sys.stdout,
        format=log_format,
        level="DEBUG" if settings.DEBUG else "INFO",
        colorize=True,
    )
    
    # Add file handler in production
    if not settings.DEBUG:
        logger.add(
            "logs/vibe_coding_{time}.log",
            format=log_format,
            level="INFO",
            rotation="500 MB",
            retention="10 days",
            compression="zip",
        )
    
    # Intercept standard logging
    class InterceptHandler(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            # Get corresponding Loguru level if it exists
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno
            
            # Find caller from where originated the logged message
            frame, depth = logging.currentframe(), 2
            while frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1
            
            logger.opt(depth=depth, exception=record.exc_info).log(
                level, record.getMessage()
            )
    
    # Set up interceptor for standard logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0)
