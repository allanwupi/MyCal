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

    calendar.refetchEvents();
  })
  .catch(error => {
    alert('Error saving event: ' + error.message);
    calendar.refetchEvents();
  });
}

// Delete event from calendar and database
async function deleteEvent(event, calendar, eventDetailsModal) {
  const confirmed = confirm(`Are you sure you want to delete "${event.title}"?`);

  if (!confirmed) {
    return;
  }

  fetch('/delete-event', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ id: event.id })
  })
  .then(response => {
    if (!response.ok) {
      return response.json().then(data => {
        throw new Error(data.error || 'Failed to delete event');
      });
    }

    event.remove();
    eventDetailsModal.hide();
  })
  .catch(error => {
    alert('Error deleting event: ' + error.message);
    calendar.refetchEvents();
  });
}

// Helper function to convert FullCalendar Event object into plain JSON
function eventToJson(event, isTask) {
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

  return {
    id: event.id,
    title: event.title,
    start: event.start ? formatLocalISO(event.start) : null,
    end: isTask
      ? (event.start ? formatLocalISO(event.start) : null)
      : (event.end ? formatLocalISO(event.end) : null),
    location: event.extendedProps && event.extendedProps.location ? event.extendedProps.location : '',
    description: event.extendedProps && event.extendedProps.description ? event.extendedProps.description : '',
    backgroundColor: event.backgroundColor || (event.extendedProps && event.extendedProps.backgroundColor) || '#6366f1',
    isTask: isTask,
    taskStatus: isTask ? event.extendedProps.taskStatus : undefined
  };
}

function formatDisplayDate(date) {
  if (!date) return 'N/A';

  return date.toLocaleString([], {
    dateStyle: 'medium',
    timeStyle: 'short'
  });
}

document.addEventListener('DOMContentLoaded', function () {
  const CALENDAR_HEIGHT_RATIO = 0.9;

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

  const eventDetailsModalElement = document.getElementById('eventDetailsModal');
  const eventDetailsModal = new bootstrap.Modal(eventDetailsModalElement);

  const detailsTitle = document.getElementById('detailsTitle');
  const detailsStart = document.getElementById('detailsStart');
  const detailsEnd = document.getElementById('detailsEnd');
  const detailsLocation = document.getElementById('detailsLocation');
  const detailsDescription = document.getElementById('detailsDescription');
  const detailsTaskStatusWrapper = document.getElementById('detailsTaskStatusWrapper');
  const detailsTaskStatus = document.getElementById('detailsTaskStatus');
  const deleteEventBtn = document.getElementById('deleteEventBtn');

  let selectedEvent = null;

  const calendar = new FullCalendar.Calendar(calendarEl, {
    fixedWeekCount: false,
    initialView: 'dayGridMonth',
    height: window.innerHeight * CALENDAR_HEIGHT_RATIO,
    scrollTime: '08:00:00',
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

    eventChange: function(changeInfo) {
      const event = changeInfo.event;
      const isTask = event.extendedProps.isTask;
      const payload = eventToJson(event, isTask);

      updateEventInfo(isTask, payload, calendar);
    },

    // Hover still shows quick event details
    eventMouseEnter: function(info) {
      const event = info.event;

      const start = formatDisplayDate(event.start);
      const end = event.end ? formatDisplayDate(event.end) : start;

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
    },

    // Click opens full details popup
    eventClick: function(info) {
      selectedEvent = info.event;

      const event = info.event;
      const start = formatDisplayDate(event.start);
      const end = event.end ? formatDisplayDate(event.end) : start;

      detailsTitle.textContent = event.title;
      detailsStart.textContent = start;
      detailsEnd.textContent = end;
      detailsLocation.textContent = event.extendedProps.location || 'No location provided';
      detailsDescription.textContent = event.extendedProps.description || 'No description provided';

      if (event.extendedProps.isTask) {
        detailsTaskStatusWrapper.style.display = 'block';
        detailsTaskStatus.textContent = event.extendedProps.taskStatus || 'No status provided';
      } else {
        detailsTaskStatusWrapper.style.display = 'none';
        detailsTaskStatus.textContent = '';
      }

      tooltip.style.display = 'none';
      eventDetailsModal.show();
    }
  });

  calendar.render();

  calendarEl.addEventListener('mousemove', function(e) {
    tooltip.style.left = (e.pageX + 16) + 'px';
    tooltip.style.top = (e.pageY + 16) + 'px';
  });

  window.addEventListener('resize', function() {
    calendar.setOption('height', window.innerHeight * CALENDAR_HEIGHT_RATIO);
  });

  deleteEventBtn.addEventListener('click', function() {
    if (selectedEvent) {
      deleteEvent(selectedEvent, calendar, eventDetailsModal);
    }
  });

  openEventModalBtn.addEventListener('click', () => {
    eventTitleInput.value = '';
    eventStartInput.value = '';
    eventEndInput.value = '';
    eventLocationInput.value = '';
    eventDescriptionInput.value = '';
    eventIsTaskInput.checked = false;

    addEventModal.show();
  });

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

    if (!title || !start || !end) {
      alert('Please enter the event title, start and end dates/times.');
      return;
    }

    if (!isTask && end <= start) {
      alert('End date/time must be after the start date/time.');
      return;
    }

    saveEventBtn.disabled = true;
    saveEventBtn.textContent = 'Saving...';

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

    saveEventBtn.disabled = false;
    saveEventBtn.textContent = 'Save Event';
    addEventModal.hide();
  });
});