import sqlite3

def get_db_connection():
    conn = sqlite3.connect('student_management.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_attendance_table():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            date TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
    ''')
    conn.commit()
    conn.close()
