// ============================================================
// CAAI Dashboard — frontend-only interactions.
// No backend calls here; this just makes the UI feel alive.
// ============================================================

document.addEventListener("DOMContentLoaded", () => {

  /* ---------- Sidebar collapse (desktop) ---------- */
  const sidebar = document.getElementById("sidebar");
  const sidebarToggle = document.getElementById("sidebarToggle");

  if (sidebarToggle) {
    sidebarToggle.addEventListener("click", () => {
      sidebar.classList.toggle("collapsed");
    });
  }

  /* ---------- Mobile menu ---------- */
  const mobileMenuBtn = document.getElementById("mobileMenuBtn");
  if (mobileMenuBtn) {
    mobileMenuBtn.addEventListener("click", () => {
      sidebar.classList.toggle("mobile-open");
    });
  }

  // Close mobile sidebar when a nav link is tapped
  document.querySelectorAll(".nav-item").forEach((link) => {
    link.addEventListener("click", () => {
      if (window.innerWidth <= 720) {
        sidebar.classList.remove("mobile-open");
      }
    });
  });

  /* ---------- Notification dropdown ---------- */
  const notifBtn = document.getElementById("notifBtn");
  const notifDropdown = document.getElementById("notifDropdown");

  if (notifBtn && notifDropdown) {
    notifBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      notifDropdown.classList.toggle("open");
    });
    document.addEventListener("click", (e) => {
      if (!notifDropdown.contains(e.target) && e.target !== notifBtn) {
        notifDropdown.classList.remove("open");
      }
    });
  }

  /* ---------- Dark mode toggle ---------- */
  const darkModeBtn = document.getElementById("darkModeBtn");
  if (darkModeBtn) {
    // Respect a previously saved preference for this session only
    // (no localStorage per platform constraints — resets on reload).
    darkModeBtn.addEventListener("click", () => {
      document.body.classList.toggle("dark");
    });
  }

  /* ---------- Animated stat counters ---------- */
  document.querySelectorAll(".stat-value[data-count]").forEach((el) => {
    const target = parseInt(el.getAttribute("data-count"), 10) || 0;
    const prefix = el.getAttribute("data-prefix") || "";
    const duration = 900;
    const start = performance.now();

    function tick(now) {
      const progress = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      const value = Math.round(eased * target);
      el.textContent = prefix + value.toLocaleString("en-IN");
      if (progress < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  });

  /* ---------- Tax Efficiency gauge ---------- */
  // Placeholder score until the Tax Engine can compute a real one.
  const gaugeCircle = document.getElementById("gaugeCircle");
  const gaugeNumber = document.getElementById("gaugeNumber");

  if (gaugeCircle && gaugeNumber) {
    const circumference = 2 * Math.PI * 52; // r = 52
    const score = 42; // placeholder — replace with a real computed score later
    const offset = circumference - (score / 100) * circumference;

    gaugeCircle.style.strokeDasharray = circumference;
    gaugeCircle.style.strokeDashoffset = circumference;

    requestAnimationFrame(() => {
      gaugeCircle.style.strokeDashoffset = offset;
    });

    const duration = 1100;
    const start = performance.now();
    function tickScore(now) {
      const progress = Math.min((now - start) / duration, 1);
      gaugeNumber.textContent = Math.round(progress * score);
      if (progress < 1) requestAnimationFrame(tickScore);
    }
    requestAnimationFrame(tickScore);
  }
});