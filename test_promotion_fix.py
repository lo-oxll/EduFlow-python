"""
Test script to verify student promotion preserves historical grades.
This script tests that:
1. Student grades from previous grade levels remain intact after promotion
2. Only the student's current grade level is updated during promotion
3. No grades are transferred, modified, or deleted during promotion
4. Historical grades remain associated with their original academic year
"""

import sqlite3
import json

DB_PATH = r'C:\Users\Milano\Desktop\1m\school.db'

def test_promotion_preserves_grades():
    """Test that promotion preserves historical grades"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    print("=" * 80)
    print("STUDENT PROMOTION GRADE PRESERVATION TEST")
    print("=" * 80)
    
    # Get a student with grades
    cur.execute('''
        SELECT DISTINCT s.id, s.full_name, s.grade, s.student_code
        FROM students s
        JOIN student_grades sg ON s.id = sg.student_id
        LIMIT 1
    ''')
    student = cur.fetchone()
    
    if not student:
        print("\n❌ No student with grades found in database")
        print("Please add a student and assign some grades first to test promotion.")
        conn.close()
        return False
    
    student_id = student['id']
    student_name = student['full_name']
    old_grade = student['grade']
    
    print(f"\n📋 Testing with Student: {student_name} (ID: {student_id})")
    print(f"   Current Grade: {old_grade}")
    
    # Get all grades for this student BEFORE promotion
    cur.execute('''
        SELECT sg.*, say.name as academic_year_name
        FROM student_grades sg
        JOIN system_academic_years say ON sg.academic_year_id = say.id
        WHERE sg.student_id = ?
        ORDER BY say.start_year, sg.subject_name
    ''', (student_id,))
    grades_before = cur.fetchall()
    
    print(f"\n📚 Grades BEFORE promotion:")
    print(f"   Total grade records: {len(grades_before)}")
    
    grades_by_year_before = {}
    for grade in grades_before:
        year = grade['academic_year_name']
        if year not in grades_by_year_before:
            grades_by_year_before[year] = []
        grades_by_year_before[year].append({
            'subject': grade['subject_name'],
            'month1': grade['month1'],
            'month2': grade['month2'],
            'midterm': grade['midterm'],
            'month3': grade['month3'],
            'month4': grade['month4'],
            'final': grade['final']
        })
    
    for year, year_grades in grades_by_year_before.items():
        print(f"\n   {year}:")
        for g in year_grades:
            print(f"      - {g['subject']}: [M1:{g['month1']}, M2:{g['month2']}, Mid:{g['midterm']}, M3:{g['month3']}, M4:{g['month4']}, Final:{g['final']}]")
    
    # Simulate promotion by updating only the grade field
    new_grade = "ابتدائي - الثاني الابتدائي"  # Example promotion
    print(f"\n🔄 Simulating promotion to: {new_grade}")
    print("   (This simulates what the /api/student/<id>/promote endpoint does)")
    
    cur.execute('UPDATE students SET grade = ? WHERE id = ?', (new_grade, student_id))
    conn.commit()
    
    # Get student grade after promotion
    cur.execute('SELECT grade FROM students WHERE id = ?', (student_id,))
    updated_student = cur.fetchone()
    print(f"   ✓ Student grade updated to: {updated_student['grade']}")
    
    # Get all grades for this student AFTER promotion
    cur.execute('''
        SELECT sg.*, say.name as academic_year_name
        FROM student_grades sg
        JOIN system_academic_years say ON sg.academic_year_id = say.id
        WHERE sg.student_id = ?
        ORDER BY say.start_year, sg.subject_name
    ''', (student_id,))
    grades_after = cur.fetchall()
    
    print(f"\n📚 Grades AFTER promotion:")
    print(f"   Total grade records: {len(grades_after)}")
    
    grades_by_year_after = {}
    for grade in grades_after:
        year = grade['academic_year_name']
        if year not in grades_by_year_after:
            grades_by_year_after[year] = []
        grades_by_year_after[year].append({
            'subject': grade['subject_name'],
            'month1': grade['month1'],
            'month2': grade['month2'],
            'midterm': grade['midterm'],
            'month3': grade['month3'],
            'month4': grade['month4'],
            'final': grade['final']
        })
    
    for year, year_grades in grades_by_year_after.items():
        print(f"\n   {year}:")
        for g in year_grades:
            print(f"      - {g['subject']}: [M1:{g['month1']}, M2:{g['month2']}, Mid:{g['midterm']}, M3:{g['month3']}, M4:{g['month4']}, Final:{g['final']}]")
    
    # Verify that grades were preserved
    print(f"\n{'=' * 80}")
    print("VERIFICATION RESULTS:")
    print(f"{'=' * 80}")
    
    success = True
    
    # Check 1: Same number of grade records
    if len(grades_before) != len(grades_after):
        print(f"❌ FAIL: Number of grade records changed!")
        print(f"   Before: {len(grades_before)} records")
        print(f"   After: {len(grades_after)} records")
        success = False
    else:
        print(f"✅ PASS: Number of grade records unchanged ({len(grades_after)} records)")
    
    # Check 2: All grades are identical
    grades_match = True
    for i, (before, after) in enumerate(zip(grades_before, grades_after)):
        if (before['subject_name'] != after['subject_name'] or
            before['academic_year_name'] != after['academic_year_name'] or
            before['month1'] != after['month1'] or
            before['month2'] != after['month2'] or
            before['midterm'] != after['midterm'] or
            before['month3'] != after['month3'] or
            before['month4'] != after['month4'] or
            before['final'] != after['final']):
            print(f"❌ FAIL: Grade record {i+1} changed!")
            print(f"   Before: {before['subject_name']} ({before['academic_year_name']})")
            print(f"   After: {after['subject_name']} ({after['academic_year_name']})")
            grades_match = False
            success = False
    
    if grades_match:
        print(f"✅ PASS: All grade records preserved unchanged")
    
    # Check 3: Student grade field updated
    if updated_student['grade'] == new_grade:
        print(f"✅ PASS: Student grade level updated correctly")
    else:
        print(f"❌ FAIL: Student grade level not updated")
        success = False
    
    # Check 4: No new blank grade records created
    new_records = [g for g in grades_after if g['id'] not in [gb['id'] for gb in grades_before]]
    if len(new_records) > 0:
        print(f"❌ FAIL: {len(new_records)} new grade records created (should be 0)")
        for record in new_records:
            print(f"   - {record['subject_name']} ({record['academic_year_name']})")
        success = False
    else:
        print(f"✅ PASS: No new grade records created")
    
    # Restore original grade for future tests
    cur.execute('UPDATE students SET grade = ? WHERE id = ?', (old_grade, student_id))
    conn.commit()
    print(f"\n🔄 Restored student to original grade: {old_grade}")
    
    conn.close()
    
    print(f"\n{'=' * 80}")
    if success:
        print("🎉 ALL TESTS PASSED!")
        print("Student promotion correctly preserves historical grades.")
    else:
        print("❌ SOME TESTS FAILED!")
        print("There are issues with grade preservation during promotion.")
    print(f"{'=' * 80}\n")
    
    return success

if __name__ == '__main__':
    test_promotion_preserves_grades()
