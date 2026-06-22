import os
from pathlib import Path

# Base project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Data directory paths
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# File paths
RAW_DATA_PATH = RAW_DATA_DIR / "zomato_dataset.parquet"
DB_PATH = DATA_DIR / "restaurants.db"
LOG_FILE_PATH = BASE_DIR / "logs" / "ingestion.log"
DATA_DICTIONARY_PATH = BASE_DIR / "Docs" / "data_dictionary.md"

# Dataset Source on Hugging Face
DATASET_NAME = "ManikaSaini/zomato-restaurant-recommendation"

# Ingestion Column Config
CRITICAL_COLUMNS = ["name", "location", "cuisines", "rating", "cost"]

# Constraint Relaxation Config
RELAXATION_TARGET_COUNT = 5
RATING_RELAX_STEP = 0.2
BUDGET_RELAX_PERCENT = 0.10

# Ensure directories exist
os.makedirs(RAW_DATA_DIR, exist_ok=True)
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
os.makedirs(BASE_DIR / "logs", exist_ok=True)
os.makedirs(BASE_DIR / "Docs", exist_ok=True)
