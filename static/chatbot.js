document.addEventListener("DOMContentLoaded", function () {
  const chatForm = document.getElementById("chat-form");
  const chatInput = document.getElementById("chat-input");
  const chatBox = document.getElementById("chat-box");

  chatForm.addEventListener("submit", function (e) {
    e.preventDefault();
    const userInput = chatInput.value.trim();
    if (userInput === "") return;

    // Append user message
    appendMessage("You", userInput);
    chatInput.value = "";

    // Handle bot logic
    handleBotReply(userInput.toLowerCase());
  });

  function appendMessage(sender, message) {
    const msgDiv = document.createElement("div");
    msgDiv.innerHTML = `<strong>${sender}:</strong> ${message}`;
    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  function handleBotReply(message) {
    if (message.includes("appointment") || message.includes("book")) {
      appendMessage("Bot", "Sure! Please provide your name, contact, issue, and preferred date/time for the appointment.");

      // Show appointment form
      document.getElementById("appointment-form").style.display = "block";
    } else {
      // Fallback response
      appendMessage("Bot", "I'm still learning! Please ask something about booking, health info, or appointment.");
    }
  }
});

// ✅ Add this function at the bottom
function submitAppointment() {
  const name = document.getElementById("appt-name").value;
  const contact = document.getElementById("appt-contact").value;
  const datetime = document.getElementById("appt-datetime").value;
  const issue = document.getElementById("appt-issue").value;

  fetch('/book_appointment', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ name, contact, datetime, issue })
  })
  .then(response => response.json())
  .then(data => {
    alert(data.message);
    document.getElementById("appointment-form").style.display = "none";
    // Optionally clear the form fields
    document.getElementById("appt-name").value = "";
    document.getElementById("appt-contact").value = "";
    document.getElementById("appt-datetime").value = "";
    document.getElementById("appt-issue").value = "";
  });
}
