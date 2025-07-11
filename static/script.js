document.addEventListener('DOMContentLoaded', function () {
  // 🔔 Auto-hide flash messages
  const message = document.getElementById('flash-message');
  if (message) {
    setTimeout(() => {
      message.style.display = 'none';
    }, 4000); // Hide after 4 seconds
  }

  // 🔐 Confirm logout
  const logoutBtn = document.querySelector('.btn-dashboard.logout');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', function (e) {
      const confirmLogout = confirm("Are you sure you want to logout?");
      if (!confirmLogout) {
        e.preventDefault();
      }
    });
  }
});
