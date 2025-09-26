document.addEventListener('DOMContentLoaded', () => {
  const toggleBtn = document.getElementById('chat-toggle');
  const chatContainer = document.getElementById('chat-container');
  const sendBtn = document.getElementById('send-btn');
  const messageInput = document.getElementById('message');
  const chatBox = document.getElementById('chat-box');

  // 채팅창 토글
  toggleBtn.addEventListener('click', () => {
    chatContainer.classList.toggle('hidden');

    // 인삿말 & 버튼은 처음 열었을 때만 출력
    if (!chatContainer.classList.contains('hidden') && !chatBox.dataset.initialized) {
      addBotMessage(
        "안녕하세요! 전동중학교 챗봇입니다.<br>궁금한 정보를 선택하거나 질문을 입력해 주세요!",
        true
      );
      chatBox.dataset.initialized = "true";
    }
  });

  // 메시지 전송 함수
  async function sendMessage() {
    const text = messageInput.value.trim();
    if (!text) return;

    // 사용자 메시지 출력 (오른쪽 말풍선)
    addUserMessage(text);
    messageInput.value = '';

    // 서버 요청
    try {
      const response = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text })
      });

      if (!response.ok) throw new Error('서버 응답 오류');

      const data = await response.json();

      // 챗봇 응답 출력 (버튼 포함)
      addBotMessage(data.response, true);

    } catch (error) {
      console.error('Error:', error);
      addBotMessage(" 오류가 발생했습니다.⚠️", true);
    }
  }

  // 사용자 메시지 출력
  function addUserMessage(text) {
    const userMsg = document.createElement('div');
    userMsg.className = 'message user-message';
    userMsg.innerText = `${text}`;
    chatBox.appendChild(userMsg);
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  // 챗봇 메시지 출력 + 버튼
  function addBotMessage(text, withButtons = false) {
    // 이전 버튼 제거
    const oldButtons = document.querySelector('.bot-buttons-wrapper');
    if (oldButtons) oldButtons.remove();

    const botMsg = document.createElement('div');
    botMsg.className = 'message bot-message';
    botMsg.innerHTML = `🤖 ${text}`;
    chatBox.appendChild(botMsg);

    if (withButtons) {
      const btnWrapper = document.createElement('div');
      btnWrapper.className = 'bot-buttons-wrapper';
      btnWrapper.innerHTML = createBotButtons();
      chatBox.appendChild(btnWrapper);

      btnWrapper.querySelectorAll('button.bot-option').forEach(btn => {
        btn.addEventListener('click', () => {
          messageInput.value = btn.dataset.text;
          sendMessage();
        });
      });
    }

    chatBox.scrollTop = chatBox.scrollHeight;
  }

  // 버튼 HTML 생성 (이미지만)
  function createBotButtons() {
    return `
      <button class="bot-option" data-text="급식"><img src="/static/UI/meal.png" alt="급식" /></button>
      <button class="bot-option" data-text="학사일정"><img src="/static/UI/schedule.png" alt="학사일정" /></button>
      <button class="bot-option" data-text="공지사항"><img src="/static/UI/notice.png" alt="공지사항" /></button>
      <button class="bot-option" data-text="가정통신문"><img src="/static/UI/letter.png" alt="가정통신문" /></button>
      <button class="bot-option" data-text="전동중학교"><img src="/static/UI/info.png" alt="전동중학교" /></button>
    `;
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
});
