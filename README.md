# BetterCAS

## Description
A web app developed for the CITS3403 Agile Web Development group project. This is a calendar and task reminder tool for university assignments and studying, featuring:
- To-do list
- Calendar views
- Sharing calendars with friends

## List of Group Members
| UWA ID   | Name               | GitHub Username |
|----------|--------------------|-----------------|
| 23810308 | Allan Wu           | allanwupi       |
| 24272225 | Aidan Mills        | Rangarade       |
| 24367195 | Hongshen Zheng     | hz7443          |
| 24227546 | Tashan Kirubagaran | tashan-kiru     |

## Instructions

### Launching the App
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

Then open the local Flask URL:

```text
http://127.0.0.1:5000/
```

Note: For local development, `SECRET_KEY` has a fallback value in `app/config.py`. For deployment, set a real secret key with:

```bash
export MYCAL_SECRET_KEY="your-secret-key-here"
```

### Tests
Not done yet
