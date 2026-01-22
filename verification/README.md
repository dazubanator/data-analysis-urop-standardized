# Verification Guide: Hand Calculation Walkthrough

This guide walks you through manually calculating each step of the data analysis pipeline so you can verify that the scripts work correctly.

## Overview of the Pipeline

The standardized analysis performs these steps:

1. **Load & Merge**: Combine CSV files
2. **Clean**: Remove rows with missing `session_group`
3. **Preprocess**: Rename face IDs and transform angles
4. **Filter**: Apply angle validation (3° < end_angle < 43°) and exclude bad subjects
5. **Balance**: Match trials into pairs
6. **Analyze**: Calculate D-values and statistics

## Dummy Data

We now use a randomized subset of 20 trials (10 pairs) selected from the authentic dataset to verify the pipeline with realistic data.

### Raw Data Snippet (First 5 rows)

| user | face_id | tube | faceSide | tip_dir | raw_angle |
|------|---------|------|----------|---------|-----------|
| 284  | ID015   | 2    | right    | right   | 11        |
| 284  | ID015   | 2    | right    | left    | -13       |
| 248  | ID030   | 1    | right    | right   | 15        |
| 248  | ID030   | 1    | right    | left    | -21       |
| ...  | ...     | ...  | ...      | ...     | ...       |

---

## Step-by-Step Hand Calculations

Here is the "real life math" for calculating the statistics for each Face ID group found in the dummy data.

### 1. Calculate D-values per Subject

**Formula**: `D` = `| |Towards Angle| - |Away Angle| |` (Absolute difference)
*Note: End angles are `Raw Angle * -1` (if left) or `Raw Angle * 1` (if right).*
*Note: We take the absolute value of the difference to ensure D-values are always non-negative.*

**Face ID015 (4 Subjects)**

* **User 284**: Towards=11, Away=-13. `D = | |11| - |-13| |` = `| 11 - 13 |` = `|-2|` = **2**
* **User 200**: Towards=-10, Away=9. `D = | |-10| - |9| |` = `| 10 - 9 |` = `|1|` = **1**
* **User 291**: Towards=15, Away=-16. `D = | |15| - |-16| |` = `| 15 - 16 |` = `|-1|` = **1**
* **User 287**: Towards=-25, Away=24. `D = | |-25| - |24| |` = `| 25 - 24 |` = `|1|` = **1**
* **Dataset for ID015**: `[2, 1, 1, 1]`

**Face ID017 (3 Subjects)**

* **User 143**: Towards=25, Away=-26. `D = | |25| - |-26| |` = `| 25 - 26 |` = `|-1|` = **1**
* **User 87**: Towards=-19, Away=14. `D = | |-19| - |14| |` = `| 19 - 14 |` = `|5|` = **5**
* **User 39**: Towards=15, Away=-14. `D = | |15| - |-14| |` = `| 15 - 14 |` = `|1|` = **1**
* **Dataset for ID017**: `[1, 5, 1]`

**Face ID030 (3 Subjects)**

* **User 248**: Towards=15, Away=-21. `D = | |15| - |-21| |` = `| 15 - 21 |` = `|-6|` = **6**
* **User 269**: Towards=17, Away=-17. `D = | |17| - |-17| |` = `| 17 - 17 |` = `|0|` = **0**
* **User 279**: Towards=-13, Away=16. `D = | |-13| - |16| |` = `| 13 - 16 |` = `|-3|` = **3**
* **Dataset for ID030**: `[6, 0, 3]`

---

### 2. Statistics Breakdown (Real Math)

#### **Face ID015** (`[2, 1, 1, 1]`)

1. **Count (N)**: 4
2. **Sum**: 2 + 1 + 1 + 1 = **5**
3. **Mean**: Sum / N = 5 / 4 = **1.25**
4. **Standard Deviation (s)**:
    * Step A (Differences from Mean):
        * (2 - 1.25)² = (0.75)² = **0.5625**
        * (1 - 1.25)² = (-0.25)² = **0.0625**
        * (1 - 1.25)² = (-0.25)² = **0.0625**
        * (1 - 1.25)² = (-0.25)² = **0.0625**
    * Step B (Sum of Squared Diffs): 0.5625 + 0.0625*3 = **0.75**
    * Step C (Variance): Sum / (N-1) = 0.75 / 3 = **0.25**
    * Step D (Std Dev): √0.25 = **0.5**
5. **SEM**: s / √N = 0.5 / √4 = 0.5 / 2 = **0.25**
6. **T-statistic**: (Mean - 0) / SEM = 1.25 / 0.25 = **5.0**
7. **P-value**: Look up t=5.0, df=3 → **0.015**

#### **Face ID017** (`[1, 5, 1]`)

1. **Count (N)**: 3
2. **Mean**: (1 + 5 + 1) / 3 = 7 / 3 ≈ **2.333**
3. **Standard Deviation (s)**:
    * ((1 - 2.33)² + (5 - 2.33)² + (1 - 2.33)²) / 2
    * ((-1.33)² + (2.67)² + (-1.33)²) / 2
    * (1.77 + 7.11 + 1.77) / 2 ≈ 10.65 / 2 ≈ 5.325
    * √5.325 ≈ **2.308**
4. **SEM**: 2.308 / √3 ≈ **1.332**
5. **T-statistic**: 2.333 / 1.332 ≈ **1.751**
6. **P-value**: Look up t=1.751, df=2 → **0.222**

#### **Face ID030** (`[6, 0, 3]`)

1. **Count (N)**: 3
2. **Mean**: (6 + 0 + 3) / 3 = 9 / 3 = **3.0**
3. **Standard Deviation (s)**:
    * ((6 - 3)² + (0 - 3)² + (3 - 3)²) / 2
    * (9 + 9 + 0) / 2 = 18 / 2 = 9
    * √9 = **3.0**
4. **SEM**: 3.0 / √3 ≈ 3.0 / 1.732 ≈ **1.732**
5. **T-statistic**: 3.0 / 1.732 ≈ **1.732**
6. **P-value**: Look up t=1.732, df=2 → **0.225**

---

### Global Statistics Check

*Verified by script automatically*

* **Mean**: 2.1000
* **Std Dev**: 1.9692
* **T-stat**: 3.3721

The `run_verification.py` script automatically verifies these exact values against the processing pipeline output.

## How to Verify

1. **Run the verification script**:

   ```bash
   python verification/run_verification.py
   ```

2. **Check the output**:
   * Ensure it prints: "✓✓✓ ALL VERIFICATIONS PASSED! ✓✓✓"
   * This confirms that the logic for D-value calculation and statistics matches our established baseline for this random dataset.

---

## Quick Reference: Key Formulas

| Step | Formula |
|------|---------|
| **End Angle** | `raw_angle × (-1)` if left, `raw_angle × (1)` if right |
| **Angle Valid** | `3 < end_angle < 43` |
| **d-value** | `abs( |end_angle_towards| - |end_angle_away| )` (absolute difference) |
| **Mean D** | `sum(d_values) / n` |
| **Std Dev** | `sqrt(sum((x - mean)²) / (n - 1))` |
| **SEM** | `std_dev / sqrt(n)` |
| **t-statistic** | `(mean - 0) / SEM` (The `0` is the Null Hypothesis: assuming no difference) |
| **P-value** | Look up `t` value in T-Distribution Table with `df = n - 1` |

### How to Calculate SEM (Standard Error of the Mean)

**Formula**: `SEM = Std Dev / √n`

**Step-by-step**:

1. Calculate the **Standard Deviation** (see above)
2. Calculate the **square root of n** (where n = number of pairs)
3. **Divide** Std Dev by √n

**Example (Face ID015)**:

* Std Dev = 0.5
* n = 4
* √4 = 2
* SEM = 0.5 / 2 = **0.25**

**IMPORTANT**: Do NOT use Std Dev directly in the T-statistic formula. You MUST calculate SEM first!

### How to Manually "Calculate" P-values

Note: You cannot calculate precise P-values with simple arithmetic. You must use a **T-Distribution Table** (found in any stats textbook or online).

**Use a TWO-TAILED test** (because we're testing if the mean is different from zero in either direction, not just greater than or less than).

1. **Calculate Degrees of Freedom (df)**: `df = n - 1` (where n is the number of pairs).
2. **Find the row**: Look for the row corresponding to your `df`.
3. **Find your t-value**: Look across that row for where your calculated `t-statistic` falls.
4. **Read the P-value**: The column header for that position gives you the P-value. Make sure you're using the **two-tailed** columns.

**If your T-value falls between two table entries**: Your P-value will be **between** the two corresponding P-values. For example, if t=5.0 falls between table entries 4.541 (p=0.02) and 5.841 (p=0.01), then your P-value is between 0.01 and 0.02 (approximately 0.015).

**Formula Key:**

* `x`: An individual d-value for a specific subject/pair.
* `mean`: The **Mean D** for the current group (the average of the d-values you just calculated).
* `n`: The number of **Pairs** (which equals the number of D-values). It is **NOT** the number of trials.
