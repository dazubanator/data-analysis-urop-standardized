#!/usr/bin/env python3
import os
import sys
import pandas as pd
import numpy as np

# Add parent directory to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from schema_analysis import TubeTrials

def main():
    print("VERIFICATION TEST - Running on Dummy Data (Signed Logic)")
    
    DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
    dummy_file = os.path.join(DATA_DIR, 'dummy_verification.csv')
    df = pd.read_csv(dummy_file)
    
    trials = TubeTrials(df)
    trials.process_angles()
    trials.mark_valid_angles(min_angle=3, max_angle=43)
    trials.mark_bad_subjects(max_invalid_trials=2)
    clean_trials = trials.select(valid_only=True)
    stats = clean_trials.calc_stats()
    
    # Precise expected means for the dummy data with signed logic
    expected_means = {
        'ID015': -0.25,
        'ID017': 1.6666,
        'ID030': -3.0
    }
    
    all_passed = True
    for face_id, exp_mean in expected_means.items():
        if face_id not in stats['face_id'].values:
            print(f"✗ FAILED: No statistics found for {face_id}")
            all_passed = False
            continue
            
        act_mean = stats[stats['face_id'] == face_id]['mean'].iloc[0]
        if abs(act_mean - exp_mean) < 0.01:
            print(f"✓ {face_id}: Mean Bias matched ({act_mean:.3f})")
        else:
            print(f"✗ {face_id}: Mean Bias discrepancy! Expected {exp_mean:.3f}, Actual {act_mean:.3f}")
            all_passed = False
            
    if all_passed:
        print("\n✓✓✓ ALL VERIFICATIONS PASSED! ✓✓✓")
        sys.exit(0)
    else:
        print("\n✗✗✗ VERIFICATION FAILED! ✗✗✗")
        sys.exit(1)

if __name__ == "__main__":
    main()
