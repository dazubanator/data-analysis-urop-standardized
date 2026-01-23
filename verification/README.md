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

**Formula**: `D` = `|Towards Angle| - |Away Angle|` (Signed difference)
*Note: End angles are `Raw Angle * -1` (if left) or `Raw Angle * 1` (if right).*
*Note: We no longer take the outer absolute value. This allows us to see if the bias is Towards (+) or Away (-).*

#### Face ID015 (4 Subjects)

* **User 284**: Towards=11, Away=-13. `D = |11| - |-13|` = `11 - 13` = **-2**
* **User 200**: Towards=-10, Away=9. `D = |-10| - |9|` = `10 - 9` = **1**
* **User 291**: Towards=15, Away=-16. `D = |15| - |-16|` = `15 - 16` = **-1**
* **User 287**: Towards=-25, Away=24. `D = |-25| - |24|` = `25 - 24` = **1**
* **Dataset for ID015**: `[-2, 1, -1, 1]`

#### Face ID017 (3 Subjects)

* **User 143**: Towards=25, Away=-26. `D = |25| - |-26|` = `25 - 26` = **-1**
* **User 87**: Towards=-19, Away=14. `D = |-19| - |14|` = `19 - 14` = **5**
* **User 39**: Towards=15, Away=-14. `D = |15| - |-14|` = `15 - 14` = **1**
* **Dataset for ID017**: `[-1, 5, 1]`

#### Face ID030 (3 Subjects)

* **User 248**: Towards=15, Away=-21. `D = |15| - |-21|` = `15 - 21` = **-6**
* **User 269**: Towards=17, Away=-17. `D = |17| - |-17|` = `17 - 17` = **0**
* **User 279**: Towards=-13, Away=16. `D = |-13| - |16|` = `13 - 16` = **-3**
* **Dataset for ID030**: `[-6, 0, -3]`

---

### 2. Statistics Breakdown (Real Math)

#### **Face ID015** (`[-2, 1, -1, 1]`)

1. **Count (N)**: 4
2. **Sum**: -2 + 1 - 1 + 1 = **-1**
3. **Mean**: Sum / N = -1 / 4 = **-0.25**
4. **Standard Deviation (s)**: **~1.258**
5. **SEM**: **0.629**
6. **T-statistic**: -0.25 / 0.629 = **-0.397**
7. **P-value**: **0.718**

#### **Face ID017** (`[-1, 5, 1]`)

1. **Count (N)**: 3
2. **Mean**: (-1 + 5 + 1) / 3 = 5 / 3 ≈ **1.667**
3. **Std Dev**: **3.215**
4. **SEM**: **1.856**
5. **T-statistic**: **0.898**
6. **P-value**: **0.464**

#### **Face ID030** (`[-6, 0, -3]`)

1. **Count (N)**: 3
2. **Mean**: (-6 + 0 - 3) / 3 = -9 / 3 = **-3.0**
3. **Std Dev**: **3.0**
4. **SEM**: **1.732**
5. **T-statistic**: **-1.732**
6. **P-value**: **0.225**

---

### Global Statistics Check

#### Summary Table

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
| :--- | :--- |
| **End Angle** | `raw_angle × (-1)` if left, `raw_angle × (1)` if right |
| **Angle Valid** | `3 < end_angle < 43` |
| **d-value** | `|end_angle_towards| - |end_angle_away|` (signed difference) |
| **Mean D** | `sum(d_values) / n` |
| **Std Dev** | `sqrt(sum((x - mean)²) / (n - 1))` |
| **SEM** | `std_dev / sqrt(n)` |
| **t-statistic** | `(mean - 0) / SEM` |
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
