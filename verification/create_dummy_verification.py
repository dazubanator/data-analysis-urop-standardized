import pandas as pd

# Create a simple dummy dataset with 2 subjects and 1 Face ID
# Designed to be easy to hand-calculate

data = {
    'user_number': [1, 1, 1, 1, 2, 2, 2, 2],
    'session_group': ['G1', 'G1', 'G1', 'G1', 'G2', 'G2', 'G2', 'G2'],
    'trialIndex': [0, 1, 2, 3, 0, 1, 2, 3],
    'tubeTypeIndex': [0, 0, 1, 1, 0, 0, 1, 1],
    'tip_direction': ['left', 'right', 'right', 'left', 'left', 'right', 'right', 'left'],
    'face_id': ['ID015', 'ID015', 'ID015', 'ID015', 'ID015', 'ID015', 'ID015', 'ID015'],
    'faceSide': ['left', 'left', 'right', 'right', 'left', 'left', 'right', 'right'],
    'towards_away': ['towards', 'away', 'towards', 'away', 'towards', 'away', 'towards', 'away'],
    # IMPORTANT: For tip_direction='left', raw_angle must be NEGATIVE
    # because the transformation multiplies by -1 (making it positive)
    'raw_angle': [-10, 5, 15, -12, -12, 7, 18, -14],
    'latency': [1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7]
}

df = pd.DataFrame(data)

# Save to verification/data/
import os
output_dir = os.path.join(os.path.dirname(__file__), 'verification', 'data')
os.makedirs(output_dir, exist_ok=True)
output_file_path = os.path.join(output_dir, 'dummy_verification.csv')
df.to_csv(output_file_path, index=False)

print(f"Dummy data created: {output_file_path}")
print("\n" + "="*70)
print("DUMMY DATA OVERVIEW")
print("="*70)
print(df.to_string(index=False))

print("\n" + "="*70)
print("EXPECTED CALCULATIONS (for verification)")
print("="*70)

print("\nUser 1:")
print("  Pair 1 (Tube 0): ")
print("    Towards (left/left): raw=-10° → end_angle=(-10)*(-1)=10°")
print("    Away (left/right): raw=5° → end_angle=5*(1)=5°")
print("    → D1 = |10| - |5| = 10 - 5 = 5")
print("  Pair 2 (Tube 1): ")
print("    Towards (right/right): raw=15° → end_angle=15*(1)=15°")
print("    Away (right/left): raw=-12° → end_angle=(-12)*(-1)=12°")
print("    → D2 = |15| - |12| = 15 - 12 = 3")
print("  Average D for User 1 = (5 + 3) / 2 = 4")

print("\nUser 2:")
print("  Pair 1 (Tube 0): ")
print("    Towards (left/left): raw=-12° → end_angle=(-12)*(-1)=12°")
print("    Away (left/right): raw=7° → end_angle=7*(1)=7°")
print("    → D3 = |12| - |7| = 12 - 7 = 5")
print("  Pair 2 (Tube 1): ")
print("    Towards (right/right): raw=18° → end_angle=18*(1)=18°")
print("    Away (right/left): raw=-14° → end_angle=(-14)*(-1)=14°")
print("    → D4 = |18| - |14| = 18 - 14 = 4")
print("  Average D for User 2 = (5 + 4) / 2 = 4.5")

print("\nStatistics for ID015:")
print("  Subject-level D values: [4, 4.5]")
print("  Mean D = (4 + 4.5) / 2 = 4.25")
print("  Variance = [(4-4.25)² + (4.5-4.25)²] / (2-1)")
print("           = [0.0625 + 0.0625] / 1 = 0.125")
print("  Std Dev = √0.125 ≈ 0.3536")
print("  SEM = 0.3536 / √2 ≈ 0.25")
print("  t-statistic = (4.25 - 0) / 0.25 = 17")
print("  df = 2 - 1 = 1")
print("  p-value ≈ 0.037 (from t-distribution table)")

print("\n" + "="*70)
