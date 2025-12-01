# Implementation Plan - Experiment Data Analysis

## Goal Description
Analyze experiment data (`facetip_data_Nov2025.csv`) by cleaning raw angles, applying validation rules, balancing trials based on specific pairing logic, and calculating D-values and statistics.

## User Review Required
> [!IMPORTANT]
> **Pairing Logic Change**: The previous script appeared to pair by Tip Direction. The new logic will pair by **Face Direction** (Face Side) as explicitly requested ("face direction is left... towards... and face direction is left... away").

> [!NOTE]
> **Angle Cleaning**: Raw angles will be multiplied by -1 if tilt is left, and 1 if tilt is right. Validity is strictly `3 < corrected_angle < 40`.

## Proposed Changes

### Analysis Script
#### [NEW] [analyze_data_v2.py](file:///c:/Users/dazub/.gemini/antigravity/scratch/experiment_analysis/analyze_data_v2.py)
- **Data Loading**: Load CSV. Filter for `sightType == 'sighted'`.
- **Cleaning**:
    - Create `end_angle`:
        - If `tip_direction` == 'left': `raw_angle * -1`
        - If `tip_direction` == 'right': `raw_angle * 1`
- **Validation**:
    - `valid_angle` = `(end_angle > 3) & (end_angle < 40)`
- **Balancing (Pairing)**:
    - Group by `[user_number, face_id, tubeTypeIndex]`.
    - Within each group, identify two distinct pairs based on **Face Side**:
        1.  **Face Left Pair**: Face Left + Tilt Left (Towards) vs. Face Left + Tilt Right (Away).
        2.  **Face Right Pair**: Face Right + Tilt Right (Towards) vs. Face Right + Tilt Left (Away).
    - **Invalidation Rule**: If *either* trial in a specific pair (e.g., the LL trial) is invalid (due to angle rule), the *entire pair* (LL and LR) is invalidated. The other pair (RR and RL) for that tube type remains valid unless one of its trials is also invalid.
- **D-Value Calculation**:
    - For each valid pair: `D = abs(Angle_Towards) - abs(Angle_Away)`
    - Max possible D-values per person: 16 (2 faces * 4 tubes * 2 pairs).
- **Aggregation**:
    - Calculate Mean D per user.
    - Calculate Grand Mean D and P-value (t-test vs 0).
    - Counts: Initial, Invalidated (Angle), Invalidated (Balancing), Valid Remaining.
    - Subject Counts.
- **Plotting**:
    - Histogram of all valid D values ("merged distribution").
    - Scatter of N valid vs Mean D per user (or User vs Mean D).

## Verification Plan

### Automated Tests
- Run `python analyze_data_v2.py`
- Check output for:
    - "Initial trials" count.
    - "Trials invalidated by angle rule" count.
    - "Trials removed by balancing" count.
    - "Average D value".
    - "P-value".
- Verify max 16 D values per user (check the code prints this or inspect the dataframe).
- Verify the pairing logic by inspecting a small sample of the dataframe in the output or via a temporary print.
