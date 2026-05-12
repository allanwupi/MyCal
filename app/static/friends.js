document.addEventListener("DOMContentLoaded", () => {
  const searchInput = document.getElementById("friendSearchInput");

  loadFriends();

  searchInput.addEventListener("input", () => {
    searchUsers();
  });
});

async function searchUsers() {
  const input = document.getElementById("friendSearchInput");
  const results = document.getElementById("friendSearchResults");

  const username = input.value.trim();

  results.innerHTML = "";

  if (!username) {
    return;
  }

  try {
    const response = await fetch(`/api/users/search?username=${encodeURIComponent(username)}`);
    const users = await response.json();

    if (!response.ok) {
      results.innerHTML = `<p class="friends-muted">${users.error || "Search failed."}</p>`;
      return;
    }

    if (users.length === 0) {
      results.innerHTML = `<p class="friends-muted">No users found.</p>`;
      return;
    }

    users.forEach((user) => {
      const row = document.createElement("div");
      row.className = "friend-row";

      row.innerHTML = `
        <span>@${user.username}</span>
        <button class="friends-small-btn" ${user.already_friends ? "disabled" : ""}>
          ${user.already_friends ? "Already Friends" : "Add"}
        </button>
      `;

      if (!user.already_friends) {
        row.querySelector("button").addEventListener("click", () => {
          addFriend(user.username);
        });
      }

      results.appendChild(row);
    });
  } catch (error) {
    results.innerHTML = `<p class="friends-muted">Something went wrong while searching.</p>`;
  }
}

async function addFriend(username) {
  try {
    const response = await fetch("/api/friends/add", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ username: username })
    });

    const data = await response.json();

    if (!response.ok) {
      alert(data.error || "Could not add friend.");
      return;
    }

    document.getElementById("friendSearchInput").value = "";
    document.getElementById("friendSearchResults").innerHTML = "";

    loadFriends();
  } catch (error) {
    alert("Something went wrong while adding friend.");
  }
}

async function loadFriends() {
  const friendsList = document.getElementById("friendsList");

  friendsList.innerHTML = `<p class="friends-muted">Loading friends...</p>`;

  try {
    const response = await fetch("/api/friends");
    const friends = await response.json();

    if (!response.ok) {
      friendsList.innerHTML = `<p class="friends-muted">${friends.error || "Could not load friends."}</p>`;
      return;
    }

    friendsList.innerHTML = "";

    if (friends.length === 0) {
      friendsList.innerHTML = `<p class="friends-muted">No friends added yet.</p>`;
      return;
    }

    friends.forEach((friend) => {
      const row = document.createElement("div");
      row.className = "friend-row";

      row.innerHTML = `
        <span>@${friend.username}</span>
        <button class="friends-remove-btn">Remove</button>
      `;

      row.querySelector("button").addEventListener("click", () => {
        removeFriend(friend.username);
      });

      friendsList.appendChild(row);
    });
  } catch (error) {
    friendsList.innerHTML = `<p class="friends-muted">Something went wrong while loading friends.</p>`;
  }
}

async function removeFriend(username) {
  const confirmed = confirm(`Remove @${username} from your friends?`);

  if (!confirmed) {
    return;
  }

  try {
    const response = await fetch("/api/friends/remove", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ username: username })
    });

    const data = await response.json();

    if (!response.ok) {
      alert(data.error || "Could not remove friend.");
      return;
    }

    loadFriends();
  } catch (error) {
    alert("Something went wrong while removing friend.");
  }
}