document.addEventListener("DOMContentLoaded", () => {
    const buttons = document.querySelectorAll(".send-reply");

    buttons.forEach(button => {
        button.addEventListener("click", () => {
            const messageId = button.getAttribute("data-message-id");
            const threadId = button.getAttribute("data-thread-id");

fetch(`/reply_to_mails/${messageId}/${threadId}`, {
    method: "POST",
})
.then(async (res) => {
    let data;
    try {
        data = await res.json();
    } catch {
        throw new Error("Server did not return JSON. Check if you're logged in or if CSRF token failed.");
    }

    if (res.ok && data.message) {
        alert("✅ Reply sent!");
    } else {
        throw new Error(data.error || "Something went wrong");
    }
})
.catch(err => {
    alert("❌ Failed to send: " + err.message);
});
        });
    });
});
