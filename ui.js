/* ==========================================================================
   全站小工具：主題切換（給不載入 script.js 的頁面用，例如英雄資料庫）
   ========================================================================== */
(function () {
  'use strict';
  function init() {
    var btn = document.getElementById('themeBtn');
    if (!btn) return;
    var saved = null;
    try { saved = localStorage.getItem('lolTheme'); } catch (e) { /* 忽略 */ }
    if (saved === 'light') {
      document.body.classList.add('light');
      btn.textContent = '🌙';
    }
    btn.addEventListener('click', function () {
      document.body.classList.toggle('light');
      var light = document.body.classList.contains('light');
      btn.textContent = light ? '🌙' : '☀️';
      try { localStorage.setItem('lolTheme', light ? 'light' : 'dark'); } catch (e) { /* 忽略 */ }
    });
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
