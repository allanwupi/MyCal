const allUsers = ["rayhan", "mohammad", "alex", "sarah", "john", "emma"];

let friends = ["rayhan", "mohammad", "alex"];
let selectedFriends = [];

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

let calendar;

document.addEventListener("DOMContentLoaded", () => {
    renderFriends();
    renderCompare();
    setupSearch();
    setupCalendar();

    document.getElementById("compareBtn").addEventListener("click", updateAvailabilityCalendar);
});

function setupSearch() {
    document.getElementById("searchInput").addEventListener("input", function () {
        const query = this.value.toLowerCase();
        const resultsDiv = document.getElementById("searchResults");
        resultsDiv.innerHTML = "";

        if (!query) return;

        const results = allUsers.filter(user =>
            user.includes(query) && !friends.includes(user)
        );

        results.forEach(user => {
            const div = document.createElement("div");
            div.className = "d-flex justify-content-between align-items-center border p-2 mb-1 rounded";

            div.innerHTML = `
                <span>${user}</span>
                <button class="btn btn-sm btn-success">Add Friend</button>
            `;

            div.querySelector("button").onclick = () => {
                friends.push(user);
                renderFriends();
                resultsDiv.innerHTML = "";
                document.getElementById("searchInput").value = "";
            };

            resultsDiv.appendChild(div);
        });
    });
}

function renderFriends() {
    const list = document.getElementById("friendsList");
    list.innerHTML = "";

    friends.forEach(user => {
        const div = document.createElement("div");
        div.className = "d-flex justify-content-between align-items-center border p-2 mb-1 rounded";

        div.innerHTML = `
            <span>${user}</span>
            <button class="btn btn-sm btn-outline-primary">Select</button>
        `;

        div.querySelector("button").onclick = () => selectFriend(user);
        list.appendChild(div);
    });
}

function selectFriend(user) {
    if (selectedFriends.includes(user)) return;

    if (selectedFriends.length >= 3) {
        alert("You can only select up to 3 friends.");
        return;
    }

    selectedFriends.push(user);
    renderCompare();
}

function renderCompare() {
    const list = document.getElementById("compareList");
    list.innerHTML = "";

    if (selectedFriends.length === 0) {
        list.innerHTML = `<p class="text-muted mb-0">No friends selected yet.</p>`;
        return;
    }

    selectedFriends.forEach(user => {
        const div = document.createElement("div");
        div.className = "d-flex justify-content-between align-items-center border p-2 mb-1 rounded";

        div.innerHTML = `
            <span>${user}</span>
            <button class="btn btn-sm btn-warning">Remove</button>
        `;

        div.querySelector("button").onclick = () => {
            selectedFriends = selectedFriends.filter(friend => friend !== user);
            renderCompare();
            updateAvailabilityCalendar();
        };

        list.appendChild(div);
    });
}

function setupCalendar() {
    const calendarEl = document.getElementById("availabilityCalendar");

    calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: "timeGridWeek",
        slotMinTime: "08:00:00",
        slotMaxTime: "20:00:00",
        allDaySlot: false,
        height: "auto",
        nowIndicator: true,
        headerToolbar: {
            left: "prev,next today",
            center: "title",
            right: "timeGridWeek"
        },
        events: []
    });

    calendar.render();
}

function updateAvailabilityCalendar() {
    if (selectedFriends.length === 0) {
        alert("Select at least one friend.");
        return;
    }

    const usersToCompare = ["you", ...selectedFriends];

    let busyEvents = [];

    usersToCompare.forEach(user => {
        const events = mockEvents[user] || [];

        events.forEach(event => {
            busyEvents.push({
                title: event.title,
                start: event.start,
                end: event.end,
                backgroundColor: "#dc3545",
                borderColor: "#dc3545"
            });
        });
    });

    const freeEvents = generateFreeTimeBlocks(busyEvents);

    calendar.removeAllEvents();

    [...freeEvents, ...busyEvents].forEach(event => {
        calendar.addEvent(event);
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
        const workingStart = new Date(`${day}T08:00:00`);
        const workingEnd = new Date(`${day}T20:00:00`);

        const dayBusy = busyEvents
            .filter(event => event.start.startsWith(day))
            .map(event => ({
                start: new Date(event.start),
                end: new Date(event.end)
            }))
            .sort((a, b) => a.start - b.start);

        let currentFreeStart = workingStart;

        dayBusy.forEach(busy => {
            if (busy.start > currentFreeStart) {
                freeBlocks.push({
                    title: "Everyone free",
                    start: currentFreeStart.toISOString(),
                    end: busy.start.toISOString(),
                    backgroundColor: "#198754",
                    borderColor: "#198754"
                });
            }

            if (busy.end > currentFreeStart) {
                currentFreeStart = busy.end;
            }
        });

        if (currentFreeStart < workingEnd) {
            freeBlocks.push({
                title: "Everyone free",
                start: currentFreeStart.toISOString(),
                end: workingEnd.toISOString(),
                backgroundColor: "#198754",
                borderColor: "#198754"
            });
        }
    });

    return freeBlocks;
}