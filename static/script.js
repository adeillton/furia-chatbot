const form = document.getElementById("chat-form");
const userInput = document.getElementById("user-input");
const chatContainer = document.getElementById("chat-box");
const floatingLogo = document.getElementById("floating-logo");

// Adiciona um indicador de "digitando" do bot
function showTypingIndicator() {
  const typingIndicator = document.createElement("div");
  typingIndicator.className = "bot-message typing";
  typingIndicator.innerHTML = "<span>.</span><span>.</span><span>.</span>";
  chatContainer.appendChild(typingIndicator);
  chatContainer.scrollTop = chatContainer.scrollHeight;
  return typingIndicator;
}

// Remove o indicador de "digitando"
function hideTypingIndicator(indicator) {
  if (indicator && indicator.parentNode) {
    indicator.remove();
  }
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const message = userInput.value.trim();
  if (!message) return;

  // Mostra a mensagem do usuário
  addMessage(message, "user-message");
  userInput.value = "";

  // Mostra que o bot está digitando
  const typingIndicator = showTypingIndicator();

  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });

    // Remove o indicador de digitação antes de processar a resposta
    hideTypingIndicator(typingIndicator);

    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}));
      throw new Error(
        errorData.reply || `Erro ${res.status}: ${res.statusText}`
      );
    }

    const data = await res.json();
    addMessage(data.reply, "bot-message");
  } catch (err) {
    hideTypingIndicator(typingIndicator);
    const errorMsg = 
      err.message.includes("Erro 429") ? "Muitas requisições. Tente mais tarde! ⏳" :
      err.message.includes("Erro 401") ? "Chave da API inválida. Configure o servidor! 🔑" :
      "Erro ao processar sua mensagem. Tente novamente! 😓";
    
    addMessage(errorMsg, "bot-message");
    console.error("Erro detalhado:", err);
  }
});

function addMessage(text, className) {
  const msg = document.createElement("div");
  msg.className = className;
  msg.innerText = text;
  chatContainer.appendChild(msg);
  chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Logo flutuante
window.addEventListener("load", () => {
  setTimeout(() => {
    if (floatingLogo) floatingLogo.style.display = "block";
  }, 3000);
});