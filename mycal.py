from app import app

if __name__ == '__main__':
    app.run()

# TO-DO
# - Ability to delete events from the calendar and database
# - Implement loading tasks from the database and displaying in the to-do list page
# - Add functionality to mark task status and update the database accordingly
# - Login and user authentication system to associate events with specific users
# - Friend system: ability to view events owned by friends on the calendar view
# - Implement calendar import functionality (iCal files) - I think we can just use a library
# - IF TIME PERMITS: Add availability sharing and scheduling features for friends (e.g., find common free time slots)
# - for above: User inputs start/end time for availability, implement logic to find common free time slots among friends and display in calendar view