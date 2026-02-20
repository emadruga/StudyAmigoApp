# 25-Question Placement Test Model for ESL Reading Ability Assessment

This document outlines a model for creating a 25-question placement test to assess English reading ability for ESL students from the Metrology, Biotechnology, and Cyber Security programs. The test is designed to replace the paid Duolingo placement test and will be administered via Google Form.

---

## Table of Contents

1. [Test Objectives](#1-test-objectives)
2. [Alignment with Three-Tier System](#2-alignment-with-three-tier-system)
3. [Question Distribution Model](#3-question-distribution-model)
4. [Question Types and Formats](#4-question-types-and-formats)
5. [Content Selection Strategy](#5-content-selection-strategy)
6. [Scoring and Tier Placement](#6-scoring-and-tier-placement)
7. [Implementation in Google Forms](#7-implementation-in-google-forms)
8. [Question Bank Development Process](#8-question-bank-development-process)
9. [Validation and Calibration](#9-validation-and-calibration)
10. [Sample Question Specifications](#10-sample-question-specifications)

---

## 1. Test Objectives

### 1.1. Primary Goals

The 25-question placement test must:

1. **Differentiate proficiency levels**: Accurately separate students into three tiers (Foundation, Developing, Expanding) based on reading ability.
2. **Predict E01 performance**: Correlate with the E01 diagnostic exercise performance described in [READING_MATERIAL_METHODOLOGY.md](../../server/docs/READING_MATERIAL_METHODOLOGY.md).
3. **Minimize test anxiety**: Use engaging, relevant content that reflects the students' technical domains. For students with no English background, avoid exposing them to 25 questions they cannot answer.
4. **Complete quickly**: Take approximately 5–20 minutes depending on the test path (avoiding fatigue effects).
5. **Provide actionable data**: Generate scores that directly inform tier placement without requiring extensive manual interpretation.
6. **Engage all proficiency levels**: Ensure that even students with zero English exposure have a positive, confidence-building first interaction with the course (v1.2).

### 1.2. What the Test Measures

- **Vocabulary recognition**: High-frequency words, cognates, and cross-domain technical terms
- **Sentence comprehension**: Understanding of simple to complex grammatical structures
- **Reading speed proxy**: Question difficulty progression reveals where student struggles begin
- **Contextual inference**: Ability to derive meaning from context (higher tiers)
- **Self-assessed proficiency**: The student's own perception of their English background, which serves as an additional placement signal (v1.2)

---

## 2. Alignment with Three-Tier System

The test must align with the proficiency characteristics defined in the three-tier system:

| Tier | Reading Level | Key Indicators | Target Score Range |
|------|--------------|----------------|-------------------|
| **Tier 1: Foundation** | No prior exposure or minimal passive exposure | Recognizes high-frequency words and cognates; struggles with simple past tense; requires visual/Portuguese support | Path A: 0–10 (out of 10) / Full test: 0–10 (out of 25) |
| **Tier 2: Developing** | High school English background | Can parse compound sentences; understands multiple tenses; limited vocabulary beyond top 1500 words | Full test: 11–18 correct (44–72%) |
| **Tier 3: Expanding** | Private English class background | Handles complex structures (passive voice, conditionals); strong academic vocabulary; inferential comprehension | Full test: 19–25 correct (76–100%) |

These ranges are **provisional** and must be calibrated after the first administration (see Section 9).

---

## 3. Question Distribution Model

### 3.1. Three-Path Entry Gate (v1.2)

The core design change in v1.2 is replacing the one-size-fits-all 25-question test with a **branching test** that routes students through different paths based on their self-assessed English background. This addresses the fundamental problem: for a student with zero English exposure, sitting through 25 questions in a language they cannot read is anxiety-inducing, uninformative (the score reflects guessing, not proficiency), and counterproductive (their first course interaction is a failure experience).

#### 3.1.1. The Self-Assessment Gate

Before any test questions, the Google Form presents a single routing question **entirely in Portuguese**:

> **Como você descreveria sua experiência com o idioma inglês?**
> *(How would you describe your experience with the English language?)*
>
> **a)** Nunca estudei inglês e não tenho contato com o idioma.
> *(I have never studied English and I have no contact with the language.)*
>
> **b)** Estudei inglês no ensino médio (escola pública ou particular), mas não me considero fluente.
> *(I studied English in high school (public or private), but I don't consider myself fluent.)*
>
> **c)** Já fiz curso de inglês ou me considero intermediário/avançado.
> *(I have taken English courses or I consider myself intermediate/advanced.)*

Based on the answer, the student is routed to one of three paths:

| Path | Self-Assessment | Questions Seen | Time Estimate | Purpose |
|------|----------------|---------------|---------------|---------|
| **Path A** | "Nunca estudei inglês" | Band 1 only (10 questions) | ~5 minutes | Confirm Tier 1; detect underestimators; build confidence through cognate recognition |
| **Path B** | "Estudei no ensino médio" | Full test (25 questions) | ~18 minutes | Standard placement across all three tiers |
| **Path C** | "Já fiz curso / intermediário+" | Full test (25 questions) | ~18 minutes | Standard placement; self-report data for validation |

**Google Forms implementation**: Use the "Go to section based on answer" feature on the routing question. Path A students go directly to Band 1 and then to the Thank You page. Path B and C students go through all three bands.

#### 3.1.2. Why Three Paths Instead of "Skip" vs. "Take"

A binary "skip the test" option was considered and rejected for three reasons:

1. **Everyone takes something**. Path A students still answer 10 questions, which produces usable data. A student who skips entirely gives us zero information — we cannot distinguish between "genuinely no English" and "anxious but actually knows something."

2. **Band 1 was designed for them**. The cognate-heavy questions (Q1: "important" = "importante") are specifically constructed to show Tier 1 students that English is more accessible than they assume. This is a *positive* first experience, not a test they fail.

3. **Detects underestimators**. A student who selects Path A but scores 8–10/10 on Band 1 is underestimating themselves — likely due to the Brazilian cultural pattern of saying "eu não sei nada de inglês" when they actually have passive knowledge from media, music, or casual exposure. These students should be flagged for the full test or directly considered for Tier 2 placement.

#### 3.1.3. The False-Skipper Problem

The opposite risk — students with real English ability selecting Path A to avoid a longer test — is mitigated by three factors:

1. **Path A is framed as positive, not as an escape**. The Portuguese wording ("Nunca estudei inglês e não tenho contato com o idioma") is specific enough that a student who studied English in high school would not honestly select it.

2. **E01 catches misplacements**. A false-skipper who ends up in Tier 1 but actually belongs in Tier 2 or 3 will show high E01 performance (Signal 2), triggering a tier reassignment within the first two weeks. The cost of a temporary misplacement is low.

3. **The instructor knows the students**. In a community college class of ~48 students, the instructor has face-to-face contact and can identify obvious mismatches early.

#### 3.1.4. The Self-Assessment as Signal 0

The routing question produces a new data point — **Signal 0: Self-reported background** — that enriches the placement system:

| Signal | Source | Data Type | Timing |
|--------|--------|-----------|--------|
| **Signal 0** | Self-assessment gate (v1.2) | Categorical: A, B, or C | Day 1 (before test) |
| **Signal 1** | Placement test score | Numeric: 0–10 (Path A) or 0–25 (Path B/C) | Day 1 (test) |
| **Signal 2** | E01 diagnostic performance | Numeric: retention rate, review time | Weeks 1–2 |

Having three signals instead of two increases placement accuracy, especially for edge cases:

- A student who self-reports Path A, scores 9/10 on Band 1, and shows high E01 performance → clear Tier 2 (self-assessment was too modest).
- A student who self-reports Path C, scores 12/25 on the full test, and shows medium E01 performance → Tier 2 (self-assessment was too generous).
- A student who self-reports Path A, scores 3/10 on Band 1, and shows low E01 performance → confirmed Tier 1 (all three signals agree).

### 3.2. Difficulty Pyramid Structure

The full test (Paths B and C) follows a pyramid structure: many easy questions at the base (to avoid discouraging Tier 1 students), fewer questions at mid-level, and several challenging questions at the top (to distinguish Tier 3 students).

| Difficulty Band | Question Count | Purpose | Target Audience |
|----------------|----------------|---------|----------------|
| **Band 1: Foundation** | 10 questions (Q1–Q10) | Assess basic vocabulary and simple sentence comprehension | All students should attempt; Tier 1 diagnostic zone |
| **Band 2: Developing** | 8 questions (Q11–Q18) | Assess compound sentences, multiple tenses, contextual vocabulary | Tier 2 diagnostic zone; Tier 1 students may struggle |
| **Band 3: Expanding** | 7 questions (Q19–Q25) | Assess complex structures, academic vocabulary, inference | Tier 3 diagnostic zone; distinguishes high proficiency |

Path A students see only Band 1. Path B and C students see all three bands.

### 3.3. Rationale for Uneven Distribution

- **More foundational questions** ensure Tier 1 students can answer enough to feel competent (avoiding test anxiety and dropout).
- **Fewer expanding questions** are sufficient to identify Tier 3 students — if a student correctly answers 5+ questions in Band 3, they clearly belong in Tier 3.
- **Google Forms limitation**: Unlike adaptive testing (e.g., Duolingo), all students on a given path see the same questions. The pyramid structure compensates by ensuring all students have accessible questions.

### 3.4. Anchor Questions

Two questions in the test serve a special psychometric role as **anchor questions**:

- **Anchor-Easy (Q1)**: Designed so that virtually all test-takers — including Path A students with no English background — should answer correctly. A student who gets Q1 wrong is a signal of test-taking behavior issues (anxiety, did not read, language barrier with the instructions themselves) rather than proficiency level. These students should be flagged for an in-person conversation with the instructor rather than relying solely on the score.

- **Anchor-Hard (Q25)**: Designed so that only strong Tier 3 students are expected to answer correctly. A student who answers Q25 correctly is a strong signal of high proficiency, even if their total score is borderline. This is especially useful for students near the 18–19 boundary. Only Path B and C students see this question.

Anchor questions are not scored differently (each is still worth 1 point), but their results should be inspected separately during item analysis (Section 9.2) and when reviewing edge-case students.

### 3.5. Distractor Design Principles

Distractors (incorrect options) should be plausible enough to discriminate between proficiency levels. Poorly designed distractors — those that no test-taker would ever select — reduce a question's discriminating power. Guidelines:

- **Band 1**: At least one distractor should be a **false cognate** or a word that looks/sounds similar to the correct answer. Avoid absurd distractors that are obviously wrong even without knowing English (e.g., "Darkness" as what plants need to grow, when the question is about sunlight).
- **Band 2**: Distractors should represent common errors that Tier 1 students make (e.g., wrong verb tense, wrong preposition) but that Tier 2 students can avoid.
- **Band 3**: Distractors should include grammatically correct but semantically wrong options, or options that require careful reading to distinguish from the correct answer.

---

## 4. Question Types and Formats

### 4.1. Question Type Distribution (Total: 25)

| Question Type | Count | Description | Difficulty Bands Used |
|--------------|-------|-------------|----------------------|
| **A. Vocabulary Matching** | 6 | Match English word to Portuguese translation or English definition | Band 1 (4), Band 2 (2) |
| **B. Sentence Completion (Cloze)** | 7 | Fill in the blank in a sentence with the correct word | Band 1 (3), Band 2 (3), Band 3 (1) |
| **C. Reading Comprehension (Short)** | 8 | Answer questions about a 2–5 sentence passage | Band 1 (2), Band 2 (3), Band 3 (3) |
| **D. Grammar Recognition** | 4 | Identify correct verb tense, sentence structure, or grammatical form | Band 2 (2), Band 3 (2) |

**Path A students** see only the 10 Band 1 questions: 4 Vocabulary Matching (A), 3 Sentence Completion (B), and 2 Reading Comprehension (C). No Grammar Recognition (D) questions appear in Band 1.

### 4.2. Detailed Question Type Specifications

#### A. Vocabulary Matching

**Format**: Multiple choice (4 options).

**Example (Band 1 - Cognate)**:
```
What does "important" mean?
a) Importante
b) Impossível
c) Importar
d) Impressionante
```

**Example (Band 2 - Non-Cognate)**:
```
What is the best definition of "achieve"?
a) To receive something
b) To reach a goal successfully
c) To believe in something
d) To teach someone
```

#### B. Sentence Completion (Cloze)

**Format**: Multiple choice (4 options).

**Example (Band 1)**:
```
The sun is very _____ today.
a) cold
b) hot
c) dark
d) small
```

**Example (Band 3)**:
```
The data was _____ by the research team after three months of fieldwork.
a) collected
b) collecting
c) collects
d) collection
```

#### C. Reading Comprehension (Short)

**Format**: Passage followed by 1–2 multiple-choice questions.

**Example (Band 1 - 2 sentences)**:
```
Passage: "Water freezes at 0 degrees Celsius. Ice is frozen water."

Question: What is ice?
a) Hot water
b) Frozen water
c) Cold air
d) Steam
```

**Example (Band 3 - 4-5 sentences, inferential)**:
```
Passage: "Cybersecurity experts recommend changing passwords regularly. However, many
people reuse the same password across multiple websites. This practice significantly
increases the risk of identity theft. If one website is compromised, all accounts using
that password become vulnerable."

Question: Why is reusing passwords dangerous?
a) Because passwords expire quickly
b) Because it makes accounts harder to access
c) Because one data breach can expose all accounts
d) Because experts recommend it
```

#### D. Grammar Recognition

**Format**: Multiple choice (4 options).

**Example (Band 2)**:
```
Which sentence is correct?
a) She go to the laboratory yesterday.
b) She goes to the laboratory yesterday.
c) She went to the laboratory yesterday.
d) She going to the laboratory yesterday.
```

**Example (Band 3)**:
```
Which sentence uses the passive voice correctly?
a) The experiment conducts by the students.
b) The experiment was conducted by the students.
c) The experiment is conducting by the students.
d) The students conducted the experiment. (Note: active voice, not passive)
```

---

## 5. Content Selection Strategy

### 5.1. Vocabulary Sources

- **Band 1**: Oxford 3000 high-frequency words + Portuguese-English cognates (e.g., "technology", "important", "system", "control", "problem")
- **Band 2**: Top 1500 most common English words + cross-domain technical vocabulary (e.g., "measurement", "accuracy", "data", "analysis")
- **Band 3**: Academic Word List (Coxhead) + semi-technical terms from Metrology, Biotechnology, and Cyber Security

### 5.2. Thematic Consistency

All passages and example sentences should relate to one or more of these cross-domain themes:

- Science and technology
- Measurement and accuracy
- Data and information
- Health and safety
- Systems and processes
- Problem-solving

**Rationale**: These themes are familiar to students from all three technical programs, reducing cognitive load from unfamiliar content and focusing the assessment on language ability.

### 5.3. Cognate Strategy

- **Band 1 (40% cognate density)**: Heavy use of cognates to allow Tier 1 students to demonstrate recognition ability. This is especially important for Path A students, where the cognate-rich Band 1 questions are the *only* questions they see — the experience should demonstrate that English is more accessible than they assume.
- **Band 2 (20% cognate density)**: Moderate cognate presence; introduce some false friends (e.g., "actually" vs. "atualmente").
- **Band 3 (<10% cognate density)**: Minimal reliance on cognates; test true English proficiency.

### 5.4. Reading Passage Length Progression

Within bands that use reading comprehension questions, passage length should increase progressively to create a smooth difficulty curve:

| Question | Band | Passage Length | Comprehension Type |
|----------|------|---------------|-------------------|
| Q5 | Band 1 | 2 sentences | Literal |
| Q8 | Band 1 | 2 sentences | Literal |
| Q13 | Band 2 | 3 sentences | Literal + reorganization |
| Q16 | Band 2 | 4 sentences | Reorganization |
| Q19 | Band 3 | 3–4 sentences | Inferential (entry-level Band 3) |
| Q22 | Band 3 | 5 sentences | Inference + vocabulary |
| Q25 | Band 3 | 5 sentences | Inference + synthesis (anchor-hard) |

**Rationale**: A student who handles a 3-sentence passage in Band 2 but fails on a 5-sentence passage in Band 3 reveals a clear proficiency boundary. Within Band 3 specifically, starting with a shorter passage (Q19) and progressing to longer ones (Q22, Q25) avoids an abrupt difficulty jump at the band transition and produces finer-grained discrimination among Tier 3 candidates.

---

## 6. Scoring and Tier Placement

### 6.1. Raw Score Calculation

Scoring depends on the test path:

| Path | Questions Answered | Maximum Score | Scoring Basis |
|------|-------------------|---------------|---------------|
| **Path A** | 10 (Band 1 only) | 10 | Out of 10 |
| **Path B** | 25 (all bands) | 25 | Out of 25 |
| **Path C** | 25 (all bands) | 25 | Out of 25 |

- Each question is worth 1 point (no partial credit).
- Google Forms automatically calculates the score when answer keys are provided.
- Path A and Path B/C scores are **not directly comparable** and must be interpreted using separate scales (see Section 6.2).

### 6.2. Tier Placement Thresholds

#### Path A Students (Band 1 only, out of 10)

| Raw Score | Percentage | Recommended Action | Rationale |
|-----------|-----------|-------------------|-----------|
| 0–4 | 0–40% | **Tier 1 (confirmed)** | Score near or below guessing level (~2.5 expected from random). All three signals agree: self-assessment = no English, test = low score. High confidence. |
| 5–7 | 50–70% | **Tier 1 (provisional)** | Student has some recognition ability (likely cognates). Confirm with E01. Likely solid Tier 1 but with a foundation to build on. |
| 8–10 | 80–100% | **Flag: possible underestimator** | Student selected "never studied English" but scored high on Band 1. Two possibilities: (a) passive exposure from media/music gave them more English than they realize, or (b) strong cognate recognition from Portuguese. **Recommendation**: offer these students the option to take the full test (Bands 2 + 3) as a follow-up, or provisionally place in Tier 1 and let E01 data decide. If E01 performance is medium or high, move to Tier 2. |

#### Path B and C Students (Full test, out of 25)

| Raw Score | Percentage | Recommended Tier | Confidence Level |
|-----------|-----------|-----------------|-----------------|
| 0–10 | 0–40% | **Tier 1: Foundation** | High confidence if score ≤ 8; review manually if 9–10. Note: a Path B student who scores 0–10 may have been better served by Path A — this informs threshold calibration (see Section 9.3). |
| 11–18 | 44–72% | **Tier 2: Developing** | This is the widest band; most Path B students will fall here. |
| 19–25 | 76–100% | **Tier 3: Expanding** | High confidence if score ≥ 20. Most Path C students should score here if their self-assessment is accurate. |

### 6.3. Three-Signal Placement Matrix (v1.2)

Final tier assignment now uses **three signals** instead of two:

#### For Path A Students

| Signal 0 (Self-Report) | Signal 1 (Band 1 Score) | Signal 2 (E01 Performance) | Final Tier |
|------------------------|------------------------|---------------------------|------------|
| Path A ("never studied") | Low (0–4) | Low | Tier 1 (confirmed — all signals agree) |
| Path A ("never studied") | Low (0–4) | Medium | Tier 1 (E01 may reflect hard work, not prior knowledge) |
| Path A ("never studied") | Low (0–4) | High | Tier 1 or 2 (instructor judgment — unexpected E01 performance) |
| Path A ("never studied") | Medium (5–7) | Low | Tier 1 (confirmed) |
| Path A ("never studied") | Medium (5–7) | Medium | Tier 1 (confirmed, with upward potential) |
| Path A ("never studied") | Medium (5–7) | High | Tier 2 (self-assessment was too modest) |
| Path A ("never studied") | High (8–10) | Low | Tier 1 (strong cognate recognition but weak retention) |
| Path A ("never studied") | High (8–10) | Medium | Tier 2 (underestimator confirmed) |
| Path A ("never studied") | High (8–10) | High | Tier 2 (clear underestimator — offer full test for next semester) |

#### For Path B and C Students

| Signal 0 (Self-Report) | Signal 1 (Full Test Score) | Signal 2 (E01 Performance) | Final Tier |
|------------------------|--------------------------|---------------------------|------------|
| Path B/C | Low (0–10) | Low | Tier 1 (confirmed) |
| Path B/C | Low (0–10) | Medium | Tier 1 or 2 (instructor judgment) |
| Path B/C | Low (0–10) | High | Tier 2 (test underestimated) |
| Path B/C | Medium (11–18) | Low | Tier 1 (test overestimated) |
| Path B/C | Medium (11–18) | Medium | Tier 2 (confirmed) |
| Path B/C | Medium (11–18) | High | Tier 2 or 3 (instructor judgment) |
| Path B/C | High (19–25) | Low | Tier 2 (test overestimated) |
| Path B/C | High (19–25) | Medium | Tier 2 or 3 (instructor judgment) |
| Path B/C | High (19–25) | High | Tier 3 (confirmed) |

**Additional cross-check for Path C students**: A student who self-reports Path C ("intermediate/advanced") but scores in the Low range (0–10) is a strong signal of self-assessment inflation. This is less common than underestimation but worth flagging.

**E01 performance metrics** (from the curated shared deck review):
- **Low**: Retention rate < 50%, or average review time > 20 seconds per card.
- **Medium**: Retention rate 50–75%, average review time 8–20 seconds.
- **High**: Retention rate > 75%, average review time < 8 seconds.

### 6.4. Edge Case Handling

- **Scores of 9–10 or 19–20 (Path B/C)**: Students near tier boundaries should be flagged for manual review before final placement.
- **Path A students scoring 8–10**: See Section 6.2 — these are potential underestimators and should be offered a follow-up full test or monitored closely during E01.
- **Anchor question signals**: A student who scores 9–10 but answered Q25 (anchor-hard) correctly may belong in Tier 2. A student who scores 11–12 but missed Q1 (anchor-easy) may have been guessing or had test-taking issues.
- **Guessing correction**: No penalty for wrong answers. On Path A (10 questions, 4 options each), random guessing yields ~2.5 correct. On the full test (25 questions), random guessing yields ~6.25 correct. Students scoring at or near the guessing floor should be flagged; E01 data is critical for these students.
- **Path B students scoring 0–10**: A student who self-reported "studied in high school" but scored in the Tier 1 range may have overestimated, or may have experienced test anxiety. The instructor should check whether these students would have been better served by Path A — this information calibrates the self-assessment gate for future semesters.

### 6.5. Mitigating Random Guessing

Random guessing yields different expected scores depending on the path:

| Path | Questions | Expected Guessing Score | Standard Deviation | Plausible Lucky Score |
|------|-----------|------------------------|-------------------|----------------------|
| Path A | 10 | ~2.5 | ~1.4 | 4–5 |
| Path B/C | 25 | ~6.25 | ~2.2 | 8–9 |

**Mitigation strategies** (tradeoffs noted):

1. **Rely on the three-signal system**: The E01 diagnostic exercise (Signal 2) is immune to guessing — it measures actual card review behavior over 1–2 weeks. The self-assessment (Signal 0) adds a qualitative cross-check. A guesser on the placement test who genuinely has no English ability will show low E01 performance, confirming Tier 1 placement. This is the primary defense.

2. **Path A reduces guessing impact**: A student who genuinely has no English and selects Path A will guess on 10 questions instead of 25. The expected guessing score (~2.5 out of 10) falls in the "Tier 1 confirmed" range (0–4), where guessing and genuine zero-knowledge produce the same placement outcome. This is a significant improvement over v1.1, where the same student would guess across 25 questions and potentially score 8–9 — high enough to cause confusion.

3. **Consider 2–3 short-answer questions in future versions** (optional): Google Forms supports short-answer questions with answer validation. Replacing 2–3 Band 1 vocabulary questions with short-answer (e.g., "Type the English word for 'casa'") would reduce guessing noise. However, this introduces spelling tolerance issues and complicates automatic grading. **Recommendation**: Defer to Version 2 after reviewing first-semester guessing patterns.

4. **Inspect per-band scores (Path B/C only)**: A student who scores 6/10 on Band 1 but 0/8 on Band 2 and 0/7 on Band 3 (total: 6) likely guessed on Band 1. A student who scores 8/10 on Band 1 but 1/8 on Band 2 and 0/7 on Band 3 (total: 9) likely has real Band 1 knowledge. Google Sheets formulas can flag these patterns automatically.

---

## 7. Implementation in Google Forms

### 7.1. Google Forms Features to Use

1. **Quiz Mode**: Enable Quiz mode to allow automatic grading.
2. **Answer Key**: Provide correct answers for each question so Google Forms calculates the score.
3. **Section Breaks**: Divide the test into sections with branching logic.
4. **Go to section based on answer**: Route students to different sections based on the self-assessment gate response (v1.2).
5. **Required Questions**: Make all questions required to prevent partial submissions.
6. **Response Validation**: Use email collection to link scores to student identities.
7. **Immediate Feedback Option**: Consider providing the score immediately after submission (transparency) OR withholding it until the instructor reviews (to prevent student anxiety).

### 7.2. Google Forms Structure (v1.2 — Branching Architecture)

The form uses Google Forms' "Go to section based on answer" feature to implement the three-path entry gate. All meta-instructions are **bilingual (English and Portuguese)** to ensure accessibility for all proficiency levels.

```
============================================================
PAGE 1: INSTRUCTIONS & SELF-ASSESSMENT GATE
============================================================

[Instructions / Instruções]

- Test purpose / Objetivo do teste:
  PT: "Este teste avalia seu nível atual de leitura em inglês. Ele nos
      ajudará a indicar materiais de leitura adequados ao seu nível."
  EN: "This test assesses your current English reading level. It will help
      us assign reading materials that match your level."

- Important note / Nota importante:
  PT: "Este teste NÃO conta como nota. Ele é usado apenas para nos
      ajudar a escolher os materiais certos para você."
  EN: "This test does NOT count as a grade. It is only used to help us
      choose the right materials for you."

- Request: Student name (Nome do aluno) and email (Email)
- Request: Program (Curso): Metrologia / Biotecnologia / Cibersegurança

[Self-Assessment Gate / Autoavaliação]

  PT: "Como você descreveria sua experiência com o idioma inglês?"
  EN: "How would you describe your experience with the English language?"

  a) "Nunca estudei inglês e não tenho contato com o idioma."
     ("I have never studied English and I have no contact with the language.")
     → Go to: SECTION 2 (Band 1 — Path A)

  b) "Estudei inglês no ensino médio (escola pública ou particular),
      mas não me considero fluente."
     ("I studied English in high school, but I don't consider myself fluent.")
     → Go to: SECTION 2 (Band 1 — Path B/C)

  c) "Já fiz curso de inglês ou me considero intermediário/avançado."
     ("I have taken English courses or I consider myself intermediate/advanced.")
     → Go to: SECTION 2 (Band 1 — Path B/C)

============================================================
SECTION 2: BAND 1 — FOUNDATION (Q1–Q10) [ALL PATHS]
============================================================

- Header:
  PT: "Parte 1: Vocabulário Básico e Frases"
  EN: "Part 1: Basic Vocabulary and Sentences"

- Time guidance:
  PT: "Tempo estimado: ~5 minutos"
  EN: "Estimated time: ~5 minutes"

- Worked Example / Exemplo Resolvido:
  PT: "Antes de começar, veja este exemplo de como responder as questões:"
  EN: "Before you start, look at this example of how to answer the questions:"

  ┌─────────────────────────────────────────────────┐
  │  Example / Exemplo:                             │
  │                                                 │
  │  What does "university" mean?                   │
  │  a) Universidade  ← ✅ Resposta correta!       │
  │  b) Uniforme                                    │
  │  c) Universal                                   │
  │  d) Único                                       │
  │                                                 │
  │  A pergunta "What does X mean?" significa       │
  │  "O que X significa?"                           │
  │  Escolha a opção que melhor traduz ou define    │
  │  a palavra em inglês.                           │
  └─────────────────────────────────────────────────┘

- Questions 1–10 (Band 1 difficulty)

- Section end routing:
  - Path A students → Go to: THANK YOU PAGE
  - Path B/C students → Go to: SECTION 3 (Band 2)

============================================================
SECTION 3: BAND 2 — DEVELOPING (Q11–Q18) [PATH B/C ONLY]
============================================================

- Header:
  PT: "Parte 2: Leitura Intermediária"
  EN: "Part 2: Intermediate Reading"

- Time guidance:
  PT: "Tempo estimado: ~6 minutos"
  EN: "Estimated time: ~6 minutes"

- Encouragement note:
  PT: "Estas questões são mais difíceis. Faça o seu melhor!
      Não há penalidade para respostas erradas."
  EN: "These questions are more difficult. Do your best!
      There is no penalty for wrong answers."

- Questions 11–18 (Band 2 difficulty)

→ Go to: SECTION 4 (Band 3)

============================================================
SECTION 4: BAND 3 — EXPANDING (Q19–Q25) [PATH B/C ONLY]
============================================================

- Header:
  PT: "Parte 3: Leitura Avançada"
  EN: "Part 3: Advanced Reading"

- Time guidance:
  PT: "Tempo estimado: ~7 minutos"
  EN: "Estimated time: ~7 minutes"

- Encouragement note:
  PT: "Estas questões são desafiadoras. Se não tiver certeza,
      faça sua melhor tentativa."
  EN: "These questions are challenging. If you are unsure,
      make your best guess."

- Questions 19–25 (Band 3 difficulty)

→ Go to: THANK YOU PAGE

============================================================
THANK YOU PAGE
============================================================

- PT: "Obrigado por completar o teste! Seus resultados nos ajudarão
      a indicar materiais de leitura adequados ao seu nível.
      Você NÃO precisa fazer mais nada agora."
  EN: "Thank you for completing the test! Your results will help us
      assign reading materials that match your level.
      You do NOT need to do anything else now."

- (Optional) Display score if immediate feedback is enabled
```

### 7.3. Google Forms Branching Implementation Notes (v1.2)

Google Forms' "Go to section based on answer" has one constraint relevant to this design: **branching is per-section, not per-question**. This means:

1. The self-assessment gate must be in its own section (Page 1), with the routing question as the last question in that section.
2. All three paths share the same Band 1 section. The branching happens *after* Band 1 completes: Path A students are routed to the Thank You page, while Path B/C students continue to Band 2.
3. To route Path A students away after Band 1, a **hidden routing question** at the end of the Band 1 section can be used. This question restates the path (e.g., "Which path were you assigned?") with pre-filled options, and its "Go to section" setting routes accordingly. Alternatively, if Google Forms preserves the original answer for section routing, the form can be structured so that Path A's "next section" is the Thank You page while Path B/C's "next section" is Band 2.

**Testing note**: Before deploying, test the form with three dummy submissions (one per path) to verify that branching works correctly and that scores are calculated properly for both 10-question and 25-question paths.

### 7.4. Data Export

Google Forms automatically exports responses to Google Sheets. Required fields for export:

- Timestamp
- Student name
- Student email
- Student program (Metrologia / Biotecnologia / Cibersegurança)
- **Self-assessment path** (A, B, or C) — Signal 0 (v1.2)
- Raw score (out of 10 for Path A, out of 25 for Path B/C)
- Individual question responses (for item analysis)

**Important**: Path A students will have blank responses for Q11–Q25. Google Sheets formulas must account for this — use `COUNTIF` only over the questions the student actually answered, not across all 25 columns.

### 7.5. Per-Band Score Breakdown in Google Sheets

In addition to the raw total score, the linked Google Sheet should include formulas to calculate **per-band subtotals**:

- **Band 1 subtotal** (out of 10): All paths
- **Band 2 subtotal** (out of 8): Path B/C only (blank for Path A)
- **Band 3 subtotal** (out of 7): Path B/C only (blank for Path A)
- **Path indicator**: Derived from the self-assessment response (A, B, or C)

These subtotals are critical for:
- Identifying guessing patterns (Section 6.5).
- Item analysis during validation (Section 9.2).
- Understanding where each student's proficiency breaks down (e.g., strong on vocabulary but weak on reading comprehension).
- Detecting underestimators (Path A students with Band 1 score ≥ 8).

---

## 8. Question Bank Development Process

### 8.1. Step 1: Generate Question Pool (Target: 50 questions)

To allow for future test revisions and prevent question leakage (students sharing answers), create a pool of **50 questions** distributed as follows:

| Difficulty Band | Target Pool Size | Questions per Test | Surplus |
|----------------|-----------------|-------------------|---------|
| Band 1 | 20 questions | 10 per test | 10 extra |
| Band 2 | 16 questions | 8 per test | 8 extra |
| Band 3 | 14 questions | 7 per test | 7 extra |

### 8.2. Step 2: Question Writing Guidelines

For each question, document:

1. **Question ID**: Unique identifier (e.g., `B1_VOCAB_001`, `B3_COMP_005`)
2. **Difficulty Band**: 1, 2, or 3
3. **Question Type**: A, B, C, or D
4. **Correct Answer**: Indicate which option is correct
5. **Distractor Rationale**: Why each incorrect option is plausible but wrong
6. **Vocabulary Level**: List key words and their frequency rank
7. **Cognate Status**: Indicate if the question relies on cognates
8. **Anchor Role**: Indicate if the question serves as anchor-easy or anchor-hard (v1.1)
9. **Path Visibility**: Which paths see this question — "All" for Band 1, "B/C only" for Bands 2–3 (v1.2)

**Example Entry**:
```
ID: B1_VOCAB_003
Band: 1 (Foundation)
Type: A (Vocabulary Matching)
Anchor: No
Path Visibility: All (Band 1)
Question: What does "system" mean?
Options:
  a) Sistema (CORRECT - cognate)
  b) Problema
  c) Assistente
  d) Sistema nervoso
Distractor Rationale:
  - Option b: Similar-sounding word
  - Option c: Partial cognate confusion
  - Option d: Compound phrase that includes the word but is too specific
Vocabulary: "system" (rank 247 in Oxford 3000)
Cognate: Yes (Portuguese "sistema")
```

### 8.3. Step 3: Peer Review

Each question should be reviewed by:

1. **Content expert**: Ensures technical accuracy of any domain-specific terms.
2. **Language expert**: Ensures grammatical correctness and appropriate difficulty.
3. **Portuguese speaker**: Validates cognate assumptions and translation accuracy.

**v1.1 addition**: During peer review, specifically verify:
- That each question has exactly **one unambiguously correct answer** (see Q7 and Q18 fixes in Section 10 for examples of what can go wrong).
- That distractors are plausible enough to attract students who genuinely do not know the answer (see Section 3.5 for distractor design principles).

**v1.2 addition**: During peer review, also verify:
- That Band 1 questions work as a **standalone 10-question test** for Path A students. This means Band 1 should cover a reasonable spread of question types (vocabulary, sentence completion, reading comprehension) and should not assume the student has seen any other questions.
- That the **worked example** (Section 7.2) accurately represents the question format used in Band 1.

### 8.4. Step 4: Pilot Testing

Before full deployment:

1. **Internal pilot**: 5–10 volunteers (colleagues or former students) take the test and provide feedback on clarity, difficulty, and time required. **Include at least 2 volunteers who take Path A only** to verify that the 10-question experience feels complete and not abruptly cut short (v1.2).
2. **Small student pilot**: 10–15 students take the test, and their scores are compared to their self-reported English experience to check for face validity.
3. **Branching test**: Verify that Google Forms routing works correctly for all three paths (v1.2).

---

## 9. Validation and Calibration

### 9.1. First Semester: Data Collection

When the test is first administered:

1. **Collect self-assessment responses** (Signal 0) for all students — how many chose Path A, B, C.
2. **Collect placement test scores** (Signal 1) for all students (N ≈ 40–50). Track Path A scores (out of 10) and Path B/C scores (out of 25) separately.
3. **Collect E01 diagnostic data** (Signal 2) — retention rate, review time, ease distribution — for all students.
4. **Record final tier placements** decided by the instructor using the combined signals.

### 9.2. Post-Semester Analysis

After the first semester, perform these analyses:

1. **Path distribution**: How many students chose each path?

   | Path | Expected Distribution | If Significantly Different |
   |------|----------------------|--------------------------|
   | Path A | ~30% (~15 students) | If >50%: the wording may be attracting false-skippers. If <15%: students may be overestimating or afraid to admit no English. |
   | Path B | ~50% (~24 students) | This should be the largest group (high-school English background). |
   | Path C | ~20% (~10 students) | If very low (<10%): students may not be selecting this even when appropriate. |

2. **Score distribution** (by path):
   - **Path A**: Plot histogram of Band 1 scores (0–10). Look for bimodal distribution (cluster near 2–3 = genuine Tier 1, cluster near 7–9 = underestimators).
   - **Path B/C**: Plot histogram of full test scores (0–25). Ideally, scores should spread across the range with peaks near 6, 14, and 22.

3. **Self-assessment accuracy**: Compare Signal 0 (self-report) with Signal 1 (test score) and Signal 2 (E01 performance):
   - **Path A underestimators**: How many Path A students scored ≥ 8/10 on Band 1? How many were eventually placed in Tier 2?
   - **Path C overestimators**: How many Path C students scored < 15/25? How many were eventually placed in Tier 1 or low Tier 2?
   - This data calibrates the self-assessment gate wording for future semesters.

4. **Correlation with E01 performance**:
   - Calculate Pearson correlation between placement test score and E01 retention rate.
   - Calculate separately for Path A and Path B/C students.
   - Expected: r > 0.6 (moderate to strong positive correlation) for Path B/C. Path A correlation may be lower due to restricted range (all Tier 1).

5. **Item analysis** (per question):
   - **Difficulty index**: Percentage of students who answered correctly. Target distribution:
     - Band 1: 70–90% correct (easy)
     - Band 2: 40–70% correct (medium)
     - Band 3: 10–40% correct (hard)
   - **Discrimination index**: Correlation between getting a specific question correct and overall test score. Questions with discrimination index < 0.2 should be revised or removed.
   - **Band 1 analysis for Path A students specifically**: Do the 10 Band 1 questions discriminate well within the Tier 1 population? If all Path A students score 2–4, the questions may be too hard for this population (or guessing-dominated). If all score 7–10, the questions are too easy and Path A is not providing useful data.

6. **Anchor question analysis** (v1.1):
   - **Q1 (anchor-easy)**: Expected difficulty index > 95%. If significantly lower, investigate whether the worked example was unclear or whether the student population has lower baseline proficiency than expected.
   - **Q25 (anchor-hard)**: Expected difficulty index 15–30% (among Path B/C students only). If higher, Band 3 may be too easy overall. If lower than 10%, the question may be too difficult even for Tier 3 students.

7. **Predictive validity**:
   - Do students placed in Tier 1 based on the test actually struggle with Tier 2 material later in the semester?
   - Do students placed in Tier 3 actually perform well on Tier 3 passages?
   - Do Path A students who were flagged as underestimators (score ≥ 8/10) actually perform better than other Tier 1 students in E01?

### 9.3. Threshold Adjustment

Based on the first-semester data:

- If too many students score in the 11–18 range (>60% of Path B/C students), the test is not differentiating well. Consider adding more Band 1 and Band 3 questions.
- If almost no Path B/C students score in Band 1 or Band 3, the test is too easy or too hard overall. Adjust question difficulty.
- If placement test scores do not correlate with E01 performance (r < 0.4), the test may be measuring something other than reading ability (e.g., test-taking skill, anxiety). Revise question types.
- **Self-assessment gate calibration** (v1.2): If too many Path A students turn out to be underestimators (>30% scoring ≥ 8/10), consider revising the Path A wording to be more specific (e.g., adding "e não consigo reconhecer palavras em inglês" — "and I cannot recognize English words") or adding a second screening question.
- **Path B low-scorers** (v1.2): If many Path B students score 0–5 on the full test, the self-assessment gate is not filtering effectively. Consider whether these students should have been routed to Path A, and adjust the Path B wording accordingly.

### 9.4. Iterative Refinement

Use the surplus questions from the 50-question pool to create **Version 2** of the test for Semester 2, replacing poorly performing questions. Continue this process each semester.

---

## 10. Sample Question Specifications

This section provides 25 fully specified sample questions (one complete test version) to serve as a template.

### Band 1: Foundation (Questions 1–10) — All Paths

*Path A students see only this section. Path B/C students see this section plus Bands 2 and 3.*

#### Q1 (Type A: Vocabulary Matching - Cognate) [ANCHOR-EASY]
**Question**: What does "important" mean?
**Options**:
a) Importante ✓
b) Impossível
c) Importar
d) Impressionante

**Rationale**: Direct cognate. Virtually all test-takers should answer correctly. Serves as the **anchor-easy** question: a student who misses Q1 is flagged for instructor follow-up (possible test anxiety, misunderstanding of instructions, or extremely low proficiency). The worked example at the top of Band 1 (Section 7.2) uses a similar cognate question ("university" = "universidade") to demonstrate the format, so even Path A students should understand what is being asked.

---

#### Q2 (Type A: Vocabulary Matching - Cognate)
**Question**: What does "control" mean?
**Options**:
a) Controlar / controle ✓
b) Contrato
c) Construir
d) Consultar

**Rationale**: High-frequency technical term, direct cognate.

---

#### Q3 (Type B: Sentence Completion - Present Simple)
**Question**: The temperature _____ 25 degrees.
**Options**:
a) are
b) is ✓
c) am
d) be

**Rationale**: Basic subject-verb agreement. "Temperature" is singular, requires "is".

---

#### Q4 (Type B: Sentence Completion - High-Frequency Adjective)
**Question**: Water is _____ for life.
**Options**:
a) necessary ✓
b) impossible
c) dangerous
d) expensive

**Rationale**: "Necessary" is a cognate (necessário). Context clue: water = essential.

---

#### Q5 (Type C: Reading Comprehension - 2 sentences, literal)
**Passage**: "A thermometer measures temperature. Temperature tells us if something is hot or cold."
**Question**: What does a thermometer measure?
**Options**:
a) Weight
b) Temperature ✓
c) Time
d) Distance

**Rationale**: Direct literal comprehension. Answer is in the first sentence.

---

#### Q6 (Type A: Vocabulary Matching - High-Frequency)
**Question**: What does "big" mean?
**Options**:
a) Pequeno
b) Grande ✓
c) Médio
d) Vazio

**Rationale**: One of the most common English adjectives. No cognate, but very basic.

---

#### Q7 (Type B: Sentence Completion - Common Verb)
**Question**: I _____ water every day.
**Options**:
a) eat
b) drink ✓
c) sleep
d) read

**Rationale**: Verb-object collocation. "Drink water" is a basic phrase. All options are base form (first person singular), so the question tests vocabulary (which verb collocates with "water"), not grammar.

**v1.1 fix**: Changed from "eats/drinks/sleeps/reads" (third-person forms) to "eat/drink/sleep/read" (base forms). The original version had a subject-verb agreement conflict: "I" requires base form, but the correct answer "drinks" was in third-person singular. This created an ambiguity where no option was fully correct.

---

#### Q8 (Type C: Reading Comprehension - 2 sentences, literal)
**Passage**: "The sun gives light and energy to the Earth. Plants use sunlight to make food and grow."
**Question**: What do plants use to grow?
**Options**:
a) Water and soil
b) Sunlight ✓
c) Wind
d) Moonlight

**Rationale**: Literal comprehension. Answer is explicit in the second sentence.

**v1.1 fix**: Improved distractors. The original options included "Darkness" and "Cold air," which were too implausible — even a student with zero English knowledge would be unlikely to select them, reducing the question's discriminating power. The revised distractors ("Water and soil", "Wind", "Moonlight") are all things that relate to nature and plant growth, making them plausible guesses for a student who did not understand the passage.

---

#### Q9 (Type A: Vocabulary Matching - Cognate)
**Question**: What does "problem" mean?
**Options**:
a) Programa
b) Problema ✓
c) Processo
d) Projeto

**Rationale**: Direct cognate. Distractors are also cognates to test precise recognition.

---

#### Q10 (Type B: Sentence Completion - Present Simple, Common Noun)
**Question**: The computer _____ information quickly.
**Options**:
a) process
b) processes ✓
c) processed
d) processing

**Rationale**: Third-person singular present simple requires the "-es" suffix. "The computer" is a singular subject. Tests whether the student recognizes the subject-verb agreement pattern. Sits at the upper boundary of Band 1, transitioning toward Band 2 difficulty.

---

### Band 2: Developing (Questions 11–18) — Path B/C Only

#### Q11 (Type A: Vocabulary Matching - Non-Cognate)
**Question**: What is the best definition of "achieve"?
**Options**:
a) To receive something
b) To reach a goal successfully ✓
c) To believe in something
d) To teach someone

**Rationale**: Common academic verb, not a cognate. Tests understanding of definition.

---

#### Q12 (Type B: Sentence Completion - Past Simple)
**Question**: She _____ the experiment last week.
**Options**:
a) completes
b) completed ✓
c) completing
d) will complete

**Rationale**: Past tense marker "last week" requires past simple form.

---

#### Q13 (Type C: Reading Comprehension - 3 sentences, literal + reorganization)
**Passage**: "Bacteria are tiny living organisms. Some bacteria are helpful and live in our bodies. Other bacteria can cause infections and make us sick."
**Question**: According to the passage, what is true about bacteria?
**Options**:
a) All bacteria are dangerous ✗
b) All bacteria are helpful ✗
c) Some bacteria are helpful, and some are harmful ✓
d) Bacteria do not live in the human body ✗

**Rationale**: Requires synthesizing information from sentences 2 and 3. Tests "some...other" structure.

---

#### Q14 (Type D: Grammar Recognition - Verb Tense)
**Question**: Which sentence is correct?
**Options**:
a) She go to the laboratory yesterday. ✗
b) She goes to the laboratory yesterday. ✗
c) She went to the laboratory yesterday. ✓
d) She going to the laboratory yesterday. ✗

**Rationale**: Tests past simple vs. present simple with time marker "yesterday".

---

#### Q15 (Type B: Sentence Completion - Comparative Adjective)
**Question**: Steel is _____ than plastic.
**Options**:
a) strong
b) stronger ✓
c) strongest
d) more strong

**Rationale**: Comparative form with "than". Common error: "more strong" instead of "stronger".

---

#### Q16 (Type C: Reading Comprehension - 4 sentences, reorganization)
**Passage**: "Cybersecurity protects computer systems from attacks. Hackers try to steal information or damage systems. Companies use firewalls and passwords to prevent attacks. Good cybersecurity is essential for businesses today."
**Question**: How do companies protect their systems?
**Options**:
a) By hiring hackers ✗
b) By using firewalls and passwords ✓
c) By avoiding the internet ✗
d) By stealing information ✗

**Rationale**: Answer is explicit in sentence 3. Requires identifying relevant information.

---

#### Q17 (Type A: Vocabulary Matching - Technical Term)
**Question**: What does "accurate" mean?
**Options**:
a) Fast and efficient
b) Correct and precise ✓
c) Large and important
d) Difficult and complex

**Rationale**: Key technical term for Metrology students. Partial cognate (acurado/preciso).

---

#### Q18 (Type B: Sentence Completion - Present Perfect)
**Question**: Scientists _____ a new vaccine that is now saving lives.
**Options**:
a) discovered
b) have discovered ✓
c) are discovering
d) will discover

**Rationale**: Present perfect is required because the action (discovering) has a result that is relevant to the present ("is now saving lives"). The temporal context "that is now saving lives" makes past simple ("discovered") incorrect — past simple would require a completed-in-the-past context (e.g., "Scientists discovered a new vaccine in 2019"). This distinguishes Tier 2 from Tier 1.

**v1.1 fix**: Added "that is now saving lives" to disambiguate. The original sentence "Scientists _____ a new vaccine" was ambiguous — both "discovered" (past simple) and "have discovered" (present perfect) were defensible without additional context. The added clause creates a clear present-relevance signal that requires present perfect.

---

### Band 3: Expanding (Questions 19–25) — Path B/C Only

#### Q19 (Type C: Reading Comprehension - 3-4 sentences, inferential)
**Passage**: "Renewable energy sources, such as solar and wind power, produce electricity without burning fossil fuels. Unlike coal and natural gas, they do not release greenhouse gases during operation. However, their energy output depends on weather conditions, which can be unpredictable."
**Question**: What is a disadvantage of renewable energy mentioned in the passage?
**Options**:
a) It produces greenhouse gases ✗
b) It is more expensive than fossil fuels ✗
c) Its output depends on unpredictable weather ✓
d) It requires burning coal ✗

**Rationale**: Entry-level Band 3 question with a shorter passage (3 sentences) to create a gradual transition from Band 2. Tests the ability to identify a specific disadvantage from a passage that discusses both advantages and disadvantages. Requires understanding the contrast signaled by "However."

**v1.1 change**: Replaced the original 5-sentence climate change passage with a shorter 3-sentence passage. The original Q19 passage was the same length and difficulty as Q22 and Q25, creating an abrupt difficulty jump at the Band 2–3 boundary. This shorter passage serves as a stepping stone.

---

#### Q20 (Type D: Grammar Recognition - Passive Voice)
**Question**: Which sentence uses the passive voice correctly?
**Options**:
a) The experiment conducts by the students. ✗
b) The experiment was conducted by the students. ✓
c) The experiment is conducting by the students. ✗
d) The students conducted the experiment. ✗ (Note: This is active voice, correct grammar but wrong structure)

**Rationale**: Tests understanding of passive construction (be + past participle).

---

#### Q21 (Type B: Sentence Completion - Conditional)
**Question**: If the temperature _____ too high, the equipment will malfunction.
**Options**:
a) rise
b) rises ✓
c) rose
d) risen

**Rationale**: First conditional (If + present simple, will + base verb). Common error: using "rise" without the -s.

---

#### Q22 (Type C: Reading Comprehension - 5 sentences, inference + vocabulary)
**Passage**: "Biotechnology involves using living organisms or their components to develop useful products. One application is the production of insulin for diabetes treatment. Historically, insulin was extracted from animal pancreases. However, modern biotechnology allows scientists to genetically engineer bacteria to produce human insulin. This method is safer, more efficient, and more cost-effective."
**Question**: Why is genetically engineered insulin better than animal-derived insulin?
**Options**:
a) It is extracted from animals ✗
b) It is safer, more efficient, and cheaper ✓
c) It requires human pancreases ✗
d) It is a historical method ✗

**Rationale**: Answer is in the final sentence. Requires understanding "safer, more efficient, more cost-effective" = better.

---

#### Q23 (Type D: Grammar Recognition - Relative Clause)
**Question**: Which sentence is grammatically correct?
**Options**:
a) The scientist who discovered the cure was awarded a prize. ✓
b) The scientist discovered the cure was awarded a prize. ✗
c) The scientist, discovered the cure, was awarded a prize. ✗
d) The scientist which discovered the cure was awarded a prize. ✗

**Rationale**: Tests understanding of relative clauses ("who" for people). Option d uses "which" (for things, not people).

---

#### Q24 (Type C: Reading Comprehension - 5 sentences, inferential)
**Passage**: "Climate change refers to long-term shifts in temperatures and weather patterns. While natural processes can cause these shifts, human activities have been the main driver since the 1800s. Burning fossil fuels generates greenhouse gas emissions that trap heat in the atmosphere. As a result, global temperatures have risen approximately 1.1°C since pre-industrial times. Scientists warn that further warming could have severe consequences for ecosystems and human societies."
**Question**: What can be inferred from the passage?
**Options**:
a) Climate change is entirely natural ✗
b) Human activities are the primary cause of recent climate change ✓
c) Global temperatures have decreased since the 1800s ✗
d) Scientists believe climate change will have no impact ✗

**Rationale**: Requires synthesizing information from sentences 2 and 3. Inferential, not just literal.

**v1.1 change**: Moved from Q19 to Q24. This 5-sentence passage with inferential comprehension is appropriate for the upper end of Band 3, not the entry point.

---

#### Q25 (Type C: Reading Comprehension - 5 sentences, inference + synthesis) [ANCHOR-HARD]
**Passage**: "Precision and accuracy are two distinct concepts in measurement. Precision refers to how close repeated measurements are to each other. Accuracy refers to how close a measurement is to the true value. A measurement can be precise but not accurate if the instrument has a systematic error. For example, a scale that consistently reads 2 kg too high is precise (consistent) but inaccurate (wrong)."
**Question**: According to the passage, what is the difference between precision and accuracy?
**Options**:
a) There is no difference; they mean the same thing ✗
b) Precision is about consistency; accuracy is about correctness ✓
c) Precision is about correctness; accuracy is about consistency ✗
d) Only accuracy matters in measurement ✗

**Rationale**: Requires understanding technical definitions and distinguishing two related concepts. Critical for Metrology students. Serves as the **anchor-hard** question: a student who answers Q25 correctly almost certainly belongs in Tier 3, even if their total score is borderline. Option c is a strong distractor because it reverses the two definitions — only a careful reader will distinguish it from the correct answer.

---

## 11. Next Steps

### 11.1. Immediate Actions (Before First Semester)

1. **Finalize question pool**: Write 50 questions (20 Band 1, 16 Band 2, 14 Band 3) following the specifications above.
2. **Peer review**: Have all questions reviewed by content, language, and Portuguese experts. Pay special attention to unambiguous correct answers and plausible distractors (see v1.1 fixes for Q7, Q8, Q18). Verify that Band 1 works as a standalone test (v1.2).
3. **Build Google Form**: Create the test in Google Forms with Quiz mode enabled.
   - Implement the three-path branching architecture (Section 7.2).
   - Use bilingual instructions throughout.
   - Include the worked example at the top of Band 1.
   - Test branching with dummy submissions for all three paths (v1.2).
4. **Set up Google Sheet**: Add per-band score formulas (Section 7.5), path indicator column (Section 7.4), and guessing-pattern flags (Section 6.5).
5. **Pilot test**: Run a small pilot (10–15 volunteers). Include at least 2 volunteers who take Path A to verify the short-form experience (v1.2).
6. **Integrate with E01**: Prepare data collection tools to merge placement test scores with E01 performance metrics. Include Signal 0 (self-assessment path) in the merge (v1.2).

### 11.2. During First Semester

1. **Administer test**: All students take the placement test in the first week. Students self-select their path via the entry gate.
2. **Review path distribution**: Check how many students chose Path A, B, and C. Flag any unexpected distributions (Section 9.2, item 1).
3. **Provisional tier assignment**: Use placement test scores + self-assessment path to make initial tier assignments.
4. **Follow up with Path A high-scorers**: Contact students who scored ≥ 8/10 on Band 1 — offer them the full test or note them for close E01 monitoring (v1.2).
5. **Check anchor questions**: Review Q1 and Q25 results to identify students needing instructor follow-up.
6. **Collect E01 data**: Track retention rate, review time, and ease distribution for all students.
7. **Final tier assignment**: Combine all three signals using the matrix in Section 6.3.

### 11.3. Post-Semester

1. **Validation analysis**: Perform all analyses described in Section 9.2, including path distribution analysis, self-assessment accuracy, and anchor question analysis.
2. **Refine thresholds**: Adjust score ranges for tier placement based on observed data.
3. **Calibrate self-assessment gate**: Based on underestimator and overestimator rates, revise the wording of the three path options if needed (v1.2).
4. **Revise questions**: Replace poorly performing questions with items from the surplus pool.
5. **Evaluate guessing mitigation**: Review whether the three-signal system adequately handled guessing, or whether short-answer questions should be introduced in Version 2.
6. **Iterate**: Create Version 2 of the test for Semester 2.

---

## 12. References

- [READING_MATERIAL_METHODOLOGY.md](../../server/docs/READING_MATERIAL_METHODOLOGY.md): Three-tier proficiency system, Duolingo + E01 dual placement strategy.
- [STUDENT_PERFORMANCE_ANALYSIS.md](../../server/docs/STUDENT_PERFORMANCE_ANALYSIS.md): Metrics for tracking student performance (retention rate, review density, ease distribution).
- Oxford 3000: List of the most important words for learners of English. Available at [Oxford Learner's Dictionaries](https://www.oxfordlearnersdictionaries.com/about/oxford3000).
- Academic Word List (AWL): Coxhead, A. (2000). A new academic word list. *TESOL Quarterly*, 34(2), 213-238.
- Flesch-Kincaid Readability: [Readable.com Readability Tools](https://readable.com/readability/flesch-reading-ease-flesch-kincaid-grade-level/) or similar tools for validating passage difficulty.

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-20 | Claude Code | Initial creation based on READING_MATERIAL_METHODOLOGY.md |
| 1.1 | 2026-02-20 | Claude Code | Revision incorporating peer review feedback. Key changes: (1) Fixed Q7 subject-verb agreement. (2) Fixed Q18 ambiguity. (3) Cleaned up Q10. (4) Improved Q8 distractors. (5) Added bilingual Portuguese instructions. (6) Added per-section time estimates. (7) Added anchor question framework. (8) Added distractor design principles. (9) Added guessing mitigation strategy. (10) Added reading passage length progression. (11) Restructured Band 3 question order. (12) Added per-band score breakdown guidance. (13) Added anchor role field to question writing guidelines. (14) Added peer review checklist for answer unambiguity and distractor quality. |
| 1.2 | 2026-02-20 | Claude Code | Structural revision introducing three-path entry gate architecture. Key changes: (1) Added self-assessment routing question in Portuguese (Section 3.1) with three paths — Path A (never studied English, Band 1 only), Path B (high school English, full test), Path C (English courses, full test). (2) Replaced binary "take/skip" with "everyone takes something" design — Path A students answer 10 questions instead of 25, producing usable data while avoiding anxiety. (3) Added worked example in Portuguese at the top of Band 1 to demystify question format for Path A students (Section 7.2). (4) Introduced Signal 0 (self-reported background) as a third placement signal alongside test score and E01 performance (Section 3.1.4). (5) Rewrote scoring system for path-aware thresholds — separate scales for Path A (out of 10) and Path B/C (out of 25) (Section 6.1–6.2). (6) Expanded placement matrix to three-signal system with separate tables for Path A and Path B/C students (Section 6.3). (7) Added underestimator detection — Path A students scoring ≥ 8/10 are flagged for follow-up (Section 6.2). (8) Added false-skipper mitigation discussion (Section 3.1.3). (9) Redesigned Google Forms structure with branching architecture using "Go to section based on answer" (Section 7.2). (10) Added Google Forms branching implementation notes (Section 7.3). (11) Updated data export to include self-assessment path and program fields (Section 7.4). (12) Added path distribution analysis and self-assessment accuracy metrics to validation framework (Section 9.2). (13) Added self-assessment gate calibration to threshold adjustment process (Section 9.3). (14) Added Path Visibility field to question writing guidelines (Section 8.2). (15) Updated pilot testing to include Path A-specific testing (Section 8.4). (16) Updated Next Steps with path-specific follow-up tasks (Section 11). |
