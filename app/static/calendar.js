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

  const addEventModalElement = document.getElementById('addEventModal');
  const addEventModal = new bootstrap.Modal(addEventModalElement);

  const calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: 'dayGridMonth',
    height: 'auto',
    headerToolbar: {
      left: 'prev,next today',
      center: 'title',
      right: 'dayGridMonth,timeGridWeek,timeGridDay'
    },
    selectable: true,
    editable: true,
    nowIndicator: true,
    events: '/get-events',

    eventMouseEnter: function(info) {
      const event = info.event;

      const start = event.start
        ? event.start.toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' })
        : 'N/A';

      const end = event.end
        ? event.end.toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' })
        : 'N/A';

      const location = event.extendedProps.location || 'No location provided';
      const description = event.extendedProps.description || 'No description provided';

      tooltip.innerHTML = `
        <strong>${event.title}</strong>
        <div><span class="tooltip-label">Start:</span> ${start}</div>
        <div><span class="tooltip-label">End:</span> ${end}</div>
        <div><span class="tooltip-label">Location:</span> ${location}</div>
        <div><span class="tooltip-label">Details:</span> ${description}</div>
      `;
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

  saveEventBtn.addEventListener('click', () => {
    const title = eventTitleInput.value.trim();
    const start = eventStartInput.value;
    const end = eventEndInput.value;
    const location = eventLocationInput.value.trim();
    const description = eventDescriptionInput.value.trim();

    // Client-side validation
    if (!title || !start) {
      alert('Please enter at least an event title and start date/time.');
      return;
    }

    if (end && end < start) {
      alert('End date/time cannot be before the start date/time.');
      return;
    }

    // Disable button during submission
    saveEventBtn.disabled = true;
    saveEventBtn.textContent = 'Saving...';

    // Send to server for validation and storage
    fetch('/save-event', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        title: title,
        start: start,
        end: end || null,
        location: location,
        description: description,
        backgroundColor: '#6366f1'
      })
    })
    .then(response => {
      if (!response.ok) {
        return response.json().then(data => {
          throw new Error(data.error || 'Failed to save event');
        });
      }
      return response.json();
    })
    .then(eventData => {
      // Server validation passed, add to calendar
      calendar.addEvent({
        id: eventData.id,
        title: eventData.title,
        start: eventData.start,
        end: eventData.end,
        backgroundColor: eventData.backgroundColor,
        extendedProps: eventData.extendedProps
      });
      addEventModal.hide();
    })
    .catch(error => {
      alert('Error saving event: ' + error.message);
    })
    .finally(() => {
      // Re-enable button
      saveEventBtn.disabled = false;
      saveEventBtn.textContent = 'Save Event';
    });
  });
});