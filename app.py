from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from decouple import Config

config = Config('.env')


app = Flask(__name__)

def create_database_connection():
    conn = sqlite3.connect('StJosephs.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            rollno INTEGER PRIMARY KEY,
            name TEXT,
            classroom TEXT
        )
    ''')
    conn.commit()

    return conn, cursor


def close_database_connection(conn):
    conn.close()

def insert_student_data(roll_no, name, classroom):
    conn, cursor = create_database_connection()
    try:
        insert_sql = "INSERT INTO students (rollno, name, classroom) VALUES (?, ?, ?)"
        cursor.execute(insert_sql, (roll_no, name, classroom))
        conn.commit()
        return True
    except sqlite3.Error as e:
        return str(e)
    finally:
        close_database_connection(conn)

def get_student_data_by_roll_no(roll_no):
    conn, cursor = create_database_connection()
    try:
        cursor.execute(
            "SELECT name, classroom FROM students WHERE rollno=?", (roll_no,))
        result = cursor.fetchone() 

        if result:
            name, classroom = result  
            return name, classroom
        else:
            return ['No data available']
    except sqlite3.Error as e:
        return str(e)
    finally:
        close_database_connection(conn)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/view_classroom', methods=['GET', 'POST'])
def view_classroom():
    error_message = None
    student_data = None 

    if request.method == 'POST':
        roll_no = request.form.get('roll_no')

        student_data = get_student_data_by_roll_no(roll_no)

        if student_data is None:
            error_message = "No data found for the provided Roll Number."

    return render_template('view_classroom.html',student_data=student_data)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username ==  config.get('USERNAME') and password ==  config.get('PASSWORD'):
            return redirect(url_for('admin'))
        else:
            error_message = "Invalid credentials. Please try again."
            return render_template('home.html', error_message=error_message)
    return render_template('home.html')


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        roll_no = request.form['roll_no']
        name = request.form['name']
        classroom = request.form['classroom']
        if insert_student_data(roll_no, name, classroom):
            success_message = "Data inserted successfully!"
            return render_template('admin.html', success_message=success_message)
        else:
            error_message = "Error inserting data. Please try again."
            return render_template('admin.html', error_message=error_message)
    return render_template('admin.html')


if __name__ == '__main__':
    app.run(debug=True)
