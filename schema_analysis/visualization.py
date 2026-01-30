import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy import stats as sp_stats

def plot_results(results, stats_df):
    """
    Generates per-face D-value distributions and summary statistics plots.
    Includes Overview and Zoomed views with significance thresholds.
    """
    if stats_df.empty:
        print("No valid data to visualize.")
        return

    unique_faces = sorted(results['face_id'].unique())
    n_faces = len(unique_faces)
    
    # Set styling
    sns.set_theme(style="whitegrid", palette="muted")
    
    # --- 1. Per-Face Distributions (Overview) ---
    print("\n--- Generating Overview Distributions ---")
    n_cols = min(3, n_faces)
    n_rows = (n_faces + n_cols - 1) // n_cols
    
    fig1 = plt.figure(figsize=(n_cols * 5, n_rows * 4))
    for i, face_id in enumerate(unique_faces):
        ax = fig1.add_subplot(n_rows, n_cols, i + 1)
        face_data = results[results['face_id'] == face_id]['d']
        face_stats = stats_df[stats_df['face_id'] == face_id].iloc[0]
        
        # Calculate Significance Threshold for the mean
        # df = n - 1
        df = face_stats['n_subjects'] - 1
        if df > 0:
            t_crit = sp_stats.t.ppf(0.975, df)
            threshold = t_crit * face_stats['sem']
        else:
            threshold = np.nan

        # Plot Histogram
        sns.histplot(face_data, kde=True, ax=ax, color='skyblue', alpha=0.6)
        
        # Reference lines
        ax.axvline(0, color='grey', linestyle='--', linewidth=2, label='Null (0°)')
        ax.axvline(face_stats['mean'], color='red', linestyle='-', linewidth=2, label=f"Mean: {face_stats['mean']:.2f}°")
        
        if not np.isnan(threshold):
            ax.axvline(threshold, color='green', linestyle=':', linewidth=1.5, label='Sig. Threshold (Mean)')
            if face_stats['mean'] < 0: # If mean is negative, show negative threshold too
                 ax.axvline(-threshold, color='green', linestyle=':', linewidth=1.5)
        
        # Formatting
        title = f"Face {face_id} (n={int(face_stats['n_subjects'])})\n"
        title += f"p={face_stats['p_value']:.4f} {'*' if face_stats['p_value'] < 0.05 else '(ns)'}"
        ax.set_title(title, fontweight='bold')
        ax.set_xlabel('D-value (degrees)')
        ax.set_ylabel('Frequency (Count)')
        if i == 0: ax.legend(fontsize='small')
        
    plt.tight_layout()
    plt.show()

    # --- 2. Per-Face Distributions (Zoomed View) ---
    print("\n--- Generating Zoomed View (Focus on Null and Mean) ---")
    fig2 = plt.figure(figsize=(n_cols * 5, n_rows * 4))
    for i, face_id in enumerate(unique_faces):
        ax = fig2.add_subplot(n_rows, n_cols, i + 1)
        face_data = results[results['face_id'] == face_id]['d']
        face_stats = stats_df[stats_df['face_id'] == face_id].iloc[0]
        
        # Plot Histogram (Zoomed)
        sns.histplot(face_data, kde=True, ax=ax, color='skyblue', alpha=0.4)
        
        # Lines
        ax.axvline(0, color='grey', linestyle='--', linewidth=2, label='Null')
        ax.axvline(face_stats['mean'], color='red', linestyle='-', linewidth=2, label=f"Mean")
        
        # Calculate threshold again
        df = face_stats['n_subjects'] - 1
        if df > 0:
            t_crit = sp_stats.t.ppf(0.975, df)
            threshold = t_crit * face_stats['sem']
            ax.axvline(threshold, color='green', linestyle=':', linewidth=1.5, label='Threshold')
            if face_stats['mean'] < 0: ax.axvline(-threshold, color='green', linestyle=':')

        # Zoom in: Set x-limits around [0, Mean] with some padding
        padding = max(abs(face_stats['mean']), threshold if not np.isnan(threshold) else 0) * 0.5
        x_min = min(0, face_stats['mean'], -threshold if not np.isnan(threshold) else 0) - padding
        x_max = max(0, face_stats['mean'], threshold if not np.isnan(threshold) else 0) + padding
        ax.set_xlim(x_min, x_max)
        
        ax.set_title(f"ZOOM: Face {face_id}", fontweight='bold')
        ax.set_xlabel('D-value (degrees)')
        ax.set_ylabel('Frequency (Count)')
        
    plt.tight_layout()
    plt.show()

    # --- 3. Summary Bar Charts ---
    print("\n--- Generating Summary Stats ---")
    fig3, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # Mean D-value with SEM
    axes[0].bar(stats_df['face_id'].astype(str), stats_df['mean'], 
                yerr=stats_df['sem'].fillna(0), capsize=5, color='teal', alpha=0.7)
    axes[0].axhline(0, color='black', linewidth=1)
    axes[0].set_title('Mean D-value per Face (±SEM)', fontweight='bold', fontsize=14)
    axes[0].set_ylabel('D-value (degrees)')

    # P-values
    colors = ['#2ecc71' if p < 0.05 else '#e74c3c' for p in stats_df['p_value']]
    axes[1].bar(stats_df['face_id'].astype(str), stats_df['p_value'], color=colors, alpha=0.8)
    axes[1].axhline(0.05, color='black', linestyle=':', label='p=0.05 Threshold')
    axes[1].set_title('Statistical Significance (P-value)', fontweight='bold', fontsize=14)
    axes[1].set_yscale('log')
    axes[1].set_ylabel('P-value (log scale)')
    axes[1].legend()
    
    plt.tight_layout()
    plt.show()
