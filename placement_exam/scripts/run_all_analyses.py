#!/usr/bin/env python3
"""
Master script to run all placement exam analyses.

This script executes all analysis scripts in sequence and generates
a comprehensive report of the placement exam results.

Usage:
    python3 run_all_analyses.py

Output:
    - Console output with progress indicators
    - All individual script outputs
    - Summary report at the end
"""

import subprocess
import sys
import os
from datetime import datetime

def run_script(script_name, description):
    """Run a Python script and capture its output."""
    print(f"\n{'=' * 80}")
    print(f"Running: {script_name}")
    print(f"Description: {description}")
    print(f"{'=' * 80}\n")

    try:
        result = subprocess.run(
            ['python3', script_name],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
        if result.stderr:
            print(f"Warnings/Errors:\n{result.stderr}", file=sys.stderr)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running {script_name}:")
        print(e.stderr)
        return False, None
    except FileNotFoundError:
        print(f"❌ Script not found: {script_name}")
        return False, None

def check_prerequisites():
    """Check if required files exist."""
    required_files = [
        '../bases/raw_google_sheets_export.csv',
        'analyze_placement_exam.py',
        'create_tier_lists.py',
        'generate_student_roster.py'
    ]

    print("Checking prerequisites...")
    all_present = True

    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} - NOT FOUND")
            all_present = False

    return all_present

def main():
    """Main execution function."""
    print(f"""
╔════════════════════════════════════════════════════════════════════════════╗
║                   PLACEMENT EXAM ANALYSIS SUITE                            ║
║                         Spring 2026                                        ║
╚════════════════════════════════════════════════════════════════════════════╝

Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
""")

    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites check failed. Please ensure all required files exist.")
        sys.exit(1)

    print("\n✅ All prerequisites present.\n")

    # Track success/failure
    results = {}

    # Script 1: Comprehensive analysis
    success, output = run_script(
        'analyze_placement_exam.py',
        'Comprehensive statistical analysis of placement exam results'
    )
    results['analyze_placement_exam'] = success
    if success:
        # Save output to file for reference
        with open('/tmp/placement_exam_analysis_output.txt', 'w') as f:
            f.write(output)
        print("📄 Analysis output saved to: /tmp/placement_exam_analysis_output.txt")

    # Script 2: Tier lists
    success, output = run_script(
        'create_tier_lists.py',
        'Generate sorted student lists by tier and course'
    )
    results['create_tier_lists'] = success
    if success:
        with open('/tmp/tier_lists_output.txt', 'w') as f:
            f.write(output)
        print("📄 Tier lists output saved to: /tmp/tier_lists_output.txt")

    # Script 3: Student roster
    success, output = run_script(
        'generate_student_roster.py',
        'Generate curated student roster with unique IDs'
    )
    results['generate_student_roster'] = success

    # Summary report
    print(f"\n{'=' * 80}")
    print("SUMMARY REPORT")
    print(f"{'=' * 80}\n")

    all_success = all(results.values())

    print("Script Execution Status:")
    for script, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"  {script:40} {status}")

    print(f"\nEnd time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if all_success:
        print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                     ✅ ALL ANALYSES COMPLETED SUCCESSFULLY                 ║
╚════════════════════════════════════════════════════════════════════════════╝

Generated files:
  • /tmp/placement_exam_analysis_output.txt - Full analysis report
  • /tmp/tier_lists_output.txt - Tier-sorted student lists
  • ../docs/STUDENT_ROSTER_SPRING_2026.csv - Student roster for LMS
  • ../bases/curated_student_roster.csv - Copy in bases folder

Next steps:
  1. Review the analysis outputs above
  2. Use the curated roster for LMS integration
  3. Follow action items in ../docs/ACTION_ITEMS_MARCH_2026.md
  4. Deploy E01 diagnostic exercise (Signal 2)
  5. Finalize tier placements by Week 3 (March 21)
""")
        return 0
    else:
        print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                     ⚠️  SOME ANALYSES FAILED                               ║
╚════════════════════════════════════════════════════════════════════════════╝

Please review the error messages above and fix any issues before proceeding.
""")
        return 1

if __name__ == '__main__':
    sys.exit(main())
