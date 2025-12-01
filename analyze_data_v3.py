import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import os

# --- Configuration ---
DATA_FILE = os.path.join('analysis_v3', 'merged_experiments_cleaned.csv')
OUTPUT_DIR = os.path.join('analysis_v3', 'output')

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)


def analyze_v3():
    print("=" * 70)
    print("ANALYSIS V3 - New Rules")
    print("=" * 70)

    # --- STEP 1: Load Data ---
    print("\n[STEP 1] Loading data...")
    try:
        df = pd.read_csv(DATA_FILE)
    except FileNotFoundError:
        print(f"Error: {DATA_FILE} not found.")
        return
    print(f"Loaded {len(df)} trials from {df['user_number'].nunique()} subjects")

    # --- STEP 2: Rename Face IDs ---
    print("\n[STEP 2] Renaming face IDs...")
    print(f"Original face IDs: {sorted(df['face_id'].unique())}")
    df['face_id'] = df['face_id'].replace({
        'ID001': 'ID017',
        'ID022': 'ID015'
    })
    print(f"Updated face IDs: {sorted(df['face_id'].unique())}")

    initial_trials = len(df)
    initial_subjects = df['user_number'].nunique()

    # --- STEP 3: Transform Raw Angles ---
    print("\n[STEP 3] Transforming raw angles...")
    def calculate_end_angle(row):
        if row['tip_direction'] == 'left':
            return row['raw_angle'] * -1
        elif row['tip_direction'] == 'right':
            return row['raw_angle'] * 1
        return row['raw_angle']
    df['end_angle'] = df.apply(calculate_end_angle, axis=1)
    print("Created end_angle column (raw × -1 for left, raw × 1 for right)")

    # --- STEP 4: Angle Validation (3 < end_angle < 40) ---
    print("\n[STEP 4] Applying angle validation rule (3 < end_angle < 40)...")
    df['angle_valid'] = (df['end_angle'] > 3) & (df['end_angle'] < 40)
    trials_invalidated_angle = len(df) - df['angle_valid'].sum()
    print(f"Trials invalidated by angle rule: {trials_invalidated_angle}")

    # --- STEP 5: Subject Exclusion (>2 Invalid Trials) ---
    print("\n[STEP 5] Excluding subjects with >2 angle-invalid trials...")
    angle_invalid_per_subject = df[~df['angle_valid']].groupby('user_number').size()
    subjects_to_exclude = angle_invalid_per_subject[angle_invalid_per_subject > 2].index.tolist()
    print(f"Subjects with >2 angle-invalid trials: {len(subjects_to_exclude)}")
    trials_from_excluded_subjects = len(df[df['user_number'].isin(subjects_to_exclude)])
    print(f"Trials removed via subject exclusion: {trials_from_excluded_subjects}")
    df = df[~df['user_number'].isin(subjects_to_exclude)].copy()
    subjects_after_exclusion = df['user_number'].nunique()
    trials_after_exclusion = len(df)
    print(f"Remaining: {trials_after_exclusion} trials from {subjects_after_exclusion} subjects")

    # --- STEP 6: Balance Trials (Pairing Logic) ---
    print("\n[STEP 6] Balancing trials (identifying valid pairs)...")
    valid_d_values = []
    used_indices = set()
    for user_id in df['user_number'].unique():
        user_df = df[df['user_number'] == user_id]
        for face_id in user_df['face_id'].unique():
            face_df = user_df[user_df['face_id'] == face_id]
            for tube_idx in face_df['tubeTypeIndex'].unique():
                tube_df = face_df[face_df['tubeTypeIndex'] == tube_idx]
                # Pair 1: Face Left (LL towards, LR away)
                towards_left = tube_df[(tube_df['faceSide'] == 'left') & (tube_df['tip_direction'] == 'left')]
                away_left = tube_df[(tube_df['faceSide'] == 'left') & (tube_df['tip_direction'] == 'right')]
                if len(towards_left) == 1 and len(away_left) == 1:
                    t_row, a_row = towards_left.iloc[0], away_left.iloc[0]
                    if t_row['angle_valid'] and a_row['angle_valid']:
                        d_val = abs(t_row['end_angle']) - abs(a_row['end_angle'])
                        valid_d_values.append({
                            'user_number': user_id,
                            'face_id': face_id,
                            'tubeTypeIndex': tube_idx,
                            'pair_type': 'FaceLeft',
                            'D': d_val
                        })
                        used_indices.update([t_row.name, a_row.name])
                # Pair 2: Face Right (RR towards, RL away)
                towards_right = tube_df[(tube_df['faceSide'] == 'right') & (tube_df['tip_direction'] == 'right')]
                away_right = tube_df[(tube_df['faceSide'] == 'right') & (tube_df['tip_direction'] == 'left')]
                if len(towards_right) == 1 and len(away_right) == 1:
                    t_row, a_row = towards_right.iloc[0], away_right.iloc[0]
                    if t_row['angle_valid'] and a_row['angle_valid']:
                        d_val = abs(t_row['end_angle']) - abs(a_row['end_angle'])
                        valid_d_values.append({
                            'user_number': user_id,
                            'face_id': face_id,
                            'tubeTypeIndex': tube_idx,
                            'pair_type': 'FaceRight',
                            'D': d_val
                        })
                        used_indices.update([t_row.name, a_row.name])
    results_df = pd.DataFrame(valid_d_values)
    angle_valid_trials_after_exclusion = df['angle_valid'].sum()
    trials_used_in_pairs = len(used_indices)
    trials_invalidated_balancing = angle_valid_trials_after_exclusion - trials_used_in_pairs
    print(f"Valid pairs found: {len(results_df)}")
    print(f"Trials used in pairs: {trials_used_in_pairs}")
    print(f"Trials invalidated by balancing: {trials_invalidated_balancing}")
    final_valid_trials = trials_used_in_pairs
    final_subjects = results_df['user_number'].nunique()

    # --- STEP 7: Summary Statistics ---
    print("\n" + "=" * 70)
    print("SUMMARY STATISTICS")
    print("=" * 70)
    print(f"\nInitial: {initial_trials} trials, {initial_subjects} subjects")
    print(f"Removed by angle rule: {trials_invalidated_angle} trials")
    print(f"Removed by subject exclusion: {trials_from_excluded_subjects} trials ({len(subjects_to_exclude)} subjects)")
    print(f"Removed by balancing: {trials_invalidated_balancing} trials")
    print(f"Final: {final_valid_trials} valid trials ({len(results_df)} pairs), {final_subjects} subjects")
    if results_df.empty:
        print("\nNo valid D values found.")
        return
    overall_mean_d = results_df['D'].mean()
    overall_std_d = results_df['D'].std()
    _, overall_p = stats.ttest_1samp(results_df['D'], 0)
    print(f"\nOverall Mean D: {overall_mean_d:.4f}")
    print(f"Overall Std D: {overall_std_d:.4f}")
    print(f"Overall P-value: {overall_p:.4f}")
    print("\n--- Statistics per Face ID ---")
    face_stats = results_df.groupby('face_id')['D'].agg(['count', 'mean', 'std'])
    face_stats['sem'] = face_stats['std'] / np.sqrt(face_stats['count'])
    p_values = []
    for face_id in face_stats.index:
        d_vals = results_df[results_df['face_id'] == face_id]['D']
        if len(d_vals) > 1:
            _, p = stats.ttest_1samp(d_vals, 0)
        else:
            p = np.nan
        p_values.append(p)
    face_stats['p_value'] = p_values
    print(face_stats)

    # --- STEP 8: Generate Visualizations ---
    print("\n[STEP 8] Generating visualizations...")
    sns.set_theme(style="whitegrid")
    # Filtering pipeline
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    stages_trials = ['Initial', 'After\nAngle Rule', 'After\nSubject\nExclusion', 'After\nBalancing']
    trials_at_stage = [initial_trials, initial_trials - trials_invalidated_angle, trials_after_exclusion, final_valid_trials]
    colors_trials = ['#3498db', '#e74c3c', '#f39c12', '#2ecc71']
    bars1 = ax1.bar(range(len(stages_trials)), trials_at_stage, color=colors_trials, alpha=0.8, edgecolor='black', linewidth=1.5)
    for i, (bar, val) in enumerate(zip(bars1, trials_at_stage)):
        ax1.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 100, f"{val:,}", ha='center', va='bottom', fontsize=10, fontweight='bold')
    ax1.set_ylabel('Number of Trials', fontsize=12, fontweight='bold')
    ax1.set_title('Trial Filtering Pipeline', fontsize=14, fontweight='bold')
    ax1.set_xticks(range(len(stages_trials)))
    ax1.set_xticklabels(stages_trials, fontsize=10)
    ax1.grid(axis='y', alpha=0.3, linestyle='--')
    # Subjects pipeline
    stages_subjects = ['Initial', 'After\nExclusion', 'Final']
    subjects_at_stage = [initial_subjects, subjects_after_exclusion, final_subjects]
    colors_subjects = ['#3498db', '#e74c3c', '#2ecc71']
    bars2 = ax2.bar(range(len(stages_subjects)), subjects_at_stage, color=colors_subjects, alpha=0.8, edgecolor='black', linewidth=1.5)
    for bar, val in zip(bars2, subjects_at_stage):
        ax2.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 3, f"{val}", ha='center', va='bottom', fontsize=10, fontweight='bold')
    ax2.set_ylabel('Number of Subjects', fontsize=12, fontweight='bold')
    ax2.set_title('Subject Filtering Pipeline', fontsize=14, fontweight='bold')
    ax2.set_xticks(range(len(stages_subjects)))
    ax2.set_xticklabels(stages_subjects, fontsize=10)
    ax2.grid(axis='y', alpha=0.3, linestyle='--')
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/filtering_pipeline.png", dpi=300, bbox_inches='tight')
    print(f"  Saved: {OUTPUT_DIR}/filtering_pipeline.png")
    plt.close()
    # Distributions per Face ID
    for face_id in sorted(results_df['face_id'].unique()):
        face_data = results_df[results_df['face_id'] == face_id]
        mean_d = face_data['D'].mean()
        count = len(face_data)
        sem = face_stats.loc[face_id, 'sem']
        p_val = face_stats.loc[face_id, 'p_value']
        df_stat = count - 1
        t_crit_05 = stats.t.ppf(0.975, df_stat)
        t_crit_10 = stats.t.ppf(0.95, df_stat)
        d_threshold_05 = t_crit_05 * sem
        d_threshold_10 = t_crit_10 * sem
        # Full range + auto‑zoom
        fig, axes = plt.subplots(1, 2, figsize=(18, 6))
        ax = axes[0]
        sns.histplot(data=face_data, x='D', binwidth=0.5, kde=True, color='#3498db', alpha=0.6, ax=ax)
        ax.axvline(0, color='black', linewidth=2, label='Null (D=0)', zorder=5)
        ax.axvline(mean_d, color='red', linewidth=2, linestyle='--', label=f'Mean D = {mean_d:.2f}', zorder=5)
        ax.axvline(d_threshold_05, color='green', linewidth=2, linestyle=':', label=f'α=0.05 (±{d_threshold_05:.2f})', zorder=4)
        ax.axvline(-d_threshold_05, color='green', linewidth=2, linestyle=':', zorder=4)
        ax.axvline(d_threshold_10, color='orange', linewidth=2, linestyle='-.', label=f'α=0.10 (±{d_threshold_10:.2f})', zorder=4)
        ax.axvline(-d_threshold_10, color='orange', linewidth=2, linestyle='-.', zorder=4)
        ax.set_xlabel('Mean D Value (degrees)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Number of Valid D Values', fontsize=12, fontweight='bold')
        ax.set_title(f'Full Range Distribution - Face {face_id}', fontsize=14, fontweight='bold')
        ax.legend(loc='upper right', fontsize=10)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        # Auto‑zoomed
        ax = axes[1]
        sns.histplot(data=face_data, x='D', binwidth=0.5, kde=True, color='#3498db', alpha=0.6, ax=ax)
        ax.axvline(0, color='black', linewidth=2, label='Null (D=0)', zorder=5)
        ax.axvline(mean_d, color='red', linewidth=2, linestyle='--', label=f'Mean D = {mean_d:.2f}', zorder=5)
        ax.axvline(d_threshold_05, color='green', linewidth=2, linestyle=':', label=f'α=0.05 (±{d_threshold_05:.2f})', zorder=4)
        ax.axvline(-d_threshold_05, color='green', linewidth=2, linestyle=':', zorder=4)
        ax.axvline(d_threshold_10, color='orange', linewidth=2, linestyle='-.', label=f'α=0.10 (±{d_threshold_10:.2f})', zorder=4)
        ax.axvline(-d_threshold_10, color='orange', linewidth=2, linestyle='-.', zorder=4)
        max_abs = max(abs(mean_d), abs(d_threshold_05), abs(d_threshold_10))
        zoom_limit = max(1.0, max_abs * 1.5)
        ax.set_xlim(-zoom_limit, zoom_limit)
        ax.set_xlabel('Mean D Value (degrees)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Number of Valid D Values', fontsize=12, fontweight='bold')
        ax.set_title(f'Auto‑Zoomed Distribution - Face {face_id}\n(n={count}, Mean={mean_d:.4f}, p={p_val:.4f})', fontsize=14, fontweight='bold')
        ax.legend(loc='upper right', fontsize=10)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        plt.tight_layout()
        plt.savefig(f"{OUTPUT_DIR}/distribution_{face_id}.png", dpi=300, bbox_inches='tight')
        print(f"  Saved: {OUTPUT_DIR}/distribution_{face_id}.png")
        plt.close()
        # Fixed zoom (-5 to 5)
        fig_fixed, ax_fixed = plt.subplots(figsize=(9, 6))
        sns.histplot(data=face_data, x='D', binwidth=0.5, kde=True, color='#3498db', alpha=0.6, ax=ax_fixed)
        ax_fixed.axvline(0, color='black', linewidth=2, label='Null (D=0)', zorder=5)
        ax_fixed.axvline(mean_d, color='red', linewidth=2, linestyle='--', label=f'Mean D = {mean_d:.2f}', zorder=5)
        ax_fixed.axvline(d_threshold_05, color='green', linewidth=2, linestyle=':', label=f'α=0.05 (±{d_threshold_05:.2f})', zorder=4)
        ax_fixed.axvline(-d_threshold_05, color='green', linewidth=2, linestyle=':', zorder=4)
        ax_fixed.axvline(d_threshold_10, color='orange', linewidth=2, linestyle='-.', label=f'α=0.10 (±{d_threshold_10:.2f})', zorder=4)
        ax_fixed.axvline(-d_threshold_10, color='orange', linewidth=2, linestyle='-.', zorder=4)
        ax_fixed.set_xlim(-5, 5)
        ax_fixed.set_xlabel('Mean D Value (degrees)', fontsize=12, fontweight='bold')
        ax_fixed.set_ylabel('Number of Valid D Values', fontsize=12, fontweight='bold')
        ax_fixed.set_title(f'Fixed Zoom Distribution - Face {face_id}\n(n={count}, Mean={mean_d:.4f}, p={p_val:.4f})', fontsize=14, fontweight='bold')
        ax_fixed.legend(loc='upper right', fontsize=10)
        ax_fixed.grid(axis='y', alpha=0.3, linestyle='--')
        plt.tight_layout()
        plt.savefig(f"{OUTPUT_DIR}/distribution_{face_id}_zoom_fixed.png", dpi=300, bbox_inches='tight')
        print(f"  Saved: {OUTPUT_DIR}/distribution_{face_id}_zoom_fixed.png")
        plt.close()
    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)
    print(f"All outputs saved to '{OUTPUT_DIR}/' directory")

if __name__ == "__main__":
    analyze_v3()
