#!/usr/bin/env python3
"""
Google Forms Placement Test Generator

This script generates an ESL placement test as a Google Form using the Google Forms API v1.
It reads from the question_bank.json and creates a quiz-mode form with:
- Three-path branching (Path A: Band 1 only, Path B/C: Full test)
- Bilingual instructions (Portuguese/English)
- Automatic grading
- Worked example for Path A students

Based on: placement_exam/docs/PROGRAMMATIC_PLACEMENT_EXAM.md
          placement_exam/docs/PLAN_FOR_PLACEMENT_EXAM_v1.2.md

Usage:
    python create_placement_form.py [--bank BANK_PATH] [--semester SEMESTER_ID]
"""

import argparse
import json
import os
import sys
from typing import Dict, List, Any
from pathlib import Path

# Google API imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/forms.body']

# Default paths
DEFAULT_BANK_PATH = '../bases/question_bank.json'
DEFAULT_CREDENTIALS_PATH = '../credentials.json'
DEFAULT_TOKEN_PATH = '../token.json'


class PlacementFormGenerator:
    """Generator for ESL Placement Test Google Forms."""

    def __init__(self, credentials_path: str, token_path: str):
        """Initialize the generator with authentication.

        Args:
            credentials_path: Path to credentials.json
            token_path: Path to token.json (will be created on first run)
        """
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None
        self.form_id = None

    def authenticate(self):
        """Authenticate with Google Forms API using OAuth2."""
        creds = None

        # Token file stores user's access and refresh tokens
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)

        # If no valid credentials, let user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)

            # Save credentials for next run
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())

        self.service = build('forms', 'v1', credentials=creds)
        print("✓ Authentication successful")

    def load_question_bank(self, bank_path: str) -> Dict[str, Any]:
        """Load and validate the question bank JSON.

        Args:
            bank_path: Path to question_bank.json

        Returns:
            Parsed question bank dictionary
        """
        with open(bank_path, 'r', encoding='utf-8') as f:
            bank = json.load(f)

        # Basic validation
        if 'questions' not in bank:
            raise ValueError("Question bank missing 'questions' field")

        print(f"✓ Loaded {len(bank['questions'])} questions from bank")
        return bank

    def create_blank_form(self, title: str, description: str = "") -> str:
        """Create a blank Google Form.

        Args:
            title: Form title
            description: Form description (optional)

        Returns:
            Form ID of the created form
        """
        try:
            form = {
                "info": {
                    "title": title,
                    "documentTitle": title
                }
            }

            if description:
                form["info"]["description"] = description

            result = self.service.forms().create(body=form).execute()
            self.form_id = result['formId']

            print(f"✓ Created blank form with ID: {self.form_id}")
            return self.form_id

        except HttpError as error:
            print(f"✗ Error creating form: {error}")
            sys.exit(1)

    def enable_quiz_mode(self):
        """Enable quiz mode on the form."""
        try:
            update = {
                "requests": [{
                    "updateSettings": {
                        "settings": {
                            "quizSettings": {
                                "isQuiz": True
                            }
                        },
                        "updateMask": "quizSettings.isQuiz"
                    }
                }]
            }

            self.service.forms().batchUpdate(
                formId=self.form_id,
                body=update
            ).execute()

            print("✓ Enabled quiz mode")

        except HttpError as error:
            print(f"✗ Error enabling quiz mode: {error}")
            sys.exit(1)

    def build_form_structure(self, question_bank: Dict[str, Any]):
        """Build the complete form structure with all items.

        Args:
            question_bank: The loaded question bank
        """
        requests = []
        current_index = 0

        # === SECTION 0: Instructions and Self-Assessment Gate ===

        # Instructions text block
        instructions_text = (
            "**Objetivo do teste / Test purpose:**\n\n"
            "PT: Este teste avalia seu nível atual de leitura em inglês. "
            "Ele nos ajudará a indicar materiais de leitura adequados ao seu nível.\n\n"
            "EN: This test assesses your current English reading level. "
            "It will help us assign reading materials that match your level.\n\n"
            "**Nota importante / Important note:**\n\n"
            "PT: Este teste NÃO conta como nota. Ele é usado apenas para nos "
            "ajudar a escolher os materiais certos para você.\n\n"
            "EN: This test does NOT count as a grade. It is only used to help us "
            "choose the right materials for you."
        )

        requests.append(self._create_text_item(instructions_text, current_index))
        current_index += 1

        # Self-assessment gate question
        gate_question = (
            "Como você descreveria sua experiência com o idioma inglês?\n\n"
            "(How would you describe your experience with the English language?)"
        )

        gate_options = [
            "Nunca estudei inglês e não tenho contato com o idioma. "
            "(I have never studied English and I have no contact with the language.)",

            "Estudei inglês no ensino médio (escola pública ou particular), "
            "mas não me considero fluente. "
            "(I studied English in high school, but I don't consider myself fluent.)",

            "Já fiz curso de inglês ou me considero intermediário/avançado. "
            "(I have taken English courses or I consider myself intermediate/advanced.)"
        ]

        # Note: We'll set up branching in a second pass after getting section IDs
        requests.append(self._create_choice_question(
            gate_question, gate_options, current_index, required=True
        ))
        current_index += 1

        # === SECTION 1: Band 1 (Foundation) ===

        # Page break with section header
        band1_header = (
            "Parte 1: Vocabulário Básico e Frases / Part 1: Basic Vocabulary and Sentences\n\n"
            "Tempo estimado / Estimated time: ~5 minutos / ~5 minutes"
        )

        requests.append(self._create_page_break(band1_header, current_index))
        current_index += 1

        # Worked example
        worked_example_text = (
            "**Antes de começar, veja este exemplo de como responder as questões:**\n"
            "**Before you start, look at this example of how to answer the questions:**\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "**Exemplo / Example:**\n\n"
            "What does \"university\" mean?\n\n"
            "a) Universidade ← ✅ Resposta correta!\n"
            "b) Uniforme\n"
            "c) Universal\n"
            "d) Único\n\n"
            "A pergunta \"What does X mean?\" significa \"O que X significa?\"\n"
            "Escolha a opção que melhor traduz ou define a palavra em inglês.\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )

        requests.append(self._create_text_item(worked_example_text, current_index))
        current_index += 1

        # Band 1 questions (Q1-Q10)
        band1_questions = [q for q in question_bank['questions'] if q['band'] == 1]
        for question in band1_questions[:10]:  # Ensure exactly 10
            requests.append(self._create_graded_question(question, current_index))
            current_index += 1

        # Post-Band 1 routing question (for path divergence)
        routing_question = (
            "Selecione a mesma opção que você escolheu na primeira página:\n\n"
            "(Select the same option you chose on the first page:)"
        )

        routing_options = [
            "Nunca estudei inglês (Path A)",
            "Estudei inglês no ensino médio (Path B)",
            "Já fiz curso de inglês (Path C)"
        ]

        # We'll set goToSectionId / goToAction in second pass
        requests.append(self._create_choice_question(
            routing_question, routing_options, current_index, required=True
        ))
        current_index += 1

        # === SECTION 2: Band 2 (Developing) ===

        band2_header = (
            "Parte 2: Leitura Intermediária / Part 2: Intermediate Reading\n\n"
            "Tempo estimado / Estimated time: ~6 minutos / ~6 minutes\n\n"
            "PT: Estas questões são mais difíceis. Faça o seu melhor! "
            "Não há penalidade para respostas erradas.\n\n"
            "EN: These questions are more difficult. Do your best! "
            "There is no penalty for wrong answers."
        )

        requests.append(self._create_page_break(band2_header, current_index))
        current_index += 1

        # Band 2 questions (Q11-Q18)
        band2_questions = [q for q in question_bank['questions'] if q['band'] == 2]
        for question in band2_questions[:8]:  # Ensure exactly 8
            requests.append(self._create_graded_question(question, current_index))
            current_index += 1

        # === SECTION 3: Band 3 (Expanding) ===

        band3_header = (
            "Parte 3: Leitura Avançada / Part 3: Advanced Reading\n\n"
            "Tempo estimado / Estimated time: ~7 minutos / ~7 minutes\n\n"
            "PT: Estas questões são desafiadoras. Se não tiver certeza, "
            "faça sua melhor tentativa.\n\n"
            "EN: These questions are challenging. If you are unsure, "
            "make your best guess."
        )

        requests.append(self._create_page_break(band3_header, current_index))
        current_index += 1

        # Band 3 questions (Q19-Q25)
        band3_questions = [q for q in question_bank['questions'] if q['band'] == 3]
        for question in band3_questions[:7]:  # Ensure exactly 7
            requests.append(self._create_graded_question(question, current_index))
            current_index += 1

        # === Send batch update ===

        try:
            self.service.forms().batchUpdate(
                formId=self.form_id,
                body={"requests": requests}
            ).execute()

            print(f"✓ Created form structure with {current_index} items")
            print(f"  - Band 1: {len(band1_questions[:10])} questions")
            print(f"  - Band 2: {len(band2_questions[:8])} questions")
            print(f"  - Band 3: {len(band3_questions[:7])} questions")

        except HttpError as error:
            print(f"✗ Error building form structure: {error}")
            sys.exit(1)

    def setup_branching(self):
        """Set up branching logic after sections are created.

        This is a second pass that reads back the form to get section IDs
        and then updates routing questions with goToSectionId.
        """
        try:
            # Read back the form to get item IDs
            form = self.service.forms().get(formId=self.form_id).execute()

            items = form.get('items', [])

            # Find section IDs
            section_ids = {}
            for i, item in enumerate(items):
                if 'pageBreakItem' in item:
                    title = item.get('title', '')
                    if 'Parte 1' in title or 'Part 1' in title:
                        section_ids['band1'] = item['itemId']
                    elif 'Parte 2' in title or 'Part 2' in title:
                        section_ids['band2'] = item['itemId']
                    elif 'Parte 3' in title or 'Part 3' in title:
                        section_ids['band3'] = item['itemId']

            # Find the gate question and routing question IDs
            gate_question_id = None
            routing_question_id = None

            for item in items:
                if 'questionItem' in item:
                    title = item.get('title', '')
                    if 'Como você descreveria' in title:
                        gate_question_id = item['itemId']
                    elif 'Selecione a mesma opção' in title:
                        routing_question_id = item['itemId']

            # Build update requests for branching
            update_requests = []

            # Gate question: all paths go to Band 1
            if gate_question_id and 'band1' in section_ids:
                # All three options route to Band 1 section
                for opt_idx in range(3):
                    update_requests.append({
                        "updateItem": {
                            "item": {
                                "itemId": gate_question_id,
                                "questionItem": {
                                    "question": {
                                        "choiceQuestion": {
                                            "options": [
                                                {"goToSectionId": section_ids['band1']}
                                            ] * 3
                                        }
                                    }
                                }
                            },
                            "location": {"index": 1},
                            "updateMask": "questionItem.question.choiceQuestion.options"
                        }
                    })

            # Routing question: Path A submits, Path B/C continue to Band 2
            if routing_question_id:
                routing_update = {
                    "updateItem": {
                        "item": {
                            "itemId": routing_question_id,
                            "questionItem": {
                                "question": {
                                    "choiceQuestion": {
                                        "options": [
                                            {"goToAction": "SUBMIT_FORM"},  # Path A
                                        ]
                                    }
                                }
                            }
                        },
                        "location": {"index": len([i for i in items if 'questionItem' in i or 'textItem' in i]) - 1},
                        "updateMask": "questionItem.question.choiceQuestion.options"
                    }
                }

                # Add Band 2 routing for Path B and C
                if 'band2' in section_ids:
                    routing_update["updateItem"]["item"]["questionItem"]["question"]["choiceQuestion"]["options"].extend([
                        {"goToSectionId": section_ids['band2']},  # Path B
                        {"goToSectionId": section_ids['band2']}   # Path C
                    ])

                update_requests.append(routing_update)

            if update_requests:
                self.service.forms().batchUpdate(
                    formId=self.form_id,
                    body={"requests": update_requests}
                ).execute()

                print("✓ Set up branching logic")
                print(f"  - Gate question routes all paths to Band 1")
                print(f"  - Routing question: Path A → Submit, Path B/C → Band 2")

        except HttpError as error:
            print(f"⚠ Warning: Could not set up branching: {error}")
            print("  You may need to configure routing manually in the form UI")

    def publish_form(self):
        """Publish the form (required after March 2026)."""
        try:
            # Method 1: Try using the responderUri field to check if already accepting responses
            form = self.service.forms().get(formId=self.form_id).execute()

            # The form needs to be "accepting responses"
            # This is controlled by the "settings.isPublished" field
            # However, the API may not expose this directly

            # Alternative: Enable "accepting responses" via settings
            self.service.forms().batchUpdate(
                formId=self.form_id,
                body={
                    "requests": [{
                        "updateSettings": {
                            "settings": {
                                "quizSettings": {
                                    "isQuiz": True
                                }
                            },
                            "updateMask": "quizSettings.isQuiz"
                        }
                    }]
                }
            ).execute()

            print("✓ Form configured")
            print("⚠  Note: You may need to manually enable 'Accepting responses'")
            print("   In the form editor, click the toggle at the top to start accepting responses")

        except HttpError as error:
            print(f"⚠ Warning: Could not fully configure form: {error}")
            print("  You may need to enable 'Accepting responses' manually")

    def print_urls(self):
        """Print the form URLs for editing and responding."""
        edit_url = f"https://docs.google.com/forms/d/{self.form_id}/edit"
        view_url = f"https://docs.google.com/forms/d/{self.form_id}/viewform"

        print("\n" + "=" * 70)
        print("✓ FORM CREATED SUCCESSFULLY")
        print("=" * 70)
        print(f"\n📝 Edit form (instructor):")
        print(f"   {edit_url}")
        print(f"\n👥 Share with students:")
        print(f"   {view_url}")
        print("\n" + "=" * 70)
        print("\n⚠️  MANUAL STEPS REQUIRED:")
        print("   1. Open the edit URL above")
        print("   2. 🔴 IMPORTANT: Click the toggle at the top to 'Start accepting responses'")
        print("      (Forms created via API default to NOT accepting responses)")
        print("   3. Click 'Responses' → 'Link to Sheets' to create response spreadsheet")
        print("   4. Go to Settings (⚙️) → Enable 'Collect email addresses'")
        print("   5. Test the form with dummy submissions for all three paths")
        print("=" * 70 + "\n")

    # === Helper methods for creating form items ===

    def _create_text_item(self, text: str, index: int) -> Dict[str, Any]:
        """Create a text description item.

        Note: textItem allows newlines, but we use description for long text.
        """
        # For text items, put content in description if it's long
        # Use a short title
        if len(text) > 100 or "\n" in text:
            return {
                "createItem": {
                    "item": {
                        "title": "",  # Empty title
                        "description": text,
                        "textItem": {}
                    },
                    "location": {"index": index}
                }
            }
        else:
            return {
                "createItem": {
                    "item": {
                        "title": text,
                        "textItem": {}
                    },
                    "location": {"index": index}
                }
            }

    def _create_page_break(self, title: str, index: int) -> Dict[str, Any]:
        """Create a page break (section) item.

        Page breaks cannot have newlines in title.
        Put multi-line content in description.
        """
        # If title has newlines, split into title (first line) and description (rest)
        description = None
        clean_title = title

        if "\n" in title:
            lines = title.split("\n")
            # First line becomes title, rest becomes description
            clean_title = lines[0]
            description = "\n".join(lines[1:]).strip()

        item = {
            "createItem": {
                "item": {
                    "title": clean_title,
                    "pageBreakItem": {}
                },
                "location": {"index": index}
            }
        }

        if description:
            item["createItem"]["item"]["description"] = description

        return item

    def _create_choice_question(self, question: str, options: List[str],
                                index: int, required: bool = True) -> Dict[str, Any]:
        """Create a multiple choice question (no grading)."""
        # Split question text if it has description (separated by \n\n)
        description = None
        title = question

        if "\n\n" in question:
            parts = question.split("\n\n", 1)
            description = parts[0]
            title = parts[1]

        # Remove any remaining newlines from title
        title = title.replace("\n", " ")

        item = {
            "createItem": {
                "item": {
                    "title": title,
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

        if description:
            item["createItem"]["item"]["description"] = description

        return item

    def _create_graded_question(self, question: Dict[str, Any], index: int) -> Dict[str, Any]:
        """Create a graded multiple choice question from question bank entry."""
        # Find correct answer
        correct_answer = next(
            opt["text"] for opt in question["options"] if opt["is_correct"]
        )

        # Handle questions with passages (reading comprehension)
        # Split on \n\n to separate passage from question
        question_text = question["question_text"]
        description = None
        title = question_text

        if "\n\n" in question_text:
            parts = question_text.split("\n\n", 1)
            description = parts[0]  # Passage goes in description
            title = parts[1]  # Actual question goes in title

        # Google Forms doesn't allow ANY newlines in title
        # Replace any remaining newlines with spaces
        title = title.replace("\n", " ")

        item = {
            "createItem": {
                "item": {
                    "title": title,
                    "questionItem": {
                        "question": {
                            "required": True,
                            "grading": {
                                "pointValue": question["point_value"],
                                "correctAnswers": {
                                    "answers": [{"value": correct_answer}]
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

        # Add description if we have a passage
        if description:
            item["createItem"]["item"]["description"] = description

        return item


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Generate ESL Placement Test Google Form from question bank'
    )
    parser.add_argument(
        '--bank',
        default=DEFAULT_BANK_PATH,
        help=f'Path to question_bank.json (default: {DEFAULT_BANK_PATH})'
    )
    parser.add_argument(
        '--credentials',
        default=DEFAULT_CREDENTIALS_PATH,
        help=f'Path to credentials.json (default: {DEFAULT_CREDENTIALS_PATH})'
    )
    parser.add_argument(
        '--token',
        default=DEFAULT_TOKEN_PATH,
        help=f'Path to token.json (default: {DEFAULT_TOKEN_PATH})'
    )
    parser.add_argument(
        '--title',
        default='Teste de Nivelamento - Inglês Instrumental / ESL Placement Test',
        help='Form title'
    )

    args = parser.parse_args()

    # Resolve paths relative to script location
    script_dir = Path(__file__).parent
    bank_path = (script_dir / args.bank).resolve()
    credentials_path = (script_dir / args.credentials).resolve()
    token_path = (script_dir / args.token).resolve()

    # Validate paths
    if not bank_path.exists():
        print(f"✗ Error: Question bank not found at {bank_path}")
        sys.exit(1)

    if not credentials_path.exists():
        print(f"✗ Error: credentials.json not found at {credentials_path}")
        print("\nPlease follow these steps:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a project and enable Google Forms API")
        print("3. Create OAuth 2.0 credentials (Desktop app)")
        print("4. Download credentials.json to placement_exam/credentials.json")
        sys.exit(1)

    print("=" * 70)
    print("ESL PLACEMENT TEST - GOOGLE FORM GENERATOR")
    print("=" * 70)
    print(f"\nQuestion bank: {bank_path}")
    print(f"Credentials:   {credentials_path}")
    print(f"Form title:    {args.title}\n")

    # Create generator
    generator = PlacementFormGenerator(
        credentials_path=str(credentials_path),
        token_path=str(token_path)
    )

    # Execute generation pipeline
    try:
        print("Step 1: Authenticating...")
        generator.authenticate()

        print("\nStep 2: Loading question bank...")
        question_bank = generator.load_question_bank(str(bank_path))

        print("\nStep 3: Creating blank form...")
        generator.create_blank_form(args.title)

        print("\nStep 4: Enabling quiz mode...")
        generator.enable_quiz_mode()

        print("\nStep 5: Building form structure...")
        generator.build_form_structure(question_bank)

        print("\nStep 6: Setting up branching logic...")
        generator.setup_branching()

        print("\nStep 7: Publishing form...")
        generator.publish_form()

        print("\n" + "=" * 70)
        generator.print_urls()

    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
