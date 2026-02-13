# Student Performance Analysis: Additional Reports for ESL Flashcard Data

This document describes additional student performance reports that can be derived from the existing exercise metrics spreadsheet and the raw Anki `.anki2` database files. These reports complement the current per-exercise metrics (card creation counts, averages, review counts, and review days) with deeper insights into learning effectiveness, behavioral patterns, and engagement quality.

---

## Table of Contents

1. [Current Data Sources](#1-current-data-sources)
2. [Longitudinal / Trend Reports](#2-longitudinal--trend-reports)
3. [Effort & Consistency Metrics](#3-effort--consistency-metrics)
4. [Creation vs. Review Balance](#4-creation-vs-review-balance)
5. [Reports from the Anki `revlog` Table](#5-reports-from-the-anki-revlog-table)
6. [Temporal / Behavioral Patterns](#6-temporal--behavioral-patterns)
7. [Composite / Summary Scores](#7-composite--summary-scores)
8. [Class-Level Aggregate Reports](#8-class-level-aggregate-reports)
9. [Recommended Implementation Priority](#9-recommended-implementation-priority)

---

## 1. Current Data Sources

### 1.1. Exercise Metrics Spreadsheet (`geral.xlsx`)

The spreadsheet contains 48 students across 9 exercises (E01–E09). Each exercise has 5 metrics:

| Column     | Description                                                    |
|------------|----------------------------------------------------------------|
| `E0X`      | Number of brand new flashcards added by the student            |
| `E0X-avg`  | New flashcards per day available for the exercise              |
| `E0X-ravg` | Number of reviews done per day                                 |
| `E0X-rdias`| Number of days the student performed reviews                   |
| `E0X-rev`  | Absolute number of reviews done during the exercise window     |

Each exercise has a defined schedule specifying when card creation and reviews start and finish.

### 1.2. Anki Database Files (`.anki2`)

Each student has an individual SQLite database following the Anki schema. The key tables for analysis are:

- **`cards`**: Card scheduling state, including `type`, `queue`, `ivl` (interval), `factor` (ease factor), `reps`, and `lapses`.
- **`revlog`**: Complete log of every review, including `id` (timestamp in ms), `cid` (card ID), `ease` (1–4), `ivl` (new interval), `lastIvl`, `time` (review duration in ms), and `type` (learn/review/relearn/cram).
- **`notes`**: Flashcard content (front/back fields).
- **`col`**: Deck definitions and configuration.

### 1.3. Student Identifiers

Student `matricula_id` values use numeric prefixes (3xxx, 4xxx, 5xxx) that correspond to different class sections or cohorts, enabling cross-cohort comparisons.

---

## 2. Longitudinal / Trend Reports

These reports exploit the nine time-windowed exercises to reveal how student behavior evolves over the course.

### 2.1. Engagement Trajectory

Plot each student's participation across E01 through E09 and classify them into behavioral archetypes:

- **Consistent**: Activity in most or all exercises (e.g., 7–9 out of 9).
- **Front-loaded**: Strong activity in early exercises, fading over time.
- **Late bloomer**: Low activity initially, increasing in later exercises.
- **Sporadic**: Irregular participation with gaps.

**Data source**: Existing spreadsheet columns. A non-zero value in any of the 5 metrics for an exercise counts as active.

**Example**: A student active in E01–E03 but absent from E04–E09 is classified as front-loaded, which may signal early motivation loss.

### 2.2. Improvement Curve

Track whether `E0X-avg` (new cards per day) and `E0X-ravg` (reviews per day) trend upward, downward, or remain flat across exercises.

- **Positive slope**: Growing engagement and study habits.
- **Negative slope**: Fatigue, loss of interest, or increasing course load.
- **Flat**: Stable habits (which may be good or bad depending on the absolute level).

**Computation**: Linear regression on the per-exercise metric values, using only exercises where the student was active.

### 2.3. Dropout Risk Indicator

Flag students who had activity in earlier exercises but none in recent ones. This identifies students at risk of complete disengagement.

**Criteria**: Active in at least one of E01–E04 but inactive in the most recent 2–3 exercises.

---

## 3. Effort & Consistency Metrics

Global metrics that summarize a student's work across all exercises.

### 3.1. Total Cards Created

Sum of `E01` through `E09` — the raw volume of flashcard content produced by the student over the entire course.

### 3.2. Total Reviews Done

Sum of `E01-rev` through `E09-rev` — the total study effort measured in review actions.

### 3.3. Active Exercise Count

How many of the 9 exercises had non-zero activity. Observed range in the current cohort is 1 to 8 out of 9.

### 3.4. Review Density

```
review_density = total_reviews / total_review_days
```

Where `total_review_days` is the sum of `E01-rdias` through `E09-rdias`. This gives a global reviews-per-active-day metric that is more meaningful than per-exercise averages because it normalizes across varying exercise durations.

### 3.5. Consistency Index

Standard deviation of `E0X-rdias` (review days) across exercises where the student was active.

- **Low standard deviation**: The student reviews a similar number of days in each exercise — consistent habits.
- **High standard deviation**: Erratic engagement — heavy effort in some exercises, minimal in others.

---

## 4. Creation vs. Review Balance

### 4.1. Review-to-Creation Ratio

```
ratio = total_reviews / total_cards_created
```

This metric reveals the balance between content creation and study effort:

- **Healthy SRS usage**: A student reviews significantly more than they create. Typical ratios range from 5:1 to 20:1 or higher.
- **Very low ratio** (e.g., < 3:1): The student creates cards but does not study them, defeating the purpose of spaced repetition.
- **Very high ratio** (or zero cards created): The student relies entirely on pre-existing or shared decks. While reviewing is still valuable, card creation is itself an active learning exercise.

### 4.2. Creator vs. Reviewer Classification

Based on the ratio above, classify students into:

- **Creators**: Primarily produce new flashcards but may under-review.
- **Reviewers**: Primarily study existing cards (from public decks or shared content).
- **Balanced**: Healthy mix of card creation and review activity.

This distinction has pedagogical value — creating flashcards requires deeper engagement with the material (identifying key concepts, formulating questions) compared to passively reviewing pre-made cards.

---

## 5. Reports from the Anki `revlog` Table

The `revlog` table in each student's `.anki2` database contains a record for every individual review action. This is the richest source of learning quality data.

### 5.1. Retention Rate

```
retention_rate = reviews_with_ease_ge_3 / total_reviews * 100
```

Where `ease >= 3` means the student answered "Good" or "Easy" and `ease = 1` means "Again" (failed).

This directly measures learning effectiveness. A student with 1000 reviews but a 60% failure rate is struggling with the material, whereas a student with 500 reviews and 90% retention is learning efficiently.

**Breakdown options**:
- Overall retention rate across all exercises.
- Per-exercise retention rate to track improvement over time.
- Retention rate by card maturity (new cards vs. young vs. mature).

### 5.2. Average Review Time per Card

From `revlog.time` (duration in milliseconds):

```
avg_review_time = sum(revlog.time) / count(revlog)
```

- **Long average times** (> 15–20 seconds): May indicate the material is difficult, or that the student is genuinely engaging with each card.
- **Very short average times** (< 3 seconds): May indicate mindless or mechanical clicking through reviews without actual recall effort.

### 5.3. Lapse Rate

```
lapse_rate = count(revlog where type = 2) / count(revlog where type in (1, 2)) * 100
```

Where `type = 2` is a relearn event (a card that was previously learned but the student failed on it). A high lapse rate indicates poor long-term retention — the student is learning cards but not retaining them.

### 5.4. Maturity Progression

From the `cards` table, `cards.ivl` (interval in days):

- **New**: Cards not yet reviewed.
- **Young**: Cards with interval < 21 days.
- **Mature**: Cards with interval >= 21 days.

Count how many of each student's cards reach mature status by the end of the course. This is the ultimate SRS success metric — mature cards are cards the student has demonstrably retained over an extended period.

### 5.5. Ease Factor Distribution

From `cards.factor` (ease factor multiplied by 1000):

- **Low ease factors** (< 2000): Cards the student finds difficult; the SRS algorithm has reduced their ease due to repeated failures.
- **Medium ease factors** (2000–2500): Normal range, default starting value is 2500.
- **High ease factors** (> 2500): Cards the student has consistently answered correctly with "Easy".

A student whose cards cluster at low ease factors is systematically struggling. Report the mean and distribution of ease factors per student.

---

## 6. Temporal / Behavioral Patterns

These reports analyze *when* and *how* students study, derived from `revlog.id` timestamps.

### 6.1. Study Session Distribution

From `revlog.id` (review timestamp in milliseconds), determine what time of day students study:

- **Morning** (06:00–12:00)
- **Afternoon** (12:00–18:00)
- **Evening** (18:00–00:00)
- **Late night** (00:00–06:00)

This can reveal study habit patterns and may correlate with performance.

### 6.2. Procrastination Index

Compare each exercise's start date to the date of the student's first activity in that exercise.

```
procrastination_index = avg(first_activity_date - exercise_start_date)
```

A large average gap across exercises indicates a pattern of delaying work. Combined with cramming detection (below), this identifies students who consistently wait until the deadline.

### 6.3. Last-Day Cramming Ratio

```
cramming_ratio = reviews_on_last_day / total_reviews_for_exercise * 100
```

For each exercise, calculate what percentage of the student's total reviews occurred on the final day of the exercise window.

- **High cramming ratio** (> 50%): The student does most of their reviewing in a single session at the deadline. This directly undermines the spaced repetition model, which relies on distributing reviews over time.
- **Low cramming ratio** (< 20%): Reviews are distributed across the exercise window, consistent with effective SRS usage.

Report both per-exercise and overall average cramming ratios.

### 6.4. Session Length Distribution

Group consecutive reviews (within 5-minute gaps between `revlog.id` timestamps) into study sessions.

Report:
- **Average session length** (in minutes and in number of reviews).
- **Session frequency** (sessions per week or per exercise).
- **Session regularity**: Standard deviation of gaps between sessions. Low SD indicates a regular study routine.

Short, frequent sessions are more effective for spaced repetition than long, infrequent sessions.

---

## 7. Composite / Summary Scores

### 7.1. Weighted Performance Score

Combine multiple metrics into a single normalized score. Suggested components and weights:

| Component           | Weight | Source                         |
|---------------------|--------|--------------------------------|
| Volume (cards + reviews) | 25% | Spreadsheet totals            |
| Consistency (active days, exercise count) | 25% | Spreadsheet + derived metrics |
| Quality (retention rate) | 30% | `revlog.ease`                 |
| Engagement (review time, ease factors) | 20% | `revlog.time`, `cards.factor` |

Normalize each component to a 0–100 scale before applying weights. The resulting composite score provides a holistic view of student performance.

### 7.2. Effort Grade

Map the composite score to a letter grade or percentage for integration with institutional gradebooks:

| Score Range | Grade |
|-------------|-------|
| 90–100      | A     |
| 80–89       | B     |
| 70–79       | C     |
| 60–69       | D     |
| < 60        | F     |

### 7.3. Peer Comparison Percentile

For each metric, compute where each student falls relative to the class:

```
percentile = (number_of_students_scoring_lower / total_students) * 100
```

This allows students and instructors to understand relative standing on any individual metric or on the composite score.

---

## 8. Class-Level Aggregate Reports

### 8.1. Class Averages and Distributions

For each metric (both existing spreadsheet metrics and the new derived ones), compute:

- Mean, median, standard deviation.
- Histograms or box plots showing the distribution.
- Quartile breakdowns (Q1, Q2, Q3, Q4).

### 8.2. Exercise Difficulty Comparison

If a particular exercise shows universally lower retention rates or higher lapse rates across the class, it may indicate that the exercise content was inherently more difficult or that the exercise schedule was poorly calibrated.

Compare across exercises:
- Average class retention rate per exercise.
- Average cards created per exercise.
- Average review effort per exercise.

### 8.3. Cohort Comparison

The `matricula_id` prefixes (3xxx, 4xxx, 5xxx) correspond to different class sections. Compare aggregate performance metrics between cohorts to identify:

- Whether one section outperforms others.
- Differences in engagement patterns (e.g., one section may be more consistent while another has higher peaks but more dropouts).
- Whether instructional differences between sections are reflected in the data.

---

## 9. Recommended Implementation Priority

The following ordering reflects the combination of pedagogical value and implementation effort:

### Priority 1 — High Value, Moderate Effort

1. **Retention rate** (from `revlog.ease`): This is the core SRS quality metric. Without it, you can measure effort but not learning. Requires reading each student's `.anki2` file and querying the `revlog` table.

2. **Cramming detection** (from `revlog.id` timestamps): Directly relevant to SRS pedagogy. A student who crams all reviews into one day is not benefiting from spaced repetition, regardless of their review count.

### Priority 2 — High Value, Low Effort

3. **Engagement trajectory and dropout risk** (from existing spreadsheet): Can be computed entirely from the current spreadsheet columns with no database access. Immediately actionable for instructor intervention.

4. **Effort & consistency metrics** (totals, review density, consistency index): Simple aggregations of existing spreadsheet data that provide a clearer global picture than per-exercise numbers alone.

### Priority 3 — Medium Value, Moderate Effort

5. **Creation vs. review balance**: Simple ratio from existing data, but the pedagogical interpretation requires context about which exercises involved shared decks vs. student-created content.

6. **Composite score and grading**: Depends on several of the above metrics being computed first. Once available, this is the most directly useful output for grading purposes.

### Priority 4 — High Value, Higher Effort

7. **Temporal and behavioral patterns** (session analysis, procrastination index): Requires parsing `revlog` timestamps and correlating with exercise schedules. Yields rich insights but needs more processing logic.

8. **Deep SRS metrics** (lapse rate, maturity progression, ease factor distribution): Requires reading both `revlog` and `cards` tables. Provides the most granular view of learning quality but is most useful for identifying struggling students rather than for grading.

### Priority 5 — Aggregate Reports

9. **Class-level and cohort comparisons**: Should be implemented last since they depend on individual metrics being computed first. High value for instructional feedback and curriculum adjustment.
