/**
 * AEPIFY THE SHIFT TOGGLE
 * Google Search (Keywords) vs ChatGPT Conversation (Intent & Context)
 */

(function () {
  'use strict';

  const btnGoogle = document.getElementById('btnShiftGoogle');
  const btnChatgpt = document.getElementById('btnShiftChatgpt');
  const panelGoogle = document.getElementById('panelGoogle');
  const panelChatgpt = document.getElementById('panelChatgpt');

  function setMode(mode) {
    if (mode === 'google') {
      if (btnGoogle) btnGoogle.classList.add('active');
      if (btnChatgpt) btnChatgpt.classList.remove('active');
      if (panelGoogle) panelGoogle.classList.add('active');
      if (panelChatgpt) panelChatgpt.classList.remove('active');
    } else {
      if (btnGoogle) btnGoogle.classList.remove('active');
      if (btnChatgpt) btnChatgpt.classList.add('active');
      if (panelGoogle) panelGoogle.classList.remove('active');
      if (panelChatgpt) panelChatgpt.classList.add('active');
    }
  }

  if (btnGoogle) {
    btnGoogle.addEventListener('click', function () {
      setMode('google');
    });
  }

  if (btnChatgpt) {
    btnChatgpt.addEventListener('click', function () {
      setMode('chatgpt');
    });
  }
})();
