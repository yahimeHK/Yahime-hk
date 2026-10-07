/* ==========================================================================
   LOL 攻略站 — 重新整理後回到原來的位置
   只做兩件事，而且只在「重新整理」時才還原（一般點連結進站不受影響）：
     1. 捲動位置：回到你剛才看到的地方
     2. 篩選狀態：搜尋框、下拉選單、分頁／分類按鈕都回到你選的那個
   狀態存在 sessionStorage：重新整理還在，關掉分頁就清掉。
   ========================================================================== */
(function () {
  'use strict';

  // 判斷這次載入是不是「重新整理」（重新整理才還原，避免影響正常瀏覽）
  let isReload = false;
  try {
    const entries = performance.getEntriesByType && performance.getEntriesByType('navigation');
    if (entries && entries.length) {
      isReload = entries[0].type === 'reload';
    } else if (performance.navigation) {
      isReload = performance.navigation.type === 1;      // 舊瀏覽器的後備判斷
    }
  } catch (_) { /* 判斷不出來就當作不是重新整理 */ }

  if (isReload && 'scrollRestoration' in history) {
    history.scrollRestoration = 'manual';                // 由我們自己還原，才不會跟瀏覽器打架
  }

  const PAGE = location.pathname;
  const K_SCROLL = 'lolKeepScroll:' + PAGE;
  const K_FIELD  = 'lolKeepField:' + PAGE + ':';
  const K_TABS   = 'lolKeepTabs:' + PAGE + ':';

  function read(key) {
    try { return sessionStorage.getItem(key); } catch (_) { return null; }
  }
  function write(key, value) {
    try { sessionStorage.setItem(key, value); } catch (_) { /* 無痕模式等，忽略 */ }
  }

  /* ------------------------------------------------------------- 捲動位置 */
  let userScrolled = false;
  ['wheel', 'touchstart', 'keydown', 'mousedown'].forEach((ev) => {
    window.addEventListener(ev, () => { userScrolled = true; }, { passive: true });
  });

  function saveScroll() {
    const y = Math.round(window.pageYOffset || document.documentElement.scrollTop || 0);
    write(K_SCROLL, String(y));
  }
  function restoreScroll() {
    if (userScrolled) return;                            // 使用者已經自己動了，不要搶
    const target = parseInt(read(K_SCROLL) || '0', 10) || 0;
    if (target <= 0) return;
    // 網站樣式有 html{scroll-behavior:smooth}，直接捲會變成「慢慢滑」，
    // 重新整理還原時要「立刻到位」，所以先暫時關掉平滑捲動。
    const html = document.documentElement;
    const prev = html.style.scrollBehavior;
    html.style.scrollBehavior = 'auto';
    window.scrollTo(0, target);
    html.style.scrollBehavior = prev;
  }

  let scrollTimer = null;
  window.addEventListener('scroll', () => {
    if (scrollTimer) return;
    scrollTimer = window.setTimeout(() => { scrollTimer = null; saveScroll(); }, 250);
  }, { passive: true });
  window.addEventListener('pagehide', saveScroll);
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'hidden') saveScroll();
  });

  /* --------------------------------------------------------- 表單／篩選值 */
  function fields() {
    return document.querySelectorAll('input[id], select[id], textarea[id]');
  }
  function saveField(el) {
    const v = (el.type === 'checkbox' || el.type === 'radio') ? (el.checked ? '1' : '0') : el.value;
    write(K_FIELD + el.id, v);
  }
  function restoreFields() {
    Array.prototype.forEach.call(fields(), (el) => {
      const v = read(K_FIELD + el.id);
      if (v === null) return;
      if (el.type === 'checkbox' || el.type === 'radio') {
        if (el.checked === (v === '1')) return;
        el.checked = (v === '1');
      } else {
        if (el.value === v) return;
        el.value = v;
      }
      // 觸發網站原本的監聽器，讓畫面重新套用這個條件
      el.dispatchEvent(new Event('input', { bubbles: true }));
      el.dispatchEvent(new Event('change', { bubbles: true }));
    });
  }

  document.addEventListener('input', (e) => {
    if (e.target && e.target.id) saveField(e.target);
  }, true);
  document.addEventListener('change', (e) => {
    if (e.target && e.target.id) saveField(e.target);
  }, true);

  /* ------------------------------------------------- 分頁／分類按鈕的選擇 */
  function tabGroups() {
    const groups = [];
    Array.prototype.forEach.call(document.querySelectorAll('.tab, .article-filter'), (b) => {
      let g = null;
      for (let i = 0; i < groups.length; i++) if (groups[i].parent === b.parentElement) g = groups[i];
      if (!g) { g = { parent: b.parentElement, buttons: [] }; groups.push(g); }
      g.buttons.push(b);
    });
    return groups;
  }
  function activeIndex(g) {
    for (let i = 0; i < g.buttons.length; i++) if (g.buttons[i].classList.contains('active')) return i;
    return -1;
  }
  function saveTabs() {
    tabGroups().forEach((g, i) => write(K_TABS + i, String(activeIndex(g))));
  }
  function restoreTabs() {
    tabGroups().forEach((g, i) => {
      const v = read(K_TABS + i);
      if (v === null) return;
      const idx = parseInt(v, 10);
      if (isNaN(idx) || idx < 0 || !g.buttons[idx]) return;
      if (!g.buttons[idx].classList.contains('active')) g.buttons[idx].click();
    });
  }
  document.addEventListener('click', (e) => {
    const b = e.target && e.target.closest ? e.target.closest('.tab, .article-filter') : null;
    if (b) window.setTimeout(saveTabs, 0);                // 等網站切換 active 後再記錄
  }, true);

  /* --------------------------------------------------------------- 起始 */
  // 這裡的監聽器會比 script.js 的 DOMContentLoaded 晚註冊，所以會後執行：
  // 那時 script.js 已經把 renderChampions 等 listener 接好，還原才會生效。
  document.addEventListener('DOMContentLoaded', () => {
    if (!isReload) return;
    restoreFields();
    restoreTabs();

    // 英雄卡片是之後才非同步載入的，版面高度會變，所以多還原幾次
    [0, 120, 350, 800, 1500, 2500].forEach((ms) => window.setTimeout(restoreScroll, ms));
  });

  window.addEventListener('load', () => {
    if (isReload) window.setTimeout(restoreScroll, 60);
  });
})();
