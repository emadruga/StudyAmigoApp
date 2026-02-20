#!/usr/bin/env python3
"""
Question Bank Validator

Validates the question_bank.json file for:
- Schema correctness
- Exactly one correct answer per question
- No duplicate IDs
- Proper band distribution
- Required fields present
- Valid status values

Usage:
    python validate_question_bank.py [--bank BANK_PATH]
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Set

DEFAULT_BANK_PATH = '../bases/question_bank.json'

# Expected band distribution for a complete test
EXPECTED_DISTRIBUTION = {
    1: 10,  # Band 1: Foundation
    2: 8,   # Band 2: Developing
    3: 7    # Band 3: Expanding
}

# Valid values
VALID_TYPES = [
    'vocabulary_matching',
    'sentence_completion',
    'reading_comprehension',
    'grammar_recognition'
]

VALID_STATUS = ['active', 'retired', 'draft']
VALID_ANCHOR = ['easy', 'hard', None]


class QuestionBankValidator:
    """Validator for ESL placement test question banks."""

    def __init__(self, bank_path: str):
        self.bank_path = bank_path
        self.errors = []
        self.warnings = []
        self.bank = None

    def validate(self) -> bool:
        """Run all validation checks.

        Returns:
            True if validation passed, False otherwise
        """
        print("=" * 70)
        print("QUESTION BANK VALIDATOR")
        print("=" * 70)
        print(f"\nValidating: {self.bank_path}\n")

        # Load the file
        if not self._load_bank():
            return False

        # Run checks
        self._check_version()
        self._check_required_fields()
        self._check_question_ids()
        self._check_band_distribution()
        self._check_options()
        self._check_anchor_questions()
        self._check_metadata()

        # Report results
        self._print_results()

        return len(self.errors) == 0

    def _load_bank(self) -> bool:
        """Load and parse the JSON file."""
        try:
            with open(self.bank_path, 'r', encoding='utf-8') as f:
                self.bank = json.load(f)

            if 'questions' not in self.bank:
                self.errors.append("Root level missing 'questions' field")
                return False

            print(f"✓ Loaded {len(self.bank['questions'])} questions")
            return True

        except FileNotFoundError:
            self.errors.append(f"File not found: {self.bank_path}")
            return False
        except json.JSONDecodeError as e:
            self.errors.append(f"JSON parse error: {e}")
            return False
        except Exception as e:
            self.errors.append(f"Unexpected error loading file: {e}")
            return False

    def _check_version(self):
        """Check version field exists."""
        if 'version' not in self.bank:
            self.warnings.append("No 'version' field in question bank")
        else:
            print(f"✓ Version: {self.bank['version']}")

    def _check_required_fields(self):
        """Check each question has all required fields."""
        required = [
            'id', 'band', 'type', 'question_text', 'options',
            'point_value', 'cognate', 'rationale', 'distractor_rationale',
            'status'
        ]

        for i, q in enumerate(self.bank['questions'], 1):
            for field in required:
                if field not in q:
                    self.errors.append(
                        f"Question {i} ({q.get('id', 'NO_ID')}): missing required field '{field}'"
                    )

            # Check type is valid
            if q.get('type') not in VALID_TYPES:
                self.errors.append(
                    f"Question {i} ({q['id']}): invalid type '{q.get('type')}'. "
                    f"Must be one of: {', '.join(VALID_TYPES)}"
                )

            # Check status is valid
            if q.get('status') not in VALID_STATUS:
                self.errors.append(
                    f"Question {i} ({q['id']}): invalid status '{q.get('status')}'. "
                    f"Must be one of: {', '.join(VALID_STATUS)}"
                )

            # Check band is valid
            if q.get('band') not in [1, 2, 3]:
                self.errors.append(
                    f"Question {i} ({q['id']}): invalid band {q.get('band')}. "
                    f"Must be 1, 2, or 3"
                )

            # Check anchor is valid
            if q.get('anchor') not in VALID_ANCHOR:
                self.errors.append(
                    f"Question {i} ({q['id']}): invalid anchor '{q.get('anchor')}'. "
                    f"Must be 'easy', 'hard', or null"
                )

        print(f"✓ Required fields check complete")

    def _check_question_ids(self):
        """Check for duplicate IDs and proper ID format."""
        ids: Set[str] = set()
        duplicates = []

        for q in self.bank['questions']:
            qid = q.get('id')

            if not qid:
                continue  # Already caught by required fields check

            if qid in ids:
                duplicates.append(qid)
            ids.add(qid)

            # Check ID format (should be B{band}_{TYPE}_{number})
            if not qid.startswith('B'):
                self.warnings.append(
                    f"Question {qid}: ID doesn't follow convention 'B{{band}}_{{TYPE}}_{{number}}'"
                )

        if duplicates:
            self.errors.append(f"Duplicate question IDs found: {', '.join(duplicates)}")
        else:
            print(f"✓ No duplicate IDs ({len(ids)} unique questions)")

    def _check_band_distribution(self):
        """Check active questions meet expected band distribution."""
        active_by_band = {1: [], 2: [], 3: []}

        for q in self.bank['questions']:
            if q.get('status') == 'active':
                band = q.get('band')
                if band in active_by_band:
                    active_by_band[band].append(q['id'])

        print(f"\n📊 Band distribution (active questions only):")
        all_match = True

        for band, expected_count in EXPECTED_DISTRIBUTION.items():
            actual_count = len(active_by_band[band])
            status = "✓" if actual_count >= expected_count else "✗"

            print(f"   {status} Band {band}: {actual_count} questions (need {expected_count})")

            if actual_count < expected_count:
                self.errors.append(
                    f"Band {band}: only {actual_count} active questions, need {expected_count}"
                )
                all_match = False
            elif actual_count > expected_count:
                self.warnings.append(
                    f"Band {band}: {actual_count} active questions, only {expected_count} needed for test. "
                    f"Extra questions available for rotation."
                )

        if all_match:
            print(f"✓ Band distribution correct for test generation")

    def _check_options(self):
        """Check each question has exactly 4 options with exactly 1 correct."""
        for q in self.bank['questions']:
            qid = q.get('id', 'NO_ID')
            options = q.get('options', [])

            # Check count
            if len(options) != 4:
                self.errors.append(
                    f"Question {qid}: has {len(options)} options, must have exactly 4"
                )
                continue

            # Check each option has required fields
            correct_count = 0
            for i, opt in enumerate(options):
                if 'text' not in opt:
                    self.errors.append(f"Question {qid}, option {i+1}: missing 'text' field")
                if 'is_correct' not in opt:
                    self.errors.append(f"Question {qid}, option {i+1}: missing 'is_correct' field")
                elif opt['is_correct'] is True:
                    correct_count += 1

            # Check exactly one correct answer
            if correct_count == 0:
                self.errors.append(f"Question {qid}: no correct answer marked")
            elif correct_count > 1:
                self.errors.append(f"Question {qid}: {correct_count} correct answers (must be exactly 1)")

        print(f"✓ Options validation complete")

    def _check_anchor_questions(self):
        """Check that anchor questions are properly designated."""
        anchors = {'easy': [], 'hard': []}

        for q in self.bank['questions']:
            if q.get('status') == 'active' and q.get('anchor'):
                anchor_type = q['anchor']
                if anchor_type in anchors:
                    anchors[anchor_type].append(q['id'])

        # Should have exactly one anchor-easy and one anchor-hard among active questions
        if len(anchors['easy']) == 0:
            self.warnings.append("No anchor-easy question found (should be Q1)")
        elif len(anchors['easy']) > 1:
            self.warnings.append(
                f"Multiple anchor-easy questions: {', '.join(anchors['easy'])} (should be only Q1)"
            )
        else:
            print(f"✓ Anchor-easy: {anchors['easy'][0]}")

        if len(anchors['hard']) == 0:
            self.warnings.append("No anchor-hard question found (should be Q25)")
        elif len(anchors['hard']) > 1:
            self.warnings.append(
                f"Multiple anchor-hard questions: {', '.join(anchors['hard'])} (should be only Q25)"
            )
        else:
            print(f"✓ Anchor-hard: {anchors['hard'][0]}")

    def _check_metadata(self):
        """Check metadata fields for completeness."""
        incomplete = []

        for q in self.bank['questions']:
            if q.get('status') != 'active':
                continue  # Only check active questions

            qid = q['id']

            # Check rationale is non-empty
            if not q.get('rationale') or len(q['rationale'].strip()) < 10:
                incomplete.append(f"{qid}: rationale too short or missing")

            # Check distractor_rationale has entries for all incorrect options
            # Find which options are incorrect
            options = q.get('options', [])
            option_letters = ['a', 'b', 'c', 'd']
            incorrect_letters = []

            for i, opt in enumerate(options):
                if not opt.get('is_correct', False):
                    incorrect_letters.append(option_letters[i])

            dist_rat = q.get('distractor_rationale', {})
            for letter in incorrect_letters:
                if letter not in dist_rat or not dist_rat[letter]:
                    incomplete.append(f"{qid}: missing distractor rationale for incorrect option '{letter}'")

        if incomplete:
            self.warnings.append(
                f"Metadata incomplete for {len(incomplete)} questions:\n   " +
                "\n   ".join(incomplete[:5]) +
                (f"\n   ... and {len(incomplete) - 5} more" if len(incomplete) > 5 else "")
            )
        else:
            print(f"✓ Metadata complete for all active questions")

    def _print_results(self):
        """Print validation results."""
        print("\n" + "=" * 70)
        print("VALIDATION RESULTS")
        print("=" * 70)

        if self.errors:
            print(f"\n❌ {len(self.errors)} ERROR(S) FOUND:\n")
            for i, error in enumerate(self.errors, 1):
                print(f"{i}. {error}")

        if self.warnings:
            print(f"\n⚠️  {len(self.warnings)} WARNING(S):\n")
            for i, warning in enumerate(self.warnings, 1):
                print(f"{i}. {warning}")

        if not self.errors and not self.warnings:
            print("\n✅ All checks passed! Question bank is valid.\n")
        elif not self.errors:
            print("\n✅ No errors found. Warnings should be reviewed but don't block usage.\n")
        else:
            print(f"\n❌ Validation failed. Fix errors before generating form.\n")

        print("=" * 70 + "\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Validate question bank JSON for ESL placement test'
    )
    parser.add_argument(
        '--bank',
        default=DEFAULT_BANK_PATH,
        help=f'Path to question_bank.json (default: {DEFAULT_BANK_PATH})'
    )

    args = parser.parse_args()

    # Resolve path relative to script location
    script_dir = Path(__file__).parent
    bank_path = (script_dir / args.bank).resolve()

    # Run validation
    validator = QuestionBankValidator(str(bank_path))
    is_valid = validator.validate()

    sys.exit(0 if is_valid else 1)


if __name__ == '__main__':
    main()
