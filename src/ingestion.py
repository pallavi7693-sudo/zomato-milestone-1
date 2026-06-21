import os
import sys
import argparse
import logging
import sqlite3
import datetime
import pandas as pd
import numpy as np
from datasets import load_dataset

# Import configuration and validation layer
from config import (
    RAW_DATA_PATH, DB_PATH, LOG_FILE_PATH, DATASET_NAME,
    CRITICAL_COLUMNS, DATA_DICTIONARY_PATH
)
from data_validation import validate_dataset

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE_PATH, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("ingestion_pipeline")

def setup_directories():
    """Ensure all required project folders exist."""
    os.makedirs(os.path.dirname(RAW_DATA_PATH), exist_ok=True)
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)
    os.makedirs(os.path.dirname(DATA_DICTIONARY_PATH), exist_ok=True)

def load_or_download_dataset() -> pd.DataFrame:
    """
    Checks for a cached Parquet dataset locally. If not found, downloads
    it from Hugging Face and caches it locally.
    
    Returns:
        pd.DataFrame: Loaded dataset.
    """
    if os.path.exists(RAW_DATA_PATH):
        logger.info("Local cached dataset found at %s. Loading...", RAW_DATA_PATH)
        df = pd.read_parquet(RAW_DATA_PATH)
        logger.info("Local cached dataset loaded successfully. Total records: %d", len(df))
        return df
    else:
        logger.info("Download started from Hugging Face dataset: %s", DATASET_NAME)
        # Load dataset from Hugging Face datasets library
        dataset_dict = load_dataset(DATASET_NAME)
        
        # Determine the correct split (default to 'train')
        split_name = 'train'
        if split_name not in dataset_dict:
            split_name = list(dataset_dict.keys())[0]
            
        df = dataset_dict[split_name].to_pandas()
        logger.info("Download completed successfully. Total raw records: %d", len(df))
        
        # Cache locally
        df.to_parquet(RAW_DATA_PATH, index=False)
        logger.info("Dataset cached locally at %s", RAW_DATA_PATH)
        return df

def map_raw_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Maps raw DataFrame column names to clean standardized names.
    Matches variations in spelling, spacing, and casing.
    """
    column_mappings = {
        "name": ["Restaurant Name", "restaurant_name", "name", "Name", "Restaurant_Name"],
        "location": ["Location", "location", "locality", "Locality", "place_name", "Place Name", "Place_Name"],
        "cuisines": ["Cuisine", "cuisines", "cuisines_list", "cuisines offered", "Cuisines", "cuisines"],
        "rating": ["Rating", "rating", "rate", "Dining Rating", "dining_rating", "Dining_Rating"],
        "cost": ["Cost", "cost", "approx_cost(for two people)", "approx_cost", "Approx Cost", "Approx_Cost", "cost_for_two", "Cost for two"],
        "votes": ["Votes", "votes", "Dining Votes", "dining_votes", "Dining_Votes"],
        "online_order": ["Online Order", "online_order", "Online_Order", "Online Order Availability", "online_order_availability", "online_order_avail"],
        "book_table": ["Book Table", "book_table", "Book_Table", "Table Booking Availability", "table_booking_availability", "book_table_avail"],
        "restaurant_type": ["Restaurant Type", "restaurant_type", "rest_type", "type", "Type", "Rest_Type"]
    }
    
    rename_dict = {}
    df_cols = list(df.columns)
    
    # Attempt to find matches for each standardized target column
    for target, alternatives in column_mappings.items():
        found = False
        # 1. Look for exact matches in the alternatives list
        for alt in alternatives:
            if alt in df_cols:
                rename_dict[alt] = target
                found = True
                break
        
        if not found:
            # 2. Look for case-insensitive match (stripping space/underscores)
            normalized_target = target.lower().replace("_", "").replace(" ", "")
            for col in df_cols:
                normalized_col = col.lower().replace("_", "").replace(" ", "").replace("(fortwopeople)", "").replace("fortwo", "")
                if normalized_col == normalized_target:
                    rename_dict[col] = target
                    found = True
                    break
                    
    logger.info("Applying column name remapping: %s", rename_dict)
    df = df.rename(columns=rename_dict)
    return df

def clean_rating(val) -> float:
    """
    Cleans Zomato rating string formats (e.g. '4.2/5', 'NEW', '-', None)
    and returns float or None.
    """
    if pd.isna(val) or val is None:
        return None
    val_str = str(val).strip().upper()
    if val_str in ["NEW", "-", "", "NONE", "NULL"]:
        return None
    # Handle formats like '4.2/5'
    if "/5" in val_str:
        val_str = val_str.split("/5")[0].strip()
    try:
        return float(val_str)
    except ValueError:
        return None

def clean_cost(val) -> int:
    """
    Cleans cost values (e.g., '₹1,200 for two', '₹800', '1500')
    and returns integer or None.
    """
    if pd.isna(val) or val is None:
        return None
    val_str = str(val).strip()
    # Remove currency symbol, commas, and description
    val_str = val_str.replace("₹", "").replace(",", "")
    if "for two" in val_str:
        val_str = val_str.split("for two")[0].strip()
    
    # Extract digits only to handle random text
    digits = "".join([c for c in val_str if c.isdigit()])
    if not digits:
        return None
    try:
        return int(digits)
    except ValueError:
        return None

def normalize_cuisines(val) -> str:
    """
    Standardizes cuisine strings:
    - lowercase
    - trim spaces
    - remove duplicate cuisines
    - use pipe separator
    """
    if pd.isna(val) or val is None:
        return ""
    val_str = str(val)
    parts = val_str.split(",")
    seen = []
    for part in parts:
        cleaned = part.strip().lower()
        if cleaned and cleaned not in seen:
            seen.append(cleaned)
    return "|".join(seen)

def clean_boolean(val) -> bool:
    """Standardizes online_order and book_table to Python booleans."""
    if pd.isna(val) or val is None:
        return False
    if isinstance(val, (bool, np.bool_)):
        return bool(val)
    val_str = str(val).strip().lower()
    if val_str in ["yes", "y", "true", "1"]:
        return True
    return False

def clean_votes(val) -> int:
    """Cleans the votes column and defaults to 0 if invalid."""
    if pd.isna(val) or val is None:
        return 0
    try:
        # handle decimal string representation
        return int(float(str(val).replace(",", "")))
    except (ValueError, TypeError):
        return 0

def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Performs data cleaning, standardization, type casting,
    and removes duplicate/incomplete rows based on CRITICAL_COLUMNS.
    """
    # 1. Clean Ratings
    df["rating"] = df["rating"].apply(clean_rating)
    # Drop rows with null ratings immediately after cleaning ratings
    df = df.dropna(subset=["rating"])
    df["rating"] = df["rating"].astype(float)
    
    # 2. Clean Costs
    df["cost"] = df["cost"].apply(clean_cost)
    # Drop rows with invalid cost values
    df = df.dropna(subset=["cost"])
    df["cost"] = df["cost"].astype(int)
    
    # 3. Clean and normalize other critical columns
    df = df.dropna(subset=["name", "location", "cuisines"])
    df["name"] = df["name"].astype(str).str.strip()
    df["location"] = df["location"].astype(str).str.strip()
    df["cuisines"] = df["cuisines"].apply(normalize_cuisines)
    
    # Drop rows where name, location or cuisines is empty string
    df = df[df["name"] != ""]
    df = df[df["location"] != ""]
    df = df[df["cuisines"] != ""]
    
    # 4. Clean optional columns to match database schema requirements
    if "votes" in df.columns:
        df["votes"] = df["votes"].apply(clean_votes)
    else:
        df["votes"] = 0
        
    if "online_order" in df.columns:
        df["online_order"] = df["online_order"].apply(clean_boolean)
    else:
        df["online_order"] = False
        
    if "book_table" in df.columns:
        df["book_table"] = df["book_table"].apply(clean_boolean)
    else:
        df["book_table"] = False
        
    if "restaurant_type" in df.columns:
        df["restaurant_type"] = df["restaurant_type"].fillna("").astype(str).str.strip()
    else:
        df["restaurant_type"] = ""
        
    # Re-verify critical column null constraints
    df = df.dropna(subset=CRITICAL_COLUMNS)
    
    # 5. Remove duplicates based on name + location, keeping first
    initial_len = len(df)
    df = df.drop_duplicates(subset=["name", "location"], keep="first")
    duplicates_removed = initial_len - len(df)
    logger.info("Duplicate rows removed (by name + location): %d", duplicates_removed)
    
    return df, duplicates_removed

def save_to_sqlite(df: pd.DataFrame, db_path: str, records_removed: int):
    """
    Saves the cleaned DataFrame into the SQLite database.
    Explicitly creates the tables and fields without dynamic type inference.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Create restaurants table explicitly
        cursor.execute("DROP TABLE IF EXISTS restaurants")
        cursor.execute("""
            CREATE TABLE restaurants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                location TEXT COLLATE NOCASE,
                cuisines TEXT,
                rating REAL,
                cost INTEGER,
                votes INTEGER,
                online_order BOOLEAN,
                book_table BOOLEAN,
                restaurant_type TEXT
            )
        """)
        
        # Create indexes to optimize query candidate scaling
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_restaurants_location ON restaurants(location)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_restaurants_filter ON restaurants(location, rating, cost)")
        
        # Create metadata table explicitly
        cursor.execute("DROP TABLE IF EXISTS ingestion_metadata")
        cursor.execute("""
            CREATE TABLE ingestion_metadata (
                ingestion_time TEXT,
                records_loaded INTEGER,
                records_removed INTEGER
            )
        """)
        
        logger.info("SQLite schema created successfully.")
        
        # Convert DataFrame to records list for bulk insert
        records = df[[
            "name", "location", "cuisines", "rating", "cost", 
            "votes", "online_order", "book_table", "restaurant_type"
        ]].values.tolist()
        
        cursor.executemany("""
            INSERT INTO restaurants (
                name, location, cuisines, rating, cost, 
                votes, online_order, book_table, restaurant_type
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, records)
        
        # Ingestion Metadata
        timestamp = datetime.datetime.now().isoformat()
        records_loaded = len(df)
        
        cursor.execute("""
            INSERT INTO ingestion_metadata (ingestion_time, records_loaded, records_removed)
            VALUES (?, ?, ?)
        """, (timestamp, records_loaded, records_removed))
        
        conn.commit()
        logger.info("Loaded %d records into restaurants table.", records_loaded)
        logger.info("Saved ingestion metadata (removed: %d). Database update complete.", records_removed)
        
    except Exception as e:
        conn.rollback()
        logger.error("Failed to load records to SQLite database: %s", str(e))
        raise e
    finally:
        conn.close()

def generate_data_dictionary(df: pd.DataFrame, dict_path: str):
    """
    Generates Docs/data_dictionary.md automatically based on the cleaned
    dataset schema, incorporating description and example values.
    """
    columns_info = {
        "id": {
            "type": "INTEGER",
            "desc": "Primary key, auto-incremented identifier for each restaurant record."
        },
        "name": {
            "type": "TEXT",
            "desc": "The name of the restaurant."
        },
        "location": {
            "type": "TEXT",
            "desc": "The locality, neighborhood, or area in which the restaurant is situated."
        },
        "cuisines": {
            "type": "TEXT",
            "desc": "Pipe-separated (|) list of normalized, lowercase cuisines offered by the restaurant."
        },
        "rating": {
            "type": "REAL",
            "desc": "Aggregated user rating score, ranging between 1.0 and 5.0."
        },
        "cost": {
            "type": "INTEGER",
            "desc": "Estimated cost of dining for two people."
        },
        "votes": {
            "type": "INTEGER",
            "desc": "Total number of votes or reviews received by the restaurant."
        },
        "online_order": {
            "type": "BOOLEAN",
            "desc": "Indicates whether the restaurant accepts online orders (True/False)."
        },
        "book_table": {
            "type": "BOOLEAN",
            "desc": "Indicates whether the restaurant allows online table bookings (True/False)."
        },
        "restaurant_type": {
            "type": "TEXT",
            "desc": "Categorical type representing the restaurant style (e.g., Casual Dining, Cafe, Pub)."
        }
    }
    
    # Build markdown table lines
    lines = [
        "# Data Dictionary - Zomato Restaurants Dataset",
        "",
        "This data dictionary outlines the schema and definitions for the cleaned `restaurants` database table.",
        "",
        "| Column Name | Data Type | Description | Example Value |",
        "| :--- | :--- | :--- | :--- |"
    ]
    
    for col_name, info in columns_info.items():
        # Get an example value from the cleaned dataframe
        example_val = "-"
        if col_name == "id":
            example_val = "1"
        elif col_name in df.columns:
            non_null_series = df[col_name].dropna()
            if not non_null_series.empty:
                val = non_null_series.iloc[0]
                if isinstance(val, (bool, np.bool_)):
                    example_val = str(val)
                elif isinstance(val, (int, np.integer, float, np.floating)):
                    example_val = str(val)
                else:
                    example_val = f'"{str(val)}"'
        
        lines.append(f"| {col_name} | {info['type']} | {info['desc']} | {example_val} |")
        
    # Write file
    with open(dict_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    logger.info("Automatically generated data dictionary at %s", dict_path)

def run_pipeline(test_mode: bool = False):
    """Executes the entire ingestion pipeline workflow."""
    setup_directories()
    
    try:
        # Load or download raw dataset
        raw_df = load_or_download_dataset()
        original_count = len(raw_df)
        
        # Standardize columns to standard naming
        mapped_df = map_raw_columns(raw_df)
        
        # Run validation layer
        validate_dataset(mapped_df, CRITICAL_COLUMNS)
        logger.info("Validation passed: All required columns present, dataset is valid.")
        
        # Clean and pre-process dataset
        cleaned_df, duplicates_removed = clean_dataset(mapped_df)
        final_count = len(cleaned_df)
        total_removed = original_count - final_count
        
        # Save records to SQLite
        save_to_sqlite(cleaned_df, DB_PATH, total_removed)
        
        # Auto-generate data dictionary
        generate_data_dictionary(cleaned_df, DATA_DICTIONARY_PATH)
        
        if test_mode:
            # Command-line verification requested output format
            print("Dataset Validation Passed")
            print(f"Rows Loaded: {final_count}")
            print(f"Rows Removed: {total_removed}")
            print("Database Created Successfully")
            
        sys.exit(0)
        
    except Exception as e:
        logger.exception("An error occurred during ingestion:")
        if test_mode:
            print(f"Ingestion Pipeline Failed: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Zomato Restaurant Recommendation System Ingestion Pipeline")
    parser.add_argument("--test", action="store_true", help="Runs pipeline and displays custom summary output.")
    args = parser.parse_args()
    
    run_pipeline(test_mode=args.test)
