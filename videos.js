/* ==========================================================================
   LOL 攻略站 — 主畫面影片切換
   點下面的小圖，就把那支影片換到上面的自訂播放器（同一個 <video>，不會重建閃爍）。
   選擇會存在 localStorage，重新整理或下次再來都還是同一支。
   ========================================================================== */
(function () {
  'use strict';

  const player = window.LOLPlayer;
  const thumbs = document.getElementById('videoThumbs');
  if (!player || !thumbs) return;                 // 這一頁沒有影片區就安靜結束

  const KEY = 'lolPlayer.featured';
  const FADE = 220;                                // 淡出時間，要跟 player.css 的 transition 一致

  const frame = document.querySelector('.salvation-player .stage__frame');
  const elTitle = document.getElementById('featureTitle');
  const elDesc  = document.getElementById('featureDesc');
  const elSpec  = document.getElementById('videoSpec');
  const elNow   = document.getElementById('nowTitle');

  const buttons = Array.prototype.slice.call(thumbs.querySelectorAll('.video-thumb'));
  if (!buttons.length) return;

  let current = null;
  let switchTimer = null;
  let fadeTimer = null;

  const store = {
    get(k, fallback) {
      try {
        const v = localStorage.getItem(k);
        return v === null ? fallback : v;
      } catch (_) { return fallback; }
    },
    set(k, v) {
      try { localStorage.setItem(k, v); } catch (_) { /* 忽略 */ }
    }
  };

  function buttonFor(id) {
    return buttons.filter((b) => b.dataset.video === String(id))[0] || buttons[0];
  }

  /** 標記哪一張小圖是目前的「主畫面」 */
  function markActive(id) {
    buttons.forEach((b) => {
      const on = b.dataset.video === String(id);
      b.classList.toggle('is-active', on);
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
      const v = b.querySelector('video');
      if (v && on && !v.paused) v.pause();          // 小圖不播聲音、不跟主畫面搶
    });
  }

  /** 更新主畫面上的文字與規格 */
  function paintMeta(d) {
    if (elTitle) elTitle.textContent = d.title || '';
    if (elDesc)  elDesc.textContent  = d.desc || '';
    if (elSpec)  elSpec.innerHTML    = d.spec || '';
    if (elNow)   elNow.textContent   = d.now || d.title || '';
    if (frame && d.ratio) frame.style.setProperty('--frame-ratio', d.ratio);
  }

  function endSwitch() {
    clearTimeout(switchTimer);
    clearTimeout(fadeTimer);
    if (frame) frame.classList.remove('is-switching');
  }

  /**
   * 切換主畫面影片。
   * @param {string}  id        影片編號
   * @param {boolean} animate   是否播放淡出／淡入轉場（使用者點擊時為 true）
   * @param {boolean} autoplay  切過去之後是否自動播放
   */
  function show(id, animate, autoplay) {
    const btn = buttonFor(id);
    const d = btn.dataset;
    if (current === String(d.video) && animate) return;   // 已經在主畫面，不重複切

    current = String(d.video);
    store.set(KEY, current);
    markActive(current);
    paintMeta(d);

    if (!animate) {
      player.switchTo(d.src, d.video, autoplay);
      return;
    }

    // 淡出 -> 換來源 -> 影片一有畫面就淡回來
    if (frame) frame.classList.add('is-switching');
    clearTimeout(switchTimer);
    clearTimeout(fadeTimer);
    switchTimer = setTimeout(() => {
      player.switchTo(d.src, d.video, autoplay);
      const v = player.video;
      const done = () => { endSwitch(); v.removeEventListener('loadeddata', done); };
      v.addEventListener('loadeddata', done);
      fadeTimer = setTimeout(endSwitch, 2500);            // 保險：就算事件沒來也會淡回來
    }, animate ? FADE : 0);
  }

  /* --------------------------------------------------------------- 事件 */
  thumbs.addEventListener('click', (e) => {
    const btn = e.target.closest ? e.target.closest('.video-thumb') : null;
    if (!btn || !thumbs.contains(btn)) return;

    // 已經是主畫面的那張：捲到播放器讓你看，不重新載入
    if (String(btn.dataset.video) === current) {
      if (frame) frame.scrollIntoView({ behavior: 'smooth', block: 'center' });
      return;
    }
    show(btn.dataset.video, true, true);
  });

  // 鍵盤操作：左右鍵在小圖之間移動焦點
  thumbs.addEventListener('keydown', (e) => {
    if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return;
    const i = buttons.indexOf(document.activeElement);
    if (i < 0) return;
    e.preventDefault();
    const next = e.key === 'ArrowRight' ? (i + 1) % buttons.length : (i - 1 + buttons.length) % buttons.length;
    buttons[next].focus();
  });

  /* ------------------------------------------------------------- 起始狀態 */
  // 影片播完廣告式的「載入中」轉圈在切換時由 player.js 負責，這裡只處理轉場結束
  player.video.addEventListener('playing', endSwitch);

  show(store.get(KEY, '1'), false, false);
})();
