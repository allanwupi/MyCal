# MyCal

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
flask db upgrade
```

Set a secret key:
```bash
export MYCAL_SECRET_KEY="your-secret-key-here"
```

For Windows powershell run instead:
```powershell
$Env:MYCAL_SECRET_KEY="your-secret-key-here"
```

Run the app:

```bash
flask --app mycal run
```

Then open the local Flask URL:

```text
http://127.0.0.1:5000/
```

### Tests
Run unit tests:

```bash
python -m unittest tests.unit_tests -v
```

Run Selenium tests:

```bash
python -m unittest tests.selenium_tests -v
```
