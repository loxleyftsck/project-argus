"""Configuration management for Market Anomaly Detection Engine."""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================
# PATHS
# ============================================
ROOT_DIR = Path(__file__).parent.parent.parent
DATA_DIR = ROOT_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = DATA_DIR / "models"
LOGS_DIR = ROOT_DIR / "logs"

# Create directories if they don't exist
for dir_path in [RAW_DATA_DIR, PROCESSED_DATA_DIR, MODELS_DIR, LOGS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# ============================================
# APPLICATION
# ============================================
APP_NAME = os.getenv("APP_NAME", "Market Anomaly Detection Engine")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# ============================================
# API CONFIGURATION
# ============================================
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_RELOAD = os.getenv("API_RELOAD", "true").lower() == "true"
API_WORKERS = int(os.getenv("API_WORKERS", "1"))

# ============================================
# DATABASE
# ============================================
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR / 'alerts.db'}")

# ============================================
# MODEL PATHS
# ============================================
MODEL_PATH = MODELS_DIR / os.getenv("MODEL_PATH", "isolation_forest.pkl").split("/")[-1]
AUTOENCODER_PATH = MODELS_DIR / os.getenv("AUTOENCODER_PATH", "autoencoder.h5").split("/")[-1]
LSTM_PATH = MODELS_DIR / os.getenv("LSTM_PATH", "lstm_detector.h5").split("/")[-1]

# ============================================
# MODEL PARAMETERS
# ============================================
CONTAMINATION = float(os.getenv("CONTAMINATION", "0.05"))
N_ESTIMATORS = int(os.getenv("N_ESTIMATORS", "100"))
RANDOM_STATE = int(os.getenv("RANDOM_STATE", "42"))

# ============================================
# DETECTION THRESHOLDS
# ============================================
VOLUME_ZSCORE_THRESHOLD = float(os.getenv("VOLUME_ZSCORE_THRESHOLD", "3.0"))
PRICE_CHANGE_THRESHOLD = float(os.getenv("PRICE_CHANGE_THRESHOLD", "10.0"))
VOLATILITY_RATIO_THRESHOLD = float(os.getenv("VOLATILITY_RATIO_THRESHOLD", "1.5"))
WASH_TRADING_CORRELATION_THRESHOLD = float(os.getenv("WASH_TRADING_CORRELATION_THRESHOLD", "0.3"))

# ============================================
# YFINANCE SETTINGS
# ============================================
YFINANCE_TIMEOUT = int(os.getenv("YFINANCE_TIMEOUT", "10"))
YFINANCE_MAX_RETRIES = int(os.getenv("YFINANCE_MAX_RETRIES", "3"))

# ============================================
# LOGGING
# ============================================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = LOGS_DIR / "app.log"

# ============================================
# MONITORING
# ============================================
DRIFT_DETECTION_ENABLED = os.getenv("DRIFT_DETECTION_ENABLED", "true").lower() == "true"
DRIFT_THRESHOLD = float(os.getenv("DRIFT_THRESHOLD", "0.05"))
PERFORMANCE_TRACKING_ENABLED = os.getenv("PERFORMANCE_TRACKING_ENABLED", "true").lower() == "true"

# ============================================
# GPU
# ============================================
USE_GPU = os.getenv("USE_GPU", "false").lower() == "true"
GPU_MEMORY_LIMIT = int(os.getenv("GPU_MEMORY_LIMIT", "4096"))

# ============================================
# MLFLOW EXPERIMENT TRACKING
# ============================================
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", f"file:///{ROOT_DIR / 'mlruns'}")
MLFLOW_EXPERIMENT_NAME = os.getenv("MLFLOW_EXPERIMENT_NAME", "market-anomaly-detection")
MLFLOW_ARTIFACT_LOCATION = os.getenv("MLFLOW_ARTIFACT_LOCATION", str(ROOT_DIR / "mlruns"))
MLFLOW_ENABLE_UI = os.getenv("MLFLOW_ENABLE_UI", "true").lower() == "true"
MLFLOW_UI_PORT = int(os.getenv("MLFLOW_UI_PORT", "5000"))

# ============================================
# SECURITY
# ============================================
SECRET_KEY = os.getenv("SECRET_KEY", "development-secret-key-change-in-production")
API_KEY_ENABLED = os.getenv("API_KEY_ENABLED", "false").lower() == "true"
API_KEY = os.getenv("API_KEY", "")


def get_config_summary() -> dict:
    """Get configuration summary for debugging.
    
    Returns:
        Dictionary with configuration values
    """
    return {
        "app_name": APP_NAME,
        "version": APP_VERSION,
        "environment": ENVIRONMENT,
        "api_port": API_PORT,
        "database": DATABASE_URL,
        "model_path": str(MODEL_PATH),
        "log_level": LOG_LEVEL,
        "gpu_enabled": USE_GPU,
    }
