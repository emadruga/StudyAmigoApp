# Placement Exam Analysis Scripts

This folder contains Python scripts used to analyze the placement exam results and generate documentation and rosters.

---

## Scripts Overview

### 1. `analyze_placement_exam.py`

**Purpose**: Comprehensive analysis of placement exam results, generating statistics and insights.

**Input**: `../bases/raw_google_sheets_export.csv`

**Output**: Console output with complete analysis (used to create `../docs/PLACEMENT_EXAM_RESULTS_ANALYSIS.md`)

**What it does**:
- Calculates path distribution (A/B/C)
- Analyzes score distributions by path
- Identifies tier placements based on thresholds
- Analyzes anchor questions (Q1 and Q25)
- Calculates per-question difficulty indices
- Identifies problematic patterns (duplicates, routing mismatches)
- Generates key findings and recommendations

**Key functions**:
- `analyze_placement_exam()`: Main analysis function
- Path classification using dictionary mapping
- Statistical calculations (mean, median, distribution)
- Anchor question validation
- Item difficulty analysis

**Usage**:
```bash
cd /Users/emadruga/proj/StudyAmigoApp/placement_exam/scripts
python3 analyze_placement_exam.py
```

**Requirements**:
- Python 3.x
- Standard library: `csv`, `statistics`, `collections.Counter`, `collections.defaultdict`

---

### 2. `create_tier_lists.py`

**Purpose**: Generate sorted student lists by tier and course for appendix in action items document.

**Input**: `../bases/raw_google_sheets_export.csv`

**Output**: Console output with tier-sorted student lists (appended to `../docs/ACTION_ITEMS_MARCH_2026.md`)

**What it does**:
- Removes duplicate submissions (keeps first)
- Assigns students to tiers based on adjusted thresholds
- Groups students by tier, then by course
- Sorts alphabetically within each course
- Identifies "Flag" students (Path A with 8-10/10)

**Key thresholds**:
- **Path A** (out of 10): 0-7 = Tier 1, 8-10 = Flag
- **Path B/C** (out of 25): 0-10 = Tier 1, 11-15 = Tier 2, 16-25 = Tier 3

**Usage**:
```bash
cd /Users/emadruga/proj/StudyAmigoApp/placement_exam/scripts
python3 create_tier_lists.py
```

---

### 3. `generate_student_roster.py`

**Purpose**: Create curated student roster CSV with unique IDs for LMS integration.

**Input**: `../bases/raw_google_sheets_export.csv`

**Output**: `../docs/STUDENT_ROSTER_SPRING_2026.csv` (also copied to `../bases/curated_student_roster.csv`)

**What it does**:
- Removes duplicates and incomplete records
- Sorts students alphabetically by name
- Assigns unique IDs per course (increment by 5)
- Calculates suggested tier based on test scores
- Exports clean 6-column CSV

**ID Scheme**:
- Biotecnologia: 3001, 3006, 3011, 3016... (base: 3000)
- Metrologia: 4001, 4006, 4011, 4016... (base: 4000)
- Segurança Cibernética: 5001, 5006, 5011, 5016... (base: 5000)

**Output columns**:
1. Course
2. ID
3. Name
4. Email
5. Path (A/B/C)
6. Suggested Tier

**Usage**:
```bash
cd /Users/emadruga/proj/StudyAmigoApp/placement_exam/scripts
python3 generate_student_roster.py
```

---

## Data Flow

```
Google Sheets Export
        ↓
../bases/raw_google_sheets_export.csv
        ↓
        ├─→ analyze_placement_exam.py
        │   └─→ Console output → ../docs/PLACEMENT_EXAM_RESULTS_ANALYSIS.md
        │
        ├─→ create_tier_lists.py
        │   └─→ Console output → Appended to ../docs/ACTION_ITEMS_MARCH_2026.md
        │
        └─→ generate_student_roster.py
            └─→ ../docs/STUDENT_ROSTER_SPRING_2026.csv
                └─→ ../bases/curated_student_roster.csv
```

---

## Common Configuration

All scripts share these configuration elements:

### Path Mapping (Self-Assessment to A/B/C)
```python
path_mapping = {
    'Nunca estudei inglês e não tenho contato com o idioma. (I have never studied English and I have no contact with the language.)': 'Path A',
    'Estudei inglês no ensino médio (escola pública ou particular), mas não me considero fluente. (I studied English in high school, but I don\'t consider myself fluent.)': 'Path B',
    'Já fiz curso de inglês ou me considero intermediário/avançado. (I have taken English courses or I consider myself intermediate/advanced.)': 'Path C'
}
```

### Tier Assignment Thresholds (Adjusted Version 1.0)
```python
# Path A (out of 10)
if score <= 4:
    tier = 'Tier 1 (confirmed)'
elif score <= 7:
    tier = 'Tier 1 (provisional)'
else:  # 8-10
    tier = 'Flag (underestimator)'

# Path B/C (out of 25)
if score <= 10:
    tier = 'Tier 1'
elif score <= 15:
    tier = 'Tier 2'
else:  # 16-25
    tier = 'Tier 3'
```

### Duplicate Handling
All scripts remove duplicates by keeping the first submission when multiple entries share the same email address:
```python
seen_emails = set()
for row in rows:
    email = row.get('Endereço de e-mail', '').lower().strip()
    if email in seen_emails:
        continue
    seen_emails.add(email)
    # Process row...
```

---

## Running All Scripts

To regenerate all analyses and rosters from scratch:

```bash
cd /Users/emadruga/proj/StudyAmigoApp/placement_exam/scripts

# 1. Run comprehensive analysis (generates insights for RESULTS_ANALYSIS.md)
python3 analyze_placement_exam.py > /tmp/analysis_output.txt

# 2. Generate tier lists (for ACTION_ITEMS appendix)
python3 create_tier_lists.py > /tmp/tier_lists_output.txt

# 3. Generate student roster (for LMS import)
python3 generate_student_roster.py
```

Or use the master script:
```bash
python3 run_all_analyses.py
```

---

## Customization for Future Semesters

### Adjusting Tier Thresholds

If post-semester analysis (Section 9.2 of plan) indicates threshold adjustments are needed for Version 2.0:

1. Edit the tier assignment logic in all three scripts
2. Update the thresholds in the comments
3. Re-run the scripts to regenerate outputs

**Example**: To change Tier 3 threshold from 16/25 to 18/25:
```python
# Path B/C (out of 25) - VERSION 2.0 THRESHOLDS
if score <= 10:
    tier = 'Tier 1'
elif score <= 17:  # Changed from 15
    tier = 'Tier 2'
else:  # 18-25 (changed from 16-25)
    tier = 'Tier 3'
```

### Changing ID Scheme

To modify the student ID pattern, edit `generate_student_roster.py`:

```python
# Current scheme (increment by 5)
course_counters[course] += 5

# To increment by 1 instead:
course_counters[course] += 1

# To change base codes (e.g., Biotech = 2xxx instead of 3xxx):
course_codes = {
    'Biotecnologia': ('Biotecnologia', 2000),  # Changed from 3000
    'Metrologia': ('Metrologia', 4000),
    'Segurança Cibernética': ('Segurança Cibernética', 5000)
}
```

---

## Adding New Analyses

To add a new analysis script:

1. Create a new `.py` file in this directory
2. Import the raw CSV from `../bases/raw_google_sheets_export.csv`
3. Follow the duplicate-handling pattern shown above
4. Document the script in this README
5. Add it to `run_all_analyses.py` if it should run automatically

**Template**:
```python
#!/usr/bin/env python3
"""
Brief description of what this script does.
"""

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

## Version History

| Version | Date | Scripts | Changes |
|---------|------|---------|---------|
| 1.0 | March 2, 2026 | All 3 scripts | Initial creation for Spring 2026 placement exam |

---

## Dependencies

All scripts use **Python 3 standard library only**:
- `csv` - CSV file reading/writing
- `statistics` - Mean, median calculations
- `collections.Counter` - Frequency counting
- `collections.defaultdict` - Grouped data structures

No external packages (pandas, numpy, etc.) are required.

---

## Error Handling

### Common Issues

1. **FileNotFoundError**: Raw CSV not found
   - **Solution**: Ensure `raw_google_sheets_export.csv` exists in `../bases/`
   - Run from correct directory: `/Users/emadruga/proj/StudyAmigoApp/placement_exam/scripts`

2. **KeyError**: Column name not found
   - **Cause**: Google Sheets export format changed
   - **Solution**: Check CSV headers match expected column names

3. **ValueError**: Score parsing fails
   - **Cause**: Malformed score string (not "X / Y" format)
   - **Solution**: Scripts include try/except blocks to handle gracefully

### Debugging

To debug issues:
```bash
# Check if input file exists
ls -lh ../bases/raw_google_sheets_export.csv

# Check CSV structure
head -2 ../bases/raw_google_sheets_export.csv

# Run with Python verbose mode
python3 -v analyze_placement_exam.py

# Check Python version
python3 --version  # Should be 3.8+
```

---

## Related Documentation

- [../docs/PLACEMENT_EXAM_RESULTS_ANALYSIS.md](../docs/PLACEMENT_EXAM_RESULTS_ANALYSIS.md) - Analysis output
- [../docs/ACTION_ITEMS_MARCH_2026.md](../docs/ACTION_ITEMS_MARCH_2026.md) - Includes tier lists
- [../docs/STUDENT_ROSTER_NOTES.md](../docs/STUDENT_ROSTER_NOTES.md) - Roster documentation
- [../docs/PLAN_FOR_PLACEMENT_EXAM_v1.2.md](../docs/PLAN_FOR_PLACEMENT_EXAM_v1.2.md) - Original plan
- [../bases/README.md](../bases/README.md) - Data files documentation

---

**Last Updated**: March 2, 2026
