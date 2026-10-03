"""Application configuration and constants."""
import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CSV_DIR = BASE_DIR / "Data_CSV"
DEFAULT_DB_PATH = DATA_DIR / "sales_database.sqlite"

# Ensure data directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Database Configuration
DB_PATH = Path(os.getenv("SQLITE_DB_PATH", str(DEFAULT_DB_PATH)))

# Safety Configuration
DEFAULT_ROW_LIMIT = int(os.getenv("DEFAULT_ROW_LIMIT", "100"))
MAX_ROW_LIMIT = int(os.getenv("MAX_ROW_LIMIT", "500"))
QUERY_TIMEOUT_SECONDS = int(os.getenv("QUERY_TIMEOUT_SECONDS", "10"))

# LLM Configuration
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
