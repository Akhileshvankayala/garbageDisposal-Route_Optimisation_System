import logging
from logging.handlers import RotatingFileHandler
import os
from config import LOG_LEVEL, LOG_FILE

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        RotatingFileHandler(LOG_FILE, maxBytes=10485760, backupCount=5),  # 10MB per file
    ],
)

# Get logger
logger = logging.getLogger(__name__)

logger.info(f"Logging initialized at level {LOG_LEVEL}")
