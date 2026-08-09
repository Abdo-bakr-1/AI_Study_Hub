/* AI Study Hub — global UI behaviour: dark mode, sidebar, alerts. */
(function () {
    "use strict";

    // ---- Dark mode toggle (persisted in localStorage) ----
    var root = document.documentElement;

    function currentTheme() {
        return root.getAttribute("data-theme") || "light";
    }

    function setTheme(theme) {
        root.setAttribute("data-theme", theme);
        try { localStorage.setItem("theme", theme); } catch (e) { /* ignore */ }
    }

    document.addEventListener("click", function (e) {
        var toggle = e.target.closest("#themeToggle");
        if (toggle) {
            setTheme(currentTheme() === "dark" ? "light" : "dark");
        }

        // Dismiss alerts
        var close = e.target.closest(".alert-close");
        if (close) {
            var alert = close.closest(".alert");
            if (alert) { alert.remove(); }
        }
    });

    // ---- Mobile sidebar toggle ----
    var sidebar = document.getElementById("sidebar");
    var sidebarToggle = document.getElementById("sidebarToggle");
    var backdrop;

    function openSidebar() {
        if (!sidebar) return;
        sidebar.classList.add("open");
        if (!backdrop) {
            backdrop = document.createElement("div");
            backdrop.className = "sidebar-backdrop";
            document.body.appendChild(backdrop);
            backdrop.addEventListener("click", closeSidebar);
        }
        backdrop.classList.add("show");
    }

    function closeSidebar() {
        if (sidebar) sidebar.classList.remove("open");
        if (backdrop) backdrop.classList.remove("show");
    }

    if (sidebarToggle) {
        sidebarToggle.addEventListener("click", function () {
            if (sidebar && sidebar.classList.contains("open")) {
                closeSidebar();
            } else {
                openSidebar();
            }
        });
    }

    // ---- Auto-dismiss success/info messages after a few seconds ----
    setTimeout(function () {
        document.querySelectorAll(".alert-success, .alert-info").forEach(function (el) {
            el.style.transition = "opacity .4s ease";
            el.style.opacity = "0";
            setTimeout(function () { el.remove(); }, 400);
        });
    }, 5000);
})();
