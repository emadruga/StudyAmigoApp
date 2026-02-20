# Programmatic Google Form Generation for the ESL Placement Test

This document describes how to programmatically generate the 25-question ESL placement test as a Google Form using Python and the Google Forms API v1. The goal is to turn a structured question bank (JSON) into a fully configured, quiz-mode Google Form with branching, answer keys, and automatic scoring — reproducibly and without manual form-building.

---

## Table of Contents

1. [Motivation](#1-motivation)
2. [Google Forms API Overview](#2-google-forms-api-overview)
3. [Architecture](#3-architecture)
4. [Question Bank Format](#4-question-bank-format)
5. [Authentication Setup](#5-authentication-setup)
6. [Form Generation Pipeline](#6-form-generation-pipeline)
7. [Branching Logic Implementation](#7-branching-logic-implementation)
8. [API Limitations and Workarounds](#8-api-limitations-and-workarounds)
9. [Project Structure](#9-project-structure)
10. [Dependencies](#10-dependencies)
11. [Step-by-Step Implementation Plan](#11-step-by-step-implementation-plan)
12. [Testing Strategy](#12-testing-strategy)

---

## 1. Motivation

### 1.1. Why Generate Programmatically?

Building the placement test manually in the Google Forms UI is feasible for a single 25-question form. However, the [PLAN_FOR_PLACEMENT_EXAM_v1.2.md](PLAN_FOR_PLACEMENT_EXAM_v1.2.md) design calls for:

- A **50-question pool** from which different 25-question test versions are assembled each semester (to prevent question leakage).
- **Three-path branching** (Path A / B / C) with per-option section routing — tedious and error-prone to configure by hand.
- **Answer keys and point values** for all 25 questions — one mistake in manual entry invalidates auto-grading.
- **Iterative refinement** — poorly performing questions are swapped out each semester. Rebuilding the form from scratch each time is unsustainable.
- **Reproducibility** — given the same question bank JSON, the script produces the same form every time. No "I forgot to set the answer key on Q14" errors.

### 1.2. What This Script Does NOT Do

- It does not administer the test or interact with students.
- It does not analyze responses (that's a separate data pipeline concern).
- It does not link the form to Google Sheets (API limitation — see Section 8).

---

## 2. Google Forms API Overview

### 2.1. API Status

The **Google Forms API v1** has been **Generally Available (GA)** since March 17, 2022. It is a stable, production-ready REST API under the Google Workspace developer umbrella.

### 2.2. Key Capabilities

| Capability | Supported | API Method |
|---|---|---|
| Create a new form | Yes | `forms.create()` |
| Add questions (multiple choice, checkbox, dropdown, short answer) | Yes | `forms.batchUpdate()` with `createItem` |
| Add page breaks (sections) | Yes | `createItem` with `pageBreakItem` |
| Add descriptive text blocks | Yes | `createItem` with `textItem` |
| Enable quiz mode | Yes | `batchUpdate()` with `updateSettings` → `quizSettings.isQuiz = true` |
| Set correct answers + point values | Yes | `grading.correctAnswers` + `grading.pointValue` on each question |
| Set feedback for right/wrong answers | Yes | `grading.whenRight` / `grading.whenWrong` |
| Per-option section routing ("Go to section based on answer") | Yes | `goToSectionId` on each `Option` in a `ChoiceQuestion` |
| Route to submit / restart form | Yes | `goToAction` enum: `SUBMIT_FORM`, `RESTART_FORM`, `NEXT_SECTION` |
| Publish form | Yes | `forms.setPublishSettings()` (required after March 31, 2026) |

### 2.3. API Interaction Model

Form creation is a **two-step process**:

1. **`forms.create()`** — Creates a blank form with a title. Returns the form ID.
2. **`forms.batchUpdate()`** — Sends a batch of update requests to add questions, sections, settings, and routing. This is where all the content goes.

All structural modifications (adding items, updating settings, setting quiz mode) go through `batchUpdate`. There is no `addQuestion()` or `enableQuiz()` — everything is a request in the batch.

### 2.4. Important Timeline Note

Starting **March 31, 2026**, forms created via the API will be in an **unpublished** state by default. The script must call `forms.setPublishSettings()` explicitly to make the form accessible to respondents. Since this project will be built and used around this date, the script must include this step from day one.

---

## 3. Architecture

### 3.1. High-Level Data Flow

```
┌─────────────────────┐
│  question_bank.json  │  ← Human-authored question pool (50 questions)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  test_selector.py   │  ← Selects 25 questions for this semester's test
│  (or manual curation)│     (10 Band 1, 8 Band 2, 7 Band 3)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  test_config.json   │  ← This semester's 25-question test definition
│                     │     + form metadata (title, descriptions, paths)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  generate_form.py   │  ← Calls Google Forms API to build the form
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Google Form (live)  │  ← Quiz-mode form with branching, answer keys,
│  URL ready to share  │     bilingual instructions, worked example
└─────────────────────┘
```

### 3.2. Separation of Concerns

- **`question_bank.json`**: The pedagogical artifact. Owned by the instructor. Contains all 50 questions with metadata (band, type, cognate status, distractor rationale, etc.). Changes between semesters as poorly performing questions are replaced.

- **`test_config.json`**: The test assembly for a specific semester. References 25 questions from the bank by ID. Includes form-level metadata (title, descriptions, bilingual text). Changes every semester.

- **`generate_form.py`**: The engineering artifact. Reads the test config, authenticates with Google, and creates the form. Should rarely change once built — only when the API changes or new form features are needed.

---

## 4. Question Bank Format

### 4.1. `question_bank.json` Schema

The question bank is the single source of truth for all questions across all semesters.

```json
{
  "version": "1.0",
  "created": "2026-02-20",
  "questions": [
    {
      "id": "B1_VOCAB_001",
      "band": 1,
      "type": "vocabulary_matching",
      "anchor": "easy",
      "question_text": "What does \"important\" mean?",
      "options": [
        { "text": "Importante", "is_correct": true },
        { "text": "Impossível", "is_correct": false },
        { "text": "Importar", "is_correct": false },
        { "text": "Impressionante", "is_correct": false }
      ],
      "point_value": 1,
      "cognate": true,
      "vocabulary_rank": 74,
      "vocabulary_source": "Oxford 3000",
      "rationale": "Direct cognate. Anchor-easy question — virtually all test-takers should answer correctly.",
      "distractor_rationale": {
        "b": "Similar prefix 'imp-', different meaning (impossible)",
        "c": "Verb form of the root (to import), different part of speech",
        "d": "Similar prefix 'imp-' and suffix '-ante', but means 'impressive'"
      },
      "feedback_correct": null,
      "feedback_incorrect": null,
      "status": "active",
      "semesters_used": ["2026-2"],
      "item_analysis": null
    },
    {
      "id": "B1_VOCAB_002",
      "band": 1,
      "type": "vocabulary_matching",
      "anchor": null,
      "question_text": "What does \"control\" mean?",
      "options": [
        { "text": "Controlar / controle", "is_correct": true },
        { "text": "Contrato", "is_correct": false },
        { "text": "Construir", "is_correct": false },
        { "text": "Consultar", "is_correct": false }
      ],
      "point_value": 1,
      "cognate": true,
      "vocabulary_rank": 247,
      "vocabulary_source": "Oxford 3000",
      "rationale": "High-frequency technical term, direct cognate.",
      "distractor_rationale": {
        "b": "Similar prefix 'contr-', means 'contract'",
        "c": "Similar prefix 'cons-', means 'to build'",
        "d": "Similar prefix 'cons-', means 'to consult'"
      },
      "feedback_correct": null,
      "feedback_incorrect": null,
      "status": "active",
      "semesters_used": [],
      "item_analysis": null
    }
  ]
}
```

### 4.2. Field Reference

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | string | Yes | Unique identifier following the convention `B{band}_{TYPE}_{number}` (e.g., `B1_VOCAB_001`, `B3_COMP_005`) |
| `band` | integer | Yes | Difficulty band: `1` (Foundation), `2` (Developing), `3` (Expanding) |
| `type` | string | Yes | Question type: `vocabulary_matching`, `sentence_completion`, `reading_comprehension`, `grammar_recognition` |
| `anchor` | string | No | `"easy"`, `"hard"`, or `null`. Only Q1 and Q25 in a given test should have anchor roles. |
| `question_text` | string | Yes | The question prompt. For reading comprehension, this includes the passage and the question separated by a double newline. |
| `options` | array | Yes | Array of 4 option objects, each with `text` (string) and `is_correct` (boolean). Exactly one option must be correct. |
| `point_value` | integer | Yes | Always `1` in the current design. |
| `cognate` | boolean | Yes | Whether the question relies on Portuguese-English cognates. |
| `vocabulary_rank` | integer | No | Frequency rank of the key vocabulary word (from Oxford 3000, AWL, etc.). |
| `vocabulary_source` | string | No | Source list for the vocabulary: `"Oxford 3000"`, `"AWL"`, `"New General Service List"`, etc. |
| `rationale` | string | Yes | Why this question is at this difficulty level and what it tests. |
| `distractor_rationale` | object | Yes | Keys `"b"`, `"c"`, `"d"` (for options b, c, d) explaining why each incorrect option is plausible. |
| `feedback_correct` | string | No | Optional feedback shown when the student answers correctly (Google Forms quiz feature). |
| `feedback_incorrect` | string | No | Optional feedback shown when the student answers incorrectly. |
| `status` | string | Yes | `"active"` (available for test assembly), `"retired"` (removed due to poor performance), `"draft"` (not yet reviewed). |
| `semesters_used` | array | Yes | List of semester IDs where this question appeared in a test (e.g., `["2026-2", "2027-1"]`). Used to track exposure and rotation. |
| `item_analysis` | object | No | Post-semester statistics: `{ "difficulty_index": 0.85, "discrimination_index": 0.45, "n_students": 48 }`. Populated after validation (Section 9 of the placement plan). |

### 4.3. Reading Comprehension Question Format

For reading comprehension questions (Type C), the `question_text` field contains both the passage and the question, separated by `\n\n`:

```json
{
  "id": "B1_COMP_001",
  "band": 1,
  "type": "reading_comprehension",
  "question_text": "Passage: \"A thermometer measures temperature. Temperature tells us if something is hot or cold.\"\n\nWhat does a thermometer measure?",
  "options": [
    { "text": "Weight", "is_correct": false },
    { "text": "Temperature", "is_correct": true },
    { "text": "Time", "is_correct": false },
    { "text": "Distance", "is_correct": false }
  ]
}
```

The generation script will need to handle this: the passage portion becomes the question `description` field in the API, and the actual question becomes the `title`.

Alternatively, the passage can be rendered as a standalone `textItem` immediately before the question. This gives better visual formatting in the form. The script should support both approaches (configurable).

### 4.4. `test_config.json` Schema

This file defines a specific semester's test — which 25 questions to include, form metadata, and bilingual text.

```json
{
  "semester": "2026-2",
  "form_title": "Teste de Nivelamento - Inglês Instrumental / Placement Test - ESL",
  "form_description": "",
  "created": "2026-07-15",

  "instructions": {
    "purpose_pt": "Este teste avalia seu nível atual de leitura em inglês. Ele nos ajudará a indicar materiais de leitura adequados ao seu nível.",
    "purpose_en": "This test assesses your current English reading level. It will help us assign reading materials that match your level.",
    "no_grade_pt": "Este teste NÃO conta como nota. Ele é usado apenas para nos ajudar a escolher os materiais certos para você.",
    "no_grade_en": "This test does NOT count as a grade. It is only used to help us choose the right materials for you.",
    "instructions_pt": "Responda todas as questões da melhor forma possível. Não há penalidade para respostas erradas — se não tiver certeza, faça sua melhor tentativa.",
    "instructions_en": "Answer all questions to the best of your ability. There is no penalty for wrong answers — if you are unsure, make your best guess."
  },

  "self_assessment_gate": {
    "question_pt": "Como você descreveria sua experiência com o idioma inglês?",
    "question_en": "How would you describe your experience with the English language?",
    "options": [
      {
        "text": "Nunca estudei inglês e não tenho contato com o idioma. (I have never studied English and I have no contact with the language.)",
        "path": "A"
      },
      {
        "text": "Estudei inglês no ensino médio (escola pública ou particular), mas não me considero fluente. (I studied English in high school, but I don't consider myself fluent.)",
        "path": "B"
      },
      {
        "text": "Já fiz curso de inglês ou me considero intermediário/avançado. (I have taken English courses or I consider myself intermediate/advanced.)",
        "path": "C"
      }
    ]
  },

  "worked_example": {
    "text_pt": "Antes de começar, veja este exemplo de como responder as questões:",
    "text_en": "Before you start, look at this example of how to answer the questions:",
    "example_question": "What does \"university\" mean?",
    "example_options": ["Universidade ← ✅ Resposta correta!", "Uniforme", "Universal", "Único"],
    "explanation_pt": "A pergunta \"What does X mean?\" significa \"O que X significa?\"\nEscolha a opção que melhor traduz ou define a palavra em inglês."
  },

  "sections": {
    "band1": {
      "header_en": "Part 1: Basic Vocabulary and Sentences",
      "header_pt": "Parte 1: Vocabulário Básico e Frases",
      "time_estimate": "~5 minutes / ~5 minutos",
      "question_ids": [
        "B1_VOCAB_001", "B1_VOCAB_002", "B1_CLOZE_001",
        "B1_CLOZE_002", "B1_COMP_001", "B1_VOCAB_003",
        "B1_CLOZE_003", "B1_COMP_002", "B1_VOCAB_004",
        "B1_CLOZE_004"
      ]
    },
    "band2": {
      "header_en": "Part 2: Intermediate Reading",
      "header_pt": "Parte 2: Leitura Intermediária",
      "time_estimate": "~6 minutes / ~6 minutos",
      "encouragement_pt": "Estas questões são mais difíceis. Faça o seu melhor! Não há penalidade para respostas erradas.",
      "encouragement_en": "These questions are more difficult. Do your best! There is no penalty for wrong answers.",
      "question_ids": [
        "B2_VOCAB_001", "B2_CLOZE_001", "B2_COMP_001",
        "B2_GRAM_001", "B2_CLOZE_002", "B2_COMP_002",
        "B2_VOCAB_002", "B2_CLOZE_003"
      ]
    },
    "band3": {
      "header_en": "Part 3: Advanced Reading",
      "header_pt": "Parte 3: Leitura Avançada",
      "time_estimate": "~7 minutes / ~7 minutos",
      "encouragement_pt": "Estas questões são desafiadoras. Se não tiver certeza, faça sua melhor tentativa.",
      "encouragement_en": "These questions are challenging. If you are unsure, make your best guess.",
      "question_ids": [
        "B3_COMP_001", "B3_GRAM_001", "B3_CLOZE_001",
        "B3_COMP_002", "B3_GRAM_002", "B3_COMP_003",
        "B3_COMP_004"
      ]
    }
  },

  "thank_you": {
    "message_pt": "Obrigado por completar o teste! Seus resultados nos ajudarão a indicar materiais de leitura adequados ao seu nível. Você NÃO precisa fazer mais nada agora.",
    "message_en": "Thank you for completing the test! Your results will help us assign reading materials that match your level. You do NOT need to do anything else now."
  },

  "settings": {
    "collect_email": true,
    "require_sign_in": false,
    "show_score_immediately": false,
    "shuffle_questions": false,
    "one_response_per_user": true
  }
}
```

---

## 5. Authentication Setup

### 5.1. Google Cloud Project Setup

Before the script can create forms, a one-time Google Cloud project setup is required:

1. **Go to** [Google Cloud Console](https://console.cloud.google.com/).
2. **Create a new project** (or use an existing one): e.g., "Placement Test Generator".
3. **Enable the Google Forms API**:
   - Navigate to **APIs & Services → Library**.
   - Search for "Google Forms API" and click **Enable**.
4. **Create OAuth 2.0 credentials**:
   - Navigate to **APIs & Services → Credentials**.
   - Click **Create Credentials → OAuth client ID**.
   - Application type: **Desktop app**.
   - Download the resulting `credentials.json` file.
5. **Configure the OAuth consent screen**:
   - Navigate to **APIs & Services → OAuth consent screen**.
   - User type: **External** (for personal Gmail) or **Internal** (for Google Workspace).
   - Add the required scopes: `https://www.googleapis.com/auth/forms.body`.
   - Add yourself as a test user (if in "Testing" publishing status).

### 5.2. First-Run Authentication Flow

On the first run, the script will:

1. Open a browser window asking you to sign in with your Google account.
2. Request permission to "Create and edit your Google Forms".
3. Store a `token.json` file locally for subsequent runs (no re-authentication needed until the token expires).

### 5.3. Security Notes

- **`credentials.json`** and **`token.json`** must be added to `.gitignore`. They contain secrets that should never be committed.
- The OAuth scope `forms.body` grants read/write access to form structure only — it cannot read form responses or access other Google Drive files.
- For response reading (if needed later), the separate scope `forms.responses.readonly` must be added.

---

## 6. Form Generation Pipeline

### 6.1. Step-by-Step API Call Sequence

The `generate_form.py` script executes the following steps:

```
Step 1: Authenticate
  └─ Load credentials.json → OAuth2 flow → get service object

Step 2: Create blank form
  └─ forms.create({ "info": { "title": "..." } })
  └─ Returns: form_id

Step 3: Enable quiz mode
  └─ forms.batchUpdate(form_id, {
       "requests": [{
         "updateSettings": {
           "settings": { "quizSettings": { "isQuiz": true } },
           "updateMask": "quizSettings.isQuiz"
         }
       }]
     })

Step 4: Build the form structure (single large batchUpdate)
  └─ Request list:
     ├─ createItem: Page 1 — Instructions (textItem with bilingual text)
     ├─ createItem: Self-assessment gate question (RADIO with goToSectionId)
     ├─ createItem: Page break — Band 1 section header
     ├─ createItem: Worked example (textItem)
     ├─ createItem: Q1 through Q10 (RADIO questions with grading)
     ├─ createItem: Page break — Band 2 section header
     ├─ createItem: Q11 through Q18 (RADIO questions with grading)
     ├─ createItem: Page break — Band 3 section header
     ├─ createItem: Q19 through Q25 (RADIO questions with grading)
     └─ (Thank you page is set via form settings, not as an item)

Step 5: Set branching routes (second batchUpdate if section IDs needed)
  └─ Update the self-assessment gate question's options with goToSectionId
  └─ This may require reading the form back to get assigned item IDs

Step 6: Publish the form (required after March 2026)
  └─ forms.setPublishSettings(form_id, { "publishSettings": { "isPublished": true } })

Step 7: Output the form URL
  └─ Print: "Form created: https://docs.google.com/forms/d/{form_id}/edit"
  └─ Print: "Respondent URL: https://docs.google.com/forms/d/{form_id}/viewform"
```

### 6.2. The Item ID Challenge

Google Forms API assigns item IDs server-side when items are created. Branching (`goToSectionId`) requires knowing the target section's item ID. This creates an ordering problem: you cannot set `goToSectionId` on the self-assessment gate until you know the Band 1 section's item ID, but the Band 1 section doesn't have an ID until it's created.

**Solution** — two-pass approach:

1. **Pass 1**: Create all items (sections, questions, text blocks) in a single `batchUpdate`. Each `createItem` request includes a `location.index` to control ordering.
2. **Read back**: Call `forms.get(form_id)` to retrieve the full form with server-assigned item IDs.
3. **Pass 2**: Send a second `batchUpdate` with `updateItem` requests that set `goToSectionId` on the self-assessment gate options and any end-of-section routing.

Alternatively, the API allows specifying your own `itemId` in the `createItem` request (a random UUID-like string). If the API accepts client-specified IDs, the entire form can be built in a single `batchUpdate` because all section IDs are known in advance. This should be tested during implementation.

### 6.3. Question Rendering

Each question from the bank is rendered as a `createItem` request:

```python
def render_question(question, index):
    """Convert a question_bank entry into a Forms API createItem request."""
    correct_answer = next(
        opt["text"] for opt in question["options"] if opt["is_correct"]
    )

    return {
        "createItem": {
            "item": {
                "title": question["question_text"],
                "questionItem": {
                    "question": {
                        "required": True,
                        "grading": {
                            "pointValue": question["point_value"],
                            "correctAnswers": {
                                "answers": [{"value": correct_answer}]
                            },
                            "whenRight": {"text": question.get("feedback_correct", "")},
                            "whenWrong": {"text": question.get("feedback_incorrect", "")}
                        },
                        "choiceQuestion": {
                            "type": "RADIO",
                            "options": [
                                {"value": opt["text"]}
                                for opt in question["options"]
                            ],
                            "shuffle": False
                        }
                    }
                }
            },
            "location": {"index": index}
        }
    }
```

---

## 7. Branching Logic Implementation

### 7.1. Form Section Layout

The form consists of the following sections (Google Forms pages):

| Section | Content | Arrives From | Routes To |
|---|---|---|---|
| **Section 0** | Instructions + self-assessment gate | Form start | Section 1 (all paths) |
| **Section 1** | Band 1 questions (Q1–Q10) + worked example | Section 0 | Path A → Section 4 (Thank You); Path B/C → Section 2 |
| **Section 2** | Band 2 questions (Q11–Q18) | Section 1 | Section 3 |
| **Section 3** | Band 3 questions (Q19–Q25) | Section 2 | Section 4 (Thank You) |
| **Section 4** | Thank You page | Section 1 (Path A) or Section 3 (Path B/C) | Form submit |

### 7.2. Self-Assessment Gate Routing

The self-assessment question is a `RADIO` type `ChoiceQuestion` in Section 0. Each option uses `goToSectionId` to route to the appropriate section:

```python
{
    "createItem": {
        "item": {
            "title": "Como você descreveria sua experiência com o idioma inglês?\n(How would you describe your experience with the English language?)",
            "questionItem": {
                "question": {
                    "required": True,
                    "choiceQuestion": {
                        "type": "RADIO",
                        "options": [
                            {
                                "value": "Nunca estudei inglês e não tenho contato com o idioma.",
                                "goToSectionId": BAND_1_SECTION_ID
                            },
                            {
                                "value": "Estudei inglês no ensino médio, mas não me considero fluente.",
                                "goToSectionId": BAND_1_SECTION_ID
                            },
                            {
                                "value": "Já fiz curso de inglês ou me considero intermediário/avançado.",
                                "goToSectionId": BAND_1_SECTION_ID
                            }
                        ]
                    }
                }
            }
        },
        "location": {"index": GATE_INDEX}
    }
}
```

Note: All three paths go to Band 1 first. The divergence happens *after* Band 1 (see Section 7.3).

### 7.3. Post-Band 1 Routing (Path A vs. Path B/C)

This is the trickiest part. After completing Band 1, Path A students must skip to Thank You, while Path B/C students must continue to Band 2.

**The Google Forms API constraint**: Section routing (via `goToAction` or `goToSectionId`) can only be set on `ChoiceQuestion` options — not on page breaks or sections themselves. Google Forms' "After section X, go to section Y" is a UI feature for the page break item, but the API exposes this through a different mechanism.

**Approach — Hidden routing question at the end of Band 1**:

Add a final question at the end of the Band 1 section that asks students to confirm their path. This question is populated based on their self-assessment (or can restate the original self-assessment) and its options carry `goToSectionId` routing:

```python
{
    "title": "Selecione a mesma opção que você escolheu na primeira página:\n(Select the same option you chose on the first page:)",
    "questionItem": {
        "question": {
            "required": True,
            "choiceQuestion": {
                "type": "RADIO",
                "options": [
                    {
                        "value": "Nunca estudei inglês (Path A)",
                        "goToAction": "SUBMIT_FORM"
                    },
                    {
                        "value": "Estudei inglês no ensino médio (Path B)",
                        "goToSectionId": BAND_2_SECTION_ID
                    },
                    {
                        "value": "Já fiz curso de inglês (Path C)",
                        "goToSectionId": BAND_2_SECTION_ID
                    }
                ]
            }
        }
    }
}
```

**Trade-off**: This adds a redundant question that the student must answer twice. However:
- It is the only reliable way to implement per-student branching after a shared section in Google Forms.
- The question is very quick to answer (one click).
- The student's answer on this routing question also serves as a data consistency check — if they answer differently from the gate, it's a signal worth noting.
- `goToAction: "SUBMIT_FORM"` for Path A sends them directly to the confirmation/thank-you page.

**Alternative approach**: If Google Forms supports default section-level routing (e.g., "After Section 1, go to Section 2" as a property of the page break), the script should use that for the default Path B/C flow and only override with `SUBMIT_FORM` for Path A. This needs to be tested during implementation.

---

## 8. API Limitations and Workarounds

| Limitation | Impact | Workaround |
|---|---|---|
| **Cannot link to Google Sheets** | The `linkedSheetId` field is read-only. No way to programmatically create the Responses → Sheets link. | **Manual step**: After the form is generated, open it in the browser, go to Responses → Link to Sheets. This is a one-click action. Alternatively, use a Google Apps Script one-liner: `FormApp.openById(formId).setDestination(FormApp.DestinationType.SPREADSHEET, sheetId)`. |
| **No response validation** | Cannot enforce regex patterns on short-answer questions. | Not needed — all questions are multiple choice (RADIO). |
| **No rich text formatting** | Cannot bold, italicize, or format text in question titles or descriptions. | Use CAPS or quotation marks for emphasis. The bilingual text uses `\n` for line breaks, which the API respects. |
| **No file upload questions** | Cannot add file upload items via the API. | Not needed for this test. |
| **~400 field limit** | Forms with more than ~400 fields may hit API errors. | The placement test has 25–26 questions + ~8 text/section items = ~34 items, well within limits. |
| **No "collect email" setting via API** | The `formSettings` does not expose the "collect respondent email" toggle. | **Manual step**: Enable "Collect email addresses" in Settings after form generation. Or use Apps Script. |
| **Forms default to unpublished (after March 2026)** | New forms won't be accessible to respondents until published. | Script calls `forms.setPublishSettings()` as the final step. |

---

## 9. Project Structure

```
placement_exam/
├── docs/
│   ├── PLAN_FOR_PLACEMENT_EXAM.md          # v1.0 original plan
│   ├── PLAN_FOR_PLACEMENT_EXAM_v1.1.md     # v1.1 with question fixes
│   ├── PLAN_FOR_PLACEMENT_EXAM_v1.2.md     # v1.2 with three-path gate
│   └── PROGRAMMATIC_PLACEMENT_EXAM.md      # This document
│
├── data/
│   ├── question_bank.json                  # Full 50-question pool
│   └── semesters/
│       ├── 2026-2_test_config.json         # Semester 2026-2 test definition
│       └── 2027-1_test_config.json         # Semester 2027-1 test definition
│
├── scripts/
│   ├── generate_form.py                    # Main form generation script
│   ├── validate_bank.py                    # Validates question_bank.json
│   │                                       # (checks for duplicates, missing
│   │                                       #  fields, exactly one correct
│   │                                       #  answer per question, etc.)
│   ├── select_questions.py                 # Selects 25 questions from pool
│   │                                       # (respects band distribution,
│   │                                       #  avoids recently used questions)
│   └── auth.py                             # Authentication helper
│
├── credentials.json                        # OAuth credentials (GITIGNORED)
├── token.json                              # OAuth token (GITIGNORED)
├── requirements.txt                        # Python dependencies
└── .gitignore                              # Ignores credentials + token
```

---

## 10. Dependencies

### 10.1. `requirements.txt`

```
google-api-python-client>=2.100.0
google-auth-oauthlib>=1.2.0
google-auth-httplib2>=0.2.0
```

### 10.2. Python Version

Python 3.9+ (any version supporting the Google client libraries).

### 10.3. Notes

- These dependencies are **separate** from the main JAVUMBO server (`/server/requirements.txt`). The placement exam generator is a standalone tool, not part of the Flask application.
- No additional frameworks needed — the Google client library handles HTTP, serialization, and authentication.

---

## 11. Step-by-Step Implementation Plan

### Phase 1: Foundation

| Step | Task | Output |
|---|---|---|
| 1.1 | Set up Google Cloud project, enable Forms API, create OAuth credentials | `credentials.json` |
| 1.2 | Create `auth.py` — OAuth2 flow with token caching | Working authentication |
| 1.3 | Write a minimal `generate_form.py` that creates a blank form with a title | Form URL printed to console |
| 1.4 | Extend to enable quiz mode on the blank form | Quiz-mode blank form |

### Phase 2: Question Bank

| Step | Task | Output |
|---|---|---|
| 2.1 | Author `question_bank.json` with all 25 sample questions from v1.2 plan | `question_bank.json` (25 questions initially, expand to 50 later) |
| 2.2 | Write `validate_bank.py` — validates JSON schema, checks for duplicates, verifies exactly one correct answer per question, checks band distribution | Validation script |
| 2.3 | Write `2026-2_test_config.json` — references the 25 questions by ID, includes all bilingual text | Test config for first semester |

### Phase 3: Form Generation (No Branching)

| Step | Task | Output |
|---|---|---|
| 3.1 | Implement section creation (page breaks with headers and descriptions) | Form with 4 sections |
| 3.2 | Implement question rendering (RADIO questions with answer keys and point values) | Form with 25 graded questions |
| 3.3 | Implement the worked example as a `textItem` before Q1 | Worked example visible in Band 1 |
| 3.4 | Implement the bilingual instructions page | Complete instructions page |
| 3.5 | Test: generate the full 25-question form, verify quiz mode and auto-grading work by submitting test responses manually | Working non-branching form |

### Phase 4: Branching

| Step | Task | Output |
|---|---|---|
| 4.1 | Implement the self-assessment gate question with `goToSectionId` routing | Gate routes to Band 1 |
| 4.2 | Implement the post-Band 1 routing question (Path A → submit, Path B/C → Band 2) | Path A students exit after Band 1 |
| 4.3 | Test all three paths with dummy submissions — verify scores are calculated correctly for both 10-question and 25-question submissions | Verified branching form |

### Phase 5: Polish and Publishing

| Step | Task | Output |
|---|---|---|
| 5.1 | Implement `forms.setPublishSettings()` call | Form auto-published |
| 5.2 | Add the `select_questions.py` script for random question selection from the 50-question pool | Question selection tool |
| 5.3 | Add command-line arguments to `generate_form.py` (e.g., `--config`, `--bank`, `--dry-run`) | CLI interface |
| 5.4 | Document the manual post-generation steps (link to Sheets, enable email collection) | Checklist in README or printed by script |
| 5.5 | Test end-to-end: run script, get form URL, submit 3 test responses (one per path), verify scores in Google Sheets | Production-ready |

### Phase 6: Expansion (Post First Semester)

| Step | Task | Output |
|---|---|---|
| 6.1 | Expand `question_bank.json` from 25 to 50 questions | Full question pool |
| 6.2 | Populate `item_analysis` fields from first-semester data | Data-informed bank |
| 6.3 | Generate Semester 2 test with rotated questions | Second form version |

---

## 12. Testing Strategy

### 12.1. Unit Tests (Python)

| Test | What It Validates |
|---|---|
| `test_validate_bank.py` | Bank validation catches: missing fields, duplicate IDs, multiple correct answers, invalid band numbers, invalid types |
| `test_render_question.py` | Question rendering produces valid API payloads: correct structure, point values, answer keys |
| `test_select_questions.py` | Selection respects band distribution (10/8/7), avoids recently used questions, handles edge cases (not enough questions in a band) |

### 12.2. Integration Tests (Against Google Forms API)

| Test | What It Validates |
|---|---|
| Create blank form | API authentication works, form ID returned |
| Create form with 1 question | Quiz mode enabled, answer key set, scoring works |
| Create form with 2 sections + routing | Branching routes correctly, `goToSectionId` accepted |
| Create full 25-question form | All questions render, all paths work, scores match expected values |

### 12.3. Manual Verification Checklist

After generating the form, verify manually:

- [ ] Form opens in browser at the respondent URL
- [ ] Instructions page shows bilingual text
- [ ] Self-assessment gate presents three options in Portuguese
- [ ] Selecting Path A → see Band 1 questions → submit → score out of 10
- [ ] Selecting Path B → see all 25 questions → submit → score out of 25
- [ ] Selecting Path C → same as Path B
- [ ] Worked example appears at the top of Band 1
- [ ] All questions show 4 options
- [ ] Quiz mode shows score after submission (if enabled)
- [ ] Section headers show bilingual titles and time estimates
- [ ] Response appears in linked Google Sheet with correct columns

---

## References

- [Google Forms API Documentation](https://developers.google.com/workspace/forms)
- [Google Forms API REST Reference](https://developers.google.com/workspace/forms/api/reference/rest/v1/forms)
- [Google Forms API Python Quickstart](https://developers.google.com/workspace/forms/api/quickstart/python)
- [Google Forms API Release Notes](https://developers.google.com/workspace/forms/release-notes)
- [Setup Quiz Grading Options](https://developers.google.com/workspace/forms/api/guides/setup-grading)
- [PLAN_FOR_PLACEMENT_EXAM_v1.2.md](PLAN_FOR_PLACEMENT_EXAM_v1.2.md) — Test design specification

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-20 | Claude Code | Initial creation. Covers API capabilities, question bank JSON schema, test config schema, authentication setup, form generation pipeline, branching implementation, API limitations, project structure, dependencies, phased implementation plan, and testing strategy. |
