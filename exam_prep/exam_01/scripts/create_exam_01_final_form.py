#!/usr/bin/env python3
"""
Exam 01 Final — Google Form Generator (Prova de Final de 1º Bimestre)

Creates the final exam as a Google Form with:
  - Name-based routing: each student's name routes to their tier section
  - Section 0: Instructions + name selector (DROP_DOWN, alphabetical, per-option goToSectionId)
  - Section X: Self-Selection (only for students without an assigned tier)
               "Após os primeiros exercícios, você se sente mais habilitado(a)
                para Tier 1, Tier 2 ou Tier 3?"
  - Section 1 (Tier 1):  Q1–10,  ~15 min, max 10 pts  → SUBMIT
  - Section 2 (Tier 2):  Q1–20,  ~25 min, max 20 pts  → SUBMIT
  - Section 3 (Tier 3):  Q1–30,  ~35 min, max 30 pts  → SUBMIT
                         (only created if Tier 3 students exist in roster)
  - Flag students (Tier 1 🏁) are routed to Section 2
  - Bilingual instructions (PT/EN)
  - Quiz mode with automatic grading

Note on name selector choice type:
  The name selector uses DROP_DOWN (lista suspensa). The Google Forms API
  supports per-option section routing (goToSectionId) for both RADIO and
  SELECT (DROP_DOWN) choice types. DROP_DOWN is preferred for 63+ names
  because a long RADIO list is unwieldy on mobile devices.

Usage:
    cd exam_prep/exam_01/scripts
    python3 create_exam_01_final_form.py

    # Custom paths
    python3 create_exam_01_final_form.py \\
        --bank ../bases/exam_01_final_bank.json \\
        --roster ../bases/curated_student_roster_v2.csv

Based on: exam_prep/exam_01/docs/PLAN_EXAM_01_FINAL.md
"""

import argparse
import csv
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from validate_question_bank import run_validation_gate

SCOPES = ['https://www.googleapis.com/auth/forms.body']

# Default paths (relative to this script's location)
DEFAULT_BANK_PATH        = '../bases/exam_01_final_bank.json'
DEFAULT_ROSTER_PATH      = '../bases/curated_student_roster_v2.csv'
DEFAULT_CREDENTIALS_PATH = '../../../placement_exam/credentials.json'
DEFAULT_TOKEN_PATH       = '../../../placement_exam/token.json'


class Exam01FinalFormGenerator:
    """Generator for the Exam 01 Final Google Form."""

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
        """Load and validate exam_01_final_bank.json."""
        with open(bank_path, 'r', encoding='utf-8') as f:
            bank = json.load(f)

        if 'questions' not in bank:
            raise ValueError("Question bank missing 'questions' field")

        t1 = [q for q in bank['questions'] if q['tier'] == 1]
        t2 = [q for q in bank['questions'] if q['tier'] == 2]
        t3 = [q for q in bank['questions'] if q['tier'] == 3]

        if len(t1) != 10:
            raise ValueError(f"Expected 10 Tier 1 questions, found {len(t1)}")
        if len(t2) != 10:
            raise ValueError(f"Expected 10 Tier 2-extra questions, found {len(t2)}")
        if t3 and len(t3) != 10:
            raise ValueError(f"Expected 0 or 10 Tier 3-extra questions, found {len(t3)}")

        print(f"✓ Loaded {len(bank['questions'])} questions "
              f"(Tier 1: {len(t1)}, Tier 2-extra: {len(t2)}, Tier 3-extra: {len(t3)})")
        return bank

    def load_roster(self, roster_path: str) -> Tuple[List[Tuple[str, str]], bool]:
        """Load curated_student_roster_v2.csv.

        Column names: Curso, ID, Nome, Email, Caminho, Suggested Tier
        Encoding: utf-8-sig (BOM-aware).

        Tier mapping:
          'Tier 2'         → 'tier2'
          'Tier 3'         → 'tier3'
          'Tier 1' / '🏁'  → 'tier1'  (flag students route to tier2 in branching)
          blank            → 'unassigned'  (routes to self-selection section)

        Returns:
            (students, has_tier3) where students is an alphabetically sorted
            list of (name, tier_key) tuples and has_tier3 indicates whether
            any Tier 3 students are present.
        """
        students = []
        skipped = 0
        with open(roster_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row['Nome'].strip()
                if not name:
                    skipped += 1
                    continue

                raw = row['Suggested Tier'].strip()
                if 'Tier 3' in raw:
                    tier = 'tier3'
                elif 'Tier 2' in raw:
                    tier = 'tier2'
                elif 'Tier 1' in raw:
                    # Includes "Tier 1 🏁" — flag students are routed to tier2
                    # in setup_branching, but stored as 'tier1' here so the
                    # branching logic can apply the flag override centrally.
                    tier = 'tier1_flag' if '🏁' in raw else 'tier1'
                else:
                    tier = 'unassigned'
                    print(f"  ℹ {name} — no tier assigned, will route to self-selection")

                students.append((name, tier))

        students.sort(key=lambda x: x[0].lower())

        counts = {t: sum(1 for _, k in students if k == t) for t in
                  ['tier1', 'tier1_flag', 'tier2', 'tier3', 'unassigned']}
        has_tier3 = counts['tier3'] > 0
        has_unassigned = counts['unassigned'] > 0

        print(f"✓ Loaded {len(students)} students")
        print(f"  → Tier 1:          {counts['tier1']}")
        print(f"  → Tier 1 🏁 (flag): {counts['tier1_flag']} (will sit Tier 2 exam)")
        print(f"  → Tier 2:          {counts['tier2']}")
        print(f"  → Tier 3:          {counts['tier3']}")
        print(f"  → Unassigned:      {counts['unassigned']} (will self-select)")
        if skipped:
            print(f"  ⚠ Skipped {skipped} rows with empty name")

        return students, has_tier3, has_unassigned

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
                             students: List[Tuple[str, str]],
                             has_tier3: bool,
                             has_unassigned: bool):
        """First pass: create all sections and items.

        Physical section order:
          Section 0 — Instructions + name selector
          Section X — Self-selection  (only if has_unassigned)
          Section 1 — Tier 1 (Q1–10)
          Section 2 — Tier 2 (Q1–20)
          Section 3 — Tier 3 (Q1–30)  (only if has_tier3)

        Routing is wired in setup_branching (second pass).
        """
        requests = []
        idx = 0

        # ── Section 0: Instructions + name selector ──────────────────── #
        instructions = (
            "PT: Esta é uma avaliação OBRIGATÓRIA de final do 1º bimestre.\n"
            "Ela vale nota. Não há penalidade para respostas erradas — faça o seu melhor.\n"
            "• Nível 1 → 10 questões (~15 min)\n"
            "• Nível 2 → 20 questões (~25 min)\n"
            "• Nível 3 → 30 questões (~35 min)\n\n"
            "EN: This is a MANDATORY end-of-term exam (1st bimester).\n"
            "It counts as a grade. No penalty for wrong answers — do your best.\n"
            "• Tier 1 → 10 questions (~15 min)\n"
            "• Tier 2 → 20 questions (~25 min)\n"
            "• Tier 3 → 30 questions (~35 min)\n\n"
            "Selecione seu nome para ser direcionado(a) automaticamente para as "
            "questões do seu nível.\n"
            "Select your name to be automatically directed to your level's questions."
        )
        requests.append(self._text_item(instructions, idx))
        idx += 1

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
            required=True,
            choice_type="DROP_DOWN"
        ))
        idx += 1

        # ── Section X: Self-Selection ─────────────────────────────────── #
        if has_unassigned:
            requests.append(self._page_break(
                title="Escolha do Nível / Level Selection",
                description=(
                    "PT: Você não possui um nível pré-definido.\n"
                    "Reflita sobre seu desempenho nos primeiros exercícios da disciplina "
                    "e escolha o nível que melhor representa sua confiança atual.\n\n"
                    "EN: You do not have a pre-assigned tier.\n"
                    "Reflect on your performance in the first exercises and choose "
                    "the level that best represents your current confidence."
                ),
                index=idx
            ))
            idx += 1

            requests.append(self._choice_question(
                title=(
                    "Após os primeiros exercícios da disciplina, você se sente mais "
                    "habilitado(a) para exames Tier 1, Tier 2 ou Tier 3?\n"
                    "(After the first exercises, which exam level do you feel ready for?)"
                ),
                description=(
                    "Tier 1 — básico / basic (~15 min)\n"
                    "Tier 2 — intermediário / intermediate (~25 min)\n"
                    "Tier 3 — avançado / advanced (~35 min)"
                ),
                options=["Tier 1 — básico / basic",
                         "Tier 2 — intermediário / intermediate",
                         "Tier 3 — avançado / advanced"],
                index=idx,
                required=True
            ))
            idx += 1

        # ── Section 1: Tier 1 questions (Q1–10) ─────────────────────── #
        requests.append(self._page_break(
            title="Nível 1 — Tempos Verbais / Tier 1 — Verbal Tenses",
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

        # ── Section 2: Tier 2 questions (Q1–20) ─────────────────────── #
        requests.append(self._page_break(
            title="Nível 2 — Tempos Verbais / Tier 2 — Verbal Tenses",
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

        tier2_qs = sorted(
            [q for q in question_bank['questions'] if q['tier'] in (1, 2)],
            key=lambda q: q['order']
        )
        for q in tier2_qs:
            requests.append(self._graded_question(q, idx))
            idx += 1

        # ── Section 3: Tier 3 questions (Q1–30) ─────────────────────── #
        if has_tier3:
            requests.append(self._page_break(
                title="Nível 3 — Tempos Verbais / Tier 3 — Verbal Tenses",
                description=(
                    "PT: 30 questões • 1 ponto cada • total: 30 pontos\n"
                    "Questões 1–10: básico | 11–20: intermediário | 21–30: avançado\n"
                    "Não há penalidade para respostas erradas. Faça o seu melhor!\n\n"
                    "EN: 30 questions • 1 point each • total: 30 points\n"
                    "Questions 1–10: basic | 11–20: intermediate | 21–30: advanced\n"
                    "There is no penalty for wrong answers. Do your best!"
                ),
                index=idx
            ))
            idx += 1

            tier3_qs = sorted(
                question_bank['questions'],
                key=lambda q: q['order']
            )
            for q in tier3_qs:
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
            if has_unassigned:
                print(f"  → Section X: self-selection question")
            print(f"  → Section 1: {len(tier1_qs)} questions (Tier 1)")
            print(f"  → Section 2: {len(tier2_qs)} questions (Tier 2 / Flag)")
            if has_tier3:
                print(f"  → Section 3: {len(question_bank['questions'])} questions (Tier 3)")
        except HttpError as error:
            print(f"✗ Error building form structure: {error}")
            sys.exit(1)

    # ------------------------------------------------------------------ #
    #  Branching (second pass)                                            #
    # ------------------------------------------------------------------ #

    def setup_branching(self,
                        students: List[Tuple[str, str]],
                        has_tier3: bool,
                        has_unassigned: bool):
        """Wire each student's name to the correct section.

        Reads back the form to get live item IDs, then:
        1. Patches the name selector with per-student goToSectionId.
        2. Patches the self-selection question (Section X) with per-option
           goToSectionId pointing to Tier 1 / 2 / 3 sections.

        Routing rules:
          tier1       → Section 1
          tier1_flag  → Section 2  (flag students sit the Tier 2 exam)
          tier2       → Section 2
          tier3       → Section 3
          unassigned  → Section X
        """
        try:
            form = self.service.forms().get(formId=self.form_id).execute()
            items = form.get('items', [])

            section_ids: Dict[str, Optional[str]] = {
                'self_select': None,
                'tier1': None,
                'tier2': None,
                'tier3': None,
            }
            name_item_id: Optional[str] = None
            name_item_index: Optional[int] = None
            self_select_item_id: Optional[str] = None
            self_select_item_index: Optional[int] = None

            for i, item in enumerate(items):
                title = item.get('title', '')

                if 'pageBreakItem' in item:
                    if 'Nível 1' in title or 'Tier 1' in title:
                        if 'Nível 2' not in title and 'Tier 2' not in title:
                            section_ids['tier1'] = item['itemId']
                    if 'Nível 2' in title or 'Tier 2' in title:
                        if 'Nível 1' not in title and 'Tier 1' not in title:
                            section_ids['tier2'] = item['itemId']
                    if 'Nível 3' in title or 'Tier 3' in title:
                        section_ids['tier3'] = item['itemId']
                    if 'Escolha do Nível' in title or 'Level Selection' in title:
                        section_ids['self_select'] = item['itemId']

                if 'questionItem' in item:
                    if 'Selecione seu nome' in title:
                        name_item_id = item['itemId']
                        name_item_index = i
                    if 'habilitado' in title or 'feel ready' in title:
                        self_select_item_id = item['itemId']
                        self_select_item_index = i

            # Validate required sections
            missing = []
            if not name_item_id:
                missing.append("name selector question")
            if not section_ids['tier1']:
                missing.append("Tier 1 section page-break")
            if not section_ids['tier2']:
                missing.append("Tier 2 section page-break")
            if has_tier3 and not section_ids['tier3']:
                missing.append("Tier 3 section page-break")
            if has_unassigned and not section_ids['self_select']:
                missing.append("Self-selection section page-break")
            if has_unassigned and not self_select_item_id:
                missing.append("Self-selection question")

            if missing:
                print(f"⚠ Could not find: {', '.join(missing)}")
                print("  Branching skipped — configure routing manually in the form UI")
                return

            # ── 1. Wire name selector ─────────────────────────────────── #
            name_options = []
            for name, tier in students:
                if tier == 'tier1':
                    dest = section_ids['tier1']
                elif tier == 'tier1_flag':
                    dest = section_ids['tier2']   # flag → tier 2 exam
                elif tier == 'tier2':
                    dest = section_ids['tier2']
                elif tier == 'tier3':
                    dest = section_ids['tier3'] or section_ids['tier2']
                else:  # unassigned
                    dest = section_ids['self_select']

                name_options.append({"value": name, "goToSectionId": dest})

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
                                        "type": "DROP_DOWN",
                                        "options": name_options,
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
            t1f = sum(1 for _, t in students if t == 'tier1_flag')
            t2 = sum(1 for _, t in students if t == 'tier2')
            t3 = sum(1 for _, t in students if t == 'tier3')
            un = sum(1 for _, t in students if t == 'unassigned')
            print(f"✓ Name selector branching configured for {len(students)} names")
            print(f"  → {t1} names → Section 1 (Tier 1)")
            print(f"  → {t1f} names → Section 2 (Tier 1 🏁 flag)")
            print(f"  → {t2} names → Section 2 (Tier 2)")
            print(f"  → {t3} names → Section 3 (Tier 3)")
            print(f"  → {un} names → Section X (self-select)")

            # ── 2. Wire self-selection question ───────────────────────── #
            if has_unassigned and self_select_item_id is not None:
                self_select_options = [
                    {
                        "value": "Tier 1 — básico / basic",
                        "goToSectionId": section_ids['tier1']
                    },
                    {
                        "value": "Tier 2 — intermediário / intermediate",
                        "goToSectionId": section_ids['tier2']
                    },
                    {
                        "value": "Tier 3 — avançado / advanced",
                        "goToSectionId": section_ids.get('tier3') or section_ids['tier2']
                    },
                ]
                self.service.forms().batchUpdate(
                    formId=self.form_id,
                    body={"requests": [{
                        "updateItem": {
                            "item": {
                                "itemId": self_select_item_id,
                                "questionItem": {
                                    "question": {
                                        "required": True,
                                        "choiceQuestion": {
                                            "type": "RADIO",
                                            "options": self_select_options,
                                            "shuffle": False
                                        }
                                    }
                                }
                            },
                            "location": {"index": self_select_item_index},
                            "updateMask": "questionItem.question.choiceQuestion.options"
                        }
                    }]}
                ).execute()
                print("✓ Self-selection branching configured")
                print("  → 'Tier 1' → Section 1")
                print("  → 'Tier 2' → Section 2")
                tier3_note = "Section 3" if section_ids.get('tier3') else "Section 2 (no Tier 3 section)"
                print(f"  → 'Tier 3' → {tier3_note}")

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
        print("✓ EXAM 01 FINAL FORM CREATED SUCCESSFULLY")
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
        print("      Submit test responses for a Tier 1, Tier 2, and unassigned name")
        print("      Verify each lands on the correct section")
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
        """Section separator."""
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
                         required: bool = True,
                         choice_type: str = "RADIO") -> Dict[str, Any]:
        """Ungraded choice question (name selector or self-selection).

        choice_type: "RADIO" (default) or "DROP_DOWN" (SELECT in the API).
        """
        return {
            "createItem": {
                "item": {
                    "title": title.replace("\n", " "),
                    "description": description,
                    "questionItem": {
                        "question": {
                            "required": required,
                            "choiceQuestion": {
                                "type": choice_type,
                                "options": [{"value": opt} for opt in options],
                                "shuffle": False
                            }
                        }
                    }
                },
                "location": {"index": index}
            }
        }

    def _graded_question(self, question: Dict[str, Any], index: int) -> Dict[str, Any]:
        """Graded RADIO question from the question bank."""
        correct = next(
            opt["text"] for opt in question["options"] if opt["is_correct"]
        )

        question_text: str = question["question_text"]
        passage: Optional[str] = None
        title: str = question_text

        # Split on the LAST \n\n: passage/context → description, question → title
        last_break = question_text.rfind("\n\n")
        if last_break != -1:
            passage = question_text[:last_break].strip()
            title = question_text[last_break:].strip()

        instruction_pt: str = question.get("instruction_pt", "")
        desc_parts = [p for p in [instruction_pt, passage] if p]
        description: Optional[str] = "\n\n".join(desc_parts) if desc_parts else None

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
        description='Generate Exam 01 Final Google Form'
    )
    parser.add_argument('--bank',        default=DEFAULT_BANK_PATH)
    parser.add_argument('--roster',      default=DEFAULT_ROSTER_PATH)
    parser.add_argument('--credentials', default=DEFAULT_CREDENTIALS_PATH)
    parser.add_argument('--token',       default=DEFAULT_TOKEN_PATH)
    parser.add_argument(
        '--title',
        default=(
            'Prova Final 1º Bimestre — Tempos Verbais / '
            'Exam 01 Final — Verbal Tenses'
        )
    )
    args = parser.parse_args()

    script_dir = Path(__file__).parent
    bank_path        = (script_dir / args.bank).resolve()
    roster_path      = (script_dir / args.roster).resolve()
    credentials_path = (script_dir / args.credentials).resolve()
    token_path       = (script_dir / args.token).resolve()

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
    print("EXAM 01 FINAL — GOOGLE FORM GENERATOR")
    print("=" * 70)
    print(f"\nQuestion bank:  {bank_path}")
    print(f"Student roster: {roster_path}")
    print(f"Form title:     {args.title}\n")

    gen = Exam01FinalFormGenerator(str(credentials_path), str(token_path))

    try:
        print("Step 1: Authenticating...")
        gen.authenticate()

        print("\nStep 2: Loading question bank...")
        question_bank = gen.load_question_bank(str(bank_path))

        print("\nStep 2.5: Validating question bank (§3.4 and §3.5)...")
        script_dir = Path(__file__).parent
        prior_banks = [
            str((script_dir / '../../../placement_exam/bases/question_bank.json').resolve()),
            str((script_dir / '../../bases/prep_exam_bank.json').resolve()),
        ]
        if not run_validation_gate(str(bank_path), prior_banks):
            print("\n✗ Form generation aborted by user after validation.")
            sys.exit(1)

        print("\nStep 3: Loading student roster...")
        students, has_tier3, has_unassigned = gen.load_roster(str(roster_path))

        print("\nStep 4: Creating blank form...")
        gen.create_blank_form(args.title)

        print("\nStep 5: Enabling quiz mode...")
        gen.enable_quiz_mode()

        print("\nStep 6: Building form structure (first pass)...")
        gen.build_form_structure(question_bank, students, has_tier3, has_unassigned)

        print("\nStep 7: Wiring branching (second pass)...")
        gen.setup_branching(students, has_tier3, has_unassigned)

        gen.print_urls()

    except Exception as exc:
        print(f"\n✗ Unexpected error: {exc}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
