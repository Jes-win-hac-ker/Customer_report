# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import mysql.connector
import csv
from io import StringIO

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Connect to MySQL
db = mysql.connector.connect(
    host="localhost",
    user="customer_report",      # CHANGE THIS
    password="1234",  # CHANGE THIS
    database="customer_report"
)
cursor = db.cursor()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        problem = request.form['problem']
        date_given = request.form['date_given']
        date_diag = request.form['date_diag']
        date_ret = request.form['date_ret']

        sql = """
        INSERT INTO reports (customer_name, phone_number, problem_description, date_given, date_diagnosed, date_returned)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        values = (name, phone, problem, date_given, date_diag, date_ret)
        cursor.execute(sql, values)
        db.commit()
        flash('Report submitted successfully!', 'success')
        return redirect(url_for('submit'))

    return render_template('submit.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    results = []
    if request.method == 'POST':
        term = request.form['term']
        sql = """
        SELECT * FROM reports WHERE BINARY customer_name = %s OR BINARY phone_number = %s
        """
        values = (term, term)
        cursor.execute(sql, values)
        results = cursor.fetchall()
    return render_template('search.html', results=results)

@app.route('/update', methods=['GET', 'POST'])
def update():
    if request.method == 'POST':
        term = request.form['term']
        problem = request.form['problem']
        date_ret = request.form['date_ret']
        sql = """
        UPDATE reports SET problem_description = %s, date_returned = %s
        WHERE BINARY customer_name = %s OR BINARY phone_number = %s
        """
        values = (problem, date_ret, term, term)
        cursor.execute(sql, values)
        db.commit()
        flash('Report updated successfully!', 'success')
        return redirect(url_for('update'))
    return render_template('update.html')

@app.route('/delete', methods=['GET', 'POST'])
def delete():
    if request.method == 'POST':
        term = request.form['term']
        sql = """
        DELETE FROM reports WHERE BINARY customer_name = %s OR BINARY phone_number = %s
        """
        values = (term, term)
        cursor.execute(sql, values)
        db.commit()
        flash('Report deleted successfully!', 'success')
        return redirect(url_for('delete'))
    return render_template('delete.html')

@app.route('/export')
def export():
    sql = "SELECT * FROM reports"
    cursor.execute(sql)
    results = cursor.fetchall()

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Name', 'Phone', 'Problem', 'Date Given', 'Date Diagnosed', 'Date Returned'])
    for row in results:
        writer.writerow(row)

    output.seek(0)
    return send_file(
        output,
        mimetype='text/csv',
        as_attachment=True,
        download_name='customer_reports.csv'
    )

if __name__ == '__main__':
    app.run(debug=True)
