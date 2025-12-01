import pandas as pd

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

# Find trials where they tilted in the WRONG direction
# This means end_angle is negative (they tilted opposite to the instruction)
wrong_direction = df[df['end_angle'] < 0]

print("=== First 5 Trials Invalidated by Wrong Tilt Direction ===")
print(f"Total trials with wrong direction: {len(wrong_direction)}\n")

if not wrong_direction.empty:
    print(wrong_direction[['user_number', 'face_id', 'tubeTypeIndex', 'faceSide', 
                           'tip_direction', 'raw_angle', 'end_angle']].head(5).to_string(index=True))
    
    print("\n\nExplanation for each:")
    for idx, (i, row) in enumerate(wrong_direction.head(5).iterrows()):
        print(f"\n{idx+1}. Index {i}:")
        print(f"   Instructed to tilt: {row['tip_direction']}")
        print(f"   Raw angle: {row['raw_angle']} ({'left' if row['raw_angle'] < 0 else 'right'})")
        print(f"   End angle: {row['end_angle']} -> NEGATIVE = Wrong direction!")
else:
    print("None found")

print("\n\nNote: These trials are invalidated because end_angle < 0, which means")
print("the participant tilted in the opposite direction from what was instructed.")
