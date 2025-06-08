document.addEventListener('DOMContentLoaded', () => {
  const toggleBtn = document.getElementById('chat-toggle');
  const chatContainer = document.getElementById('chat-container');
  const sendBtn = document.getElementById('send-btn');
  const messageInput = document.getElementById('message');
  const chatBox = document.getElementById('chat-box');

  // 채팅창 토글
  toggleBtn.addEventListener('click', () => {
    chatContainer.classList.toggle('hidden');
  });

  // 메시지 전송 함수
  async function sendMessage() {
    const text = messageInput.value.trim();
    if (!text) return;

    // 사용자 메시지 출력 (오른쪽 말풍선)
    chatBox.innerHTML += `<div class="message user-message">🙋 ${text}</div>`;
    messageInput.value = '';
    chatBox.scrollTop = chatBox.scrollHeight;

    // 서버 요청
    try {
      const response = await fetch('/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ message: text })
      });

      if (!response.ok) throw new Error('서버 응답 오류');

      const data = await response.json();

      // 챗봇 응답 출력 (왼쪽 말풍선)
      chatBox.innerHTML += `<div class="message bot-message">🤖 ${data.response}</div>`;
      chatBox.scrollTop = chatBox.scrollHeight;

    } catch (error) {
      console.error('Error:', error);
      chatBox.innerHTML += `<div class="message bot-message">⚠️ 오류가 발생했습니다.</div>`;
      chatBox.scrollTop = chatBox.scrollHeight;
    }
  }

  // 버튼 클릭으로 메시지 전송
  sendBtn.addEventListener('click', sendMessage);

  // 엔터 키로 메시지 전송
  messageInput.addEventListener('keydown', (event) => {
    if (event.key === 'Enter') {
      event.preventDefault();
      sendMessage();
    }
  });
    // 빠른 버튼으로 메시지 전송
  window.sendQuickMessage = function (text) {
    messageInput.value = text;
    sendBtn.click();
  };
});
