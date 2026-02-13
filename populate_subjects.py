#!/usr/bin/env python3
"""
Script to populate sample subjects if none exist
"""
from database import get_mysql_pool

def populate_sample_subjects():
    try:
        pool = get_mysql_pool()
        if not pool:
            print("Failed to connect to database")
            return
            
        conn = pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Check if subjects exist
        cursor.execute('SELECT COUNT(*) as count FROM subjects')
        result = cursor.fetchone()
        subject_count = result['count']
        
        print(f"Current subjects count: {subject_count}")
        
        if subject_count == 0:
            print("No subjects found. Adding sample subjects...")
            
            # Get schools
            cursor.execute('SELECT id FROM schools LIMIT 1')
            school_result = cursor.fetchone()
            
            if not school_result:
                print("No schools found. Cannot add subjects.")
                return
                
            school_id = school_result['id']
            print(f"Adding subjects for school ID: {school_id}")
            
            # Sample subjects data
            sample_subjects = [
                ('الرياضيات', 'الأول الابتدائي'),
                ('اللغة العربية', 'الأول الابتدائي'),
                ('العلوم', 'الأول الابتدائي'),
                ('اللغة الإنجليزية', 'الأول الابتدائي'),
                ('الرياضيات', 'الثاني الابتدائي'),
                ('اللغة العربية', 'الثاني الابتدائي'),
                ('العلوم', 'الثاني الابتدائي'),
                ('اللغة الإنجليزية', 'الثاني الابتدائي'),
                ('الرياضيات', 'الثالث الابتدائي'),
                ('اللغة العربية', 'الثالث الابتدائي'),
                ('العلوم', 'الثالث الابتدائي'),
                ('اللغة الإنجليزية', 'الثالث الابتدائي'),
            ]
            
            # Insert sample subjects
            for name, grade_level in sample_subjects:
                try:
                    cursor.execute(
                        'INSERT INTO subjects (school_id, name, grade_level) VALUES (%s, %s, %s)',
                        (school_id, name, grade_level)
                    )
                    print(f"Added: {name} - {grade_level}")
                except Exception as e:
                    print(f"Error adding {name}: {e}")
            
            conn.commit()
            print(f"Successfully added {len(sample_subjects)} sample subjects")
            
            # Verify insertion
            cursor.execute('SELECT COUNT(*) as count FROM subjects')
            result = cursor.fetchone()
            print(f"New subjects count: {result['count']}")
            
        else:
            print("Subjects already exist. No action needed.")
            # Show existing subjects
            cursor.execute('SELECT id, school_id, name, grade_level FROM subjects')
            subjects = cursor.fetchall()
            print("Existing subjects:")
            for subject in subjects:
                print(f"  - {subject['name']} ({subject['grade_level']}) - School: {subject['school_id']}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    populate_sample_subjects()