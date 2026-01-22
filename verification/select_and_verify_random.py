
import os
import sys
import pandas as pd
import random

# Add project root to sys.path to import schema_analysis
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from schema_analysis.data_loader import load_and_merge_csvs
from schema_analysis import TubeTrials

def main():
    print("=" * 80)
    print("RANDOM VERIFICATION DATA GENERATOR")
    print("=" * 80)

    # 1. Load Data
    data_dir = os.path.join(project_root, 'data', 'raw')
    try:
        df = load_and_merge_csvs(data_dir)
    except FileNotFoundError:
        print(f"Error: Could not find data in {data_dir}")
        return

    # 2. Process with TubeTrials (Standard Pipeline)
    print("Loading and preprocessing data...")
    trials = TubeTrials(df)
    trials.process_angles()
    trials.mark_valid_angles(min_angle=3, max_angle=40) # Using standard limits
    
    # We don't filter subjects yet because we want to see individual valid pairs 
    # even if the subject might be excluded later, or we can filter strictly. 
    # Let's filter strictly to verify the "happy path".
    trials.mark_bad_subjects(max_invalid_trials=2)
    clean_trials = trials.select(valid_only=True)
    df = clean_trials.df # Work with the underlying dataframe

    # 3. Find Valid Pairs
    # We need to manually identify potential pairs to verify the logic "from scratch"
    # or rely on the logic we are testing to find candidates.
    # To truly verify, let's find groups that *look* like they should be pairs.
    
    valid_pairs = []
    
    # Group by potential pairing keys
    grouped = df.groupby(['user_number', 'face_id', 'tubeTypeIndex'])
    
    for (user, face, tube), group in grouped:
        # Check for Face Left candidate
        t_left = group[(group['faceSide'] == 'left') & (group['tip_direction'] == 'left')]
        a_left = group[(group['faceSide'] == 'left') & (group['tip_direction'] == 'right')]
        
        if len(t_left) == 1 and len(a_left) == 1:
            valid_pairs.append({
                'type': 'FaceLeft',
                'user': user, 'face': face, 'tube': tube,
                'towards': t_left.iloc[0],
                'away': a_left.iloc[0]
            })
            
        # Check for Face Right candidate
        t_right = group[(group['faceSide'] == 'right') & (group['tip_direction'] == 'right')]
        a_right = group[(group['faceSide'] == 'right') & (group['tip_direction'] == 'left')]
        
        if len(t_right) == 1 and len(a_right) == 1:
            valid_pairs.append({
                'type': 'FaceRight',
                'user': user, 'face': face, 'tube': tube,
                'towards': t_right.iloc[0],
                'away': a_right.iloc[0]
            })

    print(f"Found {len(valid_pairs)} valid pairs available for verification.")
    
    if not valid_pairs:
        print("No valid pairs found to sample!")
        return

    # 4. Randomly Select 10 pairs
    selected_pairs = random.sample(valid_pairs, min(10, len(valid_pairs)))
    
    print("\n" + "="*80)
    print("SELECTED PAIRS FOR MANUAL VERIFICATION")
    print("="*80)
    
    csv_rows = []
    d_values = []
    
    for i, pair in enumerate(selected_pairs, 1):
        t = pair['towards']
        a = pair['away']
        
        # Calculate expected values 
        d_calc = abs(t['end_angle']) - abs(a['end_angle'])
        d_values.append(d_calc)
        
        # Add to CSV rows (user_number,session_group,trialIndex,tubeTypeIndex,tip_direction,face_id,faceSide,towards_away,raw_angle,latency)
        # Note: We need to ensure we have all these columns. TubeTrials preserves the original DF columns.
        csv_rows.append(t)
        csv_rows.append(a)
        
        # print(f"\nExample #{i}: Subject {pair['user']} | Face {pair['face']} | Tube {pair['tube']} | Type: {pair['type']}")
        # print("-" * 60)
        # print(f"{'FIELD':<20} | {'TOWARDS TRIAL':<25} | {'AWAY TRIAL':<25}")
        # print("-" * 60)
        # print(f"{'Face Side':<20} | {t['faceSide']:<25} | {a['faceSide']:<25}")
        # print(f"{'Tip Direction':<20} | {t['tip_direction']:<25} | {a['tip_direction']:<25}")
        # print(f"{'Raw Angle':<20} | {t['raw_angle']:<25.4f} | {a['raw_angle']:<25.4f}")
        # print(f"{'Multiplier':<20} | {'-1 (Left)' if t['tip_direction']=='left' else '1 (Right)':<25} | {'-1 (Left)' if a['tip_direction']=='left' else '1 (Right)':<25}")
        # print("-" * 60)
        # print(f"{'End Angle (Calc)':<20} | {t['end_angle']:<25.4f} | {a['end_angle']:<25.4f}")
        # print("-" * 60)
        # print(f"Calculation:")
        # print(f"  D = |Towards End Angle| - |Away End Angle|")
        # print(f"  D = |{t['end_angle']:.4f}| - |{a['end_angle']:.4f}|")
        # print(f"  D = {abs(t['end_angle']):.4f} - {abs(a['end_angle']):.4f}")
        # print(f"  D = {d_calc:.4f}")
        # print("="*80)

    # 5. Export to CSV
    export_df = pd.DataFrame(csv_rows)
    export_cols = ['user_number', 'session_group', 'trialIndex', 'tubeTypeIndex', 'tip_direction', 'face_id', 'faceSide', 'towards_away', 'raw_angle', 'latency']
    
    # Filter for columns that actually exist
    existing_cols = [c for c in export_cols if c in export_df.columns]
    
    output_path = os.path.join(os.path.dirname(__file__), 'data', 'dummy_verification.csv')
    export_df[existing_cols].to_csv(output_path, index=False)
    print(f"\nExported {len(export_df)} trials to {output_path}")

    # 6. Calculate Overall Stats for Verification Script
    import numpy as np
    from scipy import stats
    
    mean_d = np.mean(d_values)
    std_d = np.std(d_values, ddof=1) # Sample standard deviation
    n = len(d_values) # Number of pairs (subjects effectively, for simple analysis, or we should group by user)
    
    # Note: The main analysis groups by subject first, then takes the mean. 
    # Here we might have multiple pairs per subject or single pairs per subject.
    # To be precise, let's group by user to verify the "per-subject" logic.
    
    pairs_df = pd.DataFrame(selected_pairs)
    pairs_df['d'] = d_values
    subject_means = pairs_df.groupby('user')['d'].mean()
    
    subj_mean_val = subject_means.mean()
    subj_std_val = subject_means.std(ddof=1) if len(subject_means) > 1 else 0
    subj_sem = subj_std_val / np.sqrt(len(subject_means))
    t_stat = subj_mean_val / subj_sem if subj_sem > 0 else 0
    p_val = stats.t.sf(abs(t_stat), len(subject_means)-1) * 2 # Two-tailed p-value
    
    # Write stats to file
    with open('stats.txt', 'w') as f:
        f.write(f"Number of Pairs: {len(d_values)}\n")
        f.write(f"Number of Subjects: {len(subject_means)}\n")
        f.write(f"D-values list: {[round(d, 4) for d in d_values]}\n")
        f.write(f"Subject Means list: {[round(m, 4) for m in subject_means]}\n")
        f.write(f"Mean D (Subject Level): {subj_mean_val:.4f}\n")
        f.write(f"Std Dev (Subject Level): {subj_std_val:.4f}\n")
        f.write(f"SEM: {subj_sem:.4f}\n")
        f.write(f"T-statistic: {t_stat:.4f}\n")
        f.write(f"P-value: {p_val:.4f}\n")

    print("\n" + "="*80)
    print("STATISTICS WRITTEN TO stats.txt")
    print("="*80)

if __name__ == "__main__":
    main()
