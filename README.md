# Data Analysis - UROP Project

## File Organization Guide

This directory contains multiple versions of the experiment analysis. Files are organized by version number for easy identification.

---

## Analysis Versions

### Version 2 (V2)
**Files:**
- `analyze_data_v2.py` - Main analysis script for V2
- `create_summary_visualization_v2.py` - Creates summary visualizations
- `walkthrough_v2.md` - Markdown walkthrough
- `walkthrough_v2.html` - **HTML walkthrough with embedded images** ⭐
- `output_v2/` - All V2 output graphs and visualizations

**Key Features:**
- Angle validation: 3 < end_angle < 40 degrees
- Pairing by Face Side
- No subject-level exclusion
- **Results:** 5,910 valid trials, 237 subjects, Mean D=0.0751, p=0.4955

---

### Version 3 (V3)
**Files:**
- `analyze_data_v3.py` - Main analysis script for V3
- `walkthrough_v3.html` - **HTML walkthrough with embedded images** ⭐
- `output_v3/` - All V3 output graphs and visualizations
- `analysis_v3/` - Original V3 development directory

**Key Features:**
- Face ID mapping: ID001→ID017, ID022→ID015
- Angle validation: 3 < end_angle < 40 degrees
- **NEW:** Subject exclusion rule (>2 invalid trials)
- Pairing by Face Side
- **Results:** 4,152 valid trials, 135 subjects, Mean D=0.1479, p=0.2261

---

## Diagnostic & Investigation Scripts

- `diagnose_balancing.py` - Diagnoses balancing issues in trial pairing
- `find_wrong_direction.py` - Identifies potential wrong-direction tilts
- `users_wrong_direction.py` - Analyzes users with wrong-direction errors
- `investigate_id017_change.py` - Investigates changes in ID017 results

---

## Data Files

- `facetip_data_Nov2025.csv` - Original raw data
- `merged_experiments_cleaned.csv` - Cleaned and merged data for V3

---

## How to View Walkthroughs

### Easy Way (Recommended)
Open the HTML files in your browser - all graphs are embedded:
- `walkthrough_v2.html` - V2 analysis with all visualizations
- `walkthrough_v3.html` - V3 analysis with all visualizations

### Markdown Way
Open the .md files in VS Code and use the preview feature (Ctrl+Shift+V)

---

## Quick Comparison: V2 vs V3

| Metric | V2 | V3 |
|--------|----|----|
| **Initial Trials** | 9,491 | 9,426 |
| **Initial Subjects** | 295 | 293 |
| **Subject Exclusion** | None | 158 subjects (>2 invalid trials) |
| **Final Valid Trials** | 5,910 | 4,152 |
| **Final Subjects** | 237 | 135 |
| **Overall Mean D** | 0.0751 | 0.1479 |
| **Overall P-value** | 0.4955 | 0.2261 |
| **ID017 P-value** | 0.0592 | 0.0880 |

**Key Insight:** V3's stricter quality control (subject exclusion) resulted in:
- Fewer subjects but higher data quality
- Slightly stronger overall effect (though still not significant)
- More consistent results per face ID

---

## Running the Analyses

### V2
```powershell
python analyze_data_v2.py
python create_summary_visualization_v2.py
```

### V3
```powershell
python analyze_data_v3.py
```

---

## Output Directories

- `output_v2/` - Contains all V2 visualizations (distributions, scatter plots, summary)
- `output_v3/` - Contains all V3 visualizations (filtering pipeline, distributions)

---

**Last Updated:** November 26, 2025
