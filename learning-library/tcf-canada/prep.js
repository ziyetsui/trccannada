'use strict';
(() => {
  const read = key => { try { return localStorage.getItem(key); } catch (_) { return null; } };
  const write = (key, value) => { try { localStorage.setItem(key, value); } catch (_) {} };
  const themeButton = document.getElementById('prep-theme');
  const setTheme = theme => {
    document.documentElement.dataset.theme = theme;
    themeButton.textContent = theme === 'dark' ? '浅色模式' : '深色模式';
    themeButton.setAttribute('aria-label', theme === 'dark' ? '切换到浅色模式' : '切换到深色模式');
  };
  const preference = read('francais.theme.v1');
  const initial = ['dark', 'light'].includes(preference) ? preference :
    (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  setTheme(initial);
  themeButton.addEventListener('click', () => {
    const theme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
    setTheme(theme);
    write('francais.theme.v1', theme);
  });
  document.querySelectorAll('[data-recall]').forEach(button => {
    button.addEventListener('click', () => {
      const answer = document.getElementById(button.getAttribute('aria-controls'));
      answer.hidden = !answer.hidden;
      button.textContent = answer.hidden ? '揭晓答案' : '藏起答案，自己说';
      button.setAttribute('aria-expanded', String(!answer.hidden));
      if ('speechSynthesis' in window) window.speechSynthesis.cancel();
    });
  });
  const select = document.getElementById('prep-voice');
  const status = document.getElementById('prep-voice-status');
  const buttons = [...document.querySelectorAll('[data-speak]')];
  let voices = [];
  function loadVoices() {
    voices = 'speechSynthesis' in window ? window.speechSynthesis.getVoices().filter(v => /^fr([-_]|$)/i.test(v.lang)) : [];
    const saved = select.value || read('francais.tcf.voice.v1');
    select.replaceChildren();
    const languages = [...new Set(voices.map(v => v.lang))];
    languages.forEach(lang => {
      const option = document.createElement('option');
      option.value = lang;
      option.textContent = lang + ' · ' + voices.find(v => v.lang === lang).name;
      select.append(option);
    });
    if (languages.includes(saved)) select.value = saved;
    select.disabled = !voices.length;
    buttons.forEach(button => { button.disabled = !voices.length; });
    status.textContent = voices.length
      ? '设备合成朗读 · 慢速 0.85× · 回听后再自己说'
      : '设备暂无法语声音；可继续看图练习，也可回原课查看发音提示。';
  }
  select.addEventListener('change', () => {
    write('francais.tcf.voice.v1', select.value);
    if ('speechSynthesis' in window) window.speechSynthesis.cancel();
  });
  buttons.forEach(button => {
    button.addEventListener('click', () => {
      const voice = voices.find(v => v.lang === select.value);
      if (!voice || !('SpeechSynthesisUtterance' in window)) return;
      const utterance = new SpeechSynthesisUtterance(button.dataset.speak);
      utterance.voice = voice;
      utterance.lang = voice.lang;
      utterance.rate = 0.85;
      window.speechSynthesis.cancel();
      window.speechSynthesis.speak(utterance);
    });
  });
  document.getElementById('prep-stop').addEventListener('click', () => {
    if ('speechSynthesis' in window) window.speechSynthesis.cancel();
  });
  loadVoices();
  if ('speechSynthesis' in window) window.speechSynthesis.addEventListener('voiceschanged', loadVoices);
  window.addEventListener('pagehide', () => {
    if ('speechSynthesis' in window) window.speechSynthesis.cancel();
  });
})();
