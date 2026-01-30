
import pandas as pd
import numpy as np
import sys
import os
from unittest.mock import MagicMock

# Mock visualization libraries before they are imported by anything
sys.modules['matplotlib'] = MagicMock()
sys.modules['matplotlib.pyplot'] = MagicMock()
sys.modules['seaborn'] = MagicMock()

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from schema_analysis.tube_trials import TubeTrials

def test_angle_validation():
    print("--- Testing Angle Validation ---")
    
    # 1. Create dummy data with 50% bad angles
    # We want 10 trials. 5 valid, 5 invalid.
    # Valid range default: 3 < x < 40 (based on tube_trials.py mark_valid_angles default)
    # Let's verify defaults first.
    
    data = {
        'face_id': ['ID001'] * 10,
        'user_number': range(10),
        'faceSide': ['left'] * 10,
        'tubeTypeIndex': [0] * 10,
        'tip_direction': ['right'] * 10, # implies raw_angle * 1
        'raw_angle': [
            10, 20, 30, 35, 39, # 5 VALID (3 < x < 40)
            1, 2, 40, 45, 100   # 5 INVALID (x <= 3 or x >= 40) (Wait, default max is 40 exclusive? or 43? code said 40 in default param but processing says 43 default.. let's check tube_trials init default)
            # tube_trials.mark_valid_angles default is min=3, max=40.
            # So 40 is invalid (must be < 40).
        ]
    }
    df = pd.DataFrame(data)
    
    trials = TubeTrials(df)
    trials.process_angles() # Calculates end_angle
    
    print("\nTest 1: 50% Valid Sample")
    trials.mark_valid_angles(min_angle=3, max_angle=40)
    
    n_valid = trials.df['angle_valid'].sum()
    print(f"Valid count: {n_valid}/10")
    
    if n_valid == 5:
        print("PASS: Correctly identified 50% valid trials.")
    else:
        print(f"FAIL: Expected 5 valid, got {n_valid}")
        print(trials.df[['raw_angle', 'end_angle', 'angle_valid']])

    # 2. Edge Cases
    print("\nTest 2: Edge Cases")
    # min_angle=3, max_angle=40
    # Boundaries: 3 (invalid), 3.01 (valid), 39.99 (valid), 40 (invalid)
    edge_data = {
        'face_id': ['ID001'] * 5,
        'user_number': range(5),
         'faceSide': ['left'] * 5,
        'tubeTypeIndex': [0] * 5,
        'tip_direction': ['right'] * 5,
        'raw_angle': [3, 3.0001, 39.9999, 40, -10]
    }
    edge_df = pd.DataFrame(edge_data)
    edge_trials = TubeTrials(edge_df)
    edge_trials.process_angles()
    edge_trials.mark_valid_angles(min_angle=3, max_angle=40)
    
    results = edge_trials.df['angle_valid'].tolist()
    expected = [False, True, True, False, False] # 3 is not > 3. 40 is not < 40.
    
    for i, (res, exp, val) in enumerate(zip(results, expected, edge_data['raw_angle'])):
        status = "PASS" if res == exp else "FAIL"
        print(f"Value {val}: {res} (Expected {exp}) - {status}")

def test_subject_validity_refactor():
    print("\n--- Testing Subject Validity Refactor ---")
    # Create data with 1 bad subject (all trials invalid stats)
    # User 1: 2 invalid trials. User 2: 0 invalid trials.
    # Default max_invalid_trials=2. So > 2 is bad. Let's make User 1 have 3 invalid.
    
    data = {
         'face_id': ['ID001'] * 5,
        'user_number': [1, 1, 1, 2, 2],
        'faceSide': ['left'] * 5,
        'tubeTypeIndex': [0] * 5,
        'tip_direction': ['right'] * 5,
        'raw_angle': [1, 1, 1, 10, 10] # 1 is invalid (<3). 10 is valid.
    }
    df = pd.DataFrame(data)
    trials = TubeTrials(df)
    trials.process_angles()
    trials.mark_valid_angles(min_angle=3, max_angle=40)
    
    # User 1 has 3 invalid trials. User 2 has 0.
    # Threshold > 2 excludes. So User 1 excluded.
    trials.mark_valid_subjects(max_invalid_trials=2)
    
    cols = trials.df.columns
    if 'subject_valid' in cols and 'is_excluded_subject' not in cols:
         print("PASS: Column 'subject_valid' exists and 'is_excluded_subject' is gone.")
    else:
         print(f"FAIL: Columns found: {cols}")
         
    # Check values
    u1_valid = trials.df[trials.df['user_number'] == 1]['subject_valid'].all()
    u2_valid = trials.df[trials.df['user_number'] == 2]['subject_valid'].all()
    
    if not u1_valid and u2_valid:
        print("PASS: User 1 is invalid, User 2 is valid.")
    else:
        print(f"FAIL: User 1 valid? {u1_valid}, User 2 valid? {u2_valid}")

    # Test get_validity_stats
    print("\n--- Testing get_validity_stats ---")
    trials.get_validity_stats()

if __name__ == "__main__":
    test_angle_validation()
    test_subject_validity_refactor()
