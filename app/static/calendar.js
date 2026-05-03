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
    events: [
      {
        title: 'Assignment Due',
        start: '2026-04-25T14:00:00',
        end: '2026-04-25T16:00:00',
        backgroundColor: '#6366f1',
        extendedProps: {
          location: 'UWA Library',
          description: 'Complete and submit the final assignment.'
        }
      },
      {
        title: 'Group Meeting',
        start: '2026-04-23T10:00:00',
        end: '2026-04-23T11:00:00',
        backgroundColor: '#3b82f6',
        extendedProps: {
          location: 'Engineering Building',
          description: 'Project discussion with team members.'
        }
      },
      {
        title: 'Gym Session',
        start: '2026-04-22T18:00:00',
        end: '2026-04-22T19:30:00',
        backgroundColor: '#8b5cf6',
        extendedProps: {
          location: 'Campus Gym',
          description: 'Strength workout and cardio session.'
        }
      }
    ],

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

    if (!title || !start) {
      alert('Please enter at least an event title and start date/time.');
      return;
    }

    if (end && end < start) {
      alert('End date/time cannot be before the start date/time.');
      return;
    }

    calendar.addEvent({
      title: title,
      start: start,
      end: end || null,
      backgroundColor: '#6366f1',
      extendedProps: {
        location: location || 'No location provided',
        description: description || 'No details provided'
      }
    });

    addEventModal.hide();
  });
});