# FaceTip Experiment Analysis V3

A reproducible data analysis pipeline for the FaceTip experiment, designed for collaborative analysis in Google Colab.

## 📊 What This Analysis Does

This project analyzes experimental data from the FaceTip study, which investigates how participants perceive and respond to facial stimuli. The V3 analysis pipeline includes:

- **Face ID mapping**: Remaps ID001→ID017 and ID022→ID015
- **Angle validation**: Filters trials with end angles between 3 and 40 degrees
- **Subject exclusion**: Removes subjects with >2 invalid trials for quality control
- **Trial pairing**: Pairs "towards" and "away" trials by face side
- **D-value calculation**: Computes difference scores for statistical analysis
- **Comprehensive visualization**: Generates filtering pipeline and distribution plots

**Expected Results:**
- Initial: 9,426 trials from 293 subjects
- Final: 4,152 valid trials from 135 subjects
- Overall Mean D: 0.1479 (p = 0.2261)

---

## 🚀 Quick Start (Google Colab)

**Perfect for team collaboration!** Run the entire analysis in your browser without installing anything locally.

### Step 1: Open Google Colab
Go to [https://colab.research.google.com/](https://colab.research.google.com/)

### Step 2: Open the Notebook
1. Click **File** → **Open notebook**
2. Select the **GitHub** tab
3. Enter: `dazubanator/data-analysis-urop-v3`
4. Click on `notebooks/FaceTip_Analysis_V3.ipynb`

### Step 3: Run the Analysis
Click **Runtime** → **Run all** to execute the entire pipeline.

The notebook will:
1. Clone this repository
2. Install dependencies
3. Preprocess the raw data
4. Run the V3 analysis
5. Display all visualizations inline

**That's it!** All results will be generated and displayed in the notebook.

---

## 📁 Repository Structure

```
data-analysis-urop-v3/
├── data/
│   ├── raw/                          # Original data files
│   │   └── facetip_data_Nov2025.csv  # Raw experiment data (596 KB)
│   └── processed/                    # Cleaned data (generated, not tracked)
│       └── merged_experiments_cleaned.csv
├── scripts/
│   ├── preprocess_data.py            # Step 1: Clean raw data
│   └── analyze_data_v3.py            # Step 2: Run V3 analysis
├── notebooks/
│   └── FaceTip_Analysis_V3.ipynb     # Google Colab notebook
├── results/                          # Generated visualizations (not tracked)
│   ├── filtering_pipeline.png
│   └── distribution_*.png
├── .gitignore
├── README.md
└── requirements.txt                  # Python dependencies
```

### What's Tracked in Git?
✅ Raw data (`data/raw/`)  
✅ Analysis scripts (`scripts/`)  
✅ Colab notebook (`notebooks/`)  
✅ Documentation (`README.md`, `requirements.txt`)  

❌ Generated files (`data/processed/`, `results/`)  
❌ Legacy V2 files  

---

## 🔄 Adding New Data

When you collect new experimental data:

### Option 1: GitHub Web Interface (Easiest)
1. Go to the repository on GitHub
2. Navigate to `data/raw/`
3. Click **Add file** → **Upload files**
4. Upload your new CSV file (e.g., `facetip_data_Dec2025.csv`)
5. Edit `scripts/preprocess_data.py`:
   ```python
   RAW_DATA_FILE = os.path.join('..', 'data', 'raw', 'facetip_data_Dec2025.csv')
   ```
6. Commit the changes
7. In Google Colab, run `!git pull` and re-run all cells

### Option 2: Local Git (For Advanced Users)
```bash
# Add new data file
cp /path/to/new_data.csv data/raw/

# Update the preprocessing script to point to new file
# Edit scripts/preprocess_data.py

# Commit and push
git add data/raw/new_data.csv scripts/preprocess_data.py
git commit -m "Add December 2025 data"
git push
```

---

## 💻 Local Usage (Optional)

If you prefer to run the analysis on your local machine:

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation
```bash
# Clone the repository
git clone https://github.com/dazubanator/data-analysis-urop-v3.git
cd data-analysis-urop-v3

# Install dependencies
pip install -r requirements.txt
```

### Running the Analysis
```bash
# Step 1: Preprocess raw data
cd scripts
python preprocess_data.py

# Step 2: Run V3 analysis
python analyze_data_v3.py

# Results will be saved to ../results/
```

### View Results
- Filtering pipeline: `results/filtering_pipeline.png`
- Distribution plots: `results/distribution_ID*.png`
- Console output shows all statistics

---

## 📈 Understanding the Results

### Filtering Pipeline
Shows how many trials and subjects remain after each filtering step:
1. **Initial**: All loaded trials
2. **After Angle Rule**: Trials with valid end angles (3-40°)
3. **After Subject Exclusion**: Removed subjects with >2 invalid trials
4. **After Balancing**: Only properly paired trials

### Distribution Plots
For each face ID, you'll see:
- **Full Range**: Complete distribution of D-values
- **Auto-Zoomed**: Focused view around the mean
- **Fixed Zoom**: Standardized -5 to +5 degree view

**Key Elements:**
- **Black line**: Null hypothesis (D = 0)
- **Red dashed line**: Mean D-value
- **Green dotted lines**: α = 0.05 significance thresholds
- **Orange dash-dot lines**: α = 0.10 significance thresholds

### Statistics
- **Mean D**: Average difference between towards/away trials
- **P-value**: Statistical significance (< 0.05 is significant)
- **SEM**: Standard error of the mean
- **Count**: Number of valid trial pairs

---

## 🤝 Collaboration Workflow

### For Team Members
1. **Access the notebook**: Open the Colab notebook from the GitHub link
2. **Run the analysis**: Click "Run all" to reproduce results
3. **Share findings**: Export visualizations or share the Colab link

### For Data Collectors
1. **Upload new data**: Add CSV files to `data/raw/` via GitHub
2. **Update script**: Point preprocessing to the new file
3. **Notify team**: Team members can pull changes and re-run

### For Developers
1. **Clone locally**: `git clone https://github.com/dazubanator/data-analysis-urop-v3.git`
2. **Create branch**: `git checkout -b feature/new-analysis`
3. **Make changes**: Edit scripts or add new analyses
4. **Test locally**: Run scripts to verify changes
5. **Push and PR**: Push branch and create pull request

---

## 🔧 Dependencies

All required packages are listed in `requirements.txt`:
- **pandas** (≥2.0.0): Data manipulation
- **numpy** (≥1.24.0): Numerical computing
- **matplotlib** (≥3.7.0): Plotting
- **seaborn** (≥0.12.0): Statistical visualization
- **scipy** (≥1.10.0): Statistical tests

---

## 📝 Analysis Details

### V3 Rules
1. **Face ID Mapping**: Standardizes face identifiers
2. **End Angle Calculation**: `raw_angle × -1` for left tilt, `raw_angle × 1` for right tilt
3. **Angle Validation**: Keeps only trials where `3 < end_angle < 40`
4. **Subject Exclusion**: Removes subjects with more than 2 angle-invalid trials
5. **Trial Pairing**: 
   - Face Left: Left-Left (towards) paired with Left-Right (away)
   - Face Right: Right-Right (towards) paired with Right-Left (away)
6. **D-Value**: `|end_angle_towards| - |end_angle_away|`

### Quality Control
- Strict angle validation ensures valid measurements
- Subject-level exclusion removes unreliable participants
- Balanced pairing ensures fair comparisons

---

## 📧 Questions or Issues?

If you encounter any problems or have questions:
1. Check that you're using the latest version: `git pull`
2. Verify all dependencies are installed: `pip install -r requirements.txt`
3. Review the Colab notebook output for error messages
4. Contact the repository maintainer

---

**Last Updated**: December 2025  
**Repository**: https://github.com/dazubanator/data-analysis-urop-v3
