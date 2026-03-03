#!/usr/bin/env python3
"""
Generate student roster CSV for academic semester tracking.
Includes: Course, ID, Name, Email, Path, Suggested Tier
"""

import csv

def generate_student_roster():
    # Read CSV data
    with open('/tmp/placement_exam_results.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    path_mapping = {
        'Nunca estudei inglês e não tenho contato com o idioma. (I have never studied English and I have no contact with the language.)': 'A',
        'Estudei inglês no ensino médio (escola pública ou particular), mas não me considero fluente. (I studied English in high school, but I don\'t consider myself fluent.)': 'B',
        'Já fiz curso de inglês ou me considero intermediário/avançado. (I have taken English courses or I consider myself intermediate/advanced.)': 'C'
    }

    # Course code mapping
    course_codes = {
        'Biotecnologia': ('Biotecnologia', 3000),
        'Metrologia': ('Metrologia', 4000),
        'Segurança Cibernética': ('Segurança Cibernética', 5000)
    }

    # Collect all students
    students = []
    seen_emails = set()

    for row in rows:
        email = row.get('Endereço de e-mail', '').lower().strip()

        # Skip duplicates (keep first occurrence only)
        if email in seen_emails or not email:
            continue

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

            # Determine suggested tier based on adjusted thresholds
            if 'Path A' in path_mapping.get(exp, ''):
                if score >= 8:
                    tier = 'Flag (Tier 1 provisional)'
                else:
                    tier = 'Tier 1'
            else:
                # Path B/C thresholds (adjusted)
                if score <= 10:
                    tier = 'Tier 1'
                elif score <= 15:
                    tier = 'Tier 2'
                else:  # 16-25
                    tier = 'Tier 3'

            students.append({
                'name': name,
                'email': email,
                'course': course,
                'path': path,
                'tier': tier,
                'score': score
            })
        except:
            # Handle malformed scores
            students.append({
                'name': name,
                'email': email,
                'course': course,
                'path': path,
                'tier': 'Unknown',
                'score': 0
            })

    # Sort alphabetically by name
    students.sort(key=lambda x: x['name'])

    # Assign IDs by course (counter per course)
    course_counters = {
        'Biotecnologia': 1,
        'Metrologia': 1,
        'Segurança Cibernética': 1
    }

    output_rows = []
    for student in students:
        course = student['course']

        if course in course_codes:
            course_name, base_code = course_codes[course]
            student_id = base_code + course_counters[course]
            course_counters[course] += 5
        else:
            # Handle unknown course
            student_id = 'Unknown'
            course_name = course

        output_rows.append({
            'Course': course_name,
            'ID': student_id,
            'Name': student['name'],
            'Email': student['email'],
            'Path': student['path'],
            'Suggested Tier': student['tier']
        })

    # Write to CSV
    output_file = '/Users/emadruga/proj/StudyAmigoApp/placement_exam/docs/STUDENT_ROSTER_SPRING_2026.csv'

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['Course', 'ID', 'Name', 'Email', 'Path', 'Suggested Tier']
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(output_rows)

    print(f"✅ Student roster created: {output_file}")
    print(f"📊 Total students: {len(output_rows)}")
    print(f"\nBreakdown by course:")

    # Count by course
    from collections import Counter
    course_counts = Counter([row['Course'] for row in output_rows])
    for course, count in sorted(course_counts.items()):
        print(f"   {course}: {count} students")

    # Show ID ranges
    print(f"\nID Ranges:")
    for course in ['Biotecnologia', 'Metrologia', 'Segurança Cibernética']:
        course_students = [r for r in output_rows if r['Course'] == course and r['ID'] != 'Unknown']
        if course_students:
            ids = [int(s['ID']) for s in course_students]
            print(f"   {course}: {min(ids)} - {max(ids)}")

    # Preview first 10 rows
    print(f"\n📋 Preview (first 10 students):\n")
    for i, row in enumerate(output_rows[:10], 1):
        print(f"{i}. {row['Name']} ({row['Course']}) - ID: {row['ID']} - Tier: {row['Suggested Tier']}")

    return output_file

if __name__ == '__main__':
    generate_student_roster()
