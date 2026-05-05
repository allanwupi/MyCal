const sidebar = document.getElementById('sidebar');
const toggleSidebar = document.getElementById('toggleSidebar');

const COOKIE_NAME = 'sidebar_collapsed';
const COOKIE_MAX_AGE_SECONDS = 60 * 60 * 24 * 365;

function getCookie(name) {
  const escapedName = name.replace(/[-[\]{}()*+?.,\\^$|#\s]/g, '\\$&');
  const match = document.cookie.match(new RegExp('(?:^|; )' + escapedName + '=([^;]*)'));
  return match ? decodeURIComponent(match[1]) : null;
}

function setCookie(name, value, maxAgeSeconds) {
  document.cookie = `${name}=${encodeURIComponent(value)}; path=/; max-age=${maxAgeSeconds}; samesite=lax`;
}

function applyCollapsedState(isCollapsed) {
  sidebar.classList.toggle('collapsed', isCollapsed);
  document.documentElement.classList.toggle('sidebar-collapsed', isCollapsed);
}

function initSidebarState() {
  const isCollapsed = getCookie(COOKIE_NAME) === '1';
  applyCollapsedState(isCollapsed);

  // Enable animated transitions only after initial state is applied.
  requestAnimationFrame(() => {
    document.documentElement.classList.add('sidebar-ready');
  });
}

toggleSidebar.addEventListener('click', () => {
  const nextCollapsed = !sidebar.classList.contains('collapsed');
  applyCollapsedState(nextCollapsed);
  setCookie(COOKIE_NAME, nextCollapsed ? '1' : '0', COOKIE_MAX_AGE_SECONDS);
});

initSidebarState();

const navItems = document.querySelectorAll('.nav-links a');