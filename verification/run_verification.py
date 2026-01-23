#!/usr/bin/env python3
"""
Verification Runner Script
--------------------------
Runs the standardized analysis on dummy data and displays detailed outputs
at each step to verify correctness against hand calculations.

Expected Results (see README.md in verification directory):
- ID015: Mean = 1.25, T = 5.0, P = 0.015
- ID017: Mean = 2.333, T = 1.75, P ~ 0.22
- ID030: Mean = 3.0, T = 1.732, P = 0.225
"""

import os
import sys
import pandas as pd
import numpy as np

# Add parent directory to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from schema_analysis import TubeTrials

def main():
    print("VERIFICATION TEST - Running on Dummy Data (Absolute Logic)")
    
    DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
    dummy_file = os.path.join(DATA_DIR, 'dummy_verification.csv')
    df = pd.read_csv(dummy_file)
    
    trials = TubeTrials(df)
    trials.process_angles()
    trials.mark_valid_angles(min_angle=3, max_angle=43)
    trials.mark_bad_subjects(max_invalid_trials=2)
    clean_trials = trials.select(valid_only=True)
    stats = clean_trials.calc_stats()
    results = clean_trials.calc_d_values()
    
    # Expected values per Face ID (from README.md guide)
    expected_stats = {
        'ID015': {'mean': 1.25, 't_stat': 5.0, 'p_value': 0.015},
        'ID017': {'mean': 2.333, 't_stat': 1.75, 'p_value': 0.222},
        'ID030': {'mean': 3.0, 't_stat': 1.732, 'p_value': 0.225}
    }
    
    # Check for negative D-values (should be zero in absolute logic)
    negative_d = results[results['d'] < 0]
    if not negative_d.empty:
        print(f"✗ FAILED: Found {len(negative_d)} negative D-values! Formula should be absolute.")
        sys.exit(1)
    else:
        print("✓ D-values are all non-negative.")

    all_passed = True
    for face_id, expected in expected_stats.items():
        print(f"\n--- Checking {face_id} ---")
        face_stats = stats[stats['face_id'] == face_id]
        if face_stats.empty:
            print(f"✗ FAILED: No statistics found for {face_id}")
            all_passed = False
            continue
            
        actual = face_stats.iloc[0]
        
        def check(name, act, exp, tolerance=0.01):
            match = abs(act - exp) < tolerance
            status = "✓" if match else "✗"
            print(f"{status} {name}: Expected {exp:.3f}, Actual {act:.3f}")
            return match

        m_match = check("Mean", actual['mean'], expected['mean'])
        t_match = check("T-Stat", actual['t_stat'], expected['t_stat'], tolerance=0.1)
        p_match = check("P-Value", actual['p_value'], expected['p_value'], tolerance=0.1)
            
        if not (m_match and t_match and p_match):
            all_passed = False
            
    if all_passed:
        print("\n✓✓✓ ALL VERIFICATIONS PASSED! ✓✓✓")
        sys.exit(0)
    else:
        print("\n✗✗✗ VERIFICATION FAILED! ✗✗✗")
        sys.exit(1)

if __name__ == "__main__":
    main()
