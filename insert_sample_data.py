from db_config import create_connection

def insert_sample_data():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("USE grade_db")

    # ✅ Insert sample users
    users = [
        ('Admin User', 'admin@gage.edu', 'admin123', 'admin'),
        ('Teacher One', 'teacher@gage.edu', 'teacher123', 'teacher'),
        ('Student One', 'student@gage.edu', 'student123', 'student'),
        ('Student Two', 'student2@gage.edu', 'student123', 'student'),
    ]
    cursor.executemany("INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)", users)

    # ✅ Insert sample students (use same names as above)
    students = [
        ('Student One',),
        ('Student Two',),
    ]
    cursor.executemany("INSERT INTO students (name) VALUES (%s)", students)

    # ✅ Insert sample courses (assign to teacher ID 2 — make sure this matches the real teacher's ID)
    courses = [
        ('Python Programming', 2),
        ('Database Systems', 2),
    ]
    cursor.executemany("INSERT INTO courses (course_name, teacher_id) VALUES (%s, %s)", courses)

    # ✅ Insert sample grades (assumes student IDs 1 and 2, course IDs 1 and 2)
    grades = [
        (1, 1, 'A'),
        (1, 2, 'B+'),
        (2, 1, 'B'),
        (2, 2, 'A-'),
    ]
    cursor.executemany("INSERT INTO grades (student_id, course_id, grade) VALUES (%s, %s, %s)", grades)

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Sample data inserted successfully.")

# Run the function
if __name__ == '__main__':
    insert_sample_data()
