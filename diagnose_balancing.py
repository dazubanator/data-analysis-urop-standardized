import pandas as pd
import numpy as np

# Load data
df = pd.read_csv('facetip_data_Nov2025.csv')

# Filter for sighted trials
if 'sightType' in df.columns:
    df = df[df['sightType'] == 'sighted'].copy()

# Calculate end_angle
def calculate_end_angle(row):
    if row['tip_direction'] == 'left':
        return row['raw_angle'] * -1
    elif row['tip_direction'] == 'right':
        return row['raw_angle'] * 1
    return row['raw_angle']

df['end_angle'] = df.apply(calculate_end_angle, axis=1)
df['angle_valid'] = (df['end_angle'] > 3) & (df['end_angle'] < 40)

# Get the first 5 trials invalidated by balancing
# (These are the indices from the previous run)
balancing_invalid_indices = [0, 1, 11, 21, 46]

print("=== DIAGNOSING BALANCING INVALIDATIONS ===\n")

for idx in balancing_invalid_indices:
    trial = df.iloc[idx]
    
    print(f"\n--- Trial Index {idx} ---")
    print(f"User: {trial['user_number']}, Face: {trial['face_id']}, Tube: {trial['tubeTypeIndex']}")
    print(f"FaceSide: {trial['faceSide']}, TipDirection: {trial['tip_direction']}")
    print(f"Raw Angle: {trial['raw_angle']}, End Angle: {trial['end_angle']}, Valid: {trial['angle_valid']}")
    
    # Determine what the pair should be
    user_id = trial['user_number']
    face_id = trial['face_id']
    tube_idx = trial['tubeTypeIndex']
    face_side = trial['faceSide']
    tip_dir = trial['tip_direction']
    
    # Find the corresponding pair
    if face_side == 'left' and tip_dir == 'left':
        # This is "Face Left, Tilt Left" -> needs "Face Left, Tilt Right"
        pair_type = "Face Left, Tilt Left (Towards) -> needs Face Left, Tilt Right (Away)"
        pair_face_side = 'left'
        pair_tip_dir = 'right'
    elif face_side == 'left' and tip_dir == 'right':
        # This is "Face Left, Tilt Right" -> needs "Face Left, Tilt Left"
        pair_type = "Face Left, Tilt Right (Away) -> needs Face Left, Tilt Left (Towards)"
        pair_face_side = 'left'
        pair_tip_dir = 'left'
    elif face_side == 'right' and tip_dir == 'right':
        # This is "Face Right, Tilt Right" -> needs "Face Right, Tilt Left"
        pair_type = "Face Right, Tilt Right (Towards) -> needs Face Right, Tilt Left (Away)"
        pair_face_side = 'right'
        pair_tip_dir = 'left'
    elif face_side == 'right' and tip_dir == 'left':
        # This is "Face Right, Tilt Left" -> needs "Face Right, Tilt Right"
        pair_type = "Face Right, Tilt Left (Away) -> needs Face Right, Tilt Right (Towards)"
        pair_face_side = 'right'
        pair_tip_dir = 'right'
    
    print(f"Pair Type: {pair_type}")
    
    # Search for the pair
    pair_trials = df[
        (df['user_number'] == user_id) &
        (df['face_id'] == face_id) &
        (df['tubeTypeIndex'] == tube_idx) &
        (df['faceSide'] == pair_face_side) &
        (df['tip_direction'] == pair_tip_dir)
    ]
    
    if len(pair_trials) == 0:
        print("XX PAIR NOT FOUND IN DATA")
    elif len(pair_trials) > 1:
        print(f"!!  MULTIPLE PAIRS FOUND ({len(pair_trials)})")
        for i, (_, pair) in enumerate(pair_trials.iterrows()):
            print(f"  Pair {i+1}: Raw={pair['raw_angle']}, End={pair['end_angle']}, Valid={pair['angle_valid']}")
    else:
        pair = pair_trials.iloc[0]
        print(f"OK Pair Found: Raw={pair['raw_angle']}, End={pair['end_angle']}, Valid={pair['angle_valid']}")
        if not pair['angle_valid']:
            print(f"  XX REASON FOR EXCLUSION: Pair failed angle validation (end_angle={pair['end_angle']} not in (3, 40))")
        else:
            print(f"  !!  Both trials are angle-valid but still excluded - investigating...")

print("\n\n=== SUMMARY ===")
print("If a trial is angle-valid but excluded, check if its pair failed the angle rule.")
