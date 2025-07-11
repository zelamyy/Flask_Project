import os
import io
import pandas as pd
from flask import Flask, render_template, request, redirect, session, send_file
from db_config import create_connection
from passlib.context import CryptContext

# === Password hashing context ===
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# === Flask App Setup ===
app = Flask(__name__, template_folder='templates')
app.secret_key = "my-dev-secret-key"

# === Create default admin user ===
def create_default_admin():
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email = %s", ('admin@site.com',))
    if not cursor.fetchone():
        hashed_pw = pwd_context.hash('admin123')
        cursor.execute(
            "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
            ('Admin', 'admin@site.com', hashed_pw, 'admin')
        )
        conn.commit()
    cursor.close()
    conn.close()

# === Routes ===
@app.route('/')
def home():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']

        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()

        if user and pwd_context.verify(password, user['password']):
            session.update({
                'user_id': user['id'],
                'role': user['role'],
                'name': user['name'],
                'email': user['email']
            })
            return redirect('/dashboard')
        else:
            error = 'Invalid email or password'

        cursor.close()
        conn.close()

    return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    message = error = None
    if request.method == 'POST':
        name, email, password, role = (request.form[k] for k in ('name', 'email', 'password', 'role'))
        email = email.strip().lower()

        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            error = "Email already registered."
        else:
            hashed_password = pwd_context.hash(password)
            cursor.execute(
                "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
                (name, email, hashed_password, role)
            )
            if role == 'student':
                cursor.execute("INSERT IGNORE INTO students (name, email) VALUES (%s, %s)", (name, email))

            conn.commit()
            message = "\u2705 Registration successful! You can now log in."

        cursor.close()
        conn.close()

    return render_template("register.html", message=message, error=error)

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    role = session['role']
    if role == 'student':
        return render_template('dashboard.html', name=session['name'])
    elif role == 'teacher':
        return render_template('teacher_dashboard.html', name=session['name'])
    elif role == 'admin':
        return render_template('admin_dashboard.html', name=session['name'])

    return redirect('/login')

@app.route('/add-course', methods=['GET', 'POST'])
def add_course():
    if session.get('role') != 'teacher':
        return redirect('/login')

    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    message = error = None

    if request.method == 'POST':
        try:
            cursor.execute(
                "INSERT INTO courses (course_name, teacher_id) VALUES (%s, %s)",
                (request.form['course_name'], session['user_id'])
            )
            conn.commit()
            message = "\u2705 Course added successfully!"
        except Exception as e:
            error = f"\u274C Error: {str(e)}"

    cursor.close()
    conn.close()
    return render_template('add_course.html', message=message, error=error)

@app.route('/add-grade', methods=['GET', 'POST'])
def add_grade():
    if session.get('role') != 'teacher':
        return redirect('/login')

    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name FROM students")
    students = cursor.fetchall()

    cursor.execute("SELECT id, course_name FROM courses WHERE teacher_id = %s", (session['user_id'],))
    courses = cursor.fetchall()

    message = None
    if request.method == 'POST':
        student_id = int(request.form['student_id'])
        course_id = int(request.form['course_id'])
        grade = float(request.form['grade'])

        cursor.execute(
            "INSERT INTO grades (student_id, course_id, grade) VALUES (%s, %s, %s)",
            (student_id, course_id, grade)
        )
        conn.commit()
        message = f"\u2705 Grade {grade} submitted successfully!"

    cursor.close()
    conn.close()
    return render_template('add_grade.html', students=students, courses=courses, message=message)

@app.route('/view-grades')
def view_grades():
    if session.get('role') != 'student':
        return redirect('/login')

    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id FROM students WHERE email = %s", (session['email'],))
    student = cursor.fetchone()

    if not student:
        cursor.close()
        conn.close()
        return "Student not found."

    cursor.execute(
        "SELECT c.course_name, g.grade FROM grades g JOIN courses c ON g.course_id = c.id WHERE g.student_id = %s",
        (student['id'],)
    )
    grades = cursor.fetchall()

    # Grade classification
    def grade_to_letter(g):
        g = float(g)
        if g >= 92:
            return "A+"
        elif g >= 85:
            return "A"
        elif g >= 75:
            return "B+"
        elif g >= 65:
            return "B"
        elif g >= 50:
            return "C"
        else:
            return "F"

    for g in grades:
        g['letter'] = grade_to_letter(g['grade'])

    average = round(sum(float(g['grade']) for g in grades) / len(grades), 2) if grades else None

    cursor.close()
    conn.close()
    return render_template('view_grades.html', grades=grades, name=session['name'], average=average)

@app.route('/download-grades')
def download_grades():
    if session.get('role') != 'student':
        return redirect('/login')

    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id FROM students WHERE email = %s", (session['email'],))
    student = cursor.fetchone()

    cursor.execute(
        "SELECT c.course_name, g.grade FROM grades g JOIN courses c ON g.course_id = c.id WHERE g.student_id = %s",
        (student['id'],)
    )
    grades = cursor.fetchall()
    cursor.close()
    conn.close()

    df = pd.DataFrame(grades)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)

    return send_file(
        output,
        download_name=f"{session['name']}_grades.xlsx",
        as_attachment=True,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@app.route('/admin/students')
def admin_students():
    if session.get('role') != 'admin':
        return redirect('/login')

    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("admin_students.html", students=students)

@app.route('/admin')
def admin():
    if session.get('role') != 'admin':
        return redirect('/login')
    return render_template('admin_dashboard.html', name=session['name'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# === Run the App ===
if __name__ == '__main__':
    create_default_admin()
    app.run(debug=True)