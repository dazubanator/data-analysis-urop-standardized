import pandas as pd
import os

# Configuration
RAW_DATA_FILE = 'facetip_data_Nov2025.csv'
OUTPUT_FILE = 'merged_experiments_cleaned_reproduced.csv'

def preprocess_data():
    print("=" * 70)
    print("PREPROCESSING RAW DATA")
    print("=" * 70)

    if not os.path.exists(RAW_DATA_FILE):
        print(f"Error: {RAW_DATA_FILE} not found.")
        return

    print(f"Loading raw data from {RAW_DATA_FILE}...")
    df = pd.read_csv(RAW_DATA_FILE)
    print(f"Initial rows: {len(df)}")

    # 1. Filter out rows with missing session_group
    print("\nFiltering missing session_group...")
    initial_count = len(df)
    df = df.dropna(subset=['session_group'])
    dropped_count = initial_count - len(df)
    print(f"Dropped {dropped_count} rows with missing session_group")

    # 2. Select required columns
    required_columns = [
        'user_number',
        'session_group',
        'trialIndex',
        'tubeTypeIndex',
        'tip_direction',
        'face_id',
        'faceSide',
        'towards_away',
        'raw_angle',
        'latency'
    ]
    
    print(f"\nSelecting columns: {required_columns}")
    # Check if all columns exist
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        print(f"Error: Missing columns in raw data: {missing_cols}")
        return

    df_cleaned = df[required_columns].copy()

    # Save to output
    print(f"\nSaving cleaned data to {OUTPUT_FILE}...")
    df_cleaned.to_csv(OUTPUT_FILE, index=False)
    print("Done.")

if __name__ == "__main__":
    preprocess_data()
