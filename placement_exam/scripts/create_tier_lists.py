#!/usr/bin/env python3
"""
Create sorted student lists by tier and course for placement exam results.
"""

import csv
from collections import defaultdict

def create_tier_lists():
    # Read CSV data
    with open('/tmp/placement_exam_results.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    path_mapping = {
        'Nunca estudei inglês e não tenho contato com o idioma. (I have never studied English and I have no contact with the language.)': 'Path A',
        'Estudei inglês no ensino médio (escola pública ou particular), mas não me considero fluente. (I studied English in high school, but I don\'t consider myself fluent.)': 'Path B',
        'Já fiz curso de inglês ou me considero intermediário/avançado. (I have taken English courses or I consider myself intermediate/advanced.)': 'Path C'
    }

    # Tier assignment based on adjusted thresholds
    tier_students = {
        'Tier 1': [],
        'Tier 2': [],
        'Tier 3': [],
        'Flag': []  # Underestimators
    }

    # Track seen emails to handle duplicates
    seen_emails = set()

    for row in rows:
        email = row.get('Endereço de e-mail', '').lower().strip()

        # Skip duplicates (keep first occurrence)
        if email in seen_emails:
            continue

        if email:
            seen_emails.add(email)

        name = row.get('Nome Completo', '').strip()
        course = row.get('Seu curso técnico?', '').strip()
        score_str = row.get('Pontuação', '0 / 0')
        exp = row.get('Experiência com o Idioma', '')
        path = path_mapping.get(exp, 'Unknown')

        try:
            score, total = score_str.split(' / ')
            score = int(score)
            total = int(total)

            student_data = {
                'name': name,
                'email': email,
                'course': course,
                'score': score,
                'total': total,
                'path': path
            }

            # Apply adjusted thresholds
            if 'Path A' in path:
                # Path A thresholds (out of 10)
                if score >= 8:
                    tier_students['Flag'].append(student_data)
                else:
                    tier_students['Tier 1'].append(student_data)
            else:
                # Path B/C thresholds (out of 25) - ADJUSTED
                if score <= 10:
                    tier_students['Tier 1'].append(student_data)
                elif score <= 15:
                    tier_students['Tier 2'].append(student_data)
                else:  # 16-25
                    tier_students['Tier 3'].append(student_data)
        except:
            pass

    # Sort each tier: by course first, then alphabetically by name
    for tier in tier_students:
        tier_students[tier].sort(key=lambda x: (x['course'], x['name']))

    # Generate formatted output
    output = []
    output.append("\n---\n")
    output.append("## APPENDIX: Student Tier Assignments (Sorted by Course & Name)\n")
    output.append("**Note**: Based on placement test scores only (Signal 1). Final placements will incorporate E01 data (Signal 2).\n")
    output.append("\n**Adjusted Thresholds**:")
    output.append("- Path A (out of 10): 0-7 = Tier 1, 8-10 = Flag (underestimator)")
    output.append("- Path B/C (out of 25): 0-10 = Tier 1, 11-15 = Tier 2, 16-25 = Tier 3\n")

    # Print each tier
    for tier_name in ['Tier 1', 'Tier 2', 'Tier 3', 'Flag']:
        students = tier_students[tier_name]

        if tier_name == 'Flag':
            output.append(f"\n### {tier_name}: Potential Underestimators (Path A, 8-10/10)")
            output.append(f"**Count**: {len(students)}")
            output.append("**Action Required**: Contact these students and offer full test\n")
        else:
            output.append(f"\n### {tier_name}: {'Foundation' if tier_name == 'Tier 1' else 'Developing' if tier_name == 'Tier 2' else 'Expanding'}")
            output.append(f"**Count**: {len(students)}\n")

        if not students:
            output.append("*No students in this tier*\n")
            continue

        # Group by course
        by_course = defaultdict(list)
        for student in students:
            by_course[student['course']].append(student)

        for course in sorted(by_course.keys()):
            course_students = by_course[course]
            output.append(f"\n#### {course} ({len(course_students)} student{'s' if len(course_students) != 1 else ''})\n")

            for student in course_students:
                score_display = f"{student['score']}/{student['total']}"
                path_display = student['path'].replace('Path ', '')
                output.append(f"- **{student['name']}** - {score_display} ({path_display}) - {student['email']}")

    return '\n'.join(output)

if __name__ == '__main__':
    result = create_tier_lists()
    print(result)

    # Also save to file
    with open('/tmp/tier_lists.txt', 'w', encoding='utf-8') as f:
        f.write(result)

    print("\n\n[Output saved to /tmp/tier_lists.txt]")
