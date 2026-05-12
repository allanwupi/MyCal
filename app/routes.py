from flask import flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import or_
from app import app, db
from app.models import Event, TaskStatus, User, Friendship
from datetime import datetime
import icalendar


def normalise_email(email):
    return (email or '').strip().lower()


def normalise_username(username):
    return (username or '').strip()


def parse_datetime(value):
    if not value:
        return None

    if isinstance(value, datetime):
        return value.replace(tzinfo=None)

    value = str(value).replace('Z', '+00:00')
    parsed = datetime.fromisoformat(value)

    return parsed.replace(tzinfo=None)


def parse_task_status(status):
    if status == TaskStatus.NOT_STARTED.value:
        return TaskStatus.NOT_STARTED
    if status == TaskStatus.IN_PROGRESS.value:
        return TaskStatus.IN_PROGRESS
    if status == TaskStatus.COMPLETED.value:
        return TaskStatus.COMPLETED

    return TaskStatus.NOT_STARTED


@app.template_filter('format_datetime')
def format_datetime(dt):
    d = dt.strftime("%d").lstrip("0")
    I = dt.strftime("%I").lstrip("0")
    return f'{dt.strftime("%b")} {d}, {dt.strftime("%Y")} {I}:{dt.strftime("%M")} {dt.strftime("%p")}'


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
        .filter(
            Event.owner == current_user.email,
            Event.isTask == True
        )
        .order_by(Event.start.asc())
        .all()
    )

    return render_template(
        'todo-page.html',
        tasks=tasks,
        todo_active=True
    )


@app.route('/friends', methods=['GET'])
@login_required
def friends():
    return render_template('friends-page.html', friends_active=True)


@app.route('/imported-calendars', methods=['GET'])
@login_required
def imported_calendars():
    return render_template('import-page.html', import_active=True)


# =========================
# CALENDAR / TASK ROUTES
# =========================

@app.route('/get-events', methods=['GET'])
@login_required
def get_events_old():
    events = (
        db.session.query(Event)
        .filter(Event.owner == current_user.email)
        .all()
    )

    return jsonify([event.to_dict() for event in events]), 200


@app.route('/api/events', methods=['GET'])
@login_required
def get_events():
    events = (
        db.session.query(Event)
        .filter(Event.owner == current_user.email)
        .all()
    )

    return jsonify([event.to_dict() for event in events]), 200


@app.route('/save/event', methods=['POST'])
@login_required
def save_event():
    data = request.get_json() or {}

    title = data.get('title')
    start = data.get('start')
    end = data.get('end') or start
    location = data.get('location')
    description = data.get('description')
    background_color = data.get('backgroundColor') or '#6366f1'
    event_id = data.get('id')

    if not title or not start or not end:
        return jsonify({'error': 'Title, start, and end are required'}), 400

    try:
        start_dt = parse_datetime(start)
        end_dt = parse_datetime(end)
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400

    if event_id:
        event = (
            db.session.query(Event)
            .filter_by(id=event_id, owner=current_user.email)
            .first()
        )

        if not event:
            return jsonify({'error': 'Event not found'}), 404

        event.title = title
        event.start = start_dt
        event.end = end_dt
        event.location = location
        event.description = description
        event.backgroundColor = background_color
        event.isTask = False
        event.taskStatus = None
    else:
        event = Event(
            title=title,
            start=start_dt,
            end=end_dt,
            backgroundColor=background_color,
            location=location,
            description=description,
            isTask=False,
            taskStatus=None,
            owner=current_user.email
        )

        db.session.add(event)

    db.session.commit()

    return jsonify(event.to_dict()), 200


@app.route('/save/task', methods=['POST'])
@login_required
def save_task():
    data = request.get_json() or {}

    title = data.get('title')
    start = data.get('start')
    end = data.get('end') or start
    background_color = data.get('backgroundColor') or '#6366f1'
    task_status = parse_task_status(data.get('taskStatus'))
    event_id = data.get('id')

    if not title or not start:
        return jsonify({'error': 'Title and due date are required'}), 400

    try:
        start_dt = parse_datetime(start)
        end_dt = parse_datetime(end)
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400

    if event_id:
        task = (
            db.session.query(Event)
            .filter_by(id=event_id, owner=current_user.email)
            .first()
        )

        if not task:
            return jsonify({'error': 'Task not found'}), 404

        task.title = title
        task.start = start_dt
        task.end = end_dt
        task.backgroundColor = background_color
        task.isTask = True
        task.taskStatus = task_status
    else:
        task = Event(
            title=title,
            start=start_dt,
            end=end_dt,
            backgroundColor=background_color,
            isTask=True,
            taskStatus=task_status,
            owner=current_user.email
        )

        db.session.add(task)

    db.session.commit()

    return jsonify(task.to_dict()), 200


@app.route('/delete-event', methods=['POST'])
@login_required
def delete_event_old():
    data = request.get_json() or {}
    event_id = data.get('id')

    if not event_id:
        return jsonify({'error': 'Event ID is required'}), 400

    event = (
        db.session.query(Event)
        .filter_by(id=event_id, owner=current_user.email)
        .first()
    )

    if not event:
        return jsonify({'error': 'Event not found'}), 404

    db.session.delete(event)
    db.session.commit()

    return jsonify({'message': 'Event deleted successfully'}), 200


@app.route('/update-task-status', methods=['POST'])
@login_required
def update_task_status():
    data = request.get_json() or {}
    task_id = data.get('id')
    status = data.get('status')

    if not task_id or not status:
        return jsonify({'error': 'Task ID and status are required'}), 400

    task = (
        db.session.query(Event)
        .filter_by(id=task_id, owner=current_user.email, isTask=True)
        .first()
    )

    if not task:
        return jsonify({'error': 'Task not found'}), 404

    task.taskStatus = parse_task_status(status)
    db.session.commit()

    return jsonify(task.to_dict()), 200


@app.route('/api/events', methods=['POST'])
@login_required
def create_event():
    data = request.get_json() or {}

    if data.get('isTask'):
        return save_task()

    return save_event()


@app.route('/api/events/<int:event_id>', methods=['PUT'])
@login_required
def update_event(event_id):
    event = (
        db.session.query(Event)
        .filter_by(id=event_id, owner=current_user.email)
        .first()
    )

    if not event:
        return jsonify({'error': 'Event not found'}), 404

    data = request.get_json() or {}

    if 'title' in data:
        event.title = data['title']

    if 'start' in data:
        event.start = parse_datetime(data['start'])

    if 'end' in data:
        event.end = parse_datetime(data['end'])

    if 'backgroundColor' in data:
        event.backgroundColor = data['backgroundColor']

    if 'location' in data:
        event.location = data['location']

    if 'description' in data:
        event.description = data['description']

    if 'isTask' in data:
        event.isTask = bool(data['isTask'])

    if 'taskStatus' in data and data['taskStatus']:
        event.taskStatus = parse_task_status(data['taskStatus'])

    db.session.commit()

    return jsonify(event.to_dict()), 200


@app.route('/api/events/<int:event_id>', methods=['DELETE'])
@login_required
def delete_event(event_id):
    event = (
        db.session.query(Event)
        .filter_by(id=event_id, owner=current_user.email)
        .first()
    )

    if not event:
        return jsonify({'error': 'Event not found'}), 404

    db.session.delete(event)
    db.session.commit()

    return jsonify({'message': 'Event deleted'}), 200


# =========================
# IMPORT CALENDAR ROUTE
# =========================

@app.route('/upload', methods=['POST'])
@login_required
def upload_calendar():
    uploaded_file = request.files.get('file')

    if not uploaded_file:
        return jsonify({'error': 'No file uploaded'}), 400

    if not uploaded_file.filename.endswith('.ics'):
        return jsonify({'error': 'Please upload a valid .ics file'}), 400

    try:
        calendar_data = icalendar.Calendar.from_ical(uploaded_file.read())
    except Exception:
        return jsonify({'error': 'Could not read .ics file'}), 400

    imported_count = 0

    for component in calendar_data.walk():
        if component.name != 'VEVENT':
            continue

        title = str(component.get('summary', 'Imported Event'))

        start_value = component.get('dtstart')
        end_value = component.get('dtend')

        if not start_value:
            continue

        start_dt = start_value.dt
        end_dt = end_value.dt if end_value else start_dt

        if not isinstance(start_dt, datetime):
            start_dt = datetime.combine(start_dt, datetime.min.time())

        if not isinstance(end_dt, datetime):
            end_dt = datetime.combine(end_dt, datetime.min.time())

        start_dt = start_dt.replace(tzinfo=None)
        end_dt = end_dt.replace(tzinfo=None)

        location = str(component.get('location', ''))
        description = str(component.get('description', ''))

        event = Event(
            title=title,
            start=start_dt,
            end=end_dt,
            backgroundColor='#6366f1',
            location=location,
            description=description,
            isTask=False,
            taskStatus=None,
            owner=current_user.email
        )

        db.session.add(event)
        imported_count += 1

    db.session.commit()

    return jsonify({
        'message': f'Successfully imported {imported_count} events',
        'imported_count': imported_count
    }), 200


# =========================
# FRIENDS API ROUTES
# =========================

@app.route('/api/users/search', methods=['GET'])
@login_required
def search_users():
    username = (request.args.get('username') or '').strip()

    if not username:
        return jsonify({'error': 'Username is required'}), 400

    users = (
        db.session.query(User)
        .filter(
            User.username.ilike(f'%{username}%'),
            User.email != current_user.email
        )
        .limit(10)
        .all()
    )

    results = []

    for user in users:
        already_friends = db.session.query(Friendship).filter(
            or_(
                (Friendship.requester_email == current_user.email) &
                (Friendship.addressee_email == user.email),

                (Friendship.requester_email == user.email) &
                (Friendship.addressee_email == current_user.email)
            )
        ).first()

        results.append({
            'email': user.email,
            'username': user.username,
            'already_friends': already_friends is not None
        })

    return jsonify(results), 200


@app.route('/api/friends/add', methods=['POST'])
@login_required
def add_friend():
    data = request.get_json() or {}
    username = (data.get('username') or '').strip()

    if not username:
        return jsonify({'error': 'Username is required'}), 400

    friend = db.session.query(User).filter_by(username=username).first()

    if not friend:
        return jsonify({'error': 'User not found'}), 404

    if friend.email == current_user.email:
        return jsonify({'error': 'You cannot add yourself as a friend'}), 400

    existing_friendship = db.session.query(Friendship).filter(
        or_(
            (Friendship.requester_email == current_user.email) &
            (Friendship.addressee_email == friend.email),

            (Friendship.requester_email == friend.email) &
            (Friendship.addressee_email == current_user.email)
        )
    ).first()

    if existing_friendship:
        return jsonify({'error': 'You are already friends with this user'}), 400

    friendship = Friendship(
        requester_email=current_user.email,
        addressee_email=friend.email
    )

    db.session.add(friendship)
    db.session.commit()

    return jsonify({
        'message': f'{friend.username} has been added as a friend',
        'friendship': friendship.to_dict()
    }), 201


@app.route('/api/friends', methods=['GET'])
@login_required
def get_friends():
    friendships = db.session.query(Friendship).filter(
        or_(
            Friendship.requester_email == current_user.email,
            Friendship.addressee_email == current_user.email
        )
    ).all()

    friends = []

    for friendship in friendships:
        if friendship.requester_email == current_user.email:
            friend = friendship.addressee
        else:
            friend = friendship.requester

        friends.append({
            'friendship_id': friendship.id,
            'email': friend.email,
            'username': friend.username,
            'created_at': friendship.created_at.isoformat()
        })

    return jsonify(friends), 200


@app.route('/api/friends/remove', methods=['POST'])
@login_required
def remove_friend():
    data = request.get_json() or {}
    username = (data.get('username') or '').strip()

    if not username:
        return jsonify({'error': 'Username is required'}), 400

    friend = db.session.query(User).filter_by(username=username).first()

    if not friend:
        return jsonify({'error': 'User not found'}), 404

    friendship = db.session.query(Friendship).filter(
        or_(
            (Friendship.requester_email == current_user.email) &
            (Friendship.addressee_email == friend.email),

            (Friendship.requester_email == friend.email) &
            (Friendship.addressee_email == current_user.email)
        )
    ).first()

    if not friendship:
        return jsonify({'error': 'Friendship not found'}), 404

    db.session.delete(friendship)
    db.session.commit()

    return jsonify({
        'message': f'{friend.username} has been removed'
    }), 200