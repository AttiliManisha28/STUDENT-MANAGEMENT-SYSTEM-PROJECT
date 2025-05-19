from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    
    #Creating students table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            course TEXT NOT NULL
        )
    ''')
    
    #Creating attendance table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(id)
        )
    ''')

    #Creating grades table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS grades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            subject TEXT NOT NULL,
            grade TEXT NOT NULL,
            FOREIGN KEY(student_id) REFERENCES students(id)
        )
    ''')

    #Creating messages table for student communication
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            body TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/enrollment', methods=['GET', 'POST'])
def enrollment():
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        student_id = request.form.get('id')
        name = request.form['name']
        email = request.form['email']
        course = request.form['course']

        if student_id:
            cursor.execute('UPDATE students SET name=?, email=?, course=? WHERE id=?',
                           (name, email, course, student_id))
        else:
            cursor.execute('INSERT INTO students (name, email, course) VALUES (?, ?, ?)',
                           (name, email, course))
        conn.commit()

    edit_id = request.args.get('edit')
    edit_student = None
    if edit_id:
        cursor.execute('SELECT * FROM students WHERE id=?', (edit_id,))
        edit_student = cursor.fetchone()

    cursor.execute('SELECT * FROM students')
    students = cursor.fetchall()
    conn.close()
    return render_template('enrollment.html', students=students, edit_student=edit_student)

@app.route('/delete/<int:id>')
def delete(id):
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM students WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('enrollment'))

@app.route('/attendance', methods=['GET', 'POST'])
def attendance():
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        date = request.form['date']
        student_ids = request.form.getlist('student_id')
        for student_id in student_ids:
            status = request.form.get(f'status_{student_id}')
            cursor.execute('INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?)',
                           (student_id, date, status))
        conn.commit()
        conn.close()
        return redirect(url_for('attendance'))

    cursor.execute('SELECT id, name FROM students')
    students = cursor.fetchall()
    conn.close()
    return render_template('attendance.html', students=students)

@app.route('/view_attendance')
def view_attendance():
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT a.id, a.date, a.student_id, a.status, s.email, s.name 
        FROM attendance a 
        JOIN students s ON a.student_id = s.id
        ORDER BY a.date DESC
    ''')
    records = cursor.fetchall()
    conn.close()
    return render_template('attendance_view.html', records=records)

@app.route('/attendance/edit/<int:id>', methods=['GET', 'POST'])
def edit_attendance(id):
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        date = request.form['date']
        status = request.form['status']
        student_id = request.form['student_id']

        cursor.execute('''
            UPDATE attendance
            SET date = ?, status = ?, student_id = ?
            WHERE id = ?
        ''', (date, status, student_id, id))
        conn.commit()
        conn.close()
        return redirect(url_for('view_attendance'))

    cursor.execute('SELECT id, date, status, student_id FROM attendance WHERE id = ?', (id,))
    attendance_record = cursor.fetchone()

    cursor.execute('SELECT id, name FROM students')
    students = cursor.fetchall()
    conn.close()
    return render_template('edit_attendance.html', record=attendance_record, students=students)

@app.route('/attendance/delete/<int:id>')
def delete_attendance(id):
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM attendance WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('view_attendance'))

@app.route('/grades', methods=['GET', 'POST'])
def grades():
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        student_id = request.form['student_id']
        subject = request.form['subject']
        grade = request.form['grade']

        cursor.execute('''
        INSERT INTO grades (student_id, subject, grade)
        VALUES (?, ?, ?)
        ''', (student_id, subject, grade))
        conn.commit()

    cursor.execute('SELECT id, name FROM students')
    students = cursor.fetchall()

    cursor.execute('''
    SELECT g.id, s.name, g.subject, g.grade
    FROM grades g
    JOIN students s ON g.student_id = s.id
    ORDER BY g.id DESC
    ''')
    records = cursor.fetchall()

    conn.close()
    return render_template('grades.html', students=students, records=records)

@app.route('/grades/edit/<int:id>', methods=['GET', 'POST'])
def edit_grade(id):
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        student_id = request.form['student_id']
        subject = request.form['subject']
        grade = request.form['grade']

        cursor.execute('''
            UPDATE grades
            SET student_id = ?, subject = ?, grade = ?
            WHERE id = ?
        ''', (student_id, subject, grade, id))
        conn.commit()
        conn.close()
        return redirect(url_for('grades'))

    cursor.execute('SELECT id, student_id, subject, grade FROM grades WHERE id = ?', (id,))
    record = cursor.fetchone()

    cursor.execute('SELECT id, name FROM students')
    students = cursor.fetchall()
    conn.close()
    return render_template('edit_grade.html', record=record, students=students)

@app.route('/grades/delete/<int:id>')
def delete_grade(id):
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM grades WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('grades'))

@app.route('/communication', methods=['GET', 'POST'])
def communication():
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        cursor.execute('''
            INSERT INTO messages (title, body, timestamp)
            VALUES (?, ?, ?)
        ''', (title, body, timestamp))
        conn.commit()

    cursor.execute('SELECT * FROM messages ORDER BY id DESC')
    messages = cursor.fetchall()
    conn.close()
    return render_template('communication.html', messages=messages)

#Run the application
if __name__ == '__main__':
    init_db()
    app.run(debug=True)





#TO RUN THE FILE TYPE: python app.py, then click the link