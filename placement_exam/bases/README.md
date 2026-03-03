# Placement Exam Data Files

This folder contains the raw and processed data from the Spring 2026 placement exam.

---

## Files

### 1. `raw_google_sheets_export.csv`

**Description**: Direct export from Google Sheets containing all 57 original submissions.

**Source**: https://docs.google.com/spreadsheets/d/1odUDd_3iXa6NDq7bNV0bdes03N7zPIcUzkaqVck7eyk/edit?usp=sharing

**Export Date**: March 2, 2026

**Contents**:
- All form responses from the placement exam
- 57 rows (including 2 duplicates and 1 incomplete submission)
- 31 columns (timestamp, scores, individual question responses, metadata)

**Data Quality Issues**:
- **Duplicates**: 2 students (Bernardo Da Silva Lucas, Bruno dos Santos Lima) submitted twice
- **Incomplete data**: 1 student with missing name/course information
- **Routing mismatch**: 1 student (Laura Martins da Silva) selected different paths on self-assessment vs. routing question

**Use Cases**:
- Item analysis (question-by-question performance)
- Answer choice distribution analysis
- Validation and audit trail
- Post-semester analysis for Version 2.0 calibration

**Columns** (sample):
- `Carimbo de data/hora`: Submission timestamp
- `Pontuação`: Score (e.g., "9 / 25")
- `Experiência com o Idioma`: Self-assessment path (Portuguese)
- `What does "important" mean?`: Q1 response
- ... (all 25 question responses)
- `Endereço de e-mail`: Student email
- `Nome Completo`: Student name
- `Seu curso técnico?`: Technical program

**Important**: This file should NOT be modified. It serves as the authoritative source for all placement exam data.

---

### 2. `curated_student_roster.csv`

**Description**: Cleaned and processed student roster with assigned IDs and tier placements.

**Source**: Processed from `raw_google_sheets_export.csv` with the following transformations:
- Duplicates removed (first submission kept)
- Incomplete records excluded
- Students sorted alphabetically by name
- Unique IDs assigned per course
- Suggested tier assignments calculated

**Record Count**: 54 students (down from 57 raw submissions)

**Columns**:
1. **Course**: Technical program (Biotecnologia, Metrologia, Segurança Cibernética)
2. **ID**: Unique student identifier (3xxx for Biotech, 4xxx for Metrology, 5xxx for CyberSec)
3. **Name**: Student's full name
4. **Email**: Student's email address
5. **Path**: Self-assessment path (A/B/C)
6. **Suggested Tier**: Provisional tier placement based on test score only

**ID Scheme**:
- Biotecnologia: 3001, 3006, 3011, 3016... (increment +5)
- Metrologia: 4001, 4006, 4011, 4016... (increment +5)
- Segurança Cibernética: 5001, 5006, 5011, 5016... (increment +5)

**Tier Assignment Logic**:
- **Path A** (out of 10):
  - 0-7: Tier 1
  - 8-10: Flag (Tier 1 provisional - contact for full test)
- **Path B/C** (out of 25):
  - 0-10: Tier 1
  - 11-15: Tier 2
  - 16-25: Tier 3

**Special Cases**:
- 5 students flagged with "Flag (Tier 1 provisional - contact for full test)" (Path A underestimators)
- These students scored 8-10/10 despite selecting "Never studied English"

**Use Cases**:
- Import into LMS or grade tracking system
- E01 diagnostic exercise deployment
- Final tier assignment (after combining with E01 data)
- Semester-long student tracking

**Important**:
- This file contains **provisional** tier assignments based only on placement test scores (Signal 1)
- Final tier assignments should be made after collecting E01 data (Signal 2) by Week 3 (March 21, 2026)
- Use the three-signal placement matrix from the plan documentation

---

## Data Processing Summary

| Metric | Raw Data | Curated Roster | Change |
|--------|----------|----------------|--------|
| **Total Records** | 57 | 54 | -3 |
| **Duplicates** | 2 | 0 | Removed |
| **Incomplete** | 1 | 0 | Removed |
| **Columns** | 31 | 6 | Simplified |
| **Primary Key** | Email | ID | Added |
| **Sorting** | Timestamp | Alphabetical by Name | Changed |

---

## Data Lineage

```
Google Form (Placement Exam)
    ↓
Google Sheets (Auto-populated)
    ↓ [Manual Export as CSV - March 2, 2026]
raw_google_sheets_export.csv (57 rows, 31 columns)
    ↓ [Python Processing Script]
    - Remove duplicates (keep first submission)
    - Remove incomplete records
    - Sort alphabetically by name
    - Assign unique IDs per course
    - Calculate suggested tier
    ↓
curated_student_roster.csv (54 rows, 6 columns)
```

---

## Related Documentation

- [../docs/PLACEMENT_EXAM_RESULTS_ANALYSIS.md](../docs/PLACEMENT_EXAM_RESULTS_ANALYSIS.md) - Full analysis of exam results
- [../docs/STUDENT_ROSTER_NOTES.md](../docs/STUDENT_ROSTER_NOTES.md) - Detailed roster documentation
- [../docs/ACTION_ITEMS_MARCH_2026.md](../docs/ACTION_ITEMS_MARCH_2026.md) - Action items and next steps
- [../docs/PLAN_FOR_PLACEMENT_EXAM_v1.2.md](../docs/PLAN_FOR_PLACEMENT_EXAM_v1.2.md) - Original exam plan

---

## Version Control

| Version | Date | File | Changes |
|---------|------|------|---------|
| 1.0 | March 2, 2026 | raw_google_sheets_export.csv | Initial export from Google Sheets |
| 1.0 | March 2, 2026 | curated_student_roster.csv | Initial processed roster with 54 students |

---

## Usage Guidelines

### For Data Analysis:

Use **raw_google_sheets_export.csv** when you need:
- Question-by-question performance analysis
- Answer choice distribution
- Item difficulty and discrimination indices
- Validation of scoring logic
- Post-semester calibration for Version 2.0

### For Academic Operations:

Use **curated_student_roster.csv** when you need:
- Student contact information
- Tier assignments for material distribution
- LMS integration
- Grade tracking system setup
- E01 deployment

### Data Privacy:

Both files contain **personally identifiable information (PII)**:
- Student names
- Email addresses
- Academic performance data

**Security Requirements**:
- Do NOT commit these files to public repositories
- Store in secure, access-controlled systems only
- Delete local copies after importing to secure systems
- Follow institutional data privacy policies

---

## Contact

For questions about this data:
- Data collection: See placement exam documentation
- Processing scripts: Check `/tmp/generate_student_roster.py` (archived)
- Analysis results: See documentation files linked above

---

**Last Updated**: March 2, 2026
