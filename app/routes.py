from flask import render_template, request, url_for, redirect
from app import app

@app.route('/', methods=['GET']) # Replace this with a login page later
@app.route('/calendar', methods=['GET'])
def calendar():
    return render_template('calendar-page.html', calendar_active=True)

@app.route('/todo', methods=['GET'])
def to_do_list():
    return render_template('todo-page.html', todo_active=True)

@app.route('/friends', methods=['GET'])
def friends():
    return render_template('friends-page.html', friends_active=True)

@app.route('/import', methods=['GET'])
def imported_calendars():
    return render_template('import-page.html', import_active=True)