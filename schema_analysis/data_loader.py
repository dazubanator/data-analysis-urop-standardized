import pandas as pd
import os
from pathlib import Path

def load_and_merge_csvs(directory):
    """
    Finds and merges all CSV files in the specified directory.
    
    Args:
        directory (str): Path to directory containing CSV files
        
    Returns:
        pd.DataFrame: Merged DataFrame with all experiments
    """
    csv_files = list(Path(directory).glob('*.csv'))
    
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {directory}")
    
    print(f"Found {len(csv_files)} CSV file(s) in {directory}")
    
    dataframes = []
    for csv_file in csv_files:
        print(f"  Loading: {csv_file.name}")
        df = pd.read_csv(csv_file)
        dataframes.append(df)
    
    # Merge all dataframes
    merged_df = pd.concat(dataframes, ignore_index=True)
    print(f"Combined total: {len(merged_df)} trials")
    
    return merged_df
