import sqlite3

DB_PATH = r'C:\Users\Milano\Desktop\1m\school.db'

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("Checking database contents...")

# Check students
cur.execute('SELECT COUNT(*) as count FROM students')
student_count = cur.fetchone()['count']
print(f"Students: {student_count}")

# Check academic years
cur.execute('SELECT COUNT(*) as count FROM system_academic_years')
year_count = cur.fetchone()['count']
print(f"Academic years: {year_count}")

# Check student grades
cur.execute('SELECT COUNT(*) as count FROM student_grades')
grade_count = cur.fetchone()['count']
print(f"Student grades: {grade_count}")

# Show students with grades
cur.execute('''
    SELECT DISTINCT s.id, s.full_name, s.grade, COUNT(sg.id) as grade_count
    FROM students s
    LEFT JOIN student_grades sg ON s.id = sg.student_id
    GROUP BY s.id
    LIMIT 5
''')
students = cur.fetchall()
print(f"\nFirst 5 students:")
for s in students:
    print(f"  - {s['full_name']} ({s['grade']}): {s['grade_count']} grades")

conn.close()
