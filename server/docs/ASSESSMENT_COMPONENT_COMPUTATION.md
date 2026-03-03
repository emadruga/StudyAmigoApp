# Assessment Component Computation

This document specifies, step by step, how each of the four assessment components defined in
`STUDENT_PERFORMANCE_ANALYSIS.md § 7.1` is computed from the Anki2 database files and the
exercise metrics spreadsheet, and how they combine into a final grade on a **0–100 scale**.

The assessment is applied independently for each bimester:

| Bimester | Exercises | Count |
|----------|-----------|-------|
| **B1** (first bimester)  | E01, E02, E03, E04 | 4 |
| **B2** (second bimester) | E05, E06, E07, E08, E09 | 5 |

All four components are first normalized to a **0–100** sub-score, then combined with the weights
below to produce the bimester grade:

| # | Component   | Weight | Primary Source |
|---|-------------|--------|----------------|
| 1 | Volume      | 25 %   | Spreadsheet totals (`E0X`, `E0X-rev`) |
| 2 | Consistency | 25 %   | Spreadsheet (`E0X-rdias`) + `revlog` timestamps |
| 3 | Quality     | 30 %   | `revlog.ease`, `cards.ivl` |
| 4 | Engagement  | 20 %   | `revlog.time`, `cards.factor` |

```
bimester_grade = 0.25 × V + 0.25 × C + 0.30 × Q + 0.20 × E
```

where V, C, Q, E ∈ [0, 100].

---

## Prerequisite: Mapping Exercise Windows to Timestamps

Every exercise has four dates defined in `exercise_schedule.json`:

```json
{
  "id": "E01",
  "creation_start": "YYYY-MM-DD",
  "creation_end":   "YYYY-MM-DD",
  "review_start":   "YYYY-MM-DD",
  "review_end":     "YYYY-MM-DD"
}
```

Anki stores all timestamps as **milliseconds since Unix epoch** (UTC).
Convert a calendar date to the boundary values used in SQL queries:

```python
import datetime, calendar

def day_start_ms(date_str: str) -> int:
    """Midnight UTC at the start of the given date, in milliseconds."""
    d = datetime.date.fromisoformat(date_str)
    return int(calendar.timegm(d.timetuple())) * 1000

def day_end_ms(date_str: str) -> int:
    """23:59:59 UTC at the end of the given date, in milliseconds."""
    return day_start_ms(date_str) + 86_400_000 - 1
```

Use `day_start_ms(review_start)` and `day_end_ms(review_end)` as the SQL filter bounds
on `revlog.id` for any given exercise.

For card creation, use `day_start_ms(creation_start)` and `day_end_ms(creation_end)` as
bounds on `notes.id` (note IDs are also creation timestamps in milliseconds).

---

## Component 1 — Volume (Weight: 25 %)

Volume measures the **raw quantity of study material produced and reviewed** by the student
during the bimester. It captures effort in terms of absolute output, not quality.

### 1.1 Raw Inputs

From the spreadsheet, for each exercise EXX in the bimester:

| Variable | Spreadsheet column | Meaning |
|----------|--------------------|---------|
| `cards_EXX` | `E0X` | New flashcards added during the exercise |
| `reviews_EXX` | `E0X-rev` | Total reviews performed during the exercise |

For the bimester totals:

```
total_cards   = sum(cards_EXX   for EXX in bimester_exercises)
total_reviews = sum(reviews_EXX for EXX in bimester_exercises)
```

These values can be cross-validated directly from the Anki2 file:

```sql
-- Cards created in the bimester (count distinct notes whose ID falls in any exercise window)
SELECT COUNT(DISTINCT n.id) AS cards_created
FROM notes n
WHERE n.id BETWEEN :bimester_creation_start_ms AND :bimester_creation_end_ms;

-- Reviews performed in the bimester (cram reviews excluded)
-- type 3 = cram: bypasses the SRS scheduler and can be repeated infinitely,
-- generating inflated review counts without any learning signal.
-- Forensic example: Pietro Mozzer Mahmud (3014, E07) produced 508 revlog entries
-- for 35 cards using 88.8% cram mode, median review time 0.64 s, 99.8% ease=4.
SELECT COUNT(*) AS total_reviews
FROM revlog
WHERE id BETWEEN :bimester_review_start_ms AND :bimester_review_end_ms
  AND type != 3;   -- exclude cram
```

where `bimester_creation_start_ms` is the `creation_start` of the first exercise in the bimester
and `bimester_creation_end_ms` is the `creation_end` of the last exercise.
Similarly for review bounds.

### 1.2 Normalization

Volume is normalized using **class-level min-max scaling** for each bimester cohort.
To prevent a single outlier from compressing all other scores, the maximum is capped at
the **95th percentile** of the class distribution.

```python
import numpy as np

def minmax_sub_score(student_value: float, all_values: list[float]) -> float:
    """Normalize student_value to [0, 100] using class-level min-max."""
    lo = np.min(all_values)
    hi = np.percentile(all_values, 95)          # cap at 95th percentile
    if hi == lo:
        return 100.0 if student_value >= hi else 0.0
    return float(np.clip((student_value - lo) / (hi - lo) * 100, 0, 100))
```

Apply separately for cards and reviews:

```
cards_sub   = minmax_sub_score(total_cards,   class_total_cards_list)
reviews_sub = minmax_sub_score(total_reviews, class_total_reviews_list)
```

### 1.3 Volume Score

Reviews carry more weight than card creation because they reflect sustained study effort:

```
V = 0.40 × cards_sub + 0.60 × reviews_sub
```

---

## Component 2 — Consistency (Weight: 25 %)

Consistency measures whether the student **spread their study effort across the exercise
window** rather than concentrating it in a single session, and whether they **participated
in all exercises** of the bimester.

It is composed of two sub-scores:

| Sub-score | Captures |
|-----------|----------|
| Participation | Did the student engage in each exercise? |
| Distribution | Did the student spread reviews across days (not cram)? |

### 2.1 Participation Sub-score

```
N_bimester = number of exercises in the bimester  (4 for B1, 5 for B2)
N_active   = count of exercises in the bimester where (E0X-rdias > 0 OR E0X-rev > 0)

participation_sub = (N_active / N_bimester) × 100
```

An exercise counts as "active" if the student performed at least one **non-cram** review during
its window, confirmed via:

```sql
SELECT COUNT(DISTINCT DATE(id / 1000, 'unixepoch')) AS review_days
FROM revlog
WHERE id BETWEEN :review_start_ms AND :review_end_ms
  AND type != 3;   -- exclude cram
```

If `review_days > 0`, the exercise is active.

### 2.2 Distribution Sub-score (Anti-Cramming)

For each active exercise, compute the **last-day cramming ratio**:

```sql
-- Reviews on the final day of the exercise window (cram excluded)
SELECT COUNT(*) AS last_day_reviews
FROM revlog
WHERE id BETWEEN :last_day_start_ms AND :review_end_ms
  AND type != 3;   -- exclude cram

-- Total reviews for the exercise (cram excluded)
SELECT COUNT(*) AS exercise_reviews
FROM revlog
WHERE id BETWEEN :review_start_ms AND :review_end_ms
  AND type != 3;   -- exclude cram
```

```
cramming_ratio_EXX = last_day_reviews_EXX / exercise_reviews_EXX
```

If `exercise_reviews_EXX = 0`, skip this exercise (student was inactive).

A well-distributed student has a low cramming ratio. The per-exercise scores are:

```
distribution_sub_EXX = (1 - cramming_ratio_EXX) × 100
```

The bimester distribution sub-score is the average across active exercises:

```
distribution_sub = mean(distribution_sub_EXX for active EXX in bimester)
```

### 2.3 Consistency Score

```
C = 0.50 × participation_sub + 0.50 × distribution_sub
```

A student who participates in all exercises and never crams scores C = 100.
A student who participates in only half the exercises and always crams scores C ≈ 25.

---

## Component 3 — Quality (Weight: 30 %)

Quality measures **how much the student is actually learning**, as opposed to simply going
through the motions. It is derived entirely from the Anki2 `revlog` and `cards` tables.

It is composed of two sub-scores:

| Sub-score | Captures |
|-----------|----------|
| Retention rate | Fraction of reviews answered correctly |
| Card maturity | Fraction of cards that reached long-term retention |

### 3.1 Retention Rate Sub-score

In Anki's `revlog`, the `ease` column encodes the student's self-reported recall:

| `ease` value | Button | Meaning |
|---|---|---|
| 1 | Again | Failed — card reset |
| 2 | Hard  | Partial recall |
| 3 | Good  | Successful recall |
| 4 | Easy  | Effortless recall |

A review is considered **successful** when `ease >= 3`.

```sql
-- Compute retention rate for the bimester
SELECT
    COUNT(*) AS total_reviews,
    SUM(CASE WHEN ease >= 3 THEN 1 ELSE 0 END) AS successful_reviews
FROM revlog
WHERE id BETWEEN :bimester_review_start_ms AND :bimester_review_end_ms
  AND type IN (1, 2);   -- type 1 = review, type 2 = relearn (exclude initial learning phase)
```

> **Note:** Reviews with `type = 0` (learning/new) are excluded because the student is
> experiencing the card for the first time and failure is expected. `type = 3` (cram) is
> also excluded as it bypasses the SRS scheduler.

```
retention_sub = (successful_reviews / total_reviews) × 100
```

If `total_reviews = 0`, set `retention_sub = 0`.

### 3.2 Card Maturity Sub-score

A card becomes **mature** in Anki when its scheduled review interval (`cards.ivl`) reaches
**21 days or more**. This indicates the student has reviewed the card enough times, spread
over enough time, for it to enter long-term memory.

```sql
-- Cards that were created during the bimester AND have reached mature status
SELECT
    COUNT(*) AS total_created_cards,
    SUM(CASE WHEN c.ivl >= 21 THEN 1 ELSE 0 END) AS mature_cards
FROM cards c
JOIN notes n ON c.nid = n.id
WHERE n.id BETWEEN :bimester_creation_start_ms AND :bimester_creation_end_ms;
```

```
maturity_sub = (mature_cards / total_created_cards) × 100
```

If `total_created_cards = 0` (student created no cards — e.g., a review-only exercise),
compute maturity over all cards the student reviewed in the bimester instead:

```sql
-- Fallback: cards reviewed in the bimester
SELECT
    COUNT(DISTINCT c.id) AS total_reviewed_cards,
    SUM(CASE WHEN c.ivl >= 21 THEN 1 ELSE 0 END) AS mature_cards
FROM cards c
WHERE c.id IN (
    SELECT DISTINCT cid FROM revlog
    WHERE id BETWEEN :bimester_review_start_ms AND :bimester_review_end_ms
);
```

### 3.3 Quality Score

```
Q = 0.70 × retention_sub + 0.30 × maturity_sub
```

Retention is weighted higher because it is measured at the moment of recall (active evidence),
while card maturity is a lagging indicator that rewards earlier exercises more than later ones.

---

## Component 4 — Engagement (Weight: 20 %)

Engagement measures the **depth and authenticity of the student's interaction** with the
flashcard system. It uses two behavioral signals:

| Sub-score | Captures |
|-----------|----------|
| Review time quality | Was each review given sufficient attention? |
| Ease factor health | Is the SRS building long-term ease, or struggling? |

### 4.1 Review Time Quality Sub-score

The `revlog.time` column stores the duration of each review in **milliseconds**.

Reviews are classified by duration:

| Duration | Classification | Empirical basis |
|---|---|---|
| < 2,000 ms | Mechanical | Confirmed from student data: João Vitor (3005) had 25 % of reviews under 2 s, median 2.2 s, 100 % ease=4 — the clearest mechanical-clicking profile in the cohort |
| 2,000–59,999 ms | Engaged | Good students (Rayssa, Edina) had medians of 5–10 s; 7–8 % of their reviews fell under 2 s (fast responses to genuinely easy vocabulary — acceptable noise) |
| = 60,000 ms | Timer artifact | Anki hard-caps `revlog.time` at exactly 60,000 ms when the student leaves the screen. This is **not** a long review — it is a missing value. Exclude from all calculations. |

> **Calibration source**: thresholds derived from E07 submissions analysed below.
> The 2,000 ms lower bound matches `CHEATING_DETECTION.md § 3.3`.
> No empirical upper bound beyond the Anki 60 s cap was found in the data.
>
> | Student | ID | Class. | Median time | % < 2 s | Notes |
> |---|---|---|---|---|---|
> | Rayssa Ferreira de Assis | 3009 | ✅ Good | 5.1–7.0 s | 7–8 % | Authentic ease mix, relearning events |
> | Edina de Albuquerque | 4002 | ✅ Good | 10.1 s | ~0 % | Long times, high volume |
> | Estevão Martins de Faria | 5009 | ✅ Good | 3.73 s | 33 % | 91 % mature cards explain fast times |
> | Kauã Willians Lopes Amado | 5016 | ✅ Good | 3.89 s | 34 % | 96 % mature cards, 30 review days |
> | Gabrielle de Andrade Cavalcante | 4005 | ✅ Good | 6.14 s | 10 % | 87 % mature, std dev 9.6 s |
> | João Vitor do Amaral das Neves | 3005 | ❌ Bad | 2.2 s | 25 % | 100 % Easy, single deck only |
> | Jullia Paranhos de Moraes | 5014 | ❌ Bad | 1.28 s | 75 % | Near-zero lapses, 2,296 reviews |
> | Pietro Mozzer Mahmud | 3014 | ❌ Bad | 0.64 s | 97 % | 88.8 % cram (type=3); likely macro/script |
>
> **Important**: good long-term users (Estevão, Kauã, Gabrielle) show 30–34 % under 2 s paired
> with high maturity rates (87–96 %). The 2 s threshold must be read alongside maturity and
> ease factor — fast times alone do not indicate disengagement when cards are genuinely mature.

An engaged review is any review with `time >= 2000 AND time < 60000`:

```sql
SELECT
    COUNT(*) FILTER (WHERE time < 60000)                              AS total_reviews,
    COUNT(*) FILTER (WHERE time >= 2000 AND time < 60000)             AS engaged_reviews
FROM revlog
WHERE id BETWEEN :bimester_review_start_ms AND :bimester_review_end_ms
  AND type != 3;   -- exclude cram
```

> Reviews where `time = 60000` are excluded from both numerator and denominator so that
> Anki timeout artifacts do not deflate the score.

```
time_sub = (engaged_reviews / total_reviews) × 100
```

If `total_reviews = 0` (after excluding 60,000 ms entries), set `time_sub = 0`.

#### Zero-time fallback (older Anki clients)

Some Anki clients — older desktop versions and certain AnkiDroid configurations — record
`revlog.time = 0` for every review when the card timer is disabled or unsupported. This is
identifiable as a database format issue: these submissions typically contain only
`collection.anki2` with no `collection.anki21` file.

**Detection**:

```sql
-- Returns 1 if ALL non-cram reviews have time = 0 (missing data), 0 otherwise
SELECT CASE WHEN MAX(time) = 0 THEN 1 ELSE 0 END AS time_data_missing
FROM revlog
WHERE type != 3;
```

**Handling (Option B — reweight)**:
When `time_data_missing = 1`, the `time_sub` cannot be computed.
Drop it from the Engagement score and give full weight to `ease_sub`:

```
IF time_data_missing:
    E = ease_sub          -- 100 % weight on ease factor
ELSE:
    E = 0.50 × time_sub + 0.50 × ease_sub   -- normal formula
```

> **Empirical case**: Murilo Gomes dos Santos (5019, E08) submitted a `collection.anki2`
> export with 127 reviews across 4 days, all with `time = 0`. Ease distribution was
> 10 % Hard / 19 % Good / 71 % Easy — not suspicious. The zero times are a client
> artifact, not evidence of disengagement. Penalising him on `time_sub` would be unfair.

### 4.2 Ease Factor Health Sub-score

The `cards.factor` column stores the Anki ease factor multiplied by 1000.

| `cards.factor` value | Ease factor | Interpretation |
|---|---|---|
| < 2000 | < 2.0 | Card marked hard repeatedly — student is struggling |
| 2000–2499 | 2.0–2.499 | Below default — some difficulty |
| 2500 | 2.5 | Default (unchanged from initial value) |
| > 2500 | > 2.5 | Student answered "Easy" multiple times — strong retention |

Query the average ease factor over all cards reviewed during the bimester:

```sql
SELECT AVG(c.factor) AS mean_factor
FROM cards c
WHERE c.id IN (
    SELECT DISTINCT cid FROM revlog
    WHERE id BETWEEN :bimester_review_start_ms AND :bimester_review_end_ms
);
```

The theoretical range of `cards.factor` in Anki is **1300–3500** (ease 1.3 to 3.5).
Normalize linearly within that range:

```
ease_sub = CLIP( (mean_factor - 1300) / (3500 - 1300) × 100,  0, 100 )
```

A student whose cards average factor = 2500 (the default, neither improving nor declining)
scores `ease_sub ≈ 54.5`, which is approximately the midpoint — a fair baseline.

### 4.3 Engagement Score

```
IF time_data_missing (all revlog.time = 0):
    E = ease_sub
ELSE:
    E = 0.50 × time_sub + 0.50 × ease_sub
```

---

## Final Bimester Grade

### Formula

```
bimester_grade = 0.25 × V + 0.25 × C + 0.30 × Q + 0.20 × E
```

All four components are in [0, 100], so `bimester_grade` ∈ [0, 100].

### Grade Bands

| Score | Grade |
|-------|-------|
| 90–100 | A |
| 80–89  | B |
| 70–79  | C |
| 60–69  | D |
| < 60   | F |

### Example Walkthrough

A student in B1 (E01–E04) produces the following raw signals:

| Metric | Value |
|--------|-------|
| Cards created | 80 (class min 10, 95th pct 150) |
| Total reviews | 420 (class min 30, 95th pct 600) |
| Active exercises | 3 / 4 |
| Avg cramming ratio | 0.30 |
| Retention rate (revlog) | 78 % |
| Mature cards | 40 % of created cards |
| Engaged-time reviews | 72 % of total |
| Mean `cards.factor` | 2350 |

Step-by-step:

```
# Volume
cards_sub   = (80 - 10) / (150 - 10) × 100 = 50.0
reviews_sub = (420 - 30) / (600 - 30) × 100 = 68.4
V = 0.40 × 50.0 + 0.60 × 68.4 = 20.0 + 41.1 = 61.1

# Consistency
participation_sub  = (3 / 4) × 100 = 75.0
distribution_sub   = (1 - 0.30) × 100 = 70.0
C = 0.50 × 75.0 + 0.50 × 70.0 = 72.5

# Quality
retention_sub = 78.0
maturity_sub  = 40.0
Q = 0.70 × 78.0 + 0.30 × 40.0 = 54.6 + 12.0 = 66.6

# Engagement
time_sub = 72.0
ease_sub = CLIP( (2350 - 1300) / (3500 - 1300) × 100, 0, 100 )
         = 1050 / 2200 × 100 = 47.7
E = 0.50 × 72.0 + 0.50 × 47.7 = 36.0 + 23.9 = 59.9

# Final grade
bimester_grade = 0.25 × 61.1 + 0.25 × 72.5 + 0.30 × 66.6 + 0.20 × 59.9
              = 15.3 + 18.1 + 20.0 + 12.0
              = 65.4  →  Grade D
```

---

## Bimester-Specific Notes

### B1 (E01–E04)

- 4 exercises → `participation_sub` denominator is 4.
- Card maturity is inherently lower because there is less elapsed time; the `maturity_sub`
  threshold of 21 days is still correct — it is expected that many B1 cards will not be
  mature until after B2 has started.
- Instructors may apply a **B1 maturity correction**: if fewer than 21 calendar days elapsed
  between the first review opportunity (E01 `review_start`) and the end of B1 (E04 `review_end`),
  lower the maturity weight to 0.15 and raise the retention weight to 0.85 in the Quality formula.

### B2 (E05–E09)

- 5 exercises → `participation_sub` denominator is 5.
- By B2, cards created in B1 may now be mature; these are NOT re-counted for the B2 maturity
  sub-score. Only cards created or first reviewed during E05–E09 are considered for B2 maturity.
- Students who continue reviewing B1 cards during B2 windows will have those reviews included
  in the retention and engagement queries, which is correct — sustained review of older material
  is a sign of good SRS practice.

---

## Data Extraction Reference

The following queries summarize all database reads needed to compute one student's
bimester score, given pre-computed millisecond timestamp bounds for the bimester:

```sql
-- Q1: Volume — cards created
SELECT COUNT(DISTINCT n.id) AS cards_created
FROM notes n
WHERE n.id BETWEEN :creation_start_ms AND :creation_end_ms;

-- Q2: Volume — reviews done (cram excluded)
SELECT COUNT(*) AS total_reviews
FROM revlog
WHERE id BETWEEN :review_start_ms AND :review_end_ms
  AND type != 3;   -- exclude cram

-- Q3: Consistency — review days per exercise (run once per exercise)
SELECT COUNT(DISTINCT DATE(id / 1000, 'unixepoch')) AS review_days
FROM revlog
WHERE id BETWEEN :ex_review_start_ms AND :ex_review_end_ms
  AND type != 3;   -- exclude cram

-- Q4: Consistency — last-day reviews per exercise (run once per exercise)
SELECT COUNT(*) AS last_day_reviews
FROM revlog
WHERE id BETWEEN :last_day_start_ms AND :ex_review_end_ms
  AND type != 3;   -- exclude cram

-- Q5: Quality — retention rate (type 1=review, 2=relearn only)
SELECT
    COUNT(*) AS total,
    SUM(CASE WHEN ease >= 3 THEN 1 ELSE 0 END) AS successful
FROM revlog
WHERE id BETWEEN :review_start_ms AND :review_end_ms
  AND type IN (1, 2);

-- Q6: Quality — card maturity
SELECT
    COUNT(*) AS total_created,
    SUM(CASE WHEN c.ivl >= 21 THEN 1 ELSE 0 END) AS mature
FROM cards c
JOIN notes n ON c.nid = n.id
WHERE n.id BETWEEN :creation_start_ms AND :creation_end_ms;

-- Q7a: Engagement — detect zero-time data (older Anki client / timer disabled)
-- If time_data_missing = 1, skip Q7b and set E = ease_sub (see § 4.3).
SELECT CASE WHEN MAX(time) = 0 THEN 1 ELSE 0 END AS time_data_missing
FROM revlog
WHERE type != 3;

-- Q7b: Engagement — review time quality (run only when time_data_missing = 0)
-- Excludes time=60000 (Anki hard-cap / timeout artifact) from both numerator and denominator.
-- Excludes type=3 (cram) — cram reviews have no meaningful time signal and inflate counts.
-- Lower bound 2000 ms calibrated from E07 student data (CHEATING_DETECTION.md § 3.3).
SELECT
    COUNT(*) FILTER (WHERE time < 60000)                  AS total,
    COUNT(*) FILTER (WHERE time >= 2000 AND time < 60000) AS engaged
FROM revlog
WHERE id BETWEEN :review_start_ms AND :review_end_ms
  AND type != 3;   -- exclude cram

-- Q8: Engagement — mean ease factor
SELECT AVG(c.factor) AS mean_factor
FROM cards c
WHERE c.id IN (
    SELECT DISTINCT cid FROM revlog
    WHERE id BETWEEN :review_start_ms AND :review_end_ms
);
```

All queries operate on a single student's `.anki2` file. Run them for each student in the
cohort and collect the results into a dataframe before applying normalization (Q1, Q2 require
class-level vectors for min-max scaling).
