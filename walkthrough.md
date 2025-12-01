# Experiment Analysis Results

## Summary
The analysis processed 9491 initial trials from 295 subjects. 
- **Angle Rule**: 6764 trials were valid after applying the angle rule (3° < angle < 40°).
- **Balancing**: Using the provided balancing logic (pairing by Tip Direction), 409 additional trials were removed.
- **Final Valid Trials**: 6355 trials remained for analysis.

> [!NOTE]
> The count of **6764** matches the number of trials valid by the Angle Rule *before* balancing. The final count of **6355** reflects the dataset after strictly applying the requested balancing algorithm.

## Statistics
- **Initial Trials**: 9491
- **Invalidated by Angle Rule**: 2727
- **Valid after Angle Rule**: 6764
- **Invalidated by Balancing**: 409
- **Final Valid Trials**: 6355
- **Initial Subjects**: 295
- **Subjects Remaining**: 239
- **Subjects Invalidated**: 56
- **Average D Value**: 0.0327
- **P-value (vs 0)**: 0.7478 (Not significant)

### Statistics per Face ID
| Face ID | Count | Mean D | Std Dev | SEM | P-value |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **ID015** (Weak) | 1584 | -0.1086 | 5.7392 | 0.1442 | 0.4516 |
| **ID017** (Scary) | 804 | 0.2687 | 5.6720 | 0.2000 | 0.1796 |
| **ID030** (Scary) | 788 | 0.0761 | 5.8047 | 0.2068 | 0.7128 |

## Visualizations

### User vs Number of Valid D Values
````carousel
![User vs N Valid](/C:/Users/dazub/.gemini/antigravity/brain/59a98b4f-dc61-4d34-84dc-d79eb42c9eb0/scatter_user_n_valid.png)
<!-- slide -->
![Distribution of N Valid](/C:/Users/dazub/.gemini/antigravity/brain/59a98b4f-dc61-4d34-84dc-d79eb42c9eb0/dist_n_valid.png)
````

### User vs Mean D Value
````carousel
![User vs Mean D](/C:/Users/dazub/.gemini/antigravity/brain/59a98b4f-dc61-4d34-84dc-d79eb42c9eb0/scatter_user_mean_D.png)
<!-- slide -->
![Distribution of Mean D](/C:/Users/dazub/.gemini/antigravity/brain/59a98b4f-dc61-4d34-84dc-d79eb42c9eb0/dist_mean_D.png)
<!-- slide -->
![User vs Mean D (Zoomed +/- 3)](/C:/Users/dazub/.gemini/antigravity/brain/59a98b4f-dc61-4d34-84dc-d79eb42c9eb0/scatter_user_mean_D_zoomed.png)
<!-- slide -->
![Distribution of Mean D (Zoomed +/- 3)](/C:/Users/dazub/.gemini/antigravity/brain/59a98b4f-dc61-4d34-84dc-d79eb42c9eb0/dist_mean_D_zoomed.png)
````

### N Valid vs Mean D Value
````carousel
![N Valid vs Mean D](/C:/Users/dazub/.gemini/antigravity/brain/59a98b4f-dc61-4d34-84dc-d79eb42c9eb0/scatter_n_valid_vs_mean_D.png)
<!-- slide -->
![Joint Distribution (Bin 0.25)](/C:/Users/dazub/.gemini/antigravity/brain/59a98b4f-dc61-4d34-84dc-d79eb42c9eb0/dist_joint_n_valid_mean_D.png)
<!-- slide -->
![Joint Distribution (Zoomed +/- 3)](/C:/Users/dazub/.gemini/antigravity/brain/59a98b4f-dc61-4d34-84dc-d79eb42c9eb0/dist_joint_n_valid_mean_D_zoomed.png)
````

### Distribution of Mean D Value (Per Face ID)
````carousel
![Face ID015](/C:/Users/dazub/.gemini/antigravity/brain/59a98b4f-dc61-4d34-84dc-d79eb42c9eb0/dist_mean_D_ID015.png)
<!-- slide -->
![Face ID017](/C:/Users/dazub/.gemini/antigravity/brain/59a98b4f-dc61-4d34-84dc-d79eb42c9eb0/dist_mean_D_ID017.png)
<!-- slide -->
![Face ID030](/C:/Users/dazub/.gemini/antigravity/brain/59a98b4f-dc61-4d34-84dc-d79eb42c9eb0/dist_mean_D_ID030.png)
````
