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
wrong_direction = df[df['end_angle'] < 0]

print("=== Users with Most Wrong Direction Trials ===")
print(f"Total trials with wrong direction: {len(wrong_direction)} out of {len(df)} ({100*len(wrong_direction)/len(df):.2f}%)\n")

# Count by user
user_wrong_counts = wrong_direction.groupby('user_number').size().reset_index(name='wrong_direction_count')
user_wrong_counts = user_wrong_counts.sort_values('wrong_direction_count', ascending=False)

# Also get total trials per user for context
user_total_counts = df.groupby('user_number').size().reset_index(name='total_trials')

# Merge
user_stats = user_wrong_counts.merge(user_total_counts, on='user_number', how='left')
user_stats['wrong_pct'] = 100 * user_stats['wrong_direction_count'] / user_stats['total_trials']
user_stats = user_stats.sort_values('wrong_direction_count', ascending=False)

print("Top 20 Users by Wrong Direction Count:")
print(user_stats.head(20).to_string(index=False))

print("\n\nTop 20 Users by Wrong Direction Percentage:")
user_stats_by_pct = user_stats.sort_values('wrong_pct', ascending=False)
print(user_stats_by_pct.head(20).to_string(index=False))
