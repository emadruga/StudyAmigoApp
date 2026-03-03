# Student Roster Notes - Spring 2026

**Related File**: [STUDENT_ROSTER_SPRING_2026.csv](STUDENT_ROSTER_SPRING_2026.csv)

---

## Overview

This roster contains **54 students** across three technical programs who completed the placement exam in February-March 2026.

---

## ID Scheme

Student IDs follow this pattern:

| Course | ID Range | Starting ID | Increment |
|--------|----------|-------------|-----------|
| **Biotecnologia** | 3001-3056 | 3001 | +5 |
| **Metrologia** | 4001-4106 | 4001 | +5 |
| **Segurança Cibernética** | 5001-5096 | 5001 | +5 |

**Examples**:
- First Biotecnologia student: 3001
- Second Biotecnologia student: 3006
- Third Biotecnologia student: 3011

---

## CSV Columns

| Column | Description |
|--------|-------------|
| **Course** | Student's technical program (Biotecnologia, Metrologia, or Segurança Cibernética) |
| **ID** | Unique student identifier (see ID scheme above) |
| **Name** | Student's full name (sorted alphabetically) |
| **Email** | Student's email address |
| **Path** | Self-assessment path chosen: **A** = Never studied English, **B** = High school English, **C** = Intermediate/Advanced |
| **Suggested Tier** | Preliminary tier placement based on placement test score only (Signal 1) |

---

## Tier Assignments

### Current Status: **PROVISIONAL**

These tier assignments are based **only** on the placement test (Signal 1). Final tier assignments should be made after collecting E01 data (Signal 2) by **Week 3 (March 21, 2026)**.

### Tier Definitions:

- **Tier 1: Foundation** - Students with minimal English exposure or low test scores (Path A: 0-7/10, Path B/C: 0-10/25)
- **Tier 2: Developing** - Students with high school English background and medium test scores (Path B/C: 11-15/25)
- **Tier 3: Expanding** - Students with advanced proficiency and high test scores (Path B/C: 16-25/25)
- **Flag (Tier 1 provisional - contact for full test)** - Path A students who scored 8-10/10, indicating potential underestimation

### Current Distribution:

| Tier | Count | Percentage |
|------|-------|------------|
| Tier 1 | 30 | 55.6% |
| Tier 2 | 19 | 35.2% |
| Tier 3 | 0 | 0% |
| Flag | 5 | 9.3% |

---

## Flagged Students (Underestimators)

The following **5 students** selected Path A ("Never studied English") but scored **8-10/10** on Band 1, suggesting they have more English knowledge than they self-reported:

1. **Isabel da Silva Peixoto** (Metrologia) - ID: 4036 - isabeldasilvapeixoto@gmail.com
2. **José Augusto** (Segurança Cibernética) - ID: 5041 - joseaugustofreire381@gmail.com
3. **João Ricardo Rocha De Carvalho** (Segurança Cibernética) - ID: 5046 - joaoricardocarvalho4@gmail.com
4. **Laura Martins da Silva** (Metrologia) - ID: 4066 - lauramartinssilva2010@gmail.com
5. **Luiz Henrique Silva de Carvalho** (Segurança Cibernética) - ID: 5061 - bzkluizzin@gmail.com

### Action Required:

- **Contact these students** and offer them the option to take the full test (Bands 2 + 3)
- If they decline, place them provisionally in **Tier 1** but monitor E01 performance closely
- If E01 retention rate is ≥50% (medium performance), consider moving to **Tier 2**

See [ACTION_ITEMS_MARCH_2026.md](ACTION_ITEMS_MARCH_2026.md) for the email template.

---

## Data Quality Notes

### Duplicates Removed:

2 students submitted the test twice. Only the **first submission** was kept:

1. **Bernardo Da Silva Lucas** (bernardoslucas2009@gmail.com) - Used first submission: 12/27
2. **Bruno dos Santos Lima** (bsantos1460@gmail.com) - Kept single submission: 8/27

### Missing Data:

- 1 student in the raw data had missing name/course information and was excluded from this roster
- Final student count: **54** (down from 57 raw submissions)

---

## Usage Guidelines

### For Academic Tracking:

1. Use the **ID** as the primary key for all systems (LMS, grade tracking, E01 data collection)
2. Cross-reference with E01 performance data using **Email** as the secondary key
3. Update **Suggested Tier** to **Final Tier** after Week 3 (March 21)

### For E01 Deployment:

1. Import this roster into the E01 tracking system
2. Assign tier-specific reading materials based on **Suggested Tier**
3. Track the following metrics per student:
   - Retention rate (% of cards marked "Good" or "Easy")
   - Average review time per card (seconds)
   - Ease distribution

### For Final Placement (Week 3):

1. Apply the three-signal placement matrix from [PLAN_FOR_PLACEMENT_EXAM_v1.2.md](PLAN_FOR_PLACEMENT_EXAM_v1.2.md), Section 6.3
2. Combine:
   - **Signal 0**: Path (from this roster)
   - **Signal 1**: Placement test score (from this roster)
   - **Signal 2**: E01 retention rate & review time (from E01 system)
3. Update the roster with **Final Tier** assignments
4. Notify students of their final tier placement

---

## Path Distribution

| Path | Description | Count | Percentage |
|------|-------------|-------|------------|
| **A** | Never studied English | 9 | 16.7% |
| **B** | High school English | 36 | 66.7% |
| **C** | Intermediate/Advanced | 9 | 16.7% |

**Note**: Path B is the largest group, as expected for students with high school English background in Brazilian public education.

---

## Course Distribution

| Course | Count | Percentage |
|--------|-------|------------|
| **Biotecnologia** | 12 | 22.2% |
| **Metrologia** | 22 | 40.7% |
| **Segurança Cibernética** | 20 | 37.0% |

---

## Related Documents

- [PLACEMENT_EXAM_RESULTS_ANALYSIS.md](PLACEMENT_EXAM_RESULTS_ANALYSIS.md) - Comprehensive analysis of exam results
- [ACTION_ITEMS_MARCH_2026.md](ACTION_ITEMS_MARCH_2026.md) - Action items and student lists by tier
- [PLAN_FOR_PLACEMENT_EXAM_v1.2.md](PLAN_FOR_PLACEMENT_EXAM_v1.2.md) - Original exam design plan
- [READING_MATERIAL_METHODOLOGY.md](../../server/docs/READING_MATERIAL_METHODOLOGY.md) - Tier system and reading material design

---

**Last Updated**: March 2, 2026
**Status**: Provisional tier assignments (awaiting E01 data for final placement)
