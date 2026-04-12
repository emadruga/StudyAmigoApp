#!/usr/bin/env python3
"""
validate_question_bank.py — Pre-generation question bank validator

Enforces the rules defined in PLAN_EXAM_01_FINAL.md sections 3.4 and 3.5:

  Rule 1 — No 3rd person singular subjects (he/she/it) in sentence_completion
            questions unless the question explicitly tests 3rd person morphology.
  Rule 2 — Every sentence_completion must include a time marker or structural
            anchor that makes exactly one option grammatically correct.
  Rule 3 — No structures absent from the SRS deck (e.g. "going to" in bimester 1).
  Rule 4 — No question_text duplicated across banks in the exam series.
  Rule 5 — Structural checks: exactly 4 options, exactly 1 correct per question.

  Ambiguity review (Section 3.5): sentence_completion questions without a
  recognised time marker or structural anchor are flagged for manual review.

Usage (standalone):
    python3 validate_question_bank.py ../bases/exam_01_final_bank_v2.json

Usage (as library — called from create_exam_01_final_form.py):
    from validate_question_bank import validate_bank, ValidationResult
    result = validate_bank(bank_path, prior_bank_paths=[...])
    if not result.ok_to_proceed():
        sys.exit(1)
"""

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


# ---------------------------------------------------------------------------
# Anchor catalogue (Rule 2 / Section 3.5)
# ---------------------------------------------------------------------------

# Regex patterns that, when found in a question_text, constitute an explicit
# tense anchor.  Each entry: (tense_label, compiled_regex).
TIME_MARKERS = [
    # Simple Present
    ("Simple Present",      re.compile(r'\bevery\b',        re.I)),
    ("Simple Present",      re.compile(r'\busually\b',      re.I)),
    ("Simple Present",      re.compile(r'\balways\b',       re.I)),
    ("Simple Present",      re.compile(r'\bnever\b',        re.I)),
    ("Simple Present",      re.compile(r'\boften\b',        re.I)),
    ("Simple Present",      re.compile(r'\bon weekends?\b', re.I)),
    # Simple Past
    ("Simple Past",         re.compile(r'\byesterday\b',    re.I)),
    ("Simple Past",         re.compile(r'\blast\s+\w+',     re.I)),   # last night/week/Monday…
    ("Simple Past",         re.compile(r'\bago\b',          re.I)),
    # Present Continuous
    ("Present Continuous",  re.compile(r'\bright now\b',    re.I)),
    ("Present Continuous",  re.compile(r'\bat the moment\b',re.I)),
    ("Present Continuous",  re.compile(r'\bcurrently\b',    re.I)),
    # Simple Future
    ("Simple Future",       re.compile(r'\btomorrow\b',     re.I)),
    ("Simple Future",       re.compile(r'\bnext\s+\w+',     re.I)),   # next week/month/Friday…
    ("Simple Future",       re.compile(r'\bby tomorrow\b',  re.I)),
    ("Simple Future",       re.compile(r'\bby next\b',      re.I)),
    # Present Perfect
    ("Present Perfect",     re.compile(r'\balready\b',      re.I)),
    ("Present Perfect",     re.compile(r'\byet\b',          re.I)),
    ("Present Perfect",     re.compile(r'\bever\b',         re.I)),
    ("Present Perfect",     re.compile(r'\bso far\b',       re.I)),
    ("Present Perfect",     re.compile(r'\btwice\b',        re.I)),
    ("Present Perfect",     re.compile(r'\bthree times\b',  re.I)),
    # Past Continuous
    ("Past Continuous",     re.compile(r'\bwhen\b.+\b(went|rang|arrived|started|stopped|fell|woke)\b', re.I)),
    ("Past Continuous",     re.compile(r'\bwhile\b',        re.I)),
]

# Structural anchors: an -ing form already in the stem forces a continuous
# auxiliary.  We check if the question_text (outside the blank) contains -ing.
_ING_IN_STEM = re.compile(r'\b\w+ing\b(?!\s*_)')   # -ing word not immediately before ___

# Forbidden structures by SRS absence (Rule 3).
FORBIDDEN_STRUCTURES = [
    {
        "label": "going to",
        "pattern": re.compile(r'\bgoing to\b', re.I),
        "reason": "'going to' future is absent from the 1st bimester SRS deck.",
    },
]

# 3rd person singular pronouns (Rule 1).
THIRD_PERSON_SINGULAR = re.compile(r'\b(he|she|it)\b', re.I)

# Questions that explicitly test 3rd person morphology may use he/she/it.
THIRD_PERSON_TENSE_ASPECTS = {"3rd_person", "3rd_person_singular"}


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class Issue:
    question_id: str
    rule: str
    severity: str          # "error" | "warning"
    message: str

    def __str__(self):
        icon = "✗" if self.severity == "error" else "⚠"
        return f"  {icon} [{self.rule}] {self.question_id}: {self.message}"


@dataclass
class ValidationResult:
    issues: List[Issue] = field(default_factory=list)

    @property
    def errors(self):
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self):
        return [i for i in self.issues if i.severity == "warning"]

    def ok_to_proceed(self) -> bool:
        """True if there are no errors (warnings are allowed)."""
        return len(self.errors) == 0

    def print_report(self):
        if not self.issues:
            print("✓ Question bank passed all validation checks.")
            return

        if self.errors:
            print(f"\n{'=' * 60}")
            print(f"  ERRORS ({len(self.errors)}) — must be fixed before proceeding")
            print(f"{'=' * 60}")
            for issue in self.errors:
                print(issue)

        if self.warnings:
            print(f"\n{'=' * 60}")
            print(f"  WARNINGS ({len(self.warnings)}) — review recommended")
            print(f"{'=' * 60}")
            for issue in self.warnings:
                print(issue)

        print()


# ---------------------------------------------------------------------------
# Validation logic
# ---------------------------------------------------------------------------

def _has_time_marker(text: str) -> bool:
    """Return True if question_text contains a recognised time marker."""
    for _, pattern in TIME_MARKERS:
        if pattern.search(text):
            return True
    return False


def _has_structural_anchor(text: str) -> bool:
    """Return True if question_text has an -ing stem anchor."""
    # Remove the blank placeholder before searching
    text_no_blank = re.sub(r'_+', '', text)
    return bool(_ING_IN_STEM.search(text_no_blank))


def _is_contrast_or_identification(q: dict) -> bool:
    """Tense contrast, identification and passage questions don't need anchors."""
    return q.get("type") in (
        "tense_identification",
        "tense_contrast",
        "context_selection",
        "passage_comprehension",
    )


def validate_bank(
    bank_path: str,
    prior_bank_paths: Optional[List[str]] = None,
) -> ValidationResult:
    """
    Run all validation rules against the question bank at bank_path.

    Args:
        bank_path:         Path to the JSON bank to validate.
        prior_bank_paths:  Optional list of prior bank JSON paths to check
                           for duplicate question_text (Rule 4).

    Returns:
        ValidationResult with all found issues.
    """
    result = ValidationResult()
    prior_bank_paths = prior_bank_paths or []

    # Load main bank
    with open(bank_path, "r", encoding="utf-8") as f:
        bank = json.load(f)

    questions = bank.get("questions", [])

    # Load prior banks for Rule 4
    prior_texts: set = set()
    for prior_path in prior_bank_paths:
        p = Path(prior_path)
        if not p.exists():
            continue
        with open(p, "r", encoding="utf-8") as f:
            prior = json.load(f)
        for q in prior.get("questions", []):
            t = q.get("question_text", "").strip().lower()
            if t:
                prior_texts.add(t)

    # Track question_texts within this bank for self-duplicate check
    seen_texts: dict = {}

    for q in questions:
        qid = q.get("id", "UNKNOWN")
        qtype = q.get("type", "")
        qtext = q.get("question_text", "")
        options = q.get("options", [])
        tense_aspect = q.get("tense_aspect", "")

        # ------------------------------------------------------------------
        # Rule 5 — Structural checks (exactly 4 options, exactly 1 correct)
        # ------------------------------------------------------------------
        if len(options) != 4:
            result.issues.append(Issue(
                qid, "Rule 5", "error",
                f"Expected 4 options, found {len(options)}.",
            ))

        correct_count = sum(1 for o in options if o.get("is_correct"))
        if correct_count != 1:
            result.issues.append(Issue(
                qid, "Rule 5", "error",
                f"Expected exactly 1 correct option, found {correct_count}.",
            ))

        # ------------------------------------------------------------------
        # Rule 1 — No 3rd person singular subjects (he/she/it)
        # ------------------------------------------------------------------
        if qtype == "sentence_completion" and tense_aspect not in THIRD_PERSON_TENSE_ASPECTS:
            if THIRD_PERSON_SINGULAR.search(qtext):
                result.issues.append(Issue(
                    qid, "Rule 1", "warning",
                    f"Subject 'he/she/it' found in question_text. "
                    f"Use I/you/we/they unless testing 3rd-person morphology. "
                    f"Text: \"{qtext[:80]}\"",
                ))

        # ------------------------------------------------------------------
        # Rule 3 — No forbidden SRS-absent structures
        # ------------------------------------------------------------------
        for forbidden in FORBIDDEN_STRUCTURES:
            all_text = " ".join([
                qtext,
                " ".join(o.get("text", "") for o in options),
                q.get("rationale", ""),
            ])
            if forbidden["pattern"].search(all_text):
                result.issues.append(Issue(
                    qid, "Rule 3", "error",
                    f"Forbidden structure detected: {forbidden['label']}. "
                    f"{forbidden['reason']}",
                ))

        # ------------------------------------------------------------------
        # Rule 4 — No duplicate question_text across banks
        # ------------------------------------------------------------------
        norm_text = qtext.strip().lower()
        if norm_text in prior_texts:
            result.issues.append(Issue(
                qid, "Rule 4", "error",
                f"question_text duplicates a sentence from a prior bank: "
                f"\"{qtext[:80]}\"",
            ))
        if norm_text in seen_texts:
            result.issues.append(Issue(
                qid, "Rule 4", "error",
                f"question_text duplicates {seen_texts[norm_text]} within this bank: "
                f"\"{qtext[:80]}\"",
            ))
        else:
            seen_texts[norm_text] = qid

        # ------------------------------------------------------------------
        # Rule 2 / Section 3.5 — Ambiguity review (sentence_completion only)
        # ------------------------------------------------------------------
        if qtype == "sentence_completion":
            has_marker = _has_time_marker(qtext)
            has_anchor = _has_structural_anchor(qtext)

            if not has_marker and not has_anchor:
                result.issues.append(Issue(
                    qid, "Rule 2 / §3.5", "warning",
                    f"No recognised time marker or structural anchor found. "
                    f"Verify that exactly one option is grammatically correct. "
                    f"Text: \"{qtext[:100]}\"",
                ))

    return result


# ---------------------------------------------------------------------------
# Interactive prompt (used by the form generator)
# ---------------------------------------------------------------------------

def run_validation_gate(
    bank_path: str,
    prior_bank_paths: Optional[List[str]] = None,
) -> bool:
    """
    Validate the bank and prompt the user if issues are found.

    Returns True if form generation should proceed, False if it should abort.
    Called by create_exam_01_final_form.py before any API call is made.
    """
    print("\nValidating question bank against rules in §3.4 and §3.5...")
    result = validate_bank(bank_path, prior_bank_paths)
    result.print_report()

    if not result.issues:
        return True

    # Errors: must ask; warnings: still ask but message is softer
    n_errors   = len(result.errors)
    n_warnings = len(result.warnings)

    if n_errors > 0:
        prompt = (
            f"  {n_errors} error(s) and {n_warnings} warning(s) found.\n"
            f"  Errors MUST be fixed for a valid exam.\n"
            f"  Proceed with form generation anyway? [y/N] "
        )
    else:
        prompt = (
            f"  {n_warnings} warning(s) found (no hard errors).\n"
            f"  Warnings indicate potential ambiguity — review recommended.\n"
            f"  Proceed with form generation? [Y/n] "
        )

    try:
        answer = input(prompt).strip().lower()
    except (EOFError, KeyboardInterrupt):
        print("\nAborted.")
        return False

    if n_errors > 0:
        return answer == "y"
    else:
        return answer != "n"


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print(f"Usage: python3 {Path(__file__).name} <bank.json> [prior_bank1.json ...]")
        sys.exit(1)

    bank_path = sys.argv[1]
    prior_paths = sys.argv[2:]

    if not Path(bank_path).exists():
        print(f"✗ Bank file not found: {bank_path}")
        sys.exit(1)

    print(f"Validating: {bank_path}")
    if prior_paths:
        print(f"Prior banks: {', '.join(prior_paths)}")

    result = validate_bank(bank_path, prior_paths)
    result.print_report()

    if result.errors:
        sys.exit(1)
    elif result.warnings:
        sys.exit(2)   # Exit 2 = warnings only
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
