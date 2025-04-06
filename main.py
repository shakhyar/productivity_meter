from flask import Flask, render_template, request, redirect, url_for, send_file
import sqlite3
from datetime import datetime
from math import exp
import matplotlib.pyplot as plt
import io

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('productivity.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS productivity (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date_time TEXT,
                        distracted_minutes REAL,
                        studied_minutes REAL,
                        productivity REAL)''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = sqlite3.connect('productivity.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM productivity ORDER BY datetime(date_time) ASC')
    data = cursor.fetchall()
    conn.close()
    return render_template('index.html', data=data)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        date_time_str = request.form['date_time']
        distracted_minutes = float(request.form['distracted_minutes'])
        studied_minutes = float(request.form['studied_minutes'])
        n = distracted_minutes / studied_minutes
        P = exp(-n)

        conn = sqlite3.connect('productivity.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO productivity (date_time, distracted_minutes, studied_minutes, productivity) VALUES (?, ?, ?, ?)', (date_time_str, distracted_minutes, studied_minutes, P))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add.html')

@app.route('/delete/<int:id>')
def delete(id):
    conn = sqlite3.connect('productivity.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM productivity WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = sqlite3.connect('productivity.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM productivity WHERE id = ?', (id,))
    record = cursor.fetchone()
    conn.close()

    if request.method == 'POST':
        date_time_str = request.form['date_time']
        distracted_minutes = float(request.form['distracted_minutes'])
        studied_minutes = float(request.form['studied_minutes'])
        n = distracted_minutes / studied_minutes
        P = exp(-n)

        conn = sqlite3.connect('productivity.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE productivity SET date_time = ?, distracted_minutes = ?, studied_minutes = ?, productivity = ? WHERE id = ?',
                       (date_time_str, distracted_minutes, studied_minutes, P, id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('edit.html', record=record)

@app.route('/plot')
def plot():
    conn = sqlite3.connect('productivity.db')
    cursor = conn.cursor()
    cursor.execute('SELECT date_time, productivity FROM productivity ORDER BY datetime(date_time) ASC')
    data = cursor.fetchall()
    conn.close()

    dates = [datetime.strptime(row[0], '%Y-%m-%d %H:%M') for row in data]
    productivity = [row[1] for row in data]

    plt.figure(figsize=(10, 5))
    plt.plot(dates, productivity, marker='o')
    plt.title('Productivity Over Time')
    plt.xlabel('Date and Time')
    plt.ylabel('Productivity')
    plt.xticks(rotation=45)
    plt.tight_layout()

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    return send_file(img, mimetype='image/png')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)