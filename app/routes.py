from flask import flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import or_
from app import app, db
from app.models import Event, TaskStatus, User
from datetime import datetime
import icalendar


def normalise_email(email):
    return (email or '').strip().lower()


def normalise_username(username):
    return (username or '').strip()


@app.route('/', methods=['GET'])
def landing():
    if current_user.is_authenticated:
        return redirect(url_for('calendar'))
    return render_template('landing.html')


@app.route('/signup', methods=['POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('calendar'))

    username = normalise_username(request.form.get('username'))
    email = normalise_email(request.form.get('email'))
    password = request.form.get('password') or ''
    confirm_password = request.form.get('confirm_password') or ''

    if not username or not email or not password:
        flash('Username, email, and password are required.', 'danger')
        return redirect(url_for('landing'))

    if '@' not in email or '.' not in email:
        flash('Please enter a valid email address.', 'danger')
        return redirect(url_for('landing'))

    if len(password) < 8:
        flash('Password must be at least 8 characters long.', 'danger')
        return redirect(url_for('landing'))

    if password != confirm_password:
        flash('Passwords do not match.', 'danger')
        return redirect(url_for('landing'))

    existing_user = db.session.query(User).filter(
        or_(User.email == email, User.username == username)
    ).first()

    if existing_user:
        if existing_user.email == email:
            flash('An account with that email already exists. Please log in.', 'danger')
        else:
            flash('That username is already taken.', 'danger')
        return redirect(url_for('landing'))

    user = User(email=email, username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    login_user(user)
    flash('Account created successfully. Welcome to MyCal!', 'success')
    return redirect(url_for('calendar'))


@app.route('/login', methods=['POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('calendar'))

    identifier = (request.form.get('identifier') or '').strip()
    password = request.form.get('password') or ''
    remember = request.form.get('remember') == 'on'

    if not identifier or not password:
        flash('Email/username and password are required.', 'danger')
        return redirect(url_for('landing'))

    user = db.session.query(User).filter(
        or_(User.email == identifier.lower(), User.username == identifier)
    ).first()

    if not user or not user.check_password(password):
        flash('Invalid login details. Please try again.', 'danger')
        return redirect(url_for('landing'))

    login_user(user, remember=remember)
    flash('Logged in successfully.', 'success')
    return redirect(url_for('calendar'))


@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('landing'))


@app.route('/calendar', methods=['GET'])
@login_required
def calendar():
    return render_template('calendar-page.html', calendar_active=True)


@app.route('/todo', methods=['GET'])
@login_required
def to_do_list():
    tasks = (
        db.session.query(Event)
        .filter_by(isTask=True, owner=current_user.email)
        .order_by(Event.start.asc())
        .all()
    )
    return render_template('todo-page.html', todo_active=True, tasks=tasks)


@app.route('/friends', methods=['GET'])
@login_required
def friends():
    return render_template('friends-page.html', friends_active=True)


@app.route('/import', methods=['GET'])
@login_required
def imported_calendars():
    return render_template('import-page.html', import_active=True)


@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if not file or not file.filename.endswith('.ics'):
        return {"error": "Invalid file"}, 400
    if not(file.filename):
        return {"error": "No file provided"}, 400
    cal = icalendar.Calendar.from_ical(file.read())
    count = 0
    seen = set()
    events = []
    for component in cal.walk():
        if component.name == "VEVENT":
            uid = str(component.get('uid'))
            if uid in seen:
                continue
            seen.add(uid)
            event = Event(
                title=str(component.get('summary')),
                start=component.get('dtstart').dt,
                end=component.get('dtend').dt if component.get('dtend') else None,
                backgroundColor=component.get('color', '#6366f1'),
                location=component.get('location', ''),
                description=component.get('description', ''),
                owner = current_user.email
            )
            db.session.add(event)
            events.append(event)
            count += 1
    db.session.commit()
    return jsonify([e.to_dict() for e in events]), 200

 
@app.route('/get-events', methods=['GET'])
@login_required
def get_events():
    events = db.session.query(Event).filter_by(owner=current_user.email).all()
    return jsonify([event.to_dict() for event in events]), 200


@app.route('/save/<dtype>', methods=['POST'])
@login_required
def save_event_task(dtype):
    """Save a new event or task to the database with server-side validation.
    Note that the request MUST specify all required parameters for an event/task."""
    try:
        data = request.get_json()
        provided_id = data.get('id')
        # Try to interpret provided ID as an integer (FullCalendar may send strings)
        try:
            provided_id = int(provided_id) if provided_id is not None else None
        except (ValueError, TypeError):
            provided_id = None
        if (dtype == 'task'):
            if not data.get('start'):
                return jsonify({'error': 'Due date is required for tasks'}), 400
            try:
                from datetime import datetime
                # FullCalendar will not store the end date for tasks, so we must access the start date
                # This is the same as the end date for tasks which we define as only having a due date
                end = datetime.fromisoformat(data['start'])
            except (ValueError, TypeError):
                return jsonify({'error': 'Invalid date/time format for due date'}), 400
            
            status = data.get('taskStatus', data.get('extendedProps', {}).get('taskStatus'))
            valid_statuses = [status.value for status in TaskStatus]
            if status not in valid_statuses:
                return jsonify({'error': f'Invalid status {status}. Must be one of: {", ".join(valid_statuses)}'}), 400
            
            # If an existing event/task with the provided ID exists, update it
            event = None
            if provided_id is not None:
                event = db.session.query(Event).filter_by(id=provided_id).first()

            if event:
                event.title = data.get('title', event.title).strip()
                event.start = end
                event.end = end
                event.backgroundColor = data.get('backgroundColor', event.backgroundColor)
                event.isTask = True
                event.taskStatus = TaskStatus(status)
            else:
                # Create new task (do NOT set the primary key manually)
                event = Event(
                    title=data['title'].strip(),
                    start=end,
                    end=end,
                    backgroundColor=data.get('backgroundColor', '#6366f1'),
                    isTask=True,
                    taskStatus=TaskStatus(status),
                    owner=current_user.email
                )
        elif (dtype == 'event'): # Create a regular event
            # Server-side validation for events
            if not data.get('title') or not data['title'].strip():
                return jsonify({'error': 'Event title is required'}), 400
            if not data.get('start'):
                return jsonify({'error': 'Start date/time is required'}), 400
            if not data.get('end'):
                return jsonify({'error': 'End date/time is required'}), 400
            
            try:
                from datetime import datetime
                start = datetime.fromisoformat(data['start'])
                end = datetime.fromisoformat(data['end'])
                
                if end < start:
                    return jsonify({'error': 'End date/time cannot be before start date/time'}), 400
            except (ValueError, TypeError):
                return jsonify({'error': 'Invalid date/time format'}), 400
            
            # If an existing event with the provided ID exists, update it
            event = None
            if provided_id is not None:
                event = db.session.query(Event).filter_by(id=provided_id).first()

            if event:
                event.title = data['title'].strip()
                event.start = start
                event.end = end
                event.backgroundColor = data.get('backgroundColor', event.backgroundColor)
                event.location = (data.get('location') or data.get('extendedProps', {}).get('location') or '').strip() or None
                event.description = (data.get('description') or data.get('extendedProps', {}).get('description') or '').strip() or None
                event.isTask = False
                event.taskStatus = None
            else:
                event = Event(
                    title=data['title'].strip(),
                    start=start,
                    end=end,
                    backgroundColor=data.get('backgroundColor', '#6366f1'),
                    location=data.get('location', data.get('extendedProps', {}).get('location', '')).strip() or None,
                    description=data.get('description', data.get('extendedProps', {}).get('description', '')).strip() or None,
                    owner=current_user.email
                )
        else:
            return jsonify({'error': f'Invalid data type: {dtype}'}), 400
        # Add new events to the session; existing events are already tracked
        if event.id is None:
            db.session.add(event)
            db.session.commit()
            return jsonify(event.to_dict()), 201
        else:
            db.session.commit()
            return jsonify(event.to_dict()), 200
    
    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({'error': 'Internal Server Error'}), 500


@app.route('/update-task-status', methods=['POST'])
@login_required
def update_task_status():
    """Updates the status of a task (request should only contain the task ID and new status)."""
    try:
        data = request.get_json() or {}
        task_id = data.get('id')
        new_status = data.get('status')

        if not task_id:
            return jsonify({'error': 'Task ID is required'}), 400
        if not new_status:
            return jsonify({'error': 'Status is required'}), 400

        valid_statuses = [status.value for status in TaskStatus]
        if new_status not in valid_statuses:
            return jsonify({'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'}), 400

        task = db.session.query(Event).filter_by(id=task_id, isTask=True, owner=current_user.email).first()
        if not task:
            return jsonify({'error': 'Task not found'}), 404

        task.taskStatus = TaskStatus(new_status)
        db.session.commit()
        return jsonify(task.to_dict()), 200

    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({'error': 'Internal Server Error'}), 500


@app.route('/delete-event', methods=['POST'])
@login_required
def delete():
    """Delete an event/task from the database."""
    try:
        data = request.get_json() or {}
        event_id = data.get('id')

        if not event_id:
            return jsonify({'error': 'Event ID is required'}), 400

        event = db.session.query(Event).filter_by(id=event_id, owner=current_user.email).first()
        if not event:
            return jsonify({'error': 'Event not found'}), 404

        db.session.delete(event)
        db.session.commit()
        return jsonify({'message': 'Event deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({'error': 'Internal Server Error'}), 500