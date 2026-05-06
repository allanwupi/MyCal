// Wrapper for server request to update event time and/or duration, given a JSON payload
async function updateEventInfo(isTask, payload, calendar) {
  const route = isTask ? '/save/task' : '/save/event';
  fetch(route, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  })
  .then(response => {
    if (!response.ok) {
      return response.json().then(data => {
        throw new Error(data.error || 'Failed to save event');
      });
    }
    // Refresh calendar to ensure server values are shown
    calendar.refetchEvents();
  })
  .catch(error => {
    alert('Error saving event: ' + error.message);
    calendar.refetchEvents();
  });
}

// Helper function to convert FullCalendar Event object into plain JSON
function eventToJson(event, isTask) {
  // Note: we need to format dates as ISO strings (local time, not UTC) to preserve the original time.
  function formatLocalISO(date) {
    if (!date) return null;
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');
    return `${year}-${month}-${day}T${hours}:${minutes}:${seconds}`;
  }
  const payload = {
    id: event.id,
    title: event.title,
    start: event.start ? formatLocalISO(event.start) : null,
    end: isTask ? (event.start ? formatLocalISO(event.start) : null) : (event.end ? formatLocalISO(event.end) : null),
    location: event.extendedProps && event.extendedProps.location ? event.extendedProps.location : '',
    description: event.extendedProps && event.extendedProps.description ? event.extendedProps.description : '',
    backgroundColor: event.backgroundColor || (event.extendedProps && event.extendedProps.backgroundColor) || '#6366f1',
    isTask: isTask,
    taskStatus: isTask ? event.extendedProps.taskStatus : undefined
  };
  return payload;
}

document.addEventListener('DOMContentLoaded', function () {
  const calendarEl = document.getElementById('calendar');
  const tooltip = document.getElementById('eventTooltip');

  const openEventModalBtn = document.getElementById('openEventModalBtn');
  const saveEventBtn = document.getElementById('saveEventBtn');

  const eventTitleInput = document.getElementById('eventTitle');
  const eventStartInput = document.getElementById('eventStart');
  const eventEndInput = document.getElementById('eventEnd');
  const eventLocationInput = document.getElementById('eventLocation');
  const eventDescriptionInput = document.getElementById('eventDescription');
  const eventIsTaskInput = document.getElementById('eventIsTask');

  const addEventModalElement = document.getElementById('addEventModal');
  const addEventModal = new bootstrap.Modal(addEventModalElement);

  const calendar = new FullCalendar.Calendar(calendarEl, {
    fixedWeekCount: false,
    initialView: 'dayGridMonth',
    height: 'auto',
    allDaySlot: false,
    headerToolbar: {
      left: 'prev,next today',
      center: 'title',
      right: 'dayGridMonth,timeGridWeek,timeGridDay'
    },
    selectable: true,
    editable: true,
    nowIndicator: true,
    events: '/get-events',

    // Allow user to drag, drop and resize events on the calendar, updating the database.
    eventChange: function(changeInfo) {
      const event = changeInfo.event;
      const isTask = event.extendedProps.isTask;
      const payload = eventToJson(event, isTask);
      updateEventInfo(isTask, payload, calendar);
    },

    eventMouseEnter: function(info) {
      const event = info.event;
      const start = event.start
        ? event.start.toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' })
        : 'N/A';
      const end = event.end // FullCalendar will set the end date to None if it is the same as the start date
        ? event.end.toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' })
        : start;
      const location = event.extendedProps.location || 'No location provided';
      const description = event.extendedProps.description || 'No description provided';
      if (event.extendedProps.isTask) {
        tooltip.innerHTML = `
          <strong>${event.title}</strong>
          <div><span class="tooltip-label">Due:</span> ${end}</div> 
          <div><span class="tooltip-label">Status:</span> ${event.extendedProps.taskStatus}</div>
        `;
      } else {
        tooltip.innerHTML = `
        <strong>${event.title}</strong>
        <div><span class="tooltip-label">Start:</span> ${start}</div>
        <div><span class="tooltip-label">End:</span> ${end}</div>
        <div><span class="tooltip-label">Location:</span> ${location}</div>
        <div><span class="tooltip-label">Details:</span> ${description}</div>
      `;
      }
      tooltip.style.display = 'block';
    },
    eventMouseLeave: function() {
      tooltip.style.display = 'none';
    }
  });

  calendar.render();

  calendarEl.addEventListener('mousemove', function(e) {
    tooltip.style.left = (e.pageX + 16) + 'px';
    tooltip.style.top = (e.pageY + 16) + 'px';
  });

  openEventModalBtn.addEventListener('click', () => {
    eventTitleInput.value = '';
    eventStartInput.value = '';
    eventEndInput.value = '';
    eventLocationInput.value = '';
    eventDescriptionInput.value = '';
    addEventModal.show();
  });

  // Automatically fill in event end times upon receiving start time input
  eventStartInput.addEventListener('input', () => {
    if (!eventEndInput.value || eventEndInput.value < eventStartInput.value) {
      eventEndInput.value = eventStartInput.value;
    }
  });

  saveEventBtn.addEventListener('click', () => {
    const title = eventTitleInput.value.trim();
    const start = eventStartInput.value;
    const end = eventEndInput.value;
    const location = eventLocationInput.value.trim();
    const description = eventDescriptionInput.value.trim();
    const isTask = eventIsTaskInput.checked;

    // Client-side validation
    if (!title || !start || !end) {
      alert('Please enter the event title, start and end dates/times.');
      return;
    }
    if (!isTask && end <= start) {
      alert('End date/time must be after the start date/time.');
      return;
    }

    // Disable button during submission
    saveEventBtn.disabled = true;
    saveEventBtn.textContent = 'Saving...';

    // Send to server for validation and storage
    let route = isTask ? '/save/task' : '/save/event';

    const payload = {
      title: title,
      start: start,
      end: end,
      location: location,
      description: description,
      backgroundColor: '#6366f1',
      isTask: isTask,
      taskStatus: isTask ? 'Not Started' : undefined
    };

    updateEventInfo(isTask, payload, calendar);
    // Re-enable button and hide menu
    saveEventBtn.disabled = false;
    saveEventBtn.textContent = 'Save Event';
    addEventModal.hide();

  });
});