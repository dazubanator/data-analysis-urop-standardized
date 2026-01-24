import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def plot_results(results, stats_df):
    """
    Generates per-face D-value distributions and summary statistics plots.
    
    Args:
        results (pd.DataFrame): DataFrame containing 'face_id' and 'd' values for each pair.
        stats_df (pd.DataFrame): DataFrame containing aggregated stats per face.
    """
    if stats_df.empty:
        print("No valid data to visualize.")
        return

    unique_faces = sorted(results['face_id'].unique())
    n_faces = len(unique_faces)
    
    # Set styling
    sns.set_theme(style="whitegrid", palette="muted")
    
    # 1. Per-Face Distributions
    n_cols = min(3, n_faces)
    n_rows = (n_faces + n_cols - 1) // n_cols
    
    fig1 = plt.figure(figsize=(n_cols * 5, n_rows * 4))
    for i, face_id in enumerate(unique_faces):
        ax = fig1.add_subplot(n_rows, n_cols, i + 1)
        face_data = results[results['face_id'] == face_id]['d']
        face_stats = stats_df[stats_df['face_id'] == face_id].iloc[0]
        
        sns.histplot(face_data, kde=True, ax=ax, color='skyblue', alpha=0.6)
        
        # Reference lines
        ax.axvline(0, color='grey', linestyle='--', label='Null (0°)')
        ax.axvline(face_stats['mean'], color='red', linestyle='-', label=f"Mean: {face_stats['mean']:.2f}°")
        
        # Significance threshold (p=0.05) visualization is indirect on the distribution, 
        # but we can annotate it.
        
        # Formatting
        title = f"Face {face_id} (n={int(face_stats['n_subjects'])})\n"
        title += f"p={face_stats['p_value']:.4f} {'*' if face_stats['p_value'] < 0.05 else '(ns)'}"
        ax.set_title(title, fontweight='bold')
        ax.set_xlabel('D-value (degrees)')
        if i == 0: ax.legend()
        
    plt.tight_layout()
    plt.show()

    # 2. Summary Bar Charts
    fig2, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # Mean D-value with SEM
    axes[0].bar(stats_df['face_id'].astype(str), stats_df['mean'], 
                yerr=stats_df['sem'].fillna(0), capsize=5, color='teal', alpha=0.7)
    axes[0].axhline(0, color='black', linewidth=1)
    axes[0].set_title('Mean D-value per Face (±SEM)', fontweight='bold', fontsize=14)
    axes[0].set_ylabel('D-value (degrees)', fontsize=12)

    # P-values
    colors = ['#2ecc71' if p < 0.05 else '#e74c3c' for p in stats_df['p_value']]
    axes[1].bar(stats_df['face_id'].astype(str), stats_df['p_value'], color=colors, alpha=0.8)
    axes[1].axhline(0.05, color='black', linestyle=':', label='p=0.05 Threshold')
    axes[1].set_title('Statistical Significance (P-value)', fontweight='bold', fontsize=14)
    axes[1].set_yscale('log')
    axes[1].set_ylabel('P-value (log scale)', fontsize=12)
    axes[1].legend()
    
    plt.tight_layout()
    plt.show()
