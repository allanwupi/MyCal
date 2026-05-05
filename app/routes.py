from flask import render_template, jsonify, request, url_for, redirect
from app import app, db
from app.models import Event
import icalendar

@app.route('/', methods=['GET']) # Replace this with a login page later

@app.route('/calendar', methods=['GET'])
def calendar():
    return render_template('calendar-page.html', calendar_active=True)

@app.route('/get-events', methods=['GET'])
def get_events():
    events = db.session.query(Event).all()
    return jsonify([event.to_dict() for event in events]), 200

@app.route('/todo', methods=['GET'])
def to_do_list():
    return render_template('todo-page.html', todo_active=True)

@app.route('/friends', methods=['GET'])
def friends():
    return render_template('friends-page.html', friends_active=True)

@app.route('/import', methods=['GET'])
def imported_calendars():
    return render_template('import-page.html', import_active=True)

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']

    if not file or not file.filename.endswith('.ics'):
        return {"error": "Invalid file"}, 400

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
                end=component.get('dtend').dt if component.get('dtend') else None
            )

            db.session.add(event)
            events.append(event)
            count += 1

    db.session.commit()

    return {"message": f"{count} events added"}

@app.route('/save-event', methods=['POST'])
def save_event():
    """Save a new event to the database with server-side validation."""
    try:
        data = request.get_json()
        
        # Server-side validation
        if not data.get('title') or not data['title'].strip():
            return jsonify({'error': 'Event title is required'}), 400
        
        if not data.get('start'):
            return jsonify({'error': 'Start date/time is required'}), 400
        
        try:
            from datetime import datetime
            start = datetime.fromisoformat(data['start'])
            end = datetime.fromisoformat(data['end']) if data.get('end') else None
            
            if end and end < start:
                return jsonify({'error': 'End date/time cannot be before start date/time'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid date/time format'}), 400
        
        # Create and save the event
        event = Event(
            title=data['title'].strip(),
            start=start,
            end=end or start,  # Default end to start if not provided
            backgroundColor=data.get('backgroundColor', '#6366f1'),
            location=data.get('location', '').strip() or None,
            description=data.get('description', '').strip() or None
        )  
        db.session.add(event)
        db.session.commit()
        return jsonify(event.to_dict()), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Server error: {str(e)}'}), 500