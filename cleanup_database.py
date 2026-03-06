#!/usr/bin/env python3
"""
Database Cleanup Script for EduFlow
Removes orphaned records from database to maintain data integrity
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import database functions
sys.path.append(os.path.dirname(__file__))
from database import get_mysql_pool

def cleanup_orphaned_students():
    """Remove students whose school doesn't exist"""
    pool = get_mysql_pool()
    if not pool:
        print("❌ Failed to connect to database")
        return
    
    conn = pool.get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        
        # Find orphaned students
        cur.execute('''
            SELECT s.id, s.full_name, s.student_code, s.school_id
            FROM students s
            LEFT JOIN schools sch ON s.school_id = sch.id
            WHERE sch.id IS NULL
        ''')
        orphaned_students = cur.fetchall()
        
        if not orphaned_students:
            print("✅ No orphaned students found")
            return 0
        
        print(f"\n📋 Found {len(orphaned_students)} orphaned students:")
        for student in orphaned_students:
            print(f"   - ID: {student['id']}, Name: {student['full_name']}, "
                  f"Code: {student['student_code']}, School ID: {student['school_id']}")
        
        confirm = input("\n⚠️  Do you want to delete these orphaned students? (yes/no): ")
        if confirm.lower() != 'yes':
            print("❌ Cleanup cancelled")
            return 0
        
        # Delete related records first
        deleted_grades = 0
        deleted_attendance = 0
        deleted_students = 0
        
        for student in orphaned_students:
            student_id = student['id']
            
            # Delete student grades
            cur.execute('DELETE FROM student_grades WHERE student_id = %s', (student_id,))
            deleted_grades += cur.rowcount
            
            # Delete student attendance
            cur.execute('DELETE FROM student_attendance WHERE student_id = %s', (student_id,))
            deleted_attendance += cur.rowcount
            
            # Delete student
            cur.execute('DELETE FROM students WHERE id = %s', (student_id,))
            deleted_students += cur.rowcount
        
        conn.commit()
        
        print(f"\n✅ Cleanup completed successfully!")
        print(f"   🗑️  Deleted students: {deleted_students}")
        print(f"   🗑️  Deleted grade records: {deleted_grades}")
        print(f"   🗑️  Deleted attendance records: {deleted_attendance}")
        
        return deleted_students
        
    except Exception as e:
        print(f"❌ Error during cleanup: {str(e)}")
        conn.rollback()
        return 0
    finally:
        conn.close()

def cleanup_orphaned_teachers():
    """Remove teachers whose school doesn't exist"""
    pool = get_mysql_pool()
    if not pool:
        print("❌ Failed to connect to database")
        return
    
    conn = pool.get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        
        # Find orphaned teachers
        cur.execute('''
            SELECT t.id, t.full_name, t.teacher_code, t.school_id
            FROM teachers t
            LEFT JOIN schools sch ON t.school_id = sch.id
            WHERE sch.id IS NULL
        ''')
        orphaned_teachers = cur.fetchall()
        
        if not orphaned_teachers:
            print("✅ No orphaned teachers found")
            return 0
        
        print(f"\n📋 Found {len(orphaned_teachers)} orphaned teachers:")
        for teacher in orphaned_teachers:
            print(f"   - ID: {teacher['id']}, Name: {teacher['full_name']}, "
                  f"Code: {teacher['teacher_code']}, School ID: {teacher['school_id']}")
        
        confirm = input("\n⚠️  Do you want to delete these orphaned teachers? (yes/no): ")
        if confirm.lower() != 'yes':
            print("❌ Cleanup cancelled")
            return 0
        
        # Delete related records first
        deleted_subjects = 0
        deleted_assignments = 0
        deleted_teachers = 0
        
        for teacher in orphaned_teachers:
            teacher_id = teacher['id']
            
            # Delete teacher subjects
            cur.execute('DELETE FROM teacher_subjects WHERE teacher_id = %s', (teacher_id,))
            deleted_subjects += cur.rowcount
            
            # Delete teacher class assignments
            cur.execute('DELETE FROM teacher_class_assignments WHERE teacher_id = %s', (teacher_id,))
            deleted_assignments += cur.rowcount
            
            # Delete teacher
            cur.execute('DELETE FROM teachers WHERE id = %s', (teacher_id,))
            deleted_teachers += cur.rowcount
        
        conn.commit()
        
        print(f"\n✅ Cleanup completed successfully!")
        print(f"   🗑️  Deleted teachers: {deleted_teachers}")
        print(f"   🗑️  Deleted subject assignments: {deleted_subjects}")
        print(f"   🗑️  Deleted class assignments: {deleted_assignments}")
        
        return deleted_teachers
        
    except Exception as e:
        print(f"❌ Error during cleanup: {str(e)}")
        conn.rollback()
        return 0
    finally:
        conn.close()

def cleanup_orphaned_subjects():
    """Remove subjects whose school doesn't exist"""
    pool = get_mysql_pool()
    if not pool:
        print("❌ Failed to connect to database")
        return
    
    conn = pool.get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        
        # Find orphaned subjects
        cur.execute('''
            SELECT s.id, s.name, s.grade_level, s.school_id
            FROM subjects s
            LEFT JOIN schools sch ON s.school_id = sch.id
            WHERE sch.id IS NULL
        ''')
        orphaned_subjects = cur.fetchall()
        
        if not orphaned_subjects:
            print("✅ No orphaned subjects found")
            return 0
        
        print(f"\n📋 Found {len(orphaned_subjects)} orphaned subjects:")
        for subject in orphaned_subjects:
            print(f"   - ID: {subject['id']}, Name: {subject['name']}, "
                  f"Grade: {subject['grade_level']}, School ID: {subject['school_id']}")
        
        confirm = input("\n⚠️  Do you want to delete these orphaned subjects? (yes/no): ")
        if confirm.lower() != 'yes':
            print("❌ Cleanup cancelled")
            return 0
        
        # Delete subjects
        cur.execute('DELETE FROM subjects WHERE school_id IS NOT NULL AND school_id NOT IN (SELECT id FROM schools)')
        deleted_count = cur.rowcount
        conn.commit()
        
        print(f"\n✅ Cleanup completed successfully!")
        print(f"   🗑️  Deleted subjects: {deleted_count}")
        
        return deleted_count
        
    except Exception as e:
        print(f"❌ Error during cleanup: {str(e)}")
        conn.rollback()
        return 0
    finally:
        conn.close()

def cleanup_orphaned_grade_levels():
    """Remove grade levels whose school doesn't exist"""
    pool = get_mysql_pool()
    if not pool:
        print("❌ Failed to connect to database")
        return
    
    conn = pool.get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        
        # Find orphaned grade levels
        cur.execute('''
            SELECT g.id, g.name, g.school_id
            FROM grade_levels g
            LEFT JOIN schools sch ON g.school_id = sch.id
            WHERE sch.id IS NULL
        ''')
        orphaned_grade_levels = cur.fetchall()
        
        if not orphaned_grade_levels:
            print("✅ No orphaned grade levels found")
            return 0
        
        print(f"\n📋 Found {len(orphaned_grade_levels)} orphaned grade levels:")
        for gl in orphaned_grade_levels:
            print(f"   - ID: {gl['id']}, Name: {gl['name']}, School ID: {gl['school_id']}")
        
        confirm = input("\n⚠️  Do you want to delete these orphaned grade levels? (yes/no): ")
        if confirm.lower() != 'yes':
            print("❌ Cleanup cancelled")
            return 0
        
        # Delete grade levels
        cur.execute('DELETE FROM grade_levels WHERE school_id IS NOT NULL AND school_id NOT IN (SELECT id FROM schools)')
        deleted_count = cur.rowcount
        conn.commit()
        
        print(f"\n✅ Cleanup completed successfully!")
        print(f"   🗑️  Deleted grade levels: {deleted_count}")
        
        return deleted_count
        
    except Exception as e:
        print(f"❌ Error during cleanup: {str(e)}")
        conn.rollback()
        return 0
    finally:
        conn.close()

def run_full_cleanup():
    """Run all cleanup operations"""
    print("=" * 60)
    print("🧹 EDUFLOW DATABASE CLEANUP UTILITY")
    print("=" * 60)
    print("\nThis utility will check for and remove orphaned records:")
    print("   • Students without schools")
    print("   • Teachers without schools")
    print("   • Subjects without schools")
    print("   • Grade levels without schools")
    print("\n" + "=" * 60)
    
    confirm = input("\n⚠️  WARNING: This will permanently delete data. Continue? (yes/no): ")
    if confirm.lower() != 'yes':
        print("❌ Cleanup cancelled by user")
        return
    
    print("\n" + "=" * 60)
    print("Starting cleanup process...")
    print("=" * 60)
    
    total_deleted = 0
    
    print("\n[1/4] Checking orphaned students...")
    total_deleted += cleanup_orphaned_students()
    
    print("\n[2/4] Checking orphaned teachers...")
    total_deleted += cleanup_orphaned_teachers()
    
    print("\n[3/4] Checking orphaned subjects...")
    total_deleted += cleanup_orphaned_subjects()
    
    print("\n[4/4] Checking orphaned grade levels...")
    total_deleted += cleanup_orphaned_grade_levels()
    
    print("\n" + "=" * 60)
    print(f"✅ CLEANUP COMPLETED")
    print(f"   Total records deleted: {total_deleted}")
    print("=" * 60)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'students':
            cleanup_orphaned_students()
        elif command == 'teachers':
            cleanup_orphaned_teachers()
        elif command == 'subjects':
            cleanup_orphaned_subjects()
        elif command == 'grade-levels':
            cleanup_orphaned_grade_levels()
        elif command == 'all' or command == 'full':
            run_full_cleanup()
        else:
            print("Usage: python cleanup_database.py [students|teachers|subjects|grade-levels|all]")
    else:
        # Default: run full cleanup
        run_full_cleanup()
