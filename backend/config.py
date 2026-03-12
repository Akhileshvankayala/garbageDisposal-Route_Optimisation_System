import os
from dotenv import load_dotenv

load_dotenv()

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./meditrack.db")

# Routing Configuration
DISPOSAL_THRESHOLD = 0.8  # 80% of truck capacity triggers disposal
DEFAULT_TRUCK_CAPACITY = 1000.0  # kg
DISPOSAL_CENTER_ID = 1  # Default disposal center (hospital ID = 1)
DISPOSAL_CENTER_LOCATION = (0, 0)  # Default coordinates for disposal center

# Authentication
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# CORS
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = "logs/meditrack.log"
