# Assessment Plan: Monitoring Students During the Semester

This document describes (1) what was learned from the ten students analysed in E07/E08,
(2) a progressive monitoring procedure to apply exercise-by-exercise during a bimester, and
(3) ideas for what a Python script should do at the end of the bimester to produce the
full assessment table.

The full grading formula is specified in `ASSESSMENT_COMPONENT_COMPUTATION.md`.
The forensic signals are documented in `CHEATING_DETECTION.md`.

---

## Part 1 — What the 10-Student Analysis Taught Us

### 1.1 Student profiles confirmed by data (E07 / E08)

| Student | ID | Class. | Key signals |
|---|---|---|---|
| Rayssa Ferreira de Assis | 3009 | ✅ Good | Median 5–7 s, 7–8 % < 2 s, relearning events, authentic ease mix |
| Edina de Albuquerque | 4002 | ✅ Good | Median 10 s, ~0 % < 2 s, 2,966 reviews, 87 % mature |
| Estevão Martins de Faria | 5009 | ✅ Good | 91 % mature, 33 review days / 121 days, relearning events |
| Kauã Willians Lopes Amado | 5016 | ✅ Good | 96 % mature (highest), 30 review days, 5 % Again |
| Gabrielle de Andrade Cavalcante | 4005 | ✅ Good | Median 6 s, std dev 9.6 s (highest variance), 87 % mature |
| Pedro Rafael Sá da Silva | 5020 | ✅ Good (partial) | 465-day history, 89 % mature; HACKER deck never reviewed |
| Richard Alves de Oliveira | 4015 | ⚠️ Gray | Authentic ease (22 % Hard), but 31 % < 2 s — card content needed |
| João Vitor do Amaral das Neves | 3005 | ❌ Bad | 100 % Easy, median 2.2 s, 0 relearning, single deck |
| Jullia Paranhos de Moraes | 5014 | ❌ Bad | Median 1.28 s, 75 % < 2 s, 0.3 % Again — fastest bad student |
| Pietro Mozzer Mahmud | 3014 | ❌ Bad | 88.8 % cram (type=3), median 0.64 s — likely macro/script |

### 1.2 Three bad-student archetypes to watch for

**Archetype A — The button masher** (João Vitor, Jullia)
- All or nearly all reviews rated Easy
- Median review time well under 2 s
- Zero or near-zero relearning events
- May show a surprisingly good distribution (Jullia reviewed on 29 days) — distribution
  alone does not redeem the time and ease signals

**Archetype B — The cram abuser** (Pietro)
- `revlog.type = 3` (cram) dominates — 50 % or more of all entries
- Review times are sub-second with robot-like consistency (std dev < 700 ms)
- Cards never advance past the initial learning phase because cram bypasses the scheduler
- `cards.factor` may exceed 3,500 (above Anki's theoretical cap) as a forensic artifact

**Archetype C — The ghost** (partial engagement, not yet confirmed in this sample)
- Submits a deck, has a handful of reviews, then stops
- All activity concentrated in one or two sessions immediately before the deadline
- No mature cards, `cards.factor` unchanged from default (2,500)

### 1.3 The maturity-time interaction (important nuance)

Good long-term users (Estevão, Kauã, Gabrielle) have 30–34 % of reviews under 2 s,
which would look suspicious in isolation. The explanation is card maturity: a card reviewed
correctly 8–12 times over months is genuinely recalled in under a second. The tell that
distinguishes them from bad students:

- Their **median** stays above 2 s (3.7–6.1 s range)
- They have **real failure events** (Again > 1 %, relearning > 0)
- Their **mature card rate is 87–96 %**, consistent with long-term SRS use

The 2 s threshold must always be evaluated alongside maturity rate and ease distribution —
never in isolation.

### 1.4 Data quality exceptions found

- **Zero review times**: Murilo Gomes dos Santos (5019, E08) submitted a `collection.anki2`
  (older format) where every `revlog.time = 0`. This is a client artifact, not disengagement.
  The fallback is to drop `time_sub` and grade Engagement on ease factor alone (§ 4.3 of
  `ASSESSMENT_COMPONENT_COMPUTATION.md`).

- **Duplicate submissions**: Gabrielle submitted the same database twice under different
  filenames (`revisao` and `revisaodevideo`). Both files were byte-for-byte identical.
  When this happens, deduplicate by file hash before processing.

- **Incomplete exercise submissions**: Pedro Rafael and Kauã both submitted the HACKER deck
  after only one learning pass (type=0 only, 0 mature cards, all reviews in one session).
  This is a timing issue — they ran out of time for the SRS to cycle — not disengagement
  with the course overall.

---

## Part 2 — Progressive Monitoring During the Bimester

The bimester unfolds exercise by exercise. Not all four assessment components can be
computed with equal reliability at every stage. This section describes what to look at
and when.

### 2.1 What is available at each exercise

| Exercise | Volume | Consistency | Quality | Engagement |
|---|---|---|---|---|
| After E01 | ✅ Cards + reviews | ✅ Participation (1/N) | ⚠️ Retention rate only — no mature cards yet | ⚠️ Review time + ease factor, but small sample |
| After E02 | ✅ | ✅ Participation (2/N) + first cramming signal | ⚠️ Retention rate, still little maturity | ⚠️ Growing sample |
| After E03 | ✅ | ✅ Distribution pattern emerging | ⚠️ | ✅ Engagement signals becoming reliable |
| After E04 (B1 end) | ✅ Full B1 | ✅ Full B1 | ⚠️ Maturity low — apply B1 correction | ✅ Full B1 |
| After E05 | ✅ | ✅ | ✅ B1 cards maturing; new B2 cards starting | ✅ |
| After E09 (B2 end) | ✅ Full B2 | ✅ Full B2 | ✅ Full B2 | ✅ Full B2 |

### 2.2 Step-by-step procedure

#### Step 1 — After each exercise submission deadline

**Collect the files.**
For each student, gather the submitted `.apkg` files into a per-exercise folder:
```
submissions/
├── E01/
│   ├── 3005 - Joao Vitor/
│   ├── 3009 - Rayssa/
│   └── ...
├── E02/
└── ...
```

**Compute the Volume snapshot.**
From the spreadsheet (which you already maintain) or directly from the `.anki2` files:
- Cards created this exercise (`E0X`)
- Reviews done this exercise (`E0X-rev`)
- Review days this exercise (`E0X-rdias`)

Flag immediately: **zero activity** — any student with all three columns at zero for two
consecutive exercises is at risk of disengagement (see `STUDENT_PERFORMANCE_ANALYSIS.md § 2.3`).

**Run the quick forensic checks** (from `CHEATING_DETECTION.md`):
1. File hash collision — are any two `.apkg` files identical?
2. Duplicate submissions from the same student — deduplicate by hash.
3. Cram ratio: if `type=3 > 50 %` of revlog → flag immediately (Archetype B).
4. Ease lock: if `ease=4 > 95 %` AND `type=2 = 0` AND `median time < 2 s` → flag (Archetype A).
5. Zero-time data: if `MAX(revlog.time) = 0` → note as older client, apply fallback.

These checks take seconds per student and catch the worst cases early.

#### Step 2 — After E02 (earliest meaningful consistency signal)

With two exercises completed, you can see whether a student is participating consistently
or already dropping off. Compute:

- **Participation so far**: how many of the exercises completed so far had non-zero activity?
- **First cramming signal**: for E01 and E02, compute `last_day_reviews / total_reviews`.
  A student with > 80 % of their reviews on the final day of both exercises is already
  showing a problematic pattern.

No normalization is needed yet — just look at the raw flags and outliers.

#### Step 3 — After E03 (first quality signal)

By E03, students who are genuinely using SRS will have some reviews of `type=1` (scheduled
review of a card they learned in E01 or E02). This is when the retention rate becomes
meaningful for the first time.

Compute per student:
- Retention rate on `type=1` reviews so far (ease ≥ 3 / total type=1)
- Lapse count (type=2 entries) — their presence is a positive signal
- Ease factor distribution — are cards stuck at the default 2,500 (never properly reviewed)?

Students with zero type=1 reviews by E03 have not been returning to study their old cards —
they are creating or importing cards but not actually doing spaced repetition.

#### Step 4 — Mid-bimester check (after E02 for B1, after E06 for B2)

Compile a **mid-bimester dashboard** for the whole class. For each student, one row:

| Student | Cards | Reviews | Active ex. | Any cram? | Any flag? |
|---|---|---|---|---|---|
| ...     | cumulative | cumulative | N of M done | Y/N | list |

Sort by `Active ex.` descending to immediately see who is falling behind.
Sort by `Any flag?` to surface the forensic cases.

This is purely for instructor awareness — not for grading yet.

#### Step 5 — End of bimester (full grade computation)

Run the full Python script described in Part 3.

### 2.3 What NOT to do mid-bimester

- Do not compute the final bimester grade from partial data. Volume is valid at any point,
  but Quality (maturity sub-score) and Consistency (full distribution sub-score) only make
  sense when all exercises are in.
- Do not share individual scores with students until all submissions for the bimester are
  collected. Mid-bimester numbers will underestimate good students (whose cards haven't
  matured yet) and may inadvertently reward bad students who front-loaded activity.
- Do not use the Volume sub-score alone as a proxy for the final grade. Pietro scored high
  on raw review counts before cram exclusion. Volume without the other three components
  is meaningless.

---

## Part 3 — Ideas for the End-of-Bimester Python Script

This section describes what a Python script should do, component by component.
**No code is presented here** — this is a design brief for the implementation stage.

### 3.1 Inputs the script needs

1. **A directory of `.apkg` submissions** organised by exercise and student, as in the
   folder structure shown in Step 1 above.
2. **An exercise schedule file** (`exercise_schedule.json`) with the `creation_start`,
   `creation_end`, `review_start`, and `review_end` dates for each exercise in the bimester.
3. **The spreadsheet** (`geral.xlsx`) with the existing per-exercise metrics — used as
   a cross-validation source and as the primary source for Volume (since it is already
   curated by the instructor).
4. **The student roster** — ID, name, and which bimester (B1 or B2) is being processed.

### 3.2 Pre-processing stage

Before computing any scores, the script should:

- **Deduplicate submissions**: compute a hash (MD5 or SHA256) of each `.anki2` database
  file. If two files from the same student have the same hash, keep one and log the
  duplicate. If two files from *different* students have the same hash, raise a
  `TIER_1_COLLISION` alert (see `CHEATING_DETECTION.md § 4.1`).
- **Identify the database format**: check whether the `.apkg` contains `collection.anki21`
  (modern format) or only `collection.anki2` (older format). The older format implies
  the zero-time fallback may be needed.
- **Detect zero-time databases**: run Q7a from `ASSESSMENT_COMPONENT_COMPUTATION.md`
  and store a `time_data_missing` flag per student per submission.
- **Merge submissions per student**: some students submit multiple `.apkg` files for a
  single exercise (one per deck). The script must merge the revlog entries from all files
  for a student into a single virtual database for querying, being careful not to
  double-count cards that appear in multiple exports of the same collection.

### 3.3 Per-student, per-exercise queries

For each student and each exercise in the bimester, run queries Q1–Q8 from
`ASSESSMENT_COMPONENT_COMPUTATION.md`, filtered to the exercise's timestamp window.
Store the raw results in a structured format (e.g., a dictionary keyed by
`(student_id, exercise_id)`).

Key outputs per exercise:
- `cards_created` (Q1)
- `reviews_non_cram` (Q2)
- `review_days` (Q3)
- `last_day_reviews` (Q4)
- `retention_total`, `retention_successful` (Q5)
- `cards_total`, `cards_mature` (Q6)
- `time_data_missing` (Q7a)
- `time_total`, `time_engaged` (Q7b, only if not missing)
- `mean_factor` (Q8)
- `cram_review_count` (additional: `COUNT(*) WHERE type=3` — for the forensic flag)

### 3.4 Forensic flag computation

Before scoring, compute flags that will appear in the final table alongside the grade.
These are binary (Y/N) or categorical signals, not part of the grade formula itself, but
essential for the instructor to interpret borderline cases.

Flags to compute per student per bimester:

| Flag | Condition | Archetype |
|---|---|---|
| `CRAM_ABUSE` | type=3 ≥ 50 % of all revlog entries | Pietro (Archetype B) |
| `EASE_LOCK` | ease=4 ≥ 95 % AND relearn_count = 0 AND median_time < 2,000 ms | João Vitor (Archetype A) |
| `SUB_SECOND_MEDIAN` | median `revlog.time` < 1,500 ms | Jullia (Archetype A severe) |
| `NO_RELEARNING` | type=2 count = 0 across all exercises | Weak signal alone, strong in combination |
| `SINGLE_SESSION` | All reviews for an exercise in < 5 minutes | Archetype C ghost |
| `ZERO_TIME_DATA` | All `revlog.time = 0` | Murilo — client artifact, not cheating |
| `PARTIAL_SUBMISSION` | Missing expected decks for the exercise | Pedro Rafael / Kauã HACKER issue |
| `DUPLICATE_FILE` | Two files from same student with same hash | Gabrielle |

### 3.5 Component computation

With the per-exercise raw values in hand, aggregate them to the bimester level and apply
the formulas from `ASSESSMENT_COMPONENT_COMPUTATION.md`:

**Volume (V)**:
- Sum `cards_created` and `reviews_non_cram` across all exercises in the bimester.
- Store the class-level vectors to apply min-max normalization capped at the 95th percentile.
- Compute `cards_sub` and `reviews_sub`, then `V = 0.40 × cards_sub + 0.60 × reviews_sub`.

**Consistency (C)**:
- Count active exercises (`review_days > 0`) → `participation_sub`.
- Compute per-exercise cramming ratio → average → `distribution_sub`.
- `C = 0.50 × participation_sub + 0.50 × distribution_sub`.

**Quality (Q)**:
- Aggregate `retention_total` and `retention_successful` across all exercises →
  `retention_sub`.
- Aggregate `cards_total` and `cards_mature` → `maturity_sub`.
- Apply B1 maturity correction if fewer than 21 calendar days elapsed in the bimester
  (lower maturity weight to 0.15, raise retention weight to 0.85).
- `Q = 0.70 × retention_sub + 0.30 × maturity_sub` (or corrected weights for B1).

**Engagement (E)**:
- If `time_data_missing = 1`: `E = ease_sub` (100 % weight on ease factor).
- Otherwise: aggregate `time_total` and `time_engaged` → `time_sub`; compute
  `ease_sub` from mean `cards.factor`; `E = 0.50 × time_sub + 0.50 × ease_sub`.

**Final grade**:
- `grade = 0.25 × V + 0.25 × C + 0.30 × Q + 0.20 × E`
- Map to letter grade (A/B/C/D/F) using the bands in `ASSESSMENT_COMPONENT_COMPUTATION.md`.

### 3.6 Output table

The script should produce a single CSV or Excel table, one row per student, with these
columns in order:

| Column group | Columns |
|---|---|
| Identity | `student_id`, `name` |
| Volume | `total_cards`, `total_reviews_non_cram`, `V` |
| Consistency | `active_exercises`, `avg_cramming_ratio`, `C` |
| Quality | `retention_rate_pct`, `maturity_pct`, `Q` |
| Engagement | `time_engaged_pct`, `mean_ease_factor`, `time_data_missing`, `E` |
| Final | `bimester_grade`, `letter_grade` |
| Flags | `CRAM_ABUSE`, `EASE_LOCK`, `SUB_SECOND_MEDIAN`, `NO_RELEARNING`, `ZERO_TIME_DATA`, `PARTIAL_SUBMISSION` |

**Sort order**: by `bimester_grade` descending, so good students appear at the top and
bad students at the bottom. The flags column makes the bad students immediately visible
even if their grade landed higher than expected (e.g., a cram abuser who also did real
work in some exercises).

### 3.7 What the table tells you at a glance

- **Good student**: high grade, no flags, `retention_rate_pct > 70 %`, `maturity_pct > 50 %`,
  `time_engaged_pct > 60 %`.
- **Bad student**: any `CRAM_ABUSE`, `EASE_LOCK`, or `SUB_SECOND_MEDIAN` flag present.
  Grade will typically fall below 50 because Quality and Engagement components are near zero
  for these students even if Volume is inflated.
- **Borderline**: grade in the 55–70 range, no hard flags, but `NO_RELEARNING` present,
  or `time_engaged_pct` is low without a `ZERO_TIME_DATA` explanation. These are the students
  to look at manually.
- **Partial submitter** (Pedro Rafael / Kauã pattern): good grade on the component computed
  from the long-term deck, but `PARTIAL_SUBMISSION` flag on the exercise deck. Instructor
  must decide whether to apply a penalty to the Volume sub-score for the missing deck.

### 3.8 Additional tips for robustness

- **Run the script twice**: once including all submissions, once excluding students with
  `CRAM_ABUSE` or `EASE_LOCK` flags, to see how the Volume normalization changes when
  bad actors are removed. A single high-volume cheater can compress the min-max scale for
  the whole class.
- **Cross-validate Volume against the spreadsheet**: the script's `reviews_non_cram` count
  should approximately match `E0X-rev` from the spreadsheet. Large discrepancies (> 20 %)
  suggest a student submitted an incomplete collection or the exercise window dates are off.
- **Log every decision**: every flag raised, every fallback applied, every deduplication
  performed should be written to a log file alongside the final table so the instructor
  can audit the computation for any student.
- **Keep the raw per-exercise data**: the final table collapses everything to bimester level,
  but the per-exercise rows should be saved separately. They are needed for the mid-bimester
  monitoring procedure (Part 2) and for any grade dispute.
