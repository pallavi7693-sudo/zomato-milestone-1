import os
import sys
import pytest
import pandas as pd
import numpy as np

# Ensure src directory is in the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from ingestion import clean_rating, clean_cost, normalize_cuisines, clean_boolean
from config import CRITICAL_COLUMNS, DB_PATH
import sqlite3

def test_cuisine_normalization():
    """Test cuisine normalization rules: lowercase, trim, deduplicate, pipe separator."""
    # Test typical list with duplicates and spaces
    res = normalize_cuisines("North Indian, Chinese, Fast Food, Chinese")
    assert res == "north indian|chinese|fast food"
    
    # Test duplicate single cuisine
    res2 = normalize_cuisines("Italian, Italian")
    assert res2 == "italian"
    
    # Test empty / null cases
    assert normalize_cuisines(None) == ""
    assert normalize_cuisines(np.nan) == ""
    assert normalize_cuisines("") == ""

def test_rating_cleaning():
    """Test cleaning of rating string formats."""
    assert clean_rating("4.2/5") == 4.2
    assert clean_rating("3.8/5") == 3.8
    assert clean_rating("NEW") is None
    assert clean_rating("-") is None
    assert clean_rating(None) is None
    assert clean_rating(np.nan) is None

def test_cost_cleaning():
    """Test cleaning of cost string formats and digit extraction."""
    assert clean_cost("₹1,200 for two") == 1200
    assert clean_cost("₹800") == 800
    assert clean_cost("1500") == 1500
    assert clean_cost("1,500") == 1500
    assert clean_cost(None) is None
    assert clean_cost("invalid text") is None

def test_boolean_cleaning():
    """Test boolean conversions."""
    assert clean_boolean("Yes") is True
    assert clean_boolean("yes") is True
    assert clean_boolean("No") is False
    assert clean_boolean("no") is False
    assert clean_boolean(True) is True
    assert clean_boolean(False) is False
    assert clean_boolean(None) is False

def test_dataset_post_ingestion_checks():
    """Verify that the database holds records, types match, and no critical nulls exist."""
    # Ensure the DB file exists before querying
    if not os.path.exists(DB_PATH):
        pytest.skip("Database does not exist yet. Run ingestion script first.")
        
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query("SELECT * FROM restaurants", conn)
        
        # Test 1: Dataset contains rows
        assert len(df) > 0, "Cleaned dataset should contain rows."
        
        # Test 2: Rating column type is float
        assert df["rating"].dtype in [np.float64, np.float32, float], "Rating column must be float."
        
        # Test 3: Cost column type is integer
        assert df["cost"].dtype in [np.int64, np.int32, int], "Cost column must be integer."
        
        # Test 4: No null values remain in critical columns
        for col in CRITICAL_COLUMNS:
            null_count = df[col].isnull().sum()
            assert null_count == 0, f"Critical column '{col}' contains {null_count} null value(s)."
            
    finally:
        conn.close()
