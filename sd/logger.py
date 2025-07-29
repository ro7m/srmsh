
from loguru import logger
import sys

# Remove default logger
logger.remove()

# Add console logger
logger.add(
    sys.stderr,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    level="INFO"
)

# Add file logger
logger.add(
    "logs/identity_matching.log",
    rotation="500 MB",
    retention="10 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    level="DEBUG"
)

__all__ = ["logger"]
