# Student Performance Analysis: LLM and Machine Learning Applications

This document explores how data from individual Anki `.anki2` database files — combined with exercise schedules and course outcomes — can be used to train machine learning models and fine-tune LLMs for pedagogically relevant applications in teaching English as a Second Language (ESL).

---

## Table of Contents

1. [Available Training Data](#1-available-training-data)
2. [Application 1: Early Struggling Student Detection](#2-application-1-early-struggling-student-detection)
3. [Application 2: Optimal Review Schedule Personalization](#3-application-2-optimal-review-schedule-personalization)
4. [Application 3: Difficulty Estimation for ESL Content](#4-application-3-difficulty-estimation-for-esl-content)
5. [Application 4: Learning Style Clustering and Cohort Recommendations](#5-application-4-learning-style-clustering-and-cohort-recommendations)
6. [Application 5: Flashcard Quality Scoring](#6-application-5-flashcard-quality-scoring)
7. [Application 6: Automated Card Generation from ESL Texts](#7-application-6-automated-card-generation-from-esl-texts)
8. [Application 7: Engagement Forecasting per Exercise](#8-application-7-engagement-forecasting-per-exercise)
9. [Practical Considerations](#9-practical-considerations)
10. [Data Pipeline Recommendations](#10-data-pipeline-recommendations)

---

## 1. Available Training Data

Each student's `.anki2` SQLite database contains rich, granular interaction data that goes far beyond simple grades or attendance records.

### 1.1. Review Log (`revlog` table)

Every individual review action is recorded with:

| Field     | Description                                  | ML Relevance                              |
|-----------|----------------------------------------------|-------------------------------------------|
| `id`      | Timestamp in milliseconds                    | Temporal patterns, session detection       |
| `cid`     | Card ID                                      | Links review to specific content           |
| `ease`    | Student response (1=Again, 2=Hard, 3=Good, 4=Easy) | Ground truth for retention/difficulty |
| `ivl`     | New interval assigned after review           | SRS algorithm behavior                     |
| `lastIvl` | Previous interval before this review         | Interval progression tracking              |
| `time`    | Review duration in milliseconds              | Engagement depth, difficulty proxy          |
| `type`    | 0=learn, 1=review, 2=relearn, 3=cram        | Learning stage classification              |

### 1.2. Card State (`cards` table)

Snapshot of each card's current scheduling state:

| Field    | Description                       | ML Relevance                          |
|----------|-----------------------------------|---------------------------------------|
| `type`   | 0=new, 1=learning, 2=review, 3=relearning | Current learning stage       |
| `ivl`    | Current interval in days          | Maturity indicator                     |
| `factor` | Ease factor × 1000               | Per-card difficulty as learned by SRS  |
| `reps`   | Total review count                | Exposure frequency                     |
| `lapses` | Number of times card was forgotten | Retention failure indicator           |

### 1.3. Card Content (`notes` table)

The actual English-language content on each flashcard:

| Field  | Description                                    | ML Relevance                        |
|--------|------------------------------------------------|-------------------------------------|
| `flds` | Field content (front/back) separated by U+001F | NLP features, difficulty estimation |
| `sfld` | Sort field (typically the front of the card)    | Quick text access                   |
| `tags` | Space-separated tags                            | Content categorization              |

### 1.4. Exercise Schedule Metadata

External to the database, but critical for labeling:

- Exercise start and end dates for card creation.
- Exercise start and end dates for review activity.
- Exercise identification (E01 through E09).
- Whether the exercise involved student-created cards or publicly available decks.

### 1.5. Outcome Data

From the existing spreadsheet and course records:

- Per-exercise metrics (cards created, reviews done, review days, averages).
- Final course grades or completion status.
- Active exercise count (engagement level).

---

## 2. Application 1: Early Struggling Student Detection

### Goal

Predict, based on a student's behavior in the first 2–3 exercises, whether they will disengage or fail by the end of the course.

### Approach

**Type**: Binary classification (at risk / not at risk).

**Features** (extracted from E01–E03 data):

- Review count and frequency.
- Ease distribution (proportion of "Again" responses).
- Average review duration.
- Cramming ratio (percentage of reviews on the last day of each exercise window).
- Procrastination index (delay between exercise start and first activity).
- Session regularity (standard deviation of inter-session gaps).
- Card creation count and creation-to-review ratio.

**Labels**: Defined from E04–E09 outcomes — for example, a student who completes fewer than 3 of the remaining 6 exercises is labeled "at risk."

**Model choices**: With 48 students per semester, lightweight models are appropriate:

- Logistic regression (interpretable, works well with small data).
- Random forest or gradient boosted trees (XGBoost/LightGBM).
- Leave-one-out cross-validation to maximize use of limited data.

### Pedagogical Value

Enables proactive intervention. Instead of discovering a student has disengaged at final grading, the instructor receives an alert during week 3 or 4 and can reach out with targeted support.

---

## 3. Application 2: Optimal Review Schedule Personalization

### Goal

Learn a personalized memory model for each student to predict recall probability and optimize review intervals beyond what the standard SM-2 algorithm provides.

### Approach

**Type**: Regression / probability estimation.

**Input sequence** (per card, per student):

```
(interval, ease_response, time_spent, card_age, total_reps, total_lapses) → P(recall)
```

**Training data**: Each row in `revlog` provides a labeled example — the ease response indicates whether the student successfully recalled the card (`ease >= 3`) or not (`ease = 1`).

**Model choices**:

- **Half-life regression (HLR)**: A model specifically designed for spaced repetition (used by Duolingo). It learns a per-student, per-item half-life for memory decay.
- **Small LSTM or GRU**: Takes the sequence of a student's reviews for a given card and predicts the next outcome. Can capture patterns that SM-2's fixed formula misses.
- **Bayesian knowledge tracing**: Probabilistic model that estimates a student's latent knowledge state.

### Pedagogical Value

SM-2 uses the same parameters for all students. A personalized model could learn that a particular student forgets vocabulary after 4 days but retains grammar patterns for 10 days, and adjust intervals accordingly. This directly improves learning efficiency by ensuring cards appear exactly when they are about to be forgotten — the optimal point for memory reinforcement.

---

## 4. Application 3: Difficulty Estimation for ESL Content

### Goal

Predict how difficult a new, unseen flashcard will be for students at a given proficiency level, before anyone reviews it.

### Approach

**Type**: Regression (predicted difficulty score) or classification (easy / medium / hard).

**Features**:

- **Text features from `notes.flds`**: Word frequency (relative to standard ESL word lists), word length, number of syllables, sentence complexity, cognate similarity to Portuguese.
- **Linguistic features**: Part of speech, verb tense, idiomatic usage, presence of phrasal verbs.
- **Contextual features**: Topic/tag of the card, position in the deck sequence.

**Labels**: Aggregate class performance on existing cards:

- Average ease rating across all students who reviewed the card.
- Average lapse rate.
- Average time to reach mature interval.
- Average review duration.

**Model choices**:

- Fine-tuned sentence transformer (e.g., all-MiniLM-L6-v2) to encode card text, followed by a regression head.
- Simpler approach: TF-IDF or bag-of-words features + gradient boosted trees.

### Pedagogical Value

When an instructor creates new cards or imports a public deck for a new exercise, the model flags which cards will likely cause the most difficulty for ESL learners. This allows:

- Pre-emptive scaffolding (adding hints, context, or pronunciation guides).
- Splitting complex cards into simpler prerequisite steps.
- Sequencing cards so that easier ones build toward harder concepts.

---

## 5. Application 4: Learning Style Clustering and Cohort Recommendations

### Goal

Discover distinct learner behavior profiles within the class and provide targeted guidance to each cluster.

### Approach

**Type**: Unsupervised learning (clustering).

**Feature vector per student**:

- Preferred study times (morning / afternoon / evening / late night distribution).
- Average session length and frequency.
- Cramming ratio (average across exercises).
- Creation-to-review balance.
- Retention rate trajectory (improving, declining, stable).
- Review density (reviews per active day).
- Consistency index (standard deviation of review days across exercises).
- Procrastination index.

**Model choices**:

- K-means or Gaussian mixture models for initial exploration.
- DBSCAN if cluster shapes are non-spherical.
- Hierarchical clustering for dendrogram visualization.
- Optimal cluster count determined by silhouette score or elbow method.

### Expected Clusters

Based on the current cohort data, likely clusters include:

- **Steady daily reviewers**: Consistent sessions, low cramming ratio, good retention.
- **Weekend crammers**: Activity concentrated in 1–2 days per exercise window.
- **Content creators who under-review**: High card creation, low review-to-creation ratio.
- **Passive reviewers**: Rely on public decks, minimal card creation, but consistent review effort.
- **Minimal engagers**: Low activity across all metrics.

### Pedagogical Value

Instead of treating the class as homogeneous, the instructor can provide cluster-specific guidance:

- "Students in Cluster 3: you're creating great cards but not reviewing enough. Try adding a 10-minute daily review session."
- "Students in Cluster 2: your cramming pattern undermines spaced repetition. Try spreading your reviews across at least 3 days per exercise."

---

## 6. Application 5: Flashcard Quality Scoring

### Goal

Score student-created flashcards by their predicted learning effectiveness, combining card content analysis with actual review outcome data.

### Approach

**Type**: Regression (quality score) or ranking.

**Input**: Card text from `notes.flds` (front and back fields).

**Labels**: Learning effectiveness metrics derived from `revlog` and `cards`:

- Retention rate for that specific card (percentage of "Good" or "Easy" responses).
- Time to reach mature interval.
- Lapse count (lower is better).
- Average review duration (extremely low durations may indicate trivially easy or poorly formulated cards).

**Model choices**:

- Fine-tune a small language model (e.g., DistilBERT or a Portuguese-English bilingual model) on card text paired with effectiveness scores.
- Simpler baseline: Handcrafted text features (question word presence, field length ratio, specificity indicators) + regression model.

**Quality indicators the model can learn**:

- Cards with overly vague fronts ("What is the word?") correlate with low retention.
- Cards with too much text on the front correlate with long review times but not better retention.
- Cards that test one specific concept have higher retention than multi-part cards.
- Cards using cloze-deletion-style patterns may show different retention profiles than simple Q&A cards.

### Pedagogical Value

- Provide automated feedback to students on their card-writing skills: "This card is too vague — try making the question more specific."
- Rank cards within a deck by quality, helping instructors curate the best student-created content for sharing.
- Card creation is itself a learning activity; improving card quality improves learning twice — once during creation, once during review.

---

## 7. Application 6: Automated Card Generation from ESL Texts

### Goal

Given a passage of English text (literature, news article, textbook excerpt), automatically generate flashcards calibrated to the students' proficiency level and modeled after successful student-created cards.

### Approach

**Type**: Conditional text generation (fine-tuned LLM).

**Training pairs**: `(source_text_or_context, flashcard_front, flashcard_back)` extracted from student submissions where the resulting card achieved high retention (ease ≥ 3 on most reviews, matured within the exercise window).

**Fine-tuning base models**:

- A small instruction-tuned LLM (e.g., Llama 3 8B, Mistral 7B, or Phi-3) fine-tuned with LoRA on the card generation task.
- Alternatively, prompt engineering with a larger API-based model (GPT-4, Claude) using few-shot examples drawn from the highest-quality student cards.

**Input at inference time**: An English text passage + target difficulty level.

**Output**: A set of flashcards (front/back pairs) covering key vocabulary, grammar patterns, and comprehension questions from the passage.

### Pedagogical Value

- Closes the learning loop: the model learns what effective ESL flashcards look like from students' own successful creations, then generates similar cards from new material.
- Reduces instructor preparation time for new exercises.
- Generated cards can be pre-scored by the difficulty estimation model (Application 3) before distribution.
- Maintains calibration to the students' actual proficiency level, since the training data comes from cards that worked for this specific student population.

---

## 8. Application 7: Engagement Forecasting per Exercise

### Goal

For a new exercise, predict each student's likely engagement pattern and final metrics before the exercise begins.

### Approach

**Type**: Time series forecasting / sequence prediction.

**Input**: A student's behavioral history from all previous exercises (metrics trajectory), plus the new exercise's parameters (duration, type of task, whether it involves card creation or review-only).

**Predict**:

- Expected number of active days.
- Expected total reviews.
- Probability of zero engagement (no-show).
- Expected cramming ratio.

**Model choices**:

- Per-student autoregressive model on their metric time series.
- Collaborative filtering approach: use similar students' patterns to predict a given student's behavior on a new exercise.
- Simple baseline: Student's own exponential moving average of past exercise metrics.

### Pedagogical Value

- Allows the instructor to calibrate exercise duration and deadlines based on predicted student behavior rather than assumptions.
- If the model predicts that 60% of students will cram on the last day for a 5-day exercise window, the instructor might extend the window to 10 days with a mid-point checkpoint.
- Identifies students predicted to disengage on the upcoming exercise for pre-emptive outreach.

---

## 9. Practical Considerations

### 9.1. Dataset Size

| Aspect                    | Current State            | After 3–4 Semesters      |
|---------------------------|--------------------------|--------------------------|
| Students                  | 48                       | 150–200                  |
| Review records (estimated)| ~50,000–100,000 total    | ~200,000–500,000 total   |
| Flashcard content items   | ~5,000–10,000 cards      | ~20,000–50,000 cards     |
| Exercise windows          | 9 per student            | 9 per student            |

With 48 students, full deep learning from scratch is impractical. Recommended approaches by data scale:

| Data Scale        | Suitable Approaches                                                |
|-------------------|--------------------------------------------------------------------|
| 48 students       | Logistic regression, random forests, XGBoost, leave-one-out CV     |
| 100–200 students  | Fine-tuning pre-trained models with LoRA, small neural networks    |
| 500+ students     | Training custom models, deeper architectures                        |

### 9.2. Most Viable First Projects

Ordered by feasibility with current data:

1. **Struggling student detection** (Application 1): Binary classification on engineered features — works well with small datasets and traditional ML. Immediate practical value.
2. **Learning style clustering** (Application 4): Unsupervised methods work with small datasets. Provides immediate instructional insights.
3. **Engagement forecasting** (Application 7): Can start with simple baselines (moving averages) and grow in sophistication.

### 9.3. Highest Novelty Projects

These combine interaction data with content in ways the existing SRS and educational data mining literature has not fully explored:

1. **Personalized SRS scheduling** (Application 2): Most SRS research uses synthetic or single-population data. Per-student models trained on real ESL learner data are rare.
2. **Flashcard quality scoring** (Application 5): Linking NLP analysis of card text to actual learning outcomes is a novel intersection.

### 9.4. Language-Specific Considerations

Since the students are Portuguese-speaking ESL learners, models can exploit:

- **Cognate effects**: English-Portuguese cognates (e.g., "university" / "universidade") are typically easier. A difficulty model could incorporate cognate similarity scores.
- **Known interference patterns**: False friends (e.g., "actually" ≠ "atualmente"), verb tense mapping differences, and preposition usage are predictable difficulty sources for this L1 population.
- **Bilingual embeddings**: Models like multilingual BERT or XLM-RoBERTa can capture cross-lingual transfer effects relevant to difficulty prediction.

---

## 10. Data Pipeline Recommendations

Regardless of which applications are pursued, the highest-leverage immediate investment is to standardize the data collection pipeline so that each semester's data accumulates in a consistent, ML-ready format.

### 10.1. Per-Semester Data Export

At the end of each semester, export a structured dataset:

```
semester_data/
├── 2024-1/
│   ├── exercise_schedule.json     # Start/end dates for each exercise
│   ├── metrics.csv                # The geral.xlsx data in CSV format
│   ├── outcomes.csv               # Final grades, completion status
│   └── anki_databases/            # Copy of all student .anki2 files
│       ├── student_3001.anki2
│       ├── student_3004.anki2
│       └── ...
├── 2024-2/
│   └── ...
└── 2025-1/
    └── ...
```

### 10.2. Exercise Schedule Format

```json
{
  "semester": "2024-1",
  "exercises": [
    {
      "id": "E01",
      "creation_start": "2024-03-01",
      "creation_end": "2024-03-15",
      "review_start": "2024-03-01",
      "review_end": "2024-03-20",
      "type": "student_created",
      "description": "English literature vocabulary"
    },
    {
      "id": "E02",
      "creation_start": "2024-03-16",
      "creation_end": "2024-03-30",
      "review_start": "2024-03-16",
      "review_end": "2024-04-05",
      "type": "public_deck",
      "description": "Verbal tenses deck"
    }
  ]
}
```

### 10.3. Standardized Feature Extraction Script

Create a Python script that, given a semester directory, extracts a unified feature matrix:

```
Input:  semester_data/2024-1/
Output: features/2024-1/
        ├── student_features.csv      # One row per student, engineered features
        ├── card_features.csv         # One row per card, text + performance features
        ├── review_sequences.jsonl    # Per-student, per-card review sequences
        └── session_features.csv      # Per-student session-level behavioral features
```

This script should be run once per semester and the output stored alongside the raw data, forming the foundation for any of the applications described in this document.

### 10.4. Privacy and Ethics

- Student data must be anonymized or pseudonymized before use in any published research.
- Students should be informed (via course syllabus or consent form) that their interaction data may be used for educational research and system improvement.
- Trained models should not be used to make automated grading decisions without instructor review.
- Comply with institutional review board (IRB) or equivalent ethics committee requirements if results are to be published.
