# Authentication setup

This version integrates login/signup into the main Flask app.

## What changed

- Added Flask-Login setup in `app/__init__.py`
- Added a database-backed `User` model in `app/models.py`
- Added password hashing with Werkzeug, so raw passwords are not stored
- Added landing/login/signup page at `/`
- Added `/signup`, `/login`, and `/logout` routes
- Protected dashboard pages with `@login_required`
- Events and tasks are now saved with `owner=current_user.email`
- Calendar and to-do pages only load the logged-in user's own events/tasks

## Run locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Create the database tables:

```bash
flask --app mycal init-db
```

Run the app:

```bash
flask --app mycal run --debug
```

Then open the local Flask URL, usually:

```text
http://127.0.0.1:5000/
```

## Notes

For local development, `SECRET_KEY` has a fallback value in `app/config.py`. For deployment, set a real secret key with:

```bash
export MYCAL_SECRET_KEY="your-secret-key-here"
```
