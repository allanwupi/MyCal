document.addEventListener('DOMContentLoaded', function () {
  const todoInput = document.getElementById('todoInput');
  const todoDate = document.getElementById('todoDate');
  const addTodoBtn = document.getElementById('addTodoBtn');
  const todoList = document.getElementById('todoList');
  const filterButtons = document.querySelectorAll('.filter-buttons button');

  // TODO: BACKEND
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

    //const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    //tooltipTriggerList.forEach(el => new bootstrap.Tooltip(el));
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