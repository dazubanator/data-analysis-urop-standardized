import pandas as pd
import numpy as np
from scipy import stats

# Load data
df = pd.read_csv('facetip_data_Nov2025.csv')

# Filter for sighted trials
if 'sightType' in df.columns:
    df = df[df['sightType'] == 'sighted'].copy()

def calculate_end_angle(row):
    if row['tip_direction'] == 'left':
        return row['raw_angle'] * -1
    elif row['tip_direction'] == 'right':
        return row['raw_angle'] * 1
    return row['raw_angle']

df['end_angle'] = df.apply(calculate_end_angle, axis=1)
df['angle_valid'] = (df['end_angle'] > 3) & (df['end_angle'] < 40)

print("=== COMPARING ID017 ACROSS DIFFERENT EXCLUSION METHODS ===\n")

# Helper function to run balancing
def run_balancing(dataframe):
    valid_d_values = []
    used_indices = set()
    
    for user_id in dataframe['user_number'].unique():
        user_df = dataframe[dataframe['user_number'] == user_id]
        
        for face_id in user_df['face_id'].unique():
            face_df = user_df[user_df['face_id'] == face_id]
            
            for tube_idx in face_df['tubeTypeIndex'].unique():
                tube_df = face_df[face_df['tubeTypeIndex'] == tube_idx]
                
                # Pair 1: Face Left
                p1_towards = tube_df[(tube_df['faceSide'] == 'left') & (tube_df['tip_direction'] == 'left')]
                p1_away = tube_df[(tube_df['faceSide'] == 'left') & (tube_df['tip_direction'] == 'right')]
                
                if len(p1_towards) == 1 and len(p1_away) == 1:
                    t_row = p1_towards.iloc[0]
                    a_row = p1_away.iloc[0]
                    
                    if t_row['angle_valid'] and a_row['angle_valid']:
                        d_val = abs(t_row['end_angle']) - abs(a_row['end_angle'])
                        valid_d_values.append({
                            'user_number': user_id,
                            'face_id': face_id,
                            'tubeTypeIndex': tube_idx,
                            'pair_type': 'FaceLeft',
                            'D': d_val
                        })
                        used_indices.add(t_row.name)
                        used_indices.add(a_row.name)
                
                # Pair 2: Face Right
                p2_towards = tube_df[(tube_df['faceSide'] == 'right') & (tube_df['tip_direction'] == 'right')]
                p2_away = tube_df[(tube_df['faceSide'] == 'right') & (tube_df['tip_direction'] == 'left')]
                
                if len(p2_towards) == 1 and len(p2_away) == 1:
                    t_row = p2_towards.iloc[0]
                    a_row = p2_away.iloc[0]
                    
                    if t_row['angle_valid'] and a_row['angle_valid']:
                        d_val = abs(t_row['end_angle']) - abs(a_row['end_angle'])
                        valid_d_values.append({
                            'user_number': user_id,
                            'face_id': face_id,
                            'tubeTypeIndex': tube_idx,
                            'pair_type': 'FaceRight',
                            'D': d_val
                        })
                        used_indices.add(t_row.name)
                        used_indices.add(a_row.name)
    
    return valid_d_values, used_indices

# METHOD 1: NO EXCLUSION
print("METHOD 1: NO SUBJECT EXCLUSION")
print("-" * 50)
df_no_exclusion = df.copy()
valid_d_no_exclusion, _ = run_balancing(df_no_exclusion)
results_no_exclusion = pd.DataFrame(valid_d_no_exclusion)

id017_no_exclusion = results_no_exclusion[results_no_exclusion['face_id'] == 'ID017']['D']
mean_no_excl = id017_no_exclusion.mean()
std_no_excl = id017_no_exclusion.std()
count_no_excl = len(id017_no_exclusion)
_, p_no_excl = stats.ttest_1samp(id017_no_exclusion, 0)

print(f"ID017 - Count: {count_no_excl}, Mean: {mean_no_excl:.4f}, Std: {std_no_excl:.4f}, P: {p_no_excl:.4f}")

# METHOD 2: ANGLE-ONLY EXCLUSION (>2 angle-invalid)
print("\nMETHOD 2: ANGLE-ONLY EXCLUSION (>2 angle-invalid)")
print("-" * 50)
df_angle_only = df.copy()
angle_invalid_per_subject = df_angle_only[~df_angle_only['angle_valid']].groupby('user_number').size()
subjects_to_exclude_angle = angle_invalid_per_subject[angle_invalid_per_subject > 2].index.tolist()
df_angle_only = df_angle_only[~df_angle_only['user_number'].isin(subjects_to_exclude_angle)].copy()

valid_d_angle_only, _ = run_balancing(df_angle_only)
results_angle_only = pd.DataFrame(valid_d_angle_only)

id017_angle_only = results_angle_only[results_angle_only['face_id'] == 'ID017']['D']
mean_angle = id017_angle_only.mean()
std_angle = id017_angle_only.std()
count_angle = len(id017_angle_only)
_, p_angle = stats.ttest_1samp(id017_angle_only, 0)

print(f"Subjects excluded: {len(subjects_to_exclude_angle)}")
print(f"ID017 - Count: {count_angle}, Mean: {mean_angle:.4f}, Std: {std_angle:.4f}, P: {p_angle:.4f}")

# METHOD 3: TOTAL INVALIDATION EXCLUSION (>2 total invalid)
print("\nMETHOD 3: TOTAL INVALIDATION EXCLUSION (>2 total invalid)")
print("-" * 50)
df_total = df.copy()

# Run initial balancing to identify all invalidations
_, initial_used_indices = run_balancing(df_total)

angle_invalid_indices = set(df_total[~df_total['angle_valid']].index)
angle_valid_indices = set(df_total[df_total['angle_valid']].index)
balancing_invalid_indices = angle_valid_indices - initial_used_indices
all_invalid_indices = angle_invalid_indices | balancing_invalid_indices

df_total['temp_invalid'] = df_total.index.isin(all_invalid_indices)
invalid_per_subject = df_total[df_total['temp_invalid']].groupby('user_number').size()
subjects_to_exclude_total = invalid_per_subject[invalid_per_subject > 2].index.tolist()

df_total = df_total[~df_total['user_number'].isin(subjects_to_exclude_total)].copy()
df_total = df_total.drop(columns=['temp_invalid'])

valid_d_total, _ = run_balancing(df_total)
results_total = pd.DataFrame(valid_d_total)

id017_total = results_total[results_total['face_id'] == 'ID017']['D']
mean_total = id017_total.mean()
std_total = id017_total.std()
count_total = len(id017_total)
_, p_total = stats.ttest_1samp(id017_total, 0)

print(f"Subjects excluded: {len(subjects_to_exclude_total)}")
print(f"ID017 - Count: {count_total}, Mean: {mean_total:.4f}, Std: {std_total:.4f}, P: {p_total:.4f}")

# COMPARISON
print("\n\n=== COMPARISON FOR ID017 ===")
print("-" * 70)
print(f"{'Method':<30} {'Count':<10} {'Mean D':<12} {'Std':<12} {'P-value':<10}")
print("-" * 70)
print(f"{'No Exclusion':<30} {count_no_excl:<10} {mean_no_excl:<12.4f} {std_no_excl:<12.4f} {p_no_excl:<10.4f}")
print(f"{'Angle-Only Exclusion':<30} {count_angle:<10} {mean_angle:<12.4f} {std_angle:<12.4f} {p_angle:<10.4f}")
print(f"{'Total Invalidation Exclusion':<30} {count_total:<10} {mean_total:<12.4f} {std_total:<12.4f} {p_total:<10.4f}")
print("-" * 70)

print(f"\nChange from Angle-Only to Total:")
print(f"  Count: {count_angle} -> {count_total} (Δ = {count_total - count_angle})")
print(f"  Mean D: {mean_angle:.4f} -> {mean_total:.4f} (Δ = {mean_total - mean_angle:.4f})")
print(f"  P-value: {p_angle:.4f} -> {p_total:.4f} (Δ = {p_total - p_angle:.4f})")

# Find which subjects were excluded differently
subjects_angle_only_set = set(subjects_to_exclude_angle)
subjects_total_set = set(subjects_to_exclude_total)
additional_excluded = subjects_total_set - subjects_angle_only_set

print(f"\n\nAdditional subjects excluded by Total method: {len(additional_excluded)}")

# Check which of these additional subjects had ID017 data
if len(additional_excluded) > 0:
    df_id017_original = df[df['face_id'] == 'ID017']
    id017_users_removed = df_id017_original[df_id017_original['user_number'].isin(additional_excluded)]['user_number'].unique()
    print(f"Of these, {len(id017_users_removed)} had ID017 trials")
    
    if len(id017_users_removed) > 0:
        print(f"\nID017 users removed by Total but not Angle-Only: {sorted(id017_users_removed)[:10]}...")
