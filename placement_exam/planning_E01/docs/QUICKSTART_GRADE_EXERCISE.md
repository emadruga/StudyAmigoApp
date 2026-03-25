# QUICKSTART — grade_exercise.py

`grade_exercise.py` computes individual student grades for a single StudyAmigo
exercise (E01, E02, …) using the four-component formula:

```
Grade = 0.25 × V  +  0.25 × C  +  0.30 × Q  +  0.20 × E
```

It reads directly from the SQLite databases (admin + per-user), cross-references
a placement-exam roster CSV, and writes a CSV report.

For a full explanation of what each component measures and how the metrics are
derived from the database, see [E01_ANALISE.md](E01_ANALISE.md).

---

## Requirements

```bash
pip install numpy boto3      # boto3 only needed for S3 mode
```

Python 3.8+ required.

---

## Data sources

The script supports three ways to obtain the databases.

### 1. Local databases (recommended for E01 reporting)

Use when you have already downloaded a backup snapshot to a local directory
(e.g. `~/.cache/studyamigo/20260323/`).

```bash
python placement_exam/planning_E01/scripts/grade_exercise.py \
    --interval custom --start 2026-03-01 --end 2026-03-23 \
    --label E01 --no-card-creation \
    --roster placement_exam/docs/STUDENT_ROSTER_SPRING_2026.csv \
    --local-only \
    --admin-db ~/.cache/studyamigo/20260323/admin.db \
    --user-db-dir ~/.cache/studyamigo/20260323/user_dbs
```

### 2. S3 backup (default)

Downloads the latest complete backup from the project's S3 bucket. Requires
AWS credentials configured for the `study-amigo` profile.

```bash
python placement_exam/planning_E01/scripts/grade_exercise.py \
    --interval custom --start 2026-03-01 --end 2026-03-23 \
    --label E01 --no-card-creation \
    --roster placement_exam/docs/STUDENT_ROSTER_SPRING_2026.csv \
    --bucket study-amigo-backups-645069181643 --profile study-amigo
```

Omit `--bucket` to have the script derive the bucket name automatically via
AWS STS (requires `sts:GetCallerIdentity` permission).

To list available backup slots interactively before downloading:

```bash
python ... --list-slots
```

To select a specific slot:

```bash
python ... --week 2 --day tuesday
```

### 3. SSH — live production server

Copies the databases directly from the EC2 instance via SCP. Use only when
a fresh snapshot is needed and no recent backup is available.

```bash
python placement_exam/planning_E01/scripts/grade_exercise.py \
    --interval custom --start 2026-03-01 --end 2026-03-23 \
    --label E01 --no-card-creation \
    --roster placement_exam/docs/STUDENT_ROSTER_SPRING_2026.csv \
    --host 54.152.109.26
```

Default SSH key: `~/.ssh/study-amigo-aws`. Override with `--key`.

---

## Key flags

| Flag | Description |
|------|-------------|
| `--label LABEL` | Exercise label (e.g. `E01`). Used in output filenames and headers. |
| `--interval` | Time window: `24h`, `week`, `2weeks`, `3weeks`, `month`, or `custom`. |
| `--start YYYY-MM-DD` | Start date (required with `--interval custom`). |
| `--end YYYY-MM-DD` | End date inclusive (defaults to today if omitted). |
| `--no-card-creation` | Exclude card-creation counts from Volume. Use for exercises where the deck is pre-loaded (E01). Without this flag, Volume = 0.40 × cards_sub + 0.60 × reviews_sub. With it, Volume = reviews_sub. |
| `--roster CSV` | Path to the placement-exam roster CSV. Enables cross-referencing to identify students who took the exam but never used the app. |
| `--output FILE` | Override the default CSV output path (`<label>_grades_<YYYYMMDD>.csv`). |
| `--top N` | Number of students shown in the Top / Bottom summary tables (default: 10). |
| `--cache-dir DIR` | Directory to store downloaded databases. Re-use across runs to avoid re-downloading. |
| `--refresh` | Force re-download even if a cached copy exists. |

---

## Roster CSV format

The CSV must include the following columns (headers are case-insensitive):

| Column | Description |
|--------|-------------|
| `ID` | Institutional student ID |
| `Name` | Full name (used for fuzzy matching against the admin DB) |
| `Course` | Course / programme name |
| `Email` | Student email |
| `Path` | Learning path (A, B, C…) |
| `Suggested Tier` | Tier suggested by the placement exam |

Student names in the roster are matched to admin DB accounts using fuzzy
string matching. If the match score is below 0.55 the student is marked as
having no account. Unmatched roster students appear in the "no activity"
section of the output.

---

## Output

### Standard output

The script prints:

1. **Run header** — label, date range, formula used.
2. **Volume normalisation reference** — min, p95, and max review counts
   used for min-max scaling.
3. **Full results table** — one row per active student, sorted by grade.
4. **Top N / Bottom N tables** — quick-look ranking summaries.
5. **Students without activity** — split into "no account" and "account
   exists, zero reviews", with student ID, name, course, tier, and email.
6. **Students with reviews but not in the roster** — users present in
   the admin DB who have activity but whose name was not matched to any
   roster entry.
7. **Behaviour flags summary** — students flagged for suspicious patterns.

### Behaviour flags

| Flag | Trigger condition |
|------|------------------|
| `RET100` | 100% retention with ≥ 30 type-1/2 reviews (statistically improbable) |
| `LOW_TIME` | `time_sub` < 30% with ≥ 20 reviews (most answers under 2 seconds) |
| `CRAM` | > 80% of non-cram reviews on the last day of the window |

### CSV file

Written to `<label>_grades_<YYYYMMDD>.csv` by default. Contains one row per
registered user with all raw metrics and computed sub-scores:

```
student_id, name, course, tier, path, email, user_id, username,
total_reviews, total_reviews_raw, cards_created, review_days,
last_day_reviews, cramming_ratio,
ret_total, ret_ok, retention_pct,
total_reviewed_cards, mature_cards, maturity_pct,
time_total, time_engaged, time_sub, ease_sub, mean_factor,
time_data_missing,
V, C, Q, E, grade, grade_letter, flags
```

---

## Reproducing the E01 report

```bash
python placement_exam/planning_E01/scripts/grade_exercise.py \
    --interval custom --start 2026-03-01 --end 2026-03-23 \
    --label E01 --no-card-creation \
    --roster placement_exam/docs/STUDENT_ROSTER_SPRING_2026.csv \
    --local-only \
    --admin-db ~/.cache/studyamigo/20260323/admin.db \
    --user-db-dir ~/.cache/studyamigo/20260323/user_dbs \
    --output placement_exam/planning_E01/E01_grades_20260323.csv
```

The CSV produced is the authoritative grade sheet for E01.

---

*Script location*: `placement_exam/planning_E01/scripts/grade_exercise.py`
*Last updated*: 2026-03-24
