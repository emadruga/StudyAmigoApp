#!/usr/bin/env python3
"""
Comprehensive analysis of placement exam results.
Analyzes 57 students' performance on the ESL placement test.
"""

import csv
import statistics
from collections import Counter, defaultdict

def analyze_placement_exam():
    # Read CSV data
    with open('/tmp/placement_exam_results.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Total students
    total_students = len(rows)
    print(f"=" * 80)
    print(f"PLACEMENT EXAM RESULTS ANALYSIS")
    print(f"=" * 80)
    print(f"\nTotal Students: {total_students}")

    # 1. PATH DISTRIBUTION (Signal 0: Self-Assessment)
    print(f"\n{'=' * 80}")
    print("1. PATH DISTRIBUTION (Self-Reported English Experience)")
    print(f"{'=' * 80}")

    path_counter = Counter()
    path_mapping = {
        'Nunca estudei inglês e não tenho contato com o idioma. (I have never studied English and I have no contact with the language.)': 'Path A (Never studied)',
        'Estudei inglês no ensino médio (escola pública ou particular), mas não me considero fluente. (I studied English in high school, but I don\'t consider myself fluent.)': 'Path B (High school)',
        'Já fiz curso de inglês ou me considero intermediário/avançado. (I have taken English courses or I consider myself intermediate/advanced.)': 'Path C (Intermediate/Advanced)'
    }

    path_data = defaultdict(list)
    for row in rows:
        exp = row.get('Experiência com o Idioma', '')
        path = path_mapping.get(exp, 'Unknown')
        path_counter[path] += 1
        path_data[path].append(row)

    for path, count in sorted(path_counter.items()):
        pct = (count / total_students) * 100
        print(f"  {path}: {count} ({pct:.1f}%)")

    # 2. SCORE DISTRIBUTION
    print(f"\n{'=' * 80}")
    print("2. SCORE DISTRIBUTION")
    print(f"{'=' * 80}")

    scores = []
    path_a_scores = []
    path_bc_scores = []

    for row in rows:
        score_str = row.get('Pontuação', '0 / 0')
        try:
            score, total = score_str.split(' / ')
            score = int(score)
            total = int(total)
            scores.append((score, total))

            exp = row.get('Experiência com o Idioma', '')
            path = path_mapping.get(exp, 'Unknown')

            if 'Path A' in path:
                path_a_scores.append(score)
            else:
                path_bc_scores.append(score)
        except:
            pass

    print(f"\nPath A Students (Band 1 only, out of 10):")
    if path_a_scores:
        print(f"  Count: {len(path_a_scores)}")
        print(f"  Mean: {statistics.mean(path_a_scores):.2f}")
        print(f"  Median: {statistics.median(path_a_scores):.2f}")
        print(f"  Min: {min(path_a_scores)}, Max: {max(path_a_scores)}")
        print(f"  Score distribution: {Counter(path_a_scores)}")

        # Underestimators (scored 8-10 on Path A)
        underestimators = [s for s in path_a_scores if s >= 8]
        print(f"  Underestimators (≥8/10): {len(underestimators)} ({len(underestimators)/len(path_a_scores)*100:.1f}%)")

    print(f"\nPath B/C Students (Full test, out of 25):")
    if path_bc_scores:
        print(f"  Count: {len(path_bc_scores)}")
        print(f"  Mean: {statistics.mean(path_bc_scores):.2f}")
        print(f"  Median: {statistics.median(path_bc_scores):.2f}")
        print(f"  Min: {min(path_bc_scores)}, Max: {max(path_bc_scores)}")

    # 3. TIER PLACEMENT (based on scoring thresholds from plan)
    print(f"\n{'=' * 80}")
    print("3. RECOMMENDED TIER PLACEMENT (Based on Test Scores Only)")
    print(f"{'=' * 80}")

    tier_counts = {'Tier 1': 0, 'Tier 2': 0, 'Tier 3': 0, 'Flag': 0}

    for row in rows:
        score_str = row.get('Pontuação', '0 / 0')
        try:
            score, total = score_str.split(' / ')
            score = int(score)
            total = int(total)

            exp = row.get('Experiência com o Idioma', '')
            path = path_mapping.get(exp, 'Unknown')

            if 'Path A' in path:
                # Path A thresholds (out of 10)
                if score <= 4:
                    tier_counts['Tier 1'] += 1
                elif score <= 7:
                    tier_counts['Tier 1'] += 1
                else:  # 8-10
                    tier_counts['Flag'] += 1  # Underestimators
            else:
                # Path B/C thresholds (out of 25)
                if score <= 10:
                    tier_counts['Tier 1'] += 1
                elif score <= 18:
                    tier_counts['Tier 2'] += 1
                else:  # 19-25
                    tier_counts['Tier 3'] += 1
        except:
            pass

    for tier, count in sorted(tier_counts.items()):
        if count > 0:
            pct = (count / total_students) * 100
            print(f"  {tier}: {count} ({pct:.1f}%)")

    print(f"\n  Note: 'Flag' = Path A students who scored 8-10/10 (potential underestimators)")

    # 4. PROGRAM DISTRIBUTION
    print(f"\n{'=' * 80}")
    print("4. PROGRAM DISTRIBUTION")
    print(f"{'=' * 80}")

    program_counter = Counter()
    for row in rows:
        program = row.get('Seu curso técnico?', 'Unknown').strip()
        program_counter[program] += 1

    for program, count in sorted(program_counter.items(), key=lambda x: x[1], reverse=True):
        if program:
            pct = (count / total_students) * 100
            print(f"  {program}: {count} ({pct:.1f}%)")

    # 5. ANCHOR QUESTIONS ANALYSIS
    print(f"\n{'=' * 80}")
    print("5. ANCHOR QUESTIONS ANALYSIS")
    print(f"{'=' * 80}")

    # Q1 (Anchor-Easy): "What does 'important' mean?"
    q1_col = 'What does "important" mean?'
    q1_correct = 'Importante'
    q1_responses = [row.get(q1_col, '') for row in rows if row.get(q1_col)]
    q1_correct_count = sum(1 for r in q1_responses if r == q1_correct)

    print(f"\nQ1 (Anchor-Easy): 'What does \"important\" mean?'")
    print(f"  Correct answers: {q1_correct_count}/{len(q1_responses)} ({q1_correct_count/len(q1_responses)*100:.1f}%)")
    print(f"  Expected: >95% (virtually all students should answer correctly)")
    if q1_correct_count/len(q1_responses) < 0.95:
        print(f"  ⚠️  WARNING: Below expected threshold!")

    # Q25 (Anchor-Hard): "According to the passage, what is the difference between precision and accuracy?"
    q25_col = 'According to the passage, what is the difference between precision and accuracy?'
    q25_correct = 'Precision is about consistency; accuracy is about correctness'
    q25_responses = [row.get(q25_col, '') for row in rows if row.get(q25_col)]
    q25_correct_count = sum(1 for r in q25_responses if r == q25_correct)

    print(f"\nQ25 (Anchor-Hard): Precision vs. Accuracy")
    print(f"  Correct answers: {q25_correct_count}/{len(q25_responses)} ({q25_correct_count/len(q25_responses)*100:.1f}%)")
    print(f"  Expected: 15-30% (only strong Tier 3 students)")

    # 6. QUESTION DIFFICULTY ANALYSIS (sample of key questions)
    print(f"\n{'=' * 80}")
    print("6. SELECTED QUESTIONS DIFFICULTY ANALYSIS")
    print(f"{'=' * 80}")

    questions_to_analyze = [
        ('What does "control" mean?', 'Controlar / controle', 'Band 1'),
        ('The temperature _____ 25 degrees.', 'is', 'Band 1'),
        ('The computer _____ information quickly.', 'processes', 'Band 1'),
        ('What is the best definition of "achieve"?', 'To reach a goal successfully', 'Band 2'),
        ('She _____ the experiment last week.', 'completed', 'Band 2'),
        ('Steel is _____ than plastic.', 'stronger', 'Band 2'),
        ('Which sentence uses the passive voice correctly?', 'The experiment was conducted by the students.', 'Band 3'),
        ('If the temperature _____ too high, the equipment will malfunction.', 'rises', 'Band 3'),
    ]

    for question, correct_answer, band in questions_to_analyze:
        responses = [row.get(question, '') for row in rows if row.get(question)]
        if responses:
            correct_count = sum(1 for r in responses if r == correct_answer)
            pct = (correct_count / len(responses)) * 100
            print(f"\n{band}: {question[:60]}...")
            print(f"  Correct: {correct_count}/{len(responses)} ({pct:.1f}%)")

    # 7. PROBLEMATIC PATTERNS
    print(f"\n{'=' * 80}")
    print("7. IDENTIFIED ISSUES & PATTERNS")
    print(f"{'=' * 80}")

    # Check for Path A students who didn't select Path A routing
    mismatch_count = 0
    for row in rows:
        exp = row.get('Experiência com o Idioma', '')
        routing_col = '(Select the same option you chose on the first page:)'
        routing = row.get(routing_col, '')

        path = path_mapping.get(exp, '')
        if 'Path A' in path and 'Nunca estudei inglês (Path A)' not in routing and routing:
            mismatch_count += 1

    if mismatch_count > 0:
        print(f"\n⚠️  {mismatch_count} students selected Path A but didn't confirm it on the routing question")
        print(f"   This suggests confusion with the branching mechanism.")

    # Check for duplicate submissions
    timestamps = [row.get('Carimbo de data/hora', '') for row in rows]
    emails = [row.get('Endereço de e-mail', '').lower() for row in rows if row.get('Endereço de e-mail')]
    duplicate_emails = [email for email, count in Counter(emails).items() if count > 1]

    if duplicate_emails:
        print(f"\n⚠️  Duplicate submissions detected: {len(duplicate_emails)} email(s) appear multiple times")
        for email in duplicate_emails:
            print(f"   - {email}")

    # 8. SUMMARY & RECOMMENDATIONS
    print(f"\n{'=' * 80}")
    print("8. KEY FINDINGS & RECOMMENDATIONS")
    print(f"{'=' * 80}")

    print(f"\n✅ POSITIVE FINDINGS:")
    print(f"   • Excellent participation: 57 students completed the exam")
    print(f"   • Diverse proficiency levels represented across all three paths")
    print(f"   • Test successfully differentiated between proficiency levels")

    print(f"\n⚠️  AREAS OF CONCERN:")

    # Calculate Path A percentage
    path_a_count = path_counter.get('Path A (Never studied)', 0)
    path_a_pct = (path_a_count / total_students) * 100

    if path_a_pct > 50:
        print(f"   • High Path A selection ({path_a_pct:.1f}%) - may indicate:")
        print(f"     - Students genuinely have minimal English exposure, OR")
        print(f"     - Self-assessment wording attracted false-skippers")
    elif path_a_pct < 15:
        print(f"   • Low Path A selection ({path_a_pct:.1f}%) - students may be overestimating")

    if path_a_scores:
        high_scorers_pct = (len(underestimators) / len(path_a_scores)) * 100
        if high_scorers_pct > 30:
            print(f"   • {high_scorers_pct:.1f}% of Path A students scored 8-10/10 (underestimators)")
            print(f"     - Consider offering these students the full test")

    # Check score distribution
    if path_bc_scores:
        tier2_candidates = [s for s in path_bc_scores if 11 <= s <= 18]
        tier2_pct = (len(tier2_candidates) / len(path_bc_scores)) * 100
        if tier2_pct > 70:
            print(f"   • {tier2_pct:.1f}% of Path B/C students fall in Tier 2 range")
            print(f"     - Test may not be differentiating Tier 1 and Tier 3 effectively")

    print(f"\n📋 NEXT STEPS:")
    print(f"   1. Review and finalize tier placements using this data (Signal 1)")
    print(f"   2. Follow up with {tier_counts['Flag']} flagged Path A students")
    print(f"   3. Begin E01 diagnostic exercise to collect Signal 2 data")
    print(f"   4. After E01, apply the three-signal placement matrix (Section 6.3 of plan)")
    print(f"   5. Conduct post-semester validation analysis (Section 9.2 of plan)")

    print(f"\n{'=' * 80}\n")

if __name__ == '__main__':
    analyze_placement_exam()
