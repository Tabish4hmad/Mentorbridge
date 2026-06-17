(function () {
  const threadList = document.getElementById('inboxThreadList');
  const threadCount = document.getElementById('inboxThreadCount');
  const inboxEmpty = document.getElementById('inboxEmpty');
  const chatEmpty = document.getElementById('inboxChatEmpty');
  const chat = document.getElementById('inboxChat');
  const messagesEl = document.getElementById('inboxMessages');
  const compose = document.getElementById('inboxCompose');
  const input = document.getElementById('inboxMessageInput');
  const partnerAvatar = document.getElementById('inboxPartnerAvatar');
  const partnerName = document.getElementById('inboxPartnerName');
  const partnerMeta = document.getElementById('inboxPartnerMeta');

  if (!threadList || !compose) return;

  let activeThreadId = null;
  let lastMessageId = 0;
  let pollTimer = null;

  function html(value) {
    if (typeof escapeHTML === 'function') return escapeHTML(value);
    const div = document.createElement('div');
    div.textContent = value || '';
    return div.innerHTML;
  }

  function avatarHTML(initials, url, alt = '') {
    return url
      ? `<img class="avatar-img" src="${html(url)}" alt="${html(alt)}">`
      : html(initials || 'U');
  }

  function notify(message) {
    if (typeof toast === 'function') toast(message);
  }

  function csrf() {
    if (typeof getCookie === 'function') return getCookie('csrftoken');
    return '';
  }

  function threadHTML(thread) {
    return `
      <button class="inbox-thread" type="button" data-thread-id="${html(String(thread.id))}">
        <span class="person-avatar">${avatarHTML(thread.partnerAvatar, thread.partnerAvatarUrl, thread.partnerName)}</span>
        <span class="inbox-thread-main">
          <span class="inbox-thread-name">${html(thread.partnerName)}</span>
          <span class="inbox-thread-last">${html(thread.lastMessage)}</span>
        </span>
        <span class="inbox-thread-time">${html(thread.lastAt)}</span>
      </button>
    `;
  }

  function messageHTML(message) {
    return `
      <div class="chat-bubble ${message.isMine ? 'mine' : 'theirs'}" data-message-id="${html(String(message.id))}">
        <div>${html(message.body)}</div>
        <span>${html(message.createdAt)}</span>
      </div>
    `;
  }

  function renderThreads(threads) {
    threadCount.textContent = `${threads.length} chat${threads.length === 1 ? '' : 's'}`;
    inboxEmpty.classList.toggle('hidden', threads.length !== 0);
    const current = activeThreadId;
    threadList.querySelectorAll('.inbox-thread').forEach(el => el.remove());
    threadList.insertAdjacentHTML('beforeend', threads.map(threadHTML).join(''));
    if (current) {
      const active = threadList.querySelector(`[data-thread-id="${current}"]`);
      if (active) active.classList.add('active');
    }
    if (!current && threads[0]) openThread(threads[0].id);
  }

  function loadThreads() {
    return fetch('/api/inbox/threads/')
      .then(response => response.json())
      .then(result => {
        if (!result.ok) {
          notify(result.error || 'Could not load inbox.');
          return;
        }
        renderThreads(result.threads);
      })
      .catch(() => notify('Could not load inbox. Try again.'));
  }

  function appendMessages(messages) {
    if (!messages.length) return;
    messagesEl.insertAdjacentHTML('beforeend', messages.map(messageHTML).join(''));
    lastMessageId = Math.max(lastMessageId, ...messages.map(message => message.id));
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function loadMessages(threadId, onlyNew = false) {
    const query = onlyNew && lastMessageId ? `?after=${lastMessageId}` : '';
    return fetch(`/api/inbox/threads/${threadId}/messages/${query}`)
      .then(response => response.json())
      .then(result => {
        if (!result.ok) {
          notify(result.error || 'Could not load messages.');
          return;
        }
        partnerAvatar.innerHTML = avatarHTML(result.thread.partnerAvatar || 'U', result.thread.partnerAvatarUrl || '', result.thread.partnerName || 'Conversation');
        partnerName.textContent = result.thread.partnerName || 'Conversation';
        partnerMeta.textContent = `${result.thread.partnerRole} | ${result.thread.partnerEmail}`;
        if (!onlyNew) {
          messagesEl.innerHTML = '';
          lastMessageId = 0;
        }
        appendMessages(result.messages);
      })
      .catch(() => notify('Could not load messages. Try again.'));
  }

  function openThread(threadId) {
    activeThreadId = String(threadId);
    threadList.querySelectorAll('.inbox-thread').forEach(item => {
      item.classList.toggle('active', item.dataset.threadId === activeThreadId);
    });
    chatEmpty.classList.add('hidden');
    chat.classList.remove('hidden');
    loadMessages(activeThreadId);
    clearInterval(pollTimer);
    pollTimer = setInterval(() => loadMessages(activeThreadId, true), 3000);
  }

  threadList.addEventListener('click', event => {
    const item = event.target.closest('.inbox-thread');
    if (item) openThread(item.dataset.threadId);
  });

  compose.addEventListener('submit', event => {
    event.preventDefault();
    const body = input.value.trim();
    if (!activeThreadId || !body) return;

    fetch(`/api/inbox/threads/${activeThreadId}/messages/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrf()
      },
      body: JSON.stringify({body})
    })
      .then(response => response.json())
      .then(result => {
        if (!result.ok) {
          notify(result.error || 'Could not send message.');
          return;
        }
        input.value = '';
        appendMessages([result.message]);
        loadThreads();
      })
      .catch(() => notify('Could not send message. Try again.'));
  });

  loadThreads();
})();
