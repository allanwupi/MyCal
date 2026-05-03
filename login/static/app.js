const sidebar = document.getElementById('sidebar');
const toggleSidebar = document.getElementById('toggleSidebar');

toggleSidebar.addEventListener('click', () => {
  sidebar.classList.toggle('collapsed');
});

const navItems = document.querySelectorAll('.nav-links li');
const sections = document.querySelectorAll('.section');

navItems.forEach(item => {
  item.addEventListener('click', () => {
    navItems.forEach(nav => nav.classList.remove('active'));
    sections.forEach(section => section.classList.remove('active'));

    item.classList.add('active');
    document.getElementById(item.dataset.section).classList.add('active');
  });
});

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

  const todoInput = document.getElementById('todoInput');
  const todoDate = document.getElementById('todoDate');
  const addTodoBtn = document.getElementById('addTodoBtn');
  const todoList = document.getElementById('todoList');
  const filterButtons = document.querySelectorAll('.filter-buttons button');

  let tasks = [
    {
      id: 1,
      title: 'Finish assignment',
      dueDate: '2026-04-25',
      status: 'In Progress'
    },
    {
      id: 2,
      title: 'Go to gym',
      dueDate: '2026-04-22',
      status: 'Not Started'
    },
    {
      id: 3,
      title: 'Study for test',
      dueDate: '2026-04-20',
      status: 'Completed'
    }
  ];

  let currentFilter = 'all';

  function formatDate(dateString) {
    if (!dateString) return 'No due date';
    const date = new Date(dateString + 'T00:00:00');
    return date.toLocaleDateString([], {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  }

  function getBadgeClass(status) {
    if (status === 'Not Started') return 'bg-info text-dark';
    if (status === 'In Progress') return 'bg-warning text-dark';
    if (status === 'Completed') return 'bg-success';
    return 'bg-secondary';
  }

  function renderTasks() {
    todoList.innerHTML = '';

    let filteredTasks = tasks;

    if (currentFilter === 'pending') {
      filteredTasks = tasks.filter(task => task.status !== 'Completed');
    } else if (currentFilter === 'completed') {
      filteredTasks = tasks.filter(task => task.status === 'Completed');
    }

    if (filteredTasks.length === 0) {
      todoList.innerHTML = '<li class="empty-state">No tasks found.</li>';
      return;
    }

    filteredTasks.forEach(task => {
      const li = document.createElement('li');
      li.className = 'task-item d-flex justify-content-between align-items-center';
      li.setAttribute('data-bs-toggle', 'tooltip');
      li.setAttribute('title', `Task: ${task.title} | Due: ${formatDate(task.dueDate)} | Status: ${task.status}`);

      li.innerHTML = `
        <div class="task-left">
          <p class="fw-bold ${task.status === 'Completed' ? 'text-decoration-line-through text-muted' : ''}">
            ${task.title}
          </p>
          <small>Due: ${formatDate(task.dueDate)}</small>
        </div>

        <div class="d-flex gap-2 align-items-center flex-wrap justify-content-end">
          <div class="dropdown">
            <button class="btn btn-sm btn-outline-secondary dropdown-toggle rounded-pill px-3" data-bs-toggle="dropdown">
              Status
            </button>
            <ul class="dropdown-menu shadow border-0 rounded-4 p-2">
              <li><a class="dropdown-item rounded-3 status-option" href="#" data-id="${task.id}" data-status="Not Started"><span class="badge bg-info text-dark">Not Started</span></a></li>
              <li><a class="dropdown-item rounded-3 status-option" href="#" data-id="${task.id}" data-status="In Progress"><span class="badge bg-warning text-dark">In Progress</span></a></li>
              <li><a class="dropdown-item rounded-3 status-option" href="#" data-id="${task.id}" data-status="Completed"><span class="badge bg-success">Completed</span></a></li>
            </ul>
          </div>

          <span class="task-status-badge ${getBadgeClass(task.status)}">${task.status}</span>
          <button class="btn btn-danger btn-sm rounded-pill px-3 delete-task" data-id="${task.id}">Delete</button>
        </div>
      `;

      todoList.appendChild(li);
    });

    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipTriggerList.forEach(el => new bootstrap.Tooltip(el));
  }

  addTodoBtn.addEventListener('click', () => {
    const title = todoInput.value.trim();
    const dueDate = todoDate.value;

    if (title === '') {
      alert('Please enter a task.');
      return;
    }

    const newTask = {
      id: Date.now(),
      title: title,
      dueDate: dueDate,
      status: 'Not Started'
    };

    tasks.push(newTask);
    todoInput.value = '';
    todoDate.value = '';
    renderTasks();
  });

  todoList.addEventListener('click', (e) => {
    if (e.target.closest('.delete-task')) {
      const id = Number(e.target.closest('.delete-task').dataset.id);
      tasks = tasks.filter(task => task.id !== id);
      renderTasks();
    }

    if (e.target.closest('.status-option')) {
      e.preventDefault();
      const option = e.target.closest('.status-option');
      const id = Number(option.dataset.id);
      const newStatus = option.dataset.status;

      const task = tasks.find(task => task.id === id);
      if (task) {
        task.status = newStatus;
        renderTasks();
      }
    }
  });

  filterButtons.forEach(button => {
    button.addEventListener('click', () => {
      filterButtons.forEach(btn => btn.classList.remove('active-filter'));
      button.classList.add('active-filter');
      currentFilter = button.dataset.filter;
      renderTasks();
    });
  });

  renderTasks();
});