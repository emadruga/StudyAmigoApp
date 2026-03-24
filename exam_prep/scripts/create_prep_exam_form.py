#!/usr/bin/env python3
"""
Mid-E01 Prep Exam — Google Form Generator

Creates the prep exam as a Google Form with:
  - Name-based routing: each student's name routes to their tier section
  - Section 1 (Tier 1):  Q1–10,  ~15 min, max 10 pts
  - Section 2 (Tier 2):  Q1–20,  ~25 min, max 20 pts
  - Flag students (provisional Tier 1) are routed to Section 2 (full exam)
  - Bilingual instructions (PT/EN)
  - Quiz mode with automatic grading

Structure (Option A — routing at name level):
  Section 0: Instructions + name selector (RADIO, alphabetical, per-option goToSectionId)
  Section 1: Tier 1 questions (Q1–10)          → SUBMIT at end
  Section 2: Tier 2 questions (Q1–20, all 20)  → SUBMIT at end

Note on RADIO vs DROP_DOWN:
  The name selector uses RADIO (multiple choice list), not DROP_DOWN.
  Google Forms only supports per-option section routing (goToSectionId)
  for RADIO-type questions. DROP_DOWN questions do not honour goToSectionId
  in the form UI, even if accepted by the API.

Usage:
    cd exam_prep/scripts
    python3 create_prep_exam_form.py

    # Custom paths
    python3 create_prep_exam_form.py --bank ../bases/prep_exam_bank.json \\
                                     --roster ../bases/curated_student_roster.csv

Based on: exam_prep/docs/PLAN_PREP_EXAM.md
"""

import argparse
import csv
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/forms.body']

# Default paths (relative to this script's location)
DEFAULT_BANK_PATH        = '../bases/prep_exam_bank.json'
DEFAULT_ROSTER_PATH      = '../../placement_exam/bases/curated_student_roster.csv'
DEFAULT_CREDENTIALS_PATH = '../../placement_exam/credentials.json'
DEFAULT_TOKEN_PATH       = '../../placement_exam/token.json'


class PrepExamFormGenerator:
    """Generator for the Mid-E01 Prep Exam Google Form."""

    def __init__(self, credentials_path: str, token_path: str):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None
        self.form_id = None

    # ------------------------------------------------------------------ #
    #  Auth                                                                #
    # ------------------------------------------------------------------ #

    def authenticate(self):
        """OAuth2 — reuses the placement exam token if still valid."""
        creds = None
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
            with open(self.token_path, 'w') as f:
                f.write(creds.to_json())

        self.service = build('forms', 'v1', credentials=creds)
        print("✓ Authentication successful")

    # ------------------------------------------------------------------ #
    #  Data loading                                                        #
    # ------------------------------------------------------------------ #

    def load_question_bank(self, bank_path: str) -> Dict[str, Any]:
        """Load and validate prep_exam_bank.json."""
        with open(bank_path, 'r', encoding='utf-8') as f:
            bank = json.load(f)

        if 'questions' not in bank:
            raise ValueError("Question bank missing 'questions' field")

        t1 = [q for q in bank['questions'] if q['tier'] == 1]
        t2 = [q for q in bank['questions'] if q['tier'] == 2]

        if len(t1) != 10:
            raise ValueError(f"Expected 10 Tier 1 questions, found {len(t1)}")
        if len(t2) != 10:
            raise ValueError(f"Expected 10 Tier 2 questions, found {len(t2)}")

        print(f"✓ Loaded {len(bank['questions'])} questions "
              f"(Tier 1: {len(t1)}, Tier 2 extra: {len(t2)})")
        return bank

    def load_roster(self, roster_path: str) -> List[Tuple[str, str]]:
        """Load curated_student_roster.csv.

        Returns:
            Alphabetically sorted list of (name, 'tier1'|'tier2') tuples.
            Flag students are treated as 'tier2' (receive full 20-question exam).
        """
        # The roster CSV contains one non-UTF-8 byte (0x8b in "Cauã Jorge").
        # latin-1 decodes every byte without error; accented names may show
        # a single garbled character (e.g. "Cau‹" instead of "Cauã") but the
        # entry is still uniquely identifiable in the form dropdown.
        students = []
        with open(roster_path, 'r', encoding='latin-1') as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row['Name'].strip()
                suggested = row['Suggested Tier'].strip()
                # Flag students → full exam (tier2) to resolve placement
                tier = 'tier2' if ('Tier 2' in suggested or 'Flag' in suggested) else 'tier1'
                students.append((name, tier))

        students.sort(key=lambda x: x[0].lower())

        t1 = sum(1 for _, t in students if t == 'tier1')
        t2 = sum(1 for _, t in students if t == 'tier2')
        print(f"✓ Loaded {len(students)} students "
              f"(Tier 1: {t1}, Tier 2 + Flag: {t2})")
        return students

    # ------------------------------------------------------------------ #
    #  Form creation                                                       #
    # ------------------------------------------------------------------ #

    def create_blank_form(self, title: str) -> str:
        try:
            result = self.service.forms().create(body={
                "info": {"title": title, "documentTitle": title}
            }).execute()
            self.form_id = result['formId']
            print(f"✓ Blank form created: {self.form_id}")
            return self.form_id
        except HttpError as error:
            print(f"✗ Error creating form: {error}")
            sys.exit(1)

    def enable_quiz_mode(self):
        try:
            self.service.forms().batchUpdate(
                formId=self.form_id,
                body={"requests": [{
                    "updateSettings": {
                        "settings": {"quizSettings": {"isQuiz": True}},
                        "updateMask": "quizSettings.isQuiz"
                    }
                }]}
            ).execute()
            print("✓ Quiz mode enabled")
        except HttpError as error:
            print(f"✗ Error enabling quiz mode: {error}")
            sys.exit(1)

    def build_form_structure(self,
                             question_bank: Dict[str, Any],
                             students: List[Tuple[str, str]]):
        """First pass: create all sections and items.

        Section 0 — Instructions + name selector (routing wired in second pass)
        Section 1 — Tier 1:  Q1–10
        Section 2 — Tier 2:  Q1–20 (all 20 questions)
        """
        requests = []
        idx = 0

        # ── Section 0: Instructions ──────────────────────────────────── #
        instructions = (
            "PT: Esta é uma avaliação OPCIONAL de meio de exercício. "
            "Ela NÃO conta como nota. Serve para você medir seu próprio "
            "progresso com os Tempos Verbais estudados no JAVUMBO.\n"
            "• Nível 1 → 10 questões (~15 min)\n"
            "• Nível 2 → 20 questões (~25 min)\n\n"
            "EN: This is an OPTIONAL mid-exercise check. "
            "It does NOT count as a grade. Use it to measure your own "
            "progress with the Verbal Tenses you have been studying in JAVUMBO.\n"
            "• Tier 1 → 10 questions (~15 min)\n"
            "• Tier 2 → 20 questions (~25 min)\n\n"
            "Selecione seu nome na próxima pergunta para ser direcionado(a) "
            "automaticamente para as questões do seu nível.\n"
            "Select your name in the next question to be automatically directed "
            "to your level's questions."
        )
        requests.append(self._text_item(instructions, idx))
        idx += 1

        # Name selector — options are plain text here; goToSectionId added in second pass
        name_opts = [name for name, _ in students]
        requests.append(self._choice_question(
            title="Selecione seu nome. / Select your name.",
            description=(
                "Os nomes estão em ordem alfabética. "
                "Após selecionar, você irá automaticamente para as questões do seu nível.\n"
                "Names are in alphabetical order. "
                "After selecting, you will go automatically to your level's questions."
            ),
            options=name_opts,
            index=idx,
            required=True
        ))
        idx += 1

        # ── Section 1: Tier 1 Questions (Q1–10) ─────────────────────── #
        requests.append(self._page_break(
            title="Nível 1 — Tempos Verbais Essenciais / Tier 1 — Essential Verbal Tenses",
            description=(
                "PT: 10 questões • 1 ponto cada • total: 10 pontos\n"
                "Não há penalidade para respostas erradas. Faça o seu melhor!\n\n"
                "EN: 10 questions • 1 point each • total: 10 points\n"
                "There is no penalty for wrong answers. Do your best!"
            ),
            index=idx
        ))
        idx += 1

        tier1_qs = sorted(
            [q for q in question_bank['questions'] if q['tier'] == 1],
            key=lambda q: q['order']
        )
        for q in tier1_qs:
            requests.append(self._graded_question(q, idx))
            idx += 1

        # ── Section 2: Tier 2 Questions (Q1–20) ─────────────────────── #
        requests.append(self._page_break(
            title="Nível 2 — Tempos Verbais: Avaliação Completa / Tier 2 — Full Verbal Tenses Assessment",
            description=(
                "PT: 20 questões • 1 ponto cada • total: 20 pontos\n"
                "Questões 1–10: tempos básicos | Questões 11–20: tempos avançados\n"
                "Não há penalidade para respostas erradas. Faça o seu melhor!\n\n"
                "EN: 20 questions • 1 point each • total: 20 points\n"
                "Questions 1–10: basic tenses | Questions 11–20: advanced tenses\n"
                "There is no penalty for wrong answers. Do your best!"
            ),
            index=idx
        ))
        idx += 1

        all_qs = sorted(question_bank['questions'], key=lambda q: q['order'])
        for q in all_qs:
            requests.append(self._graded_question(q, idx))
            idx += 1

        # ── Send ─────────────────────────────────────────────────────── #
        try:
            self.service.forms().batchUpdate(
                formId=self.form_id,
                body={"requests": requests}
            ).execute()
            print(f"✓ Form structure built ({idx} items)")
            print(f"  → Section 0: instructions + name selector ({len(name_opts)} names)")
            print(f"  → Section 1: {len(tier1_qs)} questions (Tier 1)")
            print(f"  → Section 2: {len(all_qs)} questions (Tier 2 / Flag)")
        except HttpError as error:
            print(f"✗ Error building form structure: {error}")
            sys.exit(1)

    # ------------------------------------------------------------------ #
    #  Branching (second pass)                                            #
    # ------------------------------------------------------------------ #

    def setup_branching(self, students: List[Tuple[str, str]]):
        """Wire each student's name to the correct section.

        Reads back the form to get live item IDs, then patches the name
        selector with per-option goToSectionId values.
        """
        try:
            form = self.service.forms().get(formId=self.form_id).execute()
            items = form.get('items', [])

            # Locate section page-break IDs and the name question item ID
            section_ids: Dict[str, str] = {}
            name_item_id: str | None = None
            name_item_index: int | None = None

            for i, item in enumerate(items):
                title = item.get('title', '')

                if 'pageBreakItem' in item:
                    if 'Nível 1' in title or 'Tier 1' in title:
                        section_ids['tier1'] = item['itemId']
                    elif 'Nível 2' in title or 'Tier 2' in title:
                        section_ids['tier2'] = item['itemId']

                if 'questionItem' in item and 'Selecione seu nome' in title:
                    name_item_id = item['itemId']
                    name_item_index = i

            # Validate
            missing = []
            if not name_item_id:
                missing.append("name selector question")
            if 'tier1' not in section_ids:
                missing.append("Tier 1 section page-break")
            if 'tier2' not in section_ids:
                missing.append("Tier 2 section page-break")

            if missing:
                print(f"⚠ Could not find: {', '.join(missing)}")
                print("  Branching skipped — configure routing manually in the form UI")
                return

            # Build options with per-student goToSectionId
            options = []
            for name, tier in students:   # already sorted alphabetically
                options.append({
                    "value": name,
                    "goToSectionId": section_ids[tier]
                })

            self.service.forms().batchUpdate(
                formId=self.form_id,
                body={"requests": [{
                    "updateItem": {
                        "item": {
                            "itemId": name_item_id,
                            "questionItem": {
                                "question": {
                                    "required": True,
                                    "choiceQuestion": {
                                        "type": "RADIO",
                                        "options": options,
                                        "shuffle": False
                                    }
                                }
                            }
                        },
                        "location": {"index": name_item_index},
                        "updateMask": "questionItem.question.choiceQuestion.options"
                    }
                }]}
            ).execute()

            t1 = sum(1 for _, t in students if t == 'tier1')
            t2 = sum(1 for _, t in students if t == 'tier2')
            print(f"✓ Branching configured for {len(students)} names")
            print(f"  → {t1} names → Section 1 (Tier 1, Q1–10)")
            print(f"  → {t2} names → Section 2 (Tier 2/Flag, Q1–20)")

        except HttpError as error:
            print(f"⚠ Warning: Could not set up branching: {error}")
            print("  Configure routing manually in the form UI")

    # ------------------------------------------------------------------ #
    #  Output                                                              #
    # ------------------------------------------------------------------ #

    def print_urls(self):
        edit_url = f"https://docs.google.com/forms/d/{self.form_id}/edit"
        view_url = f"https://docs.google.com/forms/d/{self.form_id}/viewform"

        print("\n" + "=" * 70)
        print("✓ PREP EXAM FORM CREATED SUCCESSFULLY")
        print("=" * 70)
        print(f"\n📝 Edit form (instructor):\n   {edit_url}")
        print(f"\n👥 Share with students:\n   {view_url}")
        print("\n" + "=" * 70)
        print("\n⚠️  MANUAL STEPS REQUIRED AFTER CREATION:")
        print()
        print("   1. 🔴 Enable responses:")
        print("      Open the edit URL → click the toggle at the top")
        print("      from 'Not accepting responses' → 'Accepting responses'")
        print("      (API-created forms default to NOT accepting responses)")
        print()
        print("   2. Link to Google Sheets:")
        print("      Responses tab → Link to Sheets → create new spreadsheet")
        print()
        print("   3. Collect email addresses:")
        print("      Settings (⚙️) → Responses → Collect email addresses: ON")
        print()
        print("   4. Limit to 1 response per person:")
        print("      Settings (⚙️) → Responses → Limit to 1 response: ON")
        print()
        print("   5. Test branching:")
        print("      Submit one test response with a Tier 1 name → verify 10 questions appear")
        print("      Submit one test response with a Tier 2 name → verify 20 questions appear")
        print("      Delete test responses from the Sheets spreadsheet after testing")
        print()
        print("   6. Share the view URL with students when ready")
        print("=" * 70 + "\n")

    # ------------------------------------------------------------------ #
    #  Item builder helpers                                                #
    # ------------------------------------------------------------------ #

    def _text_item(self, text: str, index: int) -> Dict[str, Any]:
        """Description-only text block (no answer required)."""
        return {
            "createItem": {
                "item": {
                    "title": "",
                    "description": text,
                    "textItem": {}
                },
                "location": {"index": index}
            }
        }

    def _page_break(self, title: str, description: str, index: int) -> Dict[str, Any]:
        """Section separator. Title must be single-line for the API."""
        return {
            "createItem": {
                "item": {
                    "title": title,
                    "description": description,
                    "pageBreakItem": {}
                },
                "location": {"index": index}
            }
        }

    def _choice_question(self, title: str, description: str,
                         options: List[str], index: int,
                         required: bool = True) -> Dict[str, Any]:
        """Ungraded RADIO question (used for the name selector)."""
        item: Dict[str, Any] = {
            "createItem": {
                "item": {
                    "title": title,
                    "description": description,
                    "questionItem": {
                        "question": {
                            "required": required,
                            "choiceQuestion": {
                                "type": "RADIO",
                                "options": [{"value": opt} for opt in options],
                                "shuffle": False
                            }
                        }
                    }
                },
                "location": {"index": index}
            }
        }
        return item

    def _graded_question(self, question: Dict[str, Any], index: int) -> Dict[str, Any]:
        """Graded RADIO question from the question bank.

        Layout rules:
          - description = Portuguese instruction (instruction_pt) +, if present,
                          the passage/context text (everything before the last \\n\\n)
          - title       = the actual question sentence (after the last \\n\\n),
                          with any remaining \\n replaced by spaces
        """
        correct = next(
            opt["text"] for opt in question["options"] if opt["is_correct"]
        )

        question_text: str = question["question_text"]
        passage: str | None = None
        title: str = question_text

        # Split on the LAST \n\n: passage/context → description, question → title
        last_break = question_text.rfind("\n\n")
        if last_break != -1:
            passage = question_text[:last_break].strip()
            title = question_text[last_break:].strip()

        # Build description: Portuguese instruction first, passage below (if any)
        instruction_pt: str = question.get("instruction_pt", "")
        desc_parts = [p for p in [instruction_pt, passage] if p]
        description: str | None = "\n\n".join(desc_parts) if desc_parts else None

        # Google Forms API rejects newlines inside title
        title = title.replace("\n", " ")

        item: Dict[str, Any] = {
            "createItem": {
                "item": {
                    "title": title,
                    "questionItem": {
                        "question": {
                            "required": True,
                            "grading": {
                                "pointValue": question["point_value"],
                                "correctAnswers": {
                                    "answers": [{"value": correct}]
                                }
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

        if description:
            item["createItem"]["item"]["description"] = description

        return item


# ---------------------------------------------------------------------- #
#  Entry point                                                            #
# ---------------------------------------------------------------------- #

def main():
    parser = argparse.ArgumentParser(
        description='Generate Mid-E01 Prep Exam Google Form'
    )
    parser.add_argument('--bank',        default=DEFAULT_BANK_PATH)
    parser.add_argument('--roster',      default=DEFAULT_ROSTER_PATH)
    parser.add_argument('--credentials', default=DEFAULT_CREDENTIALS_PATH)
    parser.add_argument('--token',       default=DEFAULT_TOKEN_PATH)
    parser.add_argument(
        '--title',
        default=(
            'Avaliação de Progresso E01 — Tempos Verbais / '
            'E01 Progress Check — Verbal Tenses'
        )
    )
    args = parser.parse_args()

    script_dir = Path(__file__).parent
    bank_path        = (script_dir / args.bank).resolve()
    roster_path      = (script_dir / args.roster).resolve()
    credentials_path = (script_dir / args.credentials).resolve()
    token_path       = (script_dir / args.token).resolve()

    # Validate required files
    for path, label in [
        (bank_path,        'Question bank (--bank)'),
        (roster_path,      'Student roster (--roster)'),
        (credentials_path, 'credentials.json (--credentials)'),
    ]:
        if not path.exists():
            print(f"✗ {label} not found: {path}")
            if 'credentials' in label:
                print("\n  To obtain credentials.json:")
                print("  1. Go to https://console.cloud.google.com/")
                print("  2. Enable the Google Forms API")
                print("  3. Create OAuth 2.0 credentials (Desktop app)")
                print("  4. Download as credentials.json to placement_exam/")
            sys.exit(1)

    print("=" * 70)
    print("MID-E01 PREP EXAM — GOOGLE FORM GENERATOR")
    print("=" * 70)
    print(f"\nQuestion bank:  {bank_path}")
    print(f"Student roster: {roster_path}")
    print(f"Form title:     {args.title}\n")

    gen = PrepExamFormGenerator(str(credentials_path), str(token_path))

    try:
        print("Step 1: Authenticating...")
        gen.authenticate()

        print("\nStep 2: Loading question bank...")
        question_bank = gen.load_question_bank(str(bank_path))

        print("\nStep 3: Loading student roster...")
        students = gen.load_roster(str(roster_path))

        print("\nStep 4: Creating blank form...")
        gen.create_blank_form(args.title)

        print("\nStep 5: Enabling quiz mode...")
        gen.enable_quiz_mode()

        print("\nStep 6: Building form structure (first pass)...")
        gen.build_form_structure(question_bank, students)

        print("\nStep 7: Wiring name-based branching (second pass)...")
        gen.setup_branching(students)

        gen.print_urls()

    except Exception as exc:
        print(f"\n✗ Unexpected error: {exc}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
