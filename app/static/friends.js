const mockUsers = ["rayhan", "mohammad", "alex", "sarah", "john", "emma"];

let friends = ["rayhan", "mohammad", "alex"];
let selectedFriends = [];
let availabilityCalendar = null;

const mockEvents = {
  you: [
    { title: "You busy", start: "2026-05-04T10:00:00", end: "2026-05-04T12:00:00" },
    { title: "You busy", start: "2026-05-06T14:00:00", end: "2026-05-06T16:00:00" }
  ],
  rayhan: [
    { title: "Rayhan busy", start: "2026-05-04T13:00:00", end: "2026-05-04T15:00:00" },
    { title: "Rayhan busy", start: "2026-05-07T09:00:00", end: "2026-05-07T11:00:00" }
  ],
  mohammad: [
    { title: "Mohammad busy", start: "2026-05-05T11:00:00", end: "2026-05-05T13:00:00" },
    { title: "Mohammad busy", start: "2026-05-06T15:00:00", end: "2026-05-06T17:00:00" }
  ],
  alex: [
    { title: "Alex busy", start: "2026-05-04T09:00:00", end: "2026-05-04T10:30:00" },
    { title: "Alex busy", start: "2026-05-08T12:00:00", end: "2026-05-08T14:00:00" }
  ]
};

document.addEventListener("DOMContentLoaded", () => {
  setupFriendSearch();
  renderFriends();
  renderSelectedFriends();
  setupAvailabilityCalendar();

  document
    .getElementById("compareFriendsBtn")
    .addEventListener("click", updateAvailabilityCalendar);
});

function setupFriendSearch() {
  const input = document.getElementById("friendSearchInput");
  const results = document.getElementById("friendSearchResults");

  input.addEventListener("input", () => {
    const query = input.value.trim().toLowerCase();
    results.innerHTML = "";

    if (!query) return;

    const matches = mockUsers.filter(
      user => user.includes(query) && !friends.includes(user)
    );

    if (matches.length === 0) {
      results.innerHTML = `<p class="friends-muted">No users found.</p>`;
      return;
    }

    matches.forEach(user => {
      const row = document.createElement("div");
      row.className = "friend-row";
      row.innerHTML = `
        <span>@${user}</span>
        <button class="friends-small-btn">Add</button>
      `;

      row.querySelector("button").addEventListener("click", () => {
        friends.push(user);
        input.value = "";
        results.innerHTML = "";
        renderFriends();
      });

      results.appendChild(row);
    });
  });
}

function renderFriends() {
  const list = document.getElementById("friendsList");
  list.innerHTML = "";

  if (friends.length === 0) {
    list.innerHTML = `<p class="friends-muted">No friends added yet.</p>`;
    return;
  }

  friends.forEach(friend => {
    const row = document.createElement("div");
    row.className = "friend-row";

    row.innerHTML = `
      <span>@${friend}</span>
      <button class="friends-small-btn">Select</button>
    `;

    row.querySelector("button").addEventListener("click", () => {
      selectFriend(friend);
    });

    list.appendChild(row);
  });
}

function selectFriend(friend) {
  if (selectedFriends.includes(friend)) return;

  if (selectedFriends.length >= 3) {
    alert("You can only select up to 3 friends.");
    return;
  }

  selectedFriends.push(friend);
  renderSelectedFriends();
}

function renderSelectedFriends() {
  const list = document.getElementById("selectedFriendsList");
  list.innerHTML = "";

  if (selectedFriends.length === 0) {
    list.innerHTML = `<p class="friends-muted">No friends selected yet.</p>`;
    return;
  }

  selectedFriends.forEach(friend => {
    const row = document.createElement("div");
    row.className = "friend-row selected";

    row.innerHTML = `
      <span>@${friend}</span>
      <button class="friends-remove-btn">Remove</button>
    `;

    row.querySelector("button").addEventListener("click", () => {
      selectedFriends = selectedFriends.filter(item => item !== friend);
      renderSelectedFriends();
      updateAvailabilityCalendar(false);
    });

    list.appendChild(row);
  });
}

function setupAvailabilityCalendar() {
  const calendarElement = document.getElementById("friendsAvailabilityCalendar");

  availabilityCalendar = new FullCalendar.Calendar(calendarElement, {
    initialView: "timeGridWeek",
    allDaySlot: false,
    slotMinTime: "08:00:00",
    slotMaxTime: "20:00:00",
    height: "auto",
    nowIndicator: true,
    headerToolbar: {
      left: "prev,next today",
      center: "title",
      right: "timeGridWeek"
    },
    events: []
  });

  availabilityCalendar.render();
}

function updateAvailabilityCalendar(showAlert = true) {
  if (selectedFriends.length === 0) {
    availabilityCalendar.removeAllEvents();

    if (showAlert) {
      alert("Select at least one friend first.");
    }

    return;
  }

  const usersToCompare = ["you", ...selectedFriends];
  const busyEvents = [];

  usersToCompare.forEach(user => {
    const events = mockEvents[user] || [];

    events.forEach(event => {
      busyEvents.push({
        title: event.title,
        start: event.start,
        end: event.end,
        backgroundColor: "#dc3545",
        borderColor: "#dc3545",
        textColor: "#ffffff"
      });
    });
  });

  const freeEvents = generateFreeTimeBlocks(busyEvents);

  availabilityCalendar.removeAllEvents();

  [...freeEvents, ...busyEvents].forEach(event => {
    availabilityCalendar.addEvent(event);
  });
}

function generateFreeTimeBlocks(busyEvents) {
  const freeBlocks = [];

  const weekDays = [
    "2026-05-04",
    "2026-05-05",
    "2026-05-06",
    "2026-05-07",
    "2026-05-08"
  ];

  weekDays.forEach(day => {
    const dayStart = new Date(`${day}T08:00:00`);
    const dayEnd = new Date(`${day}T20:00:00`);

    const dayBusy = busyEvents
      .filter(event => event.start.startsWith(day))
      .map(event => ({
        start: new Date(event.start),
        end: new Date(event.end)
      }))
      .sort((a, b) => a.start - b.start);

    let currentFreeStart = dayStart;

    dayBusy.forEach(busy => {
      if (busy.start > currentFreeStart) {
        freeBlocks.push({
          title: "Everyone free",
          start: currentFreeStart.toISOString(),
          end: busy.start.toISOString(),
          backgroundColor: "#198754",
          borderColor: "#198754",
          textColor: "#ffffff"
        });
      }

      if (busy.end > currentFreeStart) {
        currentFreeStart = busy.end;
      }
    });

    if (currentFreeStart < dayEnd) {
      freeBlocks.push({
        title: "Everyone free",
        start: currentFreeStart.toISOString(),
        end: dayEnd.toISOString(),
        backgroundColor: "#198754",
        borderColor: "#198754",
        textColor: "#ffffff"
      });
    }
  });

  return freeBlocks;
}