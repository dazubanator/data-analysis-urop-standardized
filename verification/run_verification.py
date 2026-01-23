#!/usr/bin/env python3
"""
Verification Runner Script
--------------------------
Runs the standardized analysis on dummy data and displays detailed outputs
at each step to verify correctness against hand calculations.

Expected Results (see verification_guide.md for details):
- 8 trials total, all valid
- 4 d-value pairs: [5, 3, 5, 4]
- Subject-level D values: [4.0, 4.5]
- Statistics for ID015: mean=4.25, std≈0.354, t≈17.0, p≈0.037
"""

import os
import sys
import pandas as pd

# Add parent directory to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from schema_analysis import TubeTrials

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'=' * 70}")
    print(f"{title}")
    print(f"{'=' * 70}\n")

def main():
    print_section("VERIFICATION TEST - Running on Dummy Data")
    
    # Configuration
    DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
    MIN_ANGLE = 3
    MAX_ANGLE = 43
    MAX_INVALID_TRIALS = 2
    
    # Check if dummy data exists
    dummy_file = os.path.join(DATA_DIR, 'dummy_verification.csv')
    if not os.path.exists(dummy_file):
        print(f"Error: Dummy data not found at {dummy_file}")
        print("Run 'python verification/create_dummy_verification.py' first")
        return
    
    # Step 1: Load Data
    print_section("STEP 1: Load Data")
    df = pd.read_csv(dummy_file)
    print(f"Loaded {len(df)} trials from {dummy_file}")
    # print("\nRaw Data:")
    # print(df[['user_number', 'face_id', 'tubeTypeIndex', 'faceSide', 'tip_direction', 'raw_angle']].to_string(index=False))
    
    # Step 2: Initialize TubeTrials
    print_section("STEP 2: Initialize TubeTrials")
    trials = TubeTrials(df)
    print(f"TubeTrials object created with {len(trials)} trials")
    
    # Step 3: Process Angles
    print_section("STEP 3: Preprocess (Rename Faces & Transform Angles)")
    trials.process_angles()
    # print("\nTransformed Angles:")
    # print(trials.df[['user_number', 'raw_angle', 'tip_direction', 'end_angle']].to_string(index=False))
    
    # Step 4a: Mark Valid Angles
    # print_section("STEP 4a: Mark Valid Angles")
    trials.mark_valid_angles(min_angle=MIN_ANGLE, max_angle=MAX_ANGLE)
    # print("\nAngle Validation:")
    # print(trials.df[['user_number', 'end_angle', 'angle_valid']].to_string(index=False))
    
    # Step 4b: Mark Bad Subjects
    # print_section("STEP 4b: Exclude Bad Subjects")
    trials.mark_bad_subjects(max_invalid_trials=MAX_INVALID_TRIALS)
    # print("\nSubject Exclusion:")
    subjects_excluded = trials.df['is_excluded_subject'].sum()
    # print(f"Trials from excluded subjects: {subjects_excluded}")
    
    # Step 5: Select Valid Trials
    # print_section("STEP 5: Select Valid Trials")
    clean_trials = trials.select(valid_only=True)
    # print(f"Valid trials: {len(clean_trials)}")
    
    # Step 6: Calculate D-values
    # print_section("STEP 6: Calculate D-values (Balance & Pair)")
    results = clean_trials.calc_d_values()
    # print(f"Valid pairs found: {len(results)}")
    # print("\nD-value Pairs:")
    # print(results.to_string(index=False))
    
    # Step 7: Calculate Subject-Level D
    # print_section("STEP 7: Calculate Subject-Level D (Average per Subject)")
    subject_D = clean_trials.calc_subject_D()
    # print("\nSubject-Level D values:")
    # print(subject_D.to_string(index=False))
    
    # Step 8: Calculate Statistics
    # print_section("STEP 8: Calculate Statistics per Face ID")
    stats = clean_trials.calc_stats()
    # print("\nStatistics by Face ID:")
    # print(stats.to_string(index=False))
    
    # Verification
    print_section("VERIFICATION RESULTS")
    
    # Expected values per Face ID (from user's manual calculations)
    expected_stats = {
        'ID015': {
            'mean': 1.25,
            'std': 0.5,
            'sem': 0.25,
            't_stat': 5.0,
            'p_value': 0.015
        },
        'ID017': {
            'mean': 2.3333, # 2.333 repeating
            'std': 2.31,
            'sem': 1.334,
            't_stat': 1.75,
            'p_value': 0.20 # > 0.20
        },
        'ID030': {
            'mean': 3.0,
            'std': 3.0,
            'sem': 1.732,
            't_stat': 1.732,
            'p_value': 0.20 # > 0.20
        }
    }
    
    # Check D-values (should be positive)
    negative_d = results[results['d'] < 0]
    if not negative_d.empty:
        print(f"✗ FAILED: Found {len(negative_d)} negative D-values! (Check processing.py logic)")
    else:
        print("✓ D-values are all positive.")

    all_passed = True
    
    # Verify each face ID
    for face_id, expected in expected_stats.items():
        print(f"\n--- Checking {face_id} ---")
        face_stats = stats[stats['face_id'] == face_id]
        
        if face_stats.empty:
            print(f"✗ FAILED: No statistics found for {face_id}")
            all_passed = False
            continue
            
        actual = face_stats.iloc[0]
        
        # Helper for approximate comparison
        def check(name, act, exp, tolerance=0.01):
            match = abs(act - exp) < tolerance
            status = "✓" if match else "✗"
            print(f"{status} {name}: Expected {exp:.3f}, Actual {act:.3f}")
            return match

        m_match = check("Mean", actual['mean'], expected['mean'])
        s_match = check("Std", actual['std'], expected['std'])
        se_match = check("SEM", actual['sem'], expected['sem'])
        t_match = check("T-Stat", actual['t_stat'], expected['t_stat'], tolerance=0.1)
        
        # P-value check (since user specified "> 0.20" for some)
        if expected['p_value'] == 0.20:
            p_match = actual['p_value'] > 0.20 or abs(actual['p_value'] - 0.20) < 0.05
            status = "✓" if p_match else "✗"
            print(f"{status} P-Value: Expected > 0.20, Actual {actual['p_value']:.3f}")
        else:
            p_match = check("P-Value", actual['p_value'], expected['p_value'], tolerance=0.01)
            
        if not (m_match and s_match and se_match and t_match and p_match):
            all_passed = False

    print("\n" + "=" * 70)
    if all_passed:
        print("✓✓✓ ALL PER-FACE VERIFICATIONS PASSED! ✓✓✓")
        print("The standardized analysis matches manual calculations.")
        sys.exit(0)
    else:
        print("✗✗✗ VERIFICATION FAILED! ✗✗✗")
        print("Discrepancies found in per-face statistics.")
        sys.exit(1)
    print("=" * 70)

if __name__ == "__main__":
    main()
