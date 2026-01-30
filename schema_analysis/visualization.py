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
    
    # --- 1. Calculate Global Limits for Standardization ---
    
    # Global X limits
    all_d = results['d']
    min_d, max_d = all_d.min(), all_d.max()
    # Add 10% padding
    x_range = max_d - min_d
    x_min_global = min_d - (x_range * 0.1)
    x_max_global = max_d + (x_range * 0.1)
    
    # Global Y limits (Max Frequency)
    # We need to compute histograms to find the max frequency peak across all faces
    max_freq_global = 0
    bin_width = 2 # Fixed bin width in degrees
    
    for face_id in unique_faces:
        face_data = results[results['face_id'] == face_id]['d']
        if len(face_data) > 0:
            # Calculate histogram bins using numpy to find max counts
            # Create bins covering the range
            bins = np.arange(np.floor(face_data.min()), np.ceil(face_data.max()) + bin_width, bin_width)
            counts, _ = np.histogram(face_data, bins=bins)
            current_max = counts.max() if len(counts) > 0 else 0
            if current_max > max_freq_global:
                max_freq_global = current_max
                
    y_max_global = max_freq_global * 1.1 # Add 10% padding
    
    print(f"Global Standardization: X range [{x_min_global:.1f}, {x_max_global:.1f}], Y max {y_max_global:.1f}, Bin Width {bin_width}")

    # --- 2. Calculate Global Zoom Limits ---
    # We want a zoom window that fits "Null (0)" and "Mean" + padding for ALL faces.
    # Ideally, we find the min/max of these "interest points" across all faces and add padding.
    
    zoom_min_candidates = []
    zoom_max_candidates = []
    
    for face_id in unique_faces:
        face_stats = stats_df[stats_df['face_id'] == face_id].iloc[0]
        mean = face_stats['mean']
        
        # Calculate threshold for reference
        df = face_stats['n_subjects'] - 1
        threshold = np.nan
        if df > 0:
            t_crit = sp_stats.t.ppf(0.975, df)
            threshold = t_crit * face_stats['sem']
            
        # Interest points for this face: 0, Mean, +/- Threshold
        points = [0, mean]
        if not np.isnan(threshold):
            points.append(mean + threshold) # Upper bound of CI
            points.append(mean - threshold) # Lower bound of CI
            # Also include the significance threshold lines themselves if relevant
            points.append(threshold)
            points.append(-threshold)
            
        zoom_min_candidates.append(min(points))
        zoom_max_candidates.append(max(points))
        
    # Find global min/max for zoom
    # If no data, default to [-1, 1]
    z_min_raw = min(zoom_min_candidates) if zoom_min_candidates else -1
    z_max_raw = max(zoom_max_candidates) if zoom_max_candidates else 1
    
    # Add 20% padding to the total range
    z_range = z_max_raw - z_min_raw
    if z_range == 0: z_range = 2 # Fallback if everything is exactly 0
    
    zoom_x_min = z_min_raw - (z_range * 0.1)
    zoom_x_max = z_max_raw + (z_range * 0.1)
    
    print(f"Global Zoom Window: [{zoom_x_min:.2f}, {zoom_x_max:.2f}]")

    # --- 3. Per-Face Distributions (Overview) ---
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
        # Use fixed binwidth to ensure bars represent same "amount" of degrees across plots
        sns.histplot(face_data, kde=True, ax=ax, color='skyblue', alpha=0.6, binwidth=bin_width)
        
        # Standardize Axes
        ax.set_xlim(x_min_global, x_max_global)
        ax.set_ylim(0, y_max_global)
        
        # Add N to title for clarity on why some histograms might look small total-wise
        total_count = len(face_data)
        
        # Reference lines
        ax.axvline(0, color='grey', linestyle='--', linewidth=2, label='Null (0°)')
        ax.axvline(face_stats['mean'], color='red', linestyle='-', linewidth=2, label=f"Mean: {face_stats['mean']:.2f}°")
        
        if not np.isnan(threshold):
            ax.axvline(threshold, color='green', linestyle=':', linewidth=1.5, label='Sig. Threshold (Mean)')
            if face_stats['mean'] < 0: # If mean is negative, show negative threshold too
                 ax.axvline(-threshold, color='green', linestyle=':', linewidth=1.5)
        
        
        # Formatting
        title = f"Face {face_id} (n={total_count})\n"
        title += f"p={face_stats['p_value']:.4f} {'*' if face_stats['p_value'] < 0.05 else '(ns)'}"
        ax.set_title(title, fontweight='bold')
        ax.set_xlabel('D-value (degrees)')
        ax.set_ylabel('Frequency (D-values)')
        if i == 0: ax.legend(fontsize='small')
        
    plt.tight_layout()
    plt.show()

    # --- 4. Per-Face Distributions (Zoomed View) ---
    print("\n--- Generating Zoomed View (Focus on Null and Mean) ---")
    fig2 = plt.figure(figsize=(n_cols * 5, n_rows * 4))
    for i, face_id in enumerate(unique_faces):
        ax = fig2.add_subplot(n_rows, n_cols, i + 1)
        face_data = results[results['face_id'] == face_id]['d']
        face_stats = stats_df[stats_df['face_id'] == face_id].iloc[0]
        
        # Plot Histogram (Zoomed)
        sns.histplot(face_data, kde=True, ax=ax, color='skyblue', alpha=0.4, binwidth=bin_width)
        
        # Standardize Axes (Y only, X is zoomed)
        ax.set_ylim(0, y_max_global)
        
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

        # Standardize Zoom Scale
        ax.set_xlim(zoom_x_min, zoom_x_max)
        
        ax.set_title(f"ZOOM: Face {face_id}", fontweight='bold')
        ax.set_xlabel('D-value (degrees)')
        ax.set_ylabel('Frequency (D-values)')
        
    plt.tight_layout()
    plt.show()

    # --- 5. Summary Bar Charts ---
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
