import os
import sys
import sqlite3
import pytest
import pandas as pd

# Ensure src directory is in the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from config import DB_PATH
from ingestion import clean_dataset

def test_restaurants_table_exists():
    """Verify that the restaurants table exists in SQLite database with correct schema."""
    if not os.path.exists(DB_PATH):
        pytest.skip("Database does not exist yet. Run ingestion script first.")
        
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        
        # Querysqlite_master to check table existence
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='restaurants'")
        table = cursor.fetchone()
        assert table is not None, "Table 'restaurants' should exist in the database."
        
        # Verify schema details
        cursor.execute("PRAGMA table_info(restaurants)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        expected_columns = {
            "id": "INTEGER",
            "name": "TEXT",
            "location": "TEXT",
            "cuisines": "TEXT",
            "rating": "REAL",
            "cost": "INTEGER",
            "votes": "INTEGER",
            "online_order": "BOOLEAN",
            "book_table": "BOOLEAN",
            "restaurant_type": "TEXT"
        }
        
        for col_name, expected_type in expected_columns.items():
            assert col_name in columns, f"Column '{col_name}' must exist in restaurants table."
            assert columns[col_name] == expected_type, f"Column '{col_name}' type must be '{expected_type}', found '{columns[col_name]}'."
            
    finally:
        conn.close()

def test_metadata_table_exists():
    """Verify that the ingestion_metadata table exists and contains loading data."""
    if not os.path.exists(DB_PATH):
        pytest.skip("Database does not exist yet. Run ingestion script first.")
        
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        
        # Check table existence
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ingestion_metadata'")
        table = cursor.fetchone()
        assert table is not None, "Table 'ingestion_metadata' should exist in the database."
        
        # Verify schema details
        cursor.execute("PRAGMA table_info(ingestion_metadata)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        expected_columns = {
            "ingestion_time": "TEXT",
            "records_loaded": "INTEGER",
            "records_removed": "INTEGER"
        }
        
        for col_name, expected_type in expected_columns.items():
            assert col_name in columns, f"Column '{col_name}' must exist in ingestion_metadata table."
            assert columns[col_name] == expected_type, f"Column '{col_name}' type must be '{expected_type}', found '{columns[col_name]}'."
            
        # Verify a record exists
        cursor.execute("SELECT COUNT(*) FROM ingestion_metadata")
        count = cursor.fetchone()[0]
        assert count > 0, "ingestion_metadata table should contain at least one ingestion record."
        
    finally:
        conn.close()

def test_duplicate_removal_logic():
    """Verify that duplicate restaurants are correctly identified and removed (keeping first occurrence)."""
    # Create a mock dataframe containing duplicates
    mock_data = pd.DataFrame([
        {
            "name": "Restaurant A",
            "location": "Indiranagar",
            "cuisines": "Chinese, Thai",
            "rating": "4.2/5",
            "cost": "₹800",
            "votes": "100",
            "online_order": "Yes",
            "book_table": "No",
            "restaurant_type": "Casual Dining"
        },
        {
            # Exact duplicate name and location
            "name": "Restaurant A",
            "location": "Indiranagar",
            "cuisines": "North Indian",
            "rating": "3.8/5",
            "cost": "₹600",
            "votes": "50",
            "online_order": "No",
            "book_table": "No",
            "restaurant_type": "Casual Dining"
        },
        {
            # Different location
            "name": "Restaurant A",
            "location": "Koramangala",
            "cuisines": "Chinese",
            "rating": "4.0/5",
            "cost": "₹700",
            "votes": "120",
            "online_order": "Yes",
            "book_table": "Yes",
            "restaurant_type": "Casual Dining"
        },
        {
            # Different name
            "name": "Restaurant B",
            "location": "Indiranagar",
            "cuisines": "Italian",
            "rating": "4.5/5",
            "cost": "₹1,200",
            "votes": "200",
            "online_order": "Yes",
            "book_table": "Yes",
            "restaurant_type": "Fine Dining"
        }
    ])
    
    # Standardize column naming structure (mimicking ingestion pipeline)
    df = mock_data.rename(columns={
        "name": "name",
        "location": "location",
        "cuisines": "cuisines",
        "rating": "rating",
        "cost": "cost",
        "votes": "votes",
        "online_order": "online_order",
        "book_table": "book_table",
        "restaurant_type": "restaurant_type"
    })
    
    # Run the clean_dataset process
    cleaned_df, dup_removed = clean_dataset(df)
    
    # Assertions
    # 4 rows original, 1 duplicate (Restaurant A - Indiranagar) should be removed.
    # Total remaining should be 3.
    assert dup_removed == 1, f"Expected 1 duplicate to be removed, but got {dup_removed}."
    assert len(cleaned_df) == 3, f"Expected 3 records to remain, but got {len(cleaned_df)}."
    
    # Verify the remaining entries:
    # 1. Restaurant A in Indiranagar (first occurrence rating 4.2)
    # 2. Restaurant A in Koramangala
    # 3. Restaurant B in Indiranagar
    
    rest_a_indira = cleaned_df[(cleaned_df["name"] == "Restaurant A") & (cleaned_df["location"] == "Indiranagar")]
    assert len(rest_a_indira) == 1, "Only one Restaurant A in Indiranagar should remain."
    assert rest_a_indira.iloc[0]["rating"] == 4.2, "Should preserve the first occurrence (rating 4.2)."
    assert rest_a_indira.iloc[0]["cost"] == 800, "Should preserve the first occurrence cost (800)."
