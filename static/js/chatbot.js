// AI Financial Advisor Chatbot Logic

document.addEventListener('DOMContentLoaded', () => {
  const chatMessages = document.getElementById('chatMessages');
  const chatForm = document.getElementById('chatForm');
  const chatInput = document.getElementById('chatInput');
  const promptPills = document.querySelectorAll('.prompt-pill');

  if (!chatForm || !chatInput || !chatMessages) return;

  function formatBotText(text) {
    // Basic formatting for **bold** and newlines
    let formatted = text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/\n/g, '<br>');
    return formatted;
  }

  function appendMessage(sender, text) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `chat-msg ${sender}`;

    const avatar = document.createElement('div');
    avatar.className = 'msg-avatar';
    avatar.innerHTML = sender === 'bot' ? '<i class="ri-robot-2-line"></i>' : '<i class="ri-user-3-line"></i>';

    const bubble = document.createElement('div');
    bubble.className = 'msg-bubble';
    bubble.innerHTML = sender === 'bot' ? formatBotText(text) : text;

    msgDiv.appendChild(avatar);
    msgDiv.appendChild(bubble);

    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function appendTypingIndicator() {
    const indicator = document.createElement('div');
    indicator.className = 'chat-msg bot typing-indicator';
    indicator.id = 'botTyping';
    indicator.innerHTML = `
      <div class="msg-avatar"><i class="ri-robot-2-line"></i></div>
      <div class="msg-bubble" style="color: #94a3b8; font-style: italic;">
        <i class="ri-loader-4-line ri-spin"></i> Analyzing your financial data...
      </div>
    `;
    chatMessages.appendChild(indicator);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function removeTypingIndicator() {
    const indicator = document.getElementById('botTyping');
    if (indicator) indicator.remove();
  }

  function sendMessage(msgText) {
    const text = msgText || chatInput.value.trim();
    if (!text) return;

    appendMessage('user', text);
    chatInput.value = '';

    appendTypingIndicator();

    fetch('/advisor/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ message: text })
    })
      .then(res => res.json())
      .then(data => {
        removeTypingIndicator();
        appendMessage('bot', data.response || "I could not analyze this request right now.");
      })
      .catch(err => {
        removeTypingIndicator();
        appendMessage('bot', "Sorry, I encountered an error communicating with the financial advisory engine.");
      });
  }

  chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    sendMessage();
  });

  promptPills.forEach(pill => {
    pill.addEventListener('click', () => {
      const promptText = pill.getAttribute('data-prompt') || pill.textContent.trim();
      sendMessage(promptText);
    });
  });
});
