/* AI chat interactions: AJAX send, loading + error states, auto-scroll. */
(function () {
    "use strict";

    var form = document.getElementById("chatForm");
    var input = document.getElementById("chatInput");
    var messagesEl = document.getElementById("chatMessages");
    var errorEl = document.getElementById("chatError");
    var sendBtn = document.getElementById("chatSend");
    if (!form || !input || !messagesEl) return;

    var sendLabel = sendBtn ? sendBtn.querySelector(".send-label") : null;
    var sendSpinner = sendBtn ? sendBtn.querySelector(".send-spinner") : null;

    function getCookie(name) {
        var value = "; " + document.cookie;
        var parts = value.split("; " + name + "=");
        if (parts.length === 2) return parts.pop().split(";").shift();
        return null;
    }

    function scrollToBottom() {
        messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    function escapeHtml(text) {
        var div = document.createElement("div");
        div.textContent = text;
        return div.innerHTML.replace(/\n/g, "<br>");
    }

    function removeEmptyState() {
        var empty = document.getElementById("chatEmpty");
        if (empty) empty.remove();
    }

    function addBubble(role, text, time) {
        removeEmptyState();
        var row = document.createElement("div");
        row.className = "chat-bubble-row " + role;
        row.innerHTML =
            '<div class="chat-bubble">' +
            '<div class="bubble-role">' + (role === "user" ? "You" : "AI") + "</div>" +
            '<div class="bubble-text">' + escapeHtml(text) + "</div>" +
            (time ? '<div class="bubble-time">' + time + "</div>" : "") +
            "</div>";
        messagesEl.appendChild(row);
        scrollToBottom();
        return row;
    }

    function addTyping() {
        var row = document.createElement("div");
        row.className = "chat-bubble-row assistant";
        row.id = "typingRow";
        row.innerHTML =
            '<div class="chat-bubble"><div class="typing"><span></span><span></span><span></span></div></div>';
        messagesEl.appendChild(row);
        scrollToBottom();
    }

    function removeTyping() {
        var row = document.getElementById("typingRow");
        if (row) row.remove();
    }

    function setLoading(state) {
        if (!sendBtn) return;
        sendBtn.disabled = state;
        if (sendLabel) sendLabel.style.display = state ? "none" : "inline";
        if (sendSpinner) sendSpinner.style.display = state ? "inline" : "none";
    }

    function showError(msg) {
        if (!errorEl) return;
        errorEl.textContent = msg;
        errorEl.style.display = "block";
    }

    function hideError() {
        if (errorEl) errorEl.style.display = "none";
    }

    // Auto-grow textarea
    input.addEventListener("input", function () {
        input.style.height = "auto";
        input.style.height = Math.min(input.scrollHeight, 140) + "px";
    });

    // Enter to send, Shift+Enter for newline
    input.addEventListener("keydown", function (e) {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            form.requestSubmit ? form.requestSubmit() : form.submit();
        }
    });

    form.addEventListener("submit", function (e) {
        e.preventDefault();
        var text = input.value.trim();
        if (!text) return;

        hideError();
        addBubble("user", text, "");
        input.value = "";
        input.style.height = "auto";
        setLoading(true);
        addTyping();

        fetch(form.action, {
            method: "POST",
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: new URLSearchParams({ message: text })
        })
            .then(function (res) {
                return res.json().then(function (data) {
                    return { ok: res.ok, data: data };
                });
            })
            .then(function (result) {
                removeTyping();
                setLoading(false);
                if (!result.ok || !result.data.success) {
                    showError(result.data.error || "Something went wrong. Please try again.");
                    return;
                }
                addBubble("assistant", result.data.reply, result.data.created_at);

                // Update form action + URL so the next message stays in this conversation.
                if (result.data.conversation_id && form.action.indexOf("/send/") !== -1) {
                    var base = form.getAttribute("data-conversation-url");
                    if (base) {
                        form.action = base + result.data.conversation_id + "/send/";
                        try {
                            window.history.replaceState({}, "", base + result.data.conversation_id + "/");
                        } catch (err) { /* ignore */ }
                    }
                }
            })
            .catch(function () {
                removeTyping();
                setLoading(false);
                showError("Network error. Please check your connection and try again.");
            });
    });

    scrollToBottom();
})();
