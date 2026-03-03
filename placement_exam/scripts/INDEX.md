# Placement Exam Scripts - Complete Index

This folder contains all scripts for creating, validating, analyzing, and processing placement exam data.

---

## Quick Reference

| Script | Purpose | Input | Output | When to Use |
|--------|---------|-------|--------|-------------|
| **Pre-Exam** ||||
| `validate_question_bank.py` | Validate question JSON | `question_bank.json` | Validation report | Before creating form |
| `create_placement_form.py` | Generate Google Form | `question_bank.json` | Google Form URL | Once per semester |
| **Post-Exam** ||||
| `analyze_placement_exam.py` | Statistical analysis | Raw CSV | Console report | After exam completion |
| `create_tier_lists.py` | Generate tier lists | Raw CSV | Formatted lists | For documentation |
| `generate_student_roster.py` | Create LMS roster | Raw CSV | Clean CSV | For LMS import |
| **Automation** ||||
| `run_all_analyses.py` | Run all post-exam scripts | Raw CSV | All outputs | After exam completion |

---

## Script Categories

### 📝 Pre-Exam Scripts (Test Creation)

#### 1. `validate_question_bank.py`
**Purpose**: Validates the question bank JSON file before creating the Google Form.

**Input**: `../bases/question_bank.json`

**What it checks**:
- Schema correctness (all required fields present)
- Exactly one correct answer per question
- No duplicate question IDs
- Proper band distribution (10/8/7 for bands 1/2/3)
- Valid status values (active/retired/draft)
- Valid anchor roles (easy/hard/none)
- Proper path visibility (Path A sees Band 1 only)

**Usage**:
```bash
# Validate default question bank
python3 validate_question_bank.py

# Validate specific file
python3 validate_question_bank.py --bank /path/to/bank.json
```

**Output**: Validation report with errors and warnings

**When to run**: Before running `create_placement_form.py`

---

#### 2. `create_placement_form.py`
**Purpose**: Programmatically creates a Google Form for the placement exam using Google Forms API.

**Input**:
- `../bases/question_bank.json` - Question bank
- `../credentials.json` - Google API credentials
- `../token.json` - OAuth token (created on first run)

**What it does**:
- Creates quiz-mode Google Form
- Implements three-path branching (A/B/C)
- Adds bilingual instructions (Portuguese/English)
- Sets up automatic grading with answer keys
- Configures section routing for Path A students

**Usage**:
```bash
# Create form for current semester
python3 create_placement_form.py

# Create form with specific question bank
python3 create_placement_form.py --bank custom_bank.json --semester Spring2026
```

**Output**:
- Google Form URL
- Form ID for future edits

**When to run**: Once per semester, before distributing to students

**Requirements**:
- Google API credentials (see setup docs)
- `google-auth`, `google-auth-oauthlib`, `google-api-python-client` packages

---

### 📊 Post-Exam Scripts (Analysis & Processing)

#### 3. `analyze_placement_exam.py`
**Purpose**: Comprehensive statistical analysis of placement exam results.

**Input**: `../bases/raw_google_sheets_export.csv`

**What it analyzes**:
- Path distribution (A/B/C percentages)
- Score distributions by path
- Tier placements based on thresholds
- Anchor question performance (Q1 and Q25)
- Per-question difficulty indices
- Duplicate submissions
- Routing mismatches
- Key findings and recommendations

**Output**: Console report with:
- Summary statistics
- Distribution charts (text-based)
- Item analysis
- Identified issues
- Recommendations for next steps

**Usage**:
```bash
python3 analyze_placement_exam.py > /tmp/analysis_report.txt
```

**When to run**: Immediately after exam completion (Week 1)

**Used to create**: `../docs/PLACEMENT_EXAM_RESULTS_ANALYSIS.md`

---

#### 4. `create_tier_lists.py`
**Purpose**: Generate sorted student lists grouped by tier and course.

**Input**: `../bases/raw_google_sheets_export.csv`

**What it does**:
- Removes duplicate submissions
- Assigns students to tiers based on adjusted thresholds
- Groups students by tier, then by course
- Sorts alphabetically within each course
- Identifies "Flag" students (Path A underestimators)

**Output**: Formatted text lists with:
- Student name
- Score (e.g., "12/27")
- Path (A/B/C)
- Email address

**Usage**:
```bash
python3 create_tier_lists.py > tier_lists.txt
```

**When to run**: After initial analysis (Week 1)

**Used in**: Appendix of `../docs/ACTION_ITEMS_MARCH_2026.md`

---

#### 5. `generate_student_roster.py`
**Purpose**: Create clean, curated student roster CSV for LMS integration.

**Input**: `../bases/raw_google_sheets_export.csv`

**What it does**:
- Removes duplicates and incomplete records
- Sorts students alphabetically by name
- Assigns unique IDs per course (increment by 5)
- Calculates suggested tier based on test scores
- Exports 6-column CSV

**Output**:
- `../docs/STUDENT_ROSTER_SPRING_2026.csv`
- Copy saved to `../bases/curated_student_roster.csv`

**Columns**:
1. Course
2. ID (e.g., 3001, 4006, 5011)
3. Name
4. Email
5. Path (A/B/C)
6. Suggested Tier

**Usage**:
```bash
python3 generate_student_roster.py
```

**When to run**: After analysis, before LMS import (Week 1)

---

### 🤖 Automation Scripts

#### 6. `run_all_analyses.py`
**Purpose**: Master script that runs all post-exam analyses in sequence.

**Input**: `../bases/raw_google_sheets_export.csv`

**What it does**:
- Checks prerequisites (files exist)
- Runs all three post-exam scripts in order
- Captures and saves all outputs
- Generates summary report
- Reports success/failure for each script

**Output**:
- Console output with progress indicators
- `/tmp/placement_exam_analysis_output.txt`
- `/tmp/tier_lists_output.txt`
- All CSV files from `generate_student_roster.py`

**Usage**:
```bash
python3 run_all_analyses.py
```

**When to run**: Once after exam completion to generate all documentation at once

**Advantages**:
- One command runs everything
- Consistent execution order
- Error checking between steps
- Summary report for verification

---

## Workflow

### Pre-Exam Workflow
```
1. Develop questions
   ↓
2. Create question_bank.json
   ↓
3. python3 validate_question_bank.py
   ✅ All validations pass
   ↓
4. python3 create_placement_form.py
   ✅ Google Form created
   ↓
5. Test form with dummy data
   ↓
6. Distribute to students
```

### Post-Exam Workflow
```
1. Students complete exam
   ↓
2. Export Google Sheets to CSV
   ↓
3. Save to ../bases/raw_google_sheets_export.csv
   ↓
4. python3 run_all_analyses.py
   ✅ All analyses complete
   ↓
5. Review outputs:
   - PLACEMENT_EXAM_RESULTS_ANALYSIS.md
   - ACTION_ITEMS_MARCH_2026.md (with tier lists)
   - STUDENT_ROSTER_SPRING_2026.csv
   ↓
6. Import roster to LMS
   ↓
7. Deploy E01 diagnostic exercise
   ↓
8. Finalize tier placements (Week 3)
```

---

## File Dependencies

```
../bases/
├── question_bank.json          ← Used by validate & create scripts
├── raw_google_sheets_export.csv ← Used by all post-exam scripts
└── curated_student_roster.csv   ← Generated by generate_student_roster.py

../docs/
├── PLACEMENT_EXAM_RESULTS_ANALYSIS.md  ← Created from analyze output
├── ACTION_ITEMS_MARCH_2026.md          ← Includes tier lists output
└── STUDENT_ROSTER_SPRING_2026.csv      ← Generated by roster script

/tmp/
├── placement_exam_analysis_output.txt  ← Saved by run_all_analyses.py
└── tier_lists_output.txt               ← Saved by run_all_analyses.py
```

---

## Requirements

### Python Version
- Python 3.8 or higher

### Standard Library (No installation needed)
- `csv`
- `statistics`
- `collections`
- `json`
- `subprocess`
- `sys`
- `os`
- `datetime`
- `argparse`
- `pathlib`
- `typing`

### External Packages (For pre-exam scripts only)
```bash
pip install -r requirements.txt
```

Contents of `requirements.txt`:
```
google-auth>=2.23.0
google-auth-oauthlib>=1.1.0
google-auth-httplib2>=0.1.1
google-api-python-client>=2.100.0
```

**Note**: Post-exam analysis scripts require **no external packages** (only standard library).

---

## Common Tasks

### Task: Regenerate all documentation after exam
```bash
cd /Users/emadruga/proj/StudyAmigoApp/placement_exam/scripts
python3 run_all_analyses.py
```

### Task: Validate questions before creating form
```bash
python3 validate_question_bank.py
# If errors, fix question_bank.json and re-run
```

### Task: Create Google Form for new semester
```bash
python3 create_placement_form.py --semester Fall2026
# Follow OAuth flow on first run
# Save the generated Form URL
```

### Task: Generate roster only (skip analysis)
```bash
python3 generate_student_roster.py
```

### Task: Debug a specific script
```bash
# Run with verbose Python output
python3 -v analyze_placement_exam.py

# Check input file exists
ls -lh ../bases/raw_google_sheets_export.csv

# Test with first 10 rows only (modify script temporarily)
head -11 ../bases/raw_google_sheets_export.csv > /tmp/test.csv
# Edit script to use /tmp/test.csv
```

---

## Customization for Future Semesters

### Adjusting Tier Thresholds

If Version 2.0 requires different thresholds, update in:
- `analyze_placement_exam.py` (lines ~60-75)
- `create_tier_lists.py` (lines ~50-65)
- `generate_student_roster.py` (lines ~55-70)

Example change for Tier 3 threshold:
```python
# From: 16-25 = Tier 3
if score >= 18:  # Changed from 16
    tier = 'Tier 3'
```

### Changing ID Scheme

To modify student IDs, edit `generate_student_roster.py`:
```python
# Line ~25: Change base codes
course_codes = {
    'Biotecnologia': ('Biotecnologia', 2000),  # Changed from 3000
    'Metrologia': ('Metrologia', 4000),
    'Segurança Cibernética': ('Segurança Cibernética', 5000)
}

# Line ~80: Change increment
course_counters[course] += 1  # Changed from 5
```

### Adding New Analysis

Create a new script following this template:
```python
#!/usr/bin/env python3
"""Brief description."""

import csv
from collections import Counter

def main():
    # Read raw data
    with open('../bases/raw_google_sheets_export.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Remove duplicates
    seen_emails = set()
    clean_rows = []
    for row in rows:
        email = row.get('Endereço de e-mail', '').lower().strip()
        if email in seen_emails or not email:
            continue
        seen_emails.add(email)
        clean_rows.append(row)

    # Your analysis here
    print(f"Analyzing {len(clean_rows)} students...")

if __name__ == '__main__':
    main()
```

---

## Troubleshooting

### Error: "FileNotFoundError: raw_google_sheets_export.csv"
**Solution**:
```bash
# Check current directory
pwd  # Should be .../placement_exam/scripts

# Check if file exists
ls -lh ../bases/raw_google_sheets_export.csv

# If missing, export from Google Sheets
```

### Error: "ImportError: No module named 'google.auth'"
**Solution**: Install Google API packages (only needed for pre-exam scripts)
```bash
pip install -r requirements.txt
```

### Error: "KeyError: 'Endereço de e-mail'"
**Solution**: Google Sheets export format changed. Check column names:
```bash
head -1 ../bases/raw_google_sheets_export.csv
```

### Warning: "Duplicate submissions detected"
**Expected**: Scripts automatically handle duplicates by keeping first submission.

### No output from `create_placement_form.py`
**Solution**:
1. Check OAuth credentials exist: `ls -lh ../credentials.json`
2. Run again - will prompt for authorization on first run
3. Check for error messages about quota limits

---

## Related Documentation

- [README.md](README.md) - Detailed script documentation
- [../docs/PLAN_FOR_PLACEMENT_EXAM_v1.2.md](../docs/PLAN_FOR_PLACEMENT_EXAM_v1.2.md) - Exam design plan
- [../docs/PLACEMENT_EXAM_RESULTS_ANALYSIS.md](../docs/PLACEMENT_EXAM_RESULTS_ANALYSIS.md) - Analysis results
- [../docs/ACTION_ITEMS_MARCH_2026.md](../docs/ACTION_ITEMS_MARCH_2026.md) - Next steps
- [../bases/README.md](../bases/README.md) - Data files documentation

---

**Last Updated**: March 2, 2026
**Scripts Version**: 1.0
