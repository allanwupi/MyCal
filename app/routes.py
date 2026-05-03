from flask import render_template, request, url_for, redirect
from app import app

@app.route('/', methods=['GET'])
@app.route('/calendar', methods=['GET'])
def calendar():
    return render_template('calendar-page.html', 
                           calendar_active='active',
                           todo_active='inactive',
                           friends_active='inactive',
                           import_active='inactive')

@app.route('/todo', methods=['GET'])
def to_do_list():
    return render_template('todo-page.html',
                           calendar_active='inactive',
                           todo_active='active',
                           friends_active='inactive',
                           import_active='inactive')

@app.route('/friends', methods=['GET'])
def friends():
    return render_template('friends-page.html',
                           calendar_active='inactive',
                           todo_active='inactive',
                           friends_active='active',
                           import_active='inactive')

@app.route('/import', methods=['GET'])
def imported_calendars():
    return render_template('import-page.html',
                           calendar_active='inactive',
                           todo_active='inactive',
                           friends_active='inactive',
                           import_active='active')