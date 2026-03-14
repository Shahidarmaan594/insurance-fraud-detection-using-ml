"""
Application configuration loaded from environment variables.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Flask configuration
FLASK_ENV = os.getenv("FLASK_ENV", "development")
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
API_PORT = int(os.getenv("API_PORT", 5000))

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///fraud_detection.db")

# Model configuration
MODELS_DIR = BASE_DIR / "models"
MODEL_PATH = Path(os.getenv("MODEL_PATH", str(MODELS_DIR / "fraud_model.pkl")))
METRICS_PATH = MODELS_DIR / "model_metrics.json"

# Logging
LOGS_DIR = BASE_DIR / "logs"

# Allowed claim types
CLAIM_TYPES = ["auto", "health", "property", "liability"]

# Allowed statuses
CLAIM_STATUSES = ["pending", "approved", "rejected", "fraud"]

# Validation limits
MIN_AGE = 18
MAX_AGE = 80
MIN_CLAIM_AMOUNT = 0
MAX_CLAIM_AMOUNT = 500000
MIN_POLICY_DURATION = 1
MAX_POLICY_DURATION = 480
MIN_PREVIOUS_CLAIMS = 0
MAX_PREVIOUS_CLAIMS = 10
MAX_DESCRIPTION_LENGTH = 1000
