#!/usr/bin/env python3
"""
Standardized Analysis Script for Colab
--------------------------------------
This script processes experimental data through a standardized pipeline:
1. Load & Merge: Combine all CSV files from data/raw/
2. Clean: Remove rows with missing group_id
3. Preprocess: Rename faces, transform angles
4. Filter: Angle rule (3-43°), subject exclusion (>2 invalid)
5. Balance: Remove unmatched trials
6. Analyze: Calculate D-values and statistics

Usage:
    python standardized_analysis.py
"""

import os
import pandas as pd
from schema_analysis.data_loader import load_and_merge_csvs
from schema_analysis import TubeTrials

# Configuration
DATA_DIR = os.path.join('data', 'raw')
MIN_ANGLE = 3
MAX_ANGLE = 43
MAX_INVALID_TRIALS = 2

def main():
    print("=" * 70)
    print("STANDARDIZED ANALYSIS SCRIPT")
    print("=" * 70)
    
    # Step 1: Load & Merge Data
    print("\n[STEP 1] Loading and merging CSV files...")
    try:
        merged_df = load_and_merge_csvs(DATA_DIR)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print(f"Please ensure CSV files are in '{DATA_DIR}' directory")
        return
    
    # Step 2: Clean Data
    print("\n[STEP 2] Cleaning data (removing missing group_id)...")
    initial_count = len(merged_df)
    merged_df = merged_df.dropna(subset=['session_group'])
    cleaned_count = len(merged_df)
    dropped = initial_count - cleaned_count
    print(f"Removed {dropped} rows with missing session_group")
    print(f"Remaining: {cleaned_count} trials")
    
    # Step 3-6: Process with TubeTrials
    trials = TubeTrials(merged_df)
    
    print(f"\n[STEP 3] Preprocessing (rename faces, transform angles)...")
    trials.process_angles()
    
    print(f"\n[STEP 4] Filtering trials...")
    print(f"  Applying angle rule: {MIN_ANGLE} < end_angle < {MAX_ANGLE}")
    trials.mark_valid_angles(min_angle=MIN_ANGLE, max_angle=MAX_ANGLE)
    
    print(f"  Excluding subjects with >{MAX_INVALID_TRIALS} invalid trials...")
    trials.mark_bad_subjects(max_invalid_trials=MAX_INVALID_TRIALS)
    
    print(f"\n[STEP 5] Selecting valid trials...")
    clean_trials = trials.select(valid_only=True)
    print(f"Clean trials: {len(clean_trials)}")
    
    print(f"\n[STEP 6] Balancing (removing unmatched trials)...")
    results = clean_trials.calc_d_values()
    print(f"Valid pairs: {len(results)}")
    print(f"Paired trials: {len(results) * 2}")
    
    # Step 7: Calculate Statistics
    print(f"\n[STEP 7] Calculating statistics...")
    stats_df = clean_trials.calc_stats()
    
    # Display Results
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    
    print("\nD-Value Pairs (first 10):")
    print(results.head(10))
    
    print("\n\nStatistics by Face ID:")
    print(stats_df.to_string(index=False))
    
    # Save Results
    output_dir = 'results'
    os.makedirs(output_dir, exist_ok=True)
    
    results_file = os.path.join(output_dir, 'd_values.csv')
    stats_file = os.path.join(output_dir, 'statistics.csv')
    
    results.to_csv(results_file, index=False)
    stats_df.to_csv(stats_file, index=False)
    
    print(f"\n\nResults saved to:")
    print(f"  - {results_file}")
    print(f"  - {stats_file}")
    
    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    main()
