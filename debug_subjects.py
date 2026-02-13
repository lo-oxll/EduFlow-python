#!/usr/bin/env python3
"""
Debug script to check subjects and schools data
"""
from database import get_mysql_pool

def debug_database():
    try:
        pool = get_mysql_pool()
        if not pool:
            print("Failed to connect to database")
            return
            
        conn = pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Check schools
        cursor.execute('SELECT id, name, code FROM schools')
        schools = cursor.fetchall()
        print("=== SCHOOLS ===")
        for school in schools:
            print(f"ID: {school['id']}, Name: {school['name']}, Code: {school['code']}")
        
        print("\n=== SUBJECTS ===")
        cursor.execute('SELECT id, school_id, name, grade_level FROM subjects')
        subjects = cursor.fetchall()
        for subject in subjects:
            print(f"ID: {subject['id']}, School ID: {subject['school_id']}, Name: {subject['name']}, Grade: {subject['grade_level']}")
        
        print(f"\nTotal subjects: {len(subjects)}")
        
        # Check teacher_subjects relationships
        print("\n=== TEACHER-SUBJECT RELATIONSHIPS ===")
        cursor.execute('SELECT ts.teacher_id, ts.subject_id, s.name as subject_name, t.full_name as teacher_name FROM teacher_subjects ts JOIN subjects s ON ts.subject_id = s.id JOIN teachers t ON ts.teacher_id = t.id LIMIT 10')
        relationships = cursor.fetchall()
        for rel in relationships:
            print(f"Teacher: {rel['teacher_name']}, Subject: {rel['subject_name']}")
            
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_database()