const form = document.getElementById("chat-form");
const userInput = document.getElementById("user-input");
const chatContainer = document.getElementById("chat-box");
const floatingLogo = document.getElementById("floating-logo");

function showTypingIndicator() {
  const typingIndicator = document.createElement("div");
  typingIndicator.className = "bot-message typing";
  typingIndicator.innerHTML = "<span>.</span><span>.</span><span>.</span>";
  chatContainer.appendChild(typingIndicator);
  chatContainer.scrollTop = chatContainer.scrollHeight;
  return typingIndicator;
}

function hideTypingIndicator(indicator) {
  if (indicator && indicator.parentNode) indicator.remove();
}

// Envia comando sugerido
function autoSend(text) {
  userInput.value = text;
  form.dispatchEvent(new Event("submit"));
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const message = userInput.value.trim();
  if (!message) return;

  addMessage(message, "user-message");
  userInput.value = "";

  const typingIndicator = showTypingIndicator();
  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    hideTypingIndicator(typingIndicator);
    if (!res.ok) throw new Error((await res.json()).reply);
    const data = await res.json();
    addMessage(data.reply, "bot-message");
  } catch (err) {
    hideTypingIndicator(typingIndicator);
    addMessage(err.message || "Erro ao processar sua mensagem.", "bot-message");
    console.error(err);
  }
});

function addMessage(text, className) {
  const msg = document.createElement("div");
  msg.className = className;
  msg.innerText = text;
  chatContainer.appendChild(msg);
  chatContainer.scrollTop = chatContainer.scrollHeight;
}

window.addEventListener("load", () => {
  setTimeout(() => {
    if (floatingLogo) floatingLogo.style.display = "block";
  }, 3000);
});