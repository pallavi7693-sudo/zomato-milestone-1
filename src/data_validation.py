import pandas as pd
from typing import List

def validate_dataset(df: pd.DataFrame, required_columns: List[str]) -> bool:
    """
    Validates that the dataset was successfully loaded/downloaded,
    is not empty, and contains all required critical columns.
    
    Args:
        df: The pandas DataFrame to validate.
        required_columns: A list of column names that must exist in the DataFrame.
        
    Returns:
        bool: True if validation passes.
        
    Raises:
        ValueError: If the DataFrame is empty or if any required columns are missing.
    """
    if df is None:
        raise ValueError("Dataset validation failed: Dataset is None (failed to download or load).")
        
    if df.empty:
        raise ValueError("Dataset validation failed: Dataset is empty.")
        
    # Find missing required columns
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        # Raise descriptive exception as required
        raise ValueError(f"Missing required columns:\n{missing_columns}")
        
    return True
