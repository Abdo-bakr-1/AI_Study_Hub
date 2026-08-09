/* Dashboard charts using Chart.js. Reads data from the #charts-data JSON block
   so no user data is hard-coded into JS. */
(function () {
    "use strict";

    if (typeof Chart === "undefined") return;

    var dataEl = document.getElementById("charts-data");
    if (!dataEl) return;

    var data;
    try {
        data = JSON.parse(dataEl.textContent);
    } catch (e) {
        return;
    }

    // Pull theme-aware colors from CSS variables.
    var styles = getComputedStyle(document.documentElement);
    var textColor = styles.getPropertyValue("--text-muted").trim() || "#6b7280";
    var gridColor = styles.getPropertyValue("--border").trim() || "#e3e6ef";

    Chart.defaults.color = textColor;
    Chart.defaults.font.family = styles.getPropertyValue("--font") ||
        "-apple-system, Segoe UI, Roboto, sans-serif";

    var palette = ["#4f46e5", "#16a34a", "#d97706", "#0ea5e9", "#7c3aed", "#dc2626", "#0d9488"];

    function makeDoughnut(id, labels, values, colors) {
        var el = document.getElementById(id);
        if (!el) return;
        var total = values.reduce(function (a, b) { return a + b; }, 0);
        if (total === 0) {
            emptyChartMessage(el);
            return;
        }
        new Chart(el, {
            type: "doughnut",
            data: {
                labels: labels,
                datasets: [{ data: values, backgroundColor: colors, borderWidth: 0 }]
            },
            options: {
                responsive: true,
                plugins: { legend: { position: "bottom" } },
                cutout: "62%"
            }
        });
    }

    function makeBar(id, labels, values) {
        var el = document.getElementById(id);
        if (!el) return;
        var total = values.reduce(function (a, b) { return a + b; }, 0);
        if (total === 0) {
            emptyChartMessage(el);
            return;
        }
        new Chart(el, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [{ data: values, backgroundColor: palette, borderRadius: 6 }]
            },
            options: {
                responsive: true,
                plugins: { legend: { display: false } },
                scales: {
                    y: { beginAtZero: true, ticks: { precision: 0 }, grid: { color: gridColor } },
                    x: { grid: { display: false } }
                }
            }
        });
    }

    function emptyChartMessage(canvas) {
        var p = document.createElement("p");
        p.className = "empty-state text-center";
        p.textContent = "No data yet.";
        canvas.replaceWith(p);
    }

    // Task status (completed vs pending)
    makeDoughnut(
        "taskStatusChart",
        ["Completed", "Pending"],
        [data.completed_tasks || 0, data.pending_tasks || 0],
        ["#16a34a", "#d97706"]
    );

    // Tasks by priority
    makeBar(
        "taskPriorityChart",
        ["Low", "Medium", "High"],
        [data.priority_low || 0, data.priority_medium || 0, data.priority_high || 0]
    );

    // Notes by category
    if (data.notes_categories && data.notes_categories.length) {
        makeDoughnut(
            "notesCategoryChart",
            data.notes_categories,
            data.notes_category_counts,
            palette
        );
    } else {
        var el = document.getElementById("notesCategoryChart");
        if (el) emptyChartMessage(el);
    }
})();
