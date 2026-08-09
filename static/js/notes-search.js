/* Live client-side search for the notes list (title + content). */
(function () {
    "use strict";

    var input = document.getElementById("noteSearch");
    var grid = document.getElementById("notesGrid");
    var empty = document.getElementById("noNotesFound");
    if (!input || !grid) return;

    var cards = Array.prototype.slice.call(grid.querySelectorAll(".note-card"));

    function filter() {
        var q = input.value.trim().toLowerCase();
        var visible = 0;

        cards.forEach(function (card) {
            var title = card.getAttribute("data-title") || "";
            var content = card.getAttribute("data-content") || "";
            var match = !q || title.indexOf(q) !== -1 || content.indexOf(q) !== -1;
            card.style.display = match ? "" : "none";
            if (match) visible++;
        });

        if (empty) empty.style.display = visible === 0 ? "block" : "none";
    }

    // Do not submit the form on Enter — keep it purely client-side.
    input.addEventListener("keydown", function (e) {
        if (e.key === "Enter") e.preventDefault();
    });
    input.addEventListener("input", filter);
})();
