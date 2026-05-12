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


@app.template_filter('format_datetime')
def format_datetime(dt):
    # "o-d", "%-I" is not supported on Windows, so we need to remove leading zeros manually
    d = dt.strftime("%d").lstrip("0")
    I = dt.strftime("%I").lstrip("0")
    return f'{dt.strftime("%b")} {d}, {dt.strftime("%Y")} {I}:{dt.strftime("%M")} {dt.strftime("%p")}'
    # equivalent to strftime("%b %-d, %Y %-I:%M %p") on Unix-based systems


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
        'to-do-list.html',
        tasks=tasks,
        todo_active=True
    )


@app.route('/friends', methods=['GET'])
@login_required
def friends_page():
    return render_template('friends.html', friends_active=True)


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
