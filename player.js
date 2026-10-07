/* ==========================================================================
   LOL 攻略站 — 《救贖》自訂影片播放器
   移植自 website example/site/player.js（Salvation showcase），改動如下：
     · 只在播放器被滑過／聚焦／播放中且在畫面內時才攔截鍵盤，
       避免搶走攻略站長頁面的空白鍵與方向鍵捲動。
     · 滾輪只在控制列上調整音量，滑鼠掃過影片時不再卡住頁面捲動。
     · 提示訊息與 aria-label 全部繁中化。
     · 頁面 toast 的 id 由 toast 改為 playerToast，避免與攻略站的 #toast 衝突。
     · localStorage 命名空間改為 lolPlayer.*，不與 lolTheme 等混淆。
   無任何外部依賴，純 ES2020。
   ========================================================================== */
(function () {
  'use strict';

  const $ = (id) => document.getElementById(id);

  const video = $('video');
  if (!video) return;                       // 這一頁沒有播放器就安靜結束

  const stage    = $('stage');
  const frame    = document.querySelector('.salvation-player .stage__frame');
  const controls = $('controls');
  const bigplay  = $('bigplay');
  const spinner  = $('spinner');
  const toast    = $('playerToast');

  if (!stage || !frame || !controls || !bigplay || !spinner || !toast) return;

  const playBtn  = $('play');
  const backBtn  = $('back10');
  const fwdBtn   = $('fwd10');
  const muteBtn  = $('mute');
  const volWrap  = $('volumeWrap');
  const volInput = $('volume');
  const rateBtn  = $('rate');
  const rateLbl  = $('rateLabel');
  const pipBtn   = $('pip');
  const fsBtn    = $('fs');

  const scrub      = $('scrub');
  const seek       = $('seek');
  const played     = $('played');
  const buffered   = $('buffered');
  const scrubHover = $('scrubHover');
  const scrubTip   = $('scrubTip');

  const curEl   = $('cur');
  const durEl   = $('dur');
  const factDur = $('factDur');             // 可選：卡片上的片長顯示
  const chip    = $('progressChip');        // 可選：播放百分比

  if (!playBtn || !backBtn || !fwdBtn || !muteBtn || !volWrap || !volInput ||
      !rateBtn || !rateLbl || !pipBtn || !fsBtn || !scrub || !seek ||
      !played || !buffered || !scrubHover || !scrubTip || !curEl || !durEl) return;

  const STORE = {
    // 觀看進度是每支影片分開存的，見下面的 timeKey()
    volume: 'lolPlayer.volume',
    muted:  'lolPlayer.muted',
    rate:   'lolPlayer.rate'
  };
  const RATES = [0.5, 0.75, 1, 1.25, 1.5, 1.75, 2];
  const SEEK_STEP = 5;      // ← / → 與觸控雙擊
  const JUMP_STEP = 10;     // J / L
  const HIDE_DELAY = 2600;  // 靜止多久後控制列淡出

  let hideTimer = null;
  let toastTimer = null;
  let scrubbing = false;
  let rateIndex = RATES.indexOf(1);

  /* ---------------------------------------------------------------- utils */

  function fmt(sec) {
    if (!Number.isFinite(sec) || sec < 0) sec = 0;
    sec = Math.floor(sec);
    const h = Math.floor(sec / 3600);
    const m = Math.floor((sec % 3600) / 60);
    const s = sec % 60;
    const mm = h ? String(m).padStart(2, '0') : String(m);
    return (h ? h + ':' : '') + mm + ':' + String(s).padStart(2, '0');
  }

  /** localStorage 永不拋錯（無痕模式、file:// 限制等） */
  const store = {
    get(k, fallback) {
      try {
        const v = localStorage.getItem(k);
        return v === null ? fallback : v;
      } catch (_) { return fallback; }
    },
    set(k, v) {
      try { localStorage.setItem(k, String(v)); } catch (_) { /* 忽略 */ }
    }
  };

  // 每一支影片各自記住「看到哪裡」，切換主畫面時才不會互相蓋掉。
  let currentId = '1';
  const timeKey = (id) => 'lolPlayer.time.' + id;

  function saveTime() {
    if (Number.isFinite(video.duration) && video.currentTime > 0) {
      store.set(timeKey(currentId), video.currentTime);
    }
  }

  function flash(message) {
    if (!message) return;
    toast.textContent = message;
    toast.classList.add('is-on');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove('is-on'), 900);
  }

  function busy(on) { spinner.classList.toggle('is-on', on); }

  /**
   * 持續顯示、可行動的訊息。flash() 是短暫回饋，這個是「真的出問題了」。
   */
  function note(text, options) {
    const opts = options || {};
    const el = $('playerNote');
    if (!el) return;
    if (!text) { el.hidden = true; el.innerHTML = ''; return; }
    el.hidden = false;
    el.innerHTML = '';
    const p = document.createElement('p');
    p.textContent = text;
    el.appendChild(p);
    if (opts.retry) {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.textContent = '重試';
      btn.addEventListener('click', () => {
        el.hidden = true;
        video.load();
        video.play().catch(() => {});
      });
      el.appendChild(btn);
    }
  }

  /* ------------------------------------------------------------- controls */

  function showControls() {
    controls.dataset.state = 'shown';
    clearTimeout(hideTimer);
    if (!video.paused && !scrubbing) {
      hideTimer = setTimeout(() => {
        controls.dataset.state = 'hidden';
      }, HIDE_DELAY);
    }
  }

  function refreshPlayState() {
    const playing = !video.paused && !video.ended;
    frame.classList.toggle('is-playing', playing);
    playBtn.setAttribute('aria-label', playing ? '暫停' : '播放');
    if (playing) showControls(); else {
      clearTimeout(hideTimer);
      controls.dataset.state = 'shown';
    }
  }

  function paint() {
    const d = video.duration;
    const t = video.currentTime;

    if (Number.isFinite(d) && d > 0) {
      const pct = Math.min(100, (t / d) * 100);
      played.style.width = pct + '%';
      seek.value = String(Math.round((t / d) * 1000));
      seek.setAttribute('aria-valuetext', fmt(t) + ' / ' + fmt(d));
      if (chip) chip.textContent = Math.round(pct) + '%';
      curEl.textContent = fmt(t);
      durEl.textContent = fmt(d);
    }

    // 已緩衝區域
    let end = 0;
    for (let i = 0; i < video.buffered.length; i++) {
      if (video.buffered.start(i) <= t + 0.5) end = Math.max(end, video.buffered.end(i));
    }
    buffered.style.width = (Number.isFinite(d) && d > 0) ? Math.min(100, (end / d) * 100) + '%' : '0%';
  }

  function seekTo(seconds, announce) {
    const d = video.duration;
    if (!Number.isFinite(d) || d <= 0) return;
    const target = Math.max(0, Math.min(d - 0.05, seconds));
    video.currentTime = target;
    paint();
    if (announce) flash(fmt(target));
  }

  function nudge(delta, announce) {
    seekTo(video.currentTime + delta, announce);
  }

  /* --------------------------------------------------- 音量與速度介面 */

  function applyVolume(v, persist) {
    v = Math.max(0, Math.min(1, v));
    video.volume = v;
    if (v > 0) video.muted = false;
    else video.muted = true;
    volInput.value = String(v);
    volInput.style.setProperty('--vol', (v * 100) + '%');
    frame.classList.toggle('is-muted', video.muted);
    muteBtn.setAttribute('aria-label', video.muted ? '取消靜音' : '靜音');
    if (persist) { store.set(STORE.volume, v); store.set(STORE.muted, video.muted); }
  }

  function applyRate(r, persist) {
    video.playbackRate = r;
    rateLbl.innerHTML = (r === 1 ? '1' : String(r)) + '&times;';
    if (persist) store.set(STORE.rate, r);
  }

  /* --------------------------------------------------------------- events */

  // 播放 / 暫停
  function togglePlay() {
    if (video.paused || video.ended) video.play().catch(() => {}); else video.pause();
  }
  playBtn.addEventListener('click', togglePlay);
  bigplay.addEventListener('click', togglePlay);

  video.addEventListener('click', () => { togglePlay(); });

  video.addEventListener('play', () => { frame.classList.add('is-started'); refreshPlayState(); });
  video.addEventListener('playing', () => { busy(false); refreshPlayState(); });
  video.addEventListener('pause', refreshPlayState);

  video.addEventListener('waiting', () => busy(true));
  video.addEventListener('canplay', () => busy(false));
  video.addEventListener('seeking', () => { if (!scrubbing) busy(video.readyState < 3); });
  video.addEventListener('seeked', () => busy(false));

  video.addEventListener('ended', () => {
    refreshPlayState();
    controls.dataset.state = 'shown';
    frame.classList.add('is-started');
  });

  // 本機檔案常常在 player.js 執行前就載完 metadata（preload="metadata" 對
  // localhost／磁碟上的檔案非常快），那樣 loadedmetadata 不會再觸發，
  // 片長、上次進度與音量速度的還原就會全部安靜地失效。
  // 因此改成具名函式，並在啟動時檢查 readyState 補跑一次。
  let metadataDone = false;
  function handleMetadata() {
    if (metadataDone) return;
    metadataDone = true;
    paint();
    frame.classList.remove('has-error');
    const d = Math.round(video.duration);
    if (factDur && Number.isFinite(d)) factDur.textContent = fmt(d);

    // 瀏覽器可以播放 file:// 的影片，卻無法對它發出 byte range 請求，
    // 因此拖動時間軸會停在空白畫面。與其看起來像壞掉，不如直接說明。
    if (location.protocol === 'file:') {
      flash('以本機檔案開啟 — 時間軸拖曳會受限');
      note(
        '你是直接用 file:// 開啟這個頁面。影片可以播放，但拖曳時間軸會卡住，' +
        '因為瀏覽器無法對本機檔案發出 byte range 請求。' +
        '想要完整功能，請在網站資料夾執行 python serve.py，再開 http://127.0.0.1:8099/ 。'
      );
    }

    // 還原這支影片上次看到的位置
    const saved = parseFloat(store.get(timeKey(currentId), '0'));
    if (Number.isFinite(saved) && saved > 8 && saved < video.duration - 15) {
      video.currentTime = saved;
      flash('已從 ' + fmt(saved) + ' 繼續播放');
    }
    // 還原音量 / 靜音 / 速度
    const v = parseFloat(store.get(STORE.volume, '1'));
    applyVolume(Number.isFinite(v) ? v : 1, false);
    if (store.get(STORE.muted, 'false') === 'true') { video.muted = true; frame.classList.add('is-muted'); }
    const r = parseFloat(store.get(STORE.rate, '1'));
    rateIndex = Math.max(0, RATES.indexOf(Number.isFinite(r) && RATES.includes(r) ? r : 1));
    applyRate(RATES[rateIndex], false);
  }
  video.addEventListener('loadedmetadata', handleMetadata);

  video.addEventListener('timeupdate', () => { if (!scrubbing) paint(); });
  video.addEventListener('progress', paint);

  video.addEventListener('error', () => {
    busy(false);

    // 已經載入過內容（readyState > 0）之後才出現的 error，通常只是瀏覽器
    // 中止請求或頁面正在關閉的雜訊，影片本身沒有問題。這時候彈出
    // 「格式不支援」只會嚇到使用者，因此只留 console 訊息。
    if (video.readyState > 0) {
      console.warn('[LOLPlayer] 已載入後又收到媒體 error（多為中止）',
                   video.error && video.error.code);
      return;
    }

    const err = video.error;
    const code = err ? err.code : 0;
    const why = {
      1: '載入被中止',
      2: '發生網路錯誤',
      3: '這個檔案無法解碼',
      4: '這個瀏覽器不支援此格式'
    }[code] || '原因不明';

    const src = video.currentSrc || video.getAttribute('src') || '(無)';
    const isFile = location.protocol === 'file:';
    const isMissing = code === 4 || code === 2;

    let help = '影片載入失敗：' + why + '。';
    if (isMissing && isFile) {
      help += ' 正在找：' + src + ' — 請確認 assetsvideo1.mp4 就在 assets/ 目錄中。' +
              '想要穩定播放，請執行 python serve.py 後開 http://127.0.0.1:8099/ 。';
    } else if (isMissing) {
      help += ' 正在找：' + src + ' — 請確認檔案存在且路徑正確。';
    } else {
      help += ' 來源：' + src;
    }

    frame.classList.add('has-error');
    note(help, { retry: true });
    flash('影片載入失敗');
    console.warn('[LOLPlayer] media error', { code: code, message: err && err.message, src: src });
  });

  // ── 時間軸：拖曳 scrub ────────────────────────────────────────────────
  function ratioFromEvent(e) {
    const r = scrub.getBoundingClientRect();
    return Math.max(0, Math.min(1, (e.clientX - r.left) / r.width));
  }

  scrub.addEventListener('pointerdown', (e) => {
    if (e.button !== 0) return;
    scrubbing = true;
    scrub.classList.add('is-dragging');
    // setPointerCapture 讓拖曳可以離開時間軸，但瀏覽器可能拒絕
    // （例如 pointer id 已失效）——seek 仍然必須發生。
    try { scrub.setPointerCapture(e.pointerId); } catch (_) { /* 非致命 */ }
    seekTo(ratioFromEvent(e) * video.duration, false);
    e.preventDefault();
  });

  scrub.addEventListener('pointermove', (e) => {
    const ratio = ratioFromEvent(e);
    const d = Number.isFinite(video.duration) ? video.duration : 0;

    scrubTip.textContent = fmt(ratio * d);
    const x = Math.max(24, Math.min(scrub.getBoundingClientRect().width - 24, ratio * scrub.getBoundingClientRect().width));
    scrubHover.hidden = false;
    scrubHover.style.left = x + 'px';

    if (scrubbing) seekTo(ratio * d, false);
  });

  scrub.addEventListener('pointerleave', () => { scrubHover.hidden = true; });

  scrub.addEventListener('pointerup', (e) => {
    if (!scrubbing) return;
    scrubbing = false;
    scrub.classList.remove('is-dragging');
    try { scrub.releasePointerCapture(e.pointerId); } catch (_) { /* 沒捕捉到時會丟錯，屬正常情況 */ }
    paint();
    showControls();
  });

  // range input 本身的鍵盤存取
  seek.addEventListener('change', () => {
    if (scrubbing) return;
    const d = video.duration;
    if (Number.isFinite(d) && d > 0) seekTo((Number(seek.value) / 1000) * d, false);
  });
  seek.addEventListener('input', () => {
    const d = video.duration;
    if (Number.isFinite(d) && d > 0 && !scrubbing) {
      played.style.width = (Number(seek.value) / 10) + '%';
      curEl.textContent = fmt((Number(seek.value) / 1000) * d);
    }
  });

  // ── 音量 ───────────────────────────────────────────────────────────────
  muteBtn.addEventListener('click', () => {
    if (video.muted) {
      applyVolume(video.volume > 0 ? video.volume : 0.7, true);
      flash('已取消靜音');
    } else {
      video.muted = true;
      frame.classList.add('is-muted');
      muteBtn.setAttribute('aria-label', '取消靜音');
      store.set(STORE.muted, true);
      flash('已靜音');
    }
  });

  volInput.addEventListener('input', () => applyVolume(parseFloat(volInput.value), true));

  // 音量滑桿在 hover / focus 時滑出
  volWrap.addEventListener('pointerenter', () => volWrap.classList.add('is-open'));
  volWrap.addEventListener('pointerleave', () => { if (!volWrap.contains(document.activeElement)) volWrap.classList.remove('is-open'); });
  muteBtn.addEventListener('pointerenter', () => volWrap.classList.add('is-open'));
  volWrap.addEventListener('focusin', () => volWrap.classList.add('is-open'));
  volWrap.addEventListener('focusout', () => volWrap.classList.remove('is-open'));

  // 滾輪只在控制列上調整音量。原版是整個播放區都吃滾輪，
  // 但這裡是長頁面，滑過影片就被吃掉捲動會很恼人。
  frame.addEventListener('wheel', (e) => {
    if (!controls.contains(e.target)) return;
    if (Math.abs(e.deltaY) < 1) return;
    e.preventDefault();
    const step = e.deltaY < 0 ? 0.05 : -0.05;
    video.muted = false;
    applyVolume(video.volume + step, true);
    volWrap.classList.add('is-open');
    flash('音量 ' + Math.round(video.volume * 100) + '%');
  }, { passive: false });

  // ── 前後跳轉 ───────────────────────────────────────────────────────────
  backBtn.addEventListener('click', () => nudge(-JUMP_STEP, true));
  fwdBtn.addEventListener('click', () => nudge(JUMP_STEP, true));

  // ── 播放速度 ───────────────────────────────────────────────────────────
  rateBtn.addEventListener('click', () => {
    rateIndex = (rateIndex + 1) % RATES.length;
    applyRate(RATES[rateIndex], true);
    flash('速度 ' + RATES[rateIndex] + '\u00D7');
  });

  // ── 子母畫面 ───────────────────────────────────────────────────────────
  const pipSupported = document.pictureInPictureEnabled && typeof video.requestPictureInPicture === 'function';
  if (!pipSupported) {
    pipBtn.hidden = true;
  } else {
    pipBtn.addEventListener('click', async () => {
      try {
        if (document.pictureInPictureElement) await document.exitPictureInPicture();
        else await video.requestPictureInPicture();
      } catch (err) { flash('子母畫面無法使用'); }
    });
    video.addEventListener('enterpictureinpicture', () => { bigplay.style.opacity = 0; });
    video.addEventListener('leavepictureinpicture', () => { bigplay.style.opacity = ''; });
  }

  // ── 全螢幕 ─────────────────────────────────────────────────────────────
  function fsElement() {
    return document.fullscreenElement || document.webkitFullscreenElement || null;
  }
  fsBtn.addEventListener('click', () => {
    const el = frame;
    if (fsElement()) {
      (document.exitFullscreen || document.webkitExitFullscreen).call(document);
    } else if (el.requestFullscreen) {
      el.requestFullscreen().catch(() => flash('全螢幕被瀏覽器阻擋'));
    } else if (el.webkitRequestFullscreen) {
      el.webkitRequestFullscreen();
    } else {
      flash('此瀏覽器不支援全螢幕');
    }
  });
  ['fullscreenchange', 'webkitfullscreenchange'].forEach((ev) =>
    document.addEventListener(ev, () => {
      const on = !!fsElement();
      frame.classList.toggle('is-fs', on);
      fsBtn.setAttribute('aria-label', on ? '離開全螢幕' : '全螢幕');
      if (on) showControls();
    })
  );

  // ── 自動隱藏控制列 ─────────────────────────────────────────────────────
  ['pointermove', 'pointerdown', 'touchstart', 'focusin'].forEach((ev) =>
    frame.addEventListener(ev, showControls, { passive: true })
  );
  frame.addEventListener('pointerleave', () => {
    if (!video.paused) controls.dataset.state = 'hidden';
  });

  // ── 鍵盤快捷鍵 ─────────────────────────────────────────────────────────
  // 只在播放器「正在被使用」時生效：滑鼠停在播放器上、焦點在播放器內，
  // 或影片正在播放且仍在畫面內。否則空白鍵與方向鍵要留給頁面捲動。
  function engaged() {
    if (stage.contains(document.activeElement)) return true;
    if (frame.matches(':hover')) return true;
    if (!video.paused) {
      const r = frame.getBoundingClientRect();
      return r.bottom > 0 && r.top < (window.innerHeight || 0);
    }
    return false;
  }

  document.addEventListener('keydown', (e) => {
    const t = e.target;
    const typing = t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA' || t.isContentEditable);

    // range 控制項有焦點時，方向鍵交給瀏覽器原生處理
    if (typing && (t === seek || t === volInput)) return;
    if (typing) return;
    if (!engaged()) return;

    const k = e.key;

    if (k === ' ' || k === 'Spacebar' || k === 'k' || k === 'K') {
      e.preventDefault(); togglePlay(); flash(video.paused ? '播放' : '暫停'); return;
    }
    if (k === 'ArrowRight') { e.preventDefault(); nudge(SEEK_STEP, true); return; }
    if (k === 'ArrowLeft')  { e.preventDefault(); nudge(-SEEK_STEP, true); return; }
    if (k === 'l' || k === 'L') { e.preventDefault(); nudge(JUMP_STEP, true); return; }
    if (k === 'j' || k === 'J') { e.preventDefault(); nudge(-JUMP_STEP, true); return; }

    if (k === 'ArrowUp') {
      e.preventDefault();
      video.muted = false; applyVolume(video.volume + 0.05, true); flash('音量 ' + Math.round(video.volume * 100) + '%'); return;
    }
    if (k === 'ArrowDown') {
      e.preventDefault();
      applyVolume(video.volume - 0.05, true); flash('音量 ' + Math.round(video.volume * 100) + '%'); return;
    }

    if (k === 'm' || k === 'M') { e.preventDefault(); muteBtn.click(); return; }
    if (k === 'f' || k === 'F') { e.preventDefault(); fsBtn.click(); return; }
    if (k === 'p' || k === 'P') { e.preventDefault(); if (!pipBtn.hidden) pipBtn.click(); return; }
    if (k === 'Home') { e.preventDefault(); seekTo(0, true); return; }
    if (k === 'End')  { e.preventDefault(); seekTo(video.duration - 0.2, true); return; }

    if (k === '>' || k === '.') { e.preventDefault(); rateBtn.click(); return; }
    if (k === '<' || k === ',') {
      e.preventDefault();
      rateIndex = (rateIndex - 1 + RATES.length) % RATES.length;
      applyRate(RATES[rateIndex], true);
      flash('速度 ' + RATES[rateIndex] + '\u00D7');
      return;
    }

    if (/^[0-9]$/.test(k) && Number.isFinite(video.duration)) {
      e.preventDefault();
      seekTo((Number(k) / 10) * video.duration, true);
    }
  });

  // ── 每幾秒記住播放位置 ─────────────────────────────────────────────────
  setInterval(() => {
    if (!video.paused) saveTime();
  }, 4000);

  window.addEventListener('beforeunload', () => {
    saveTime();
  });

  /* ------------------------------------------------------- 切換主畫面影片 */
  /**
   * 換成另一支影片。沿用同一個 <video> 與同一組控制項，所以畫面不會重建閃爍。
   * @param {string}  src       影片路徑
   * @param {string}  id        影片編號（每支各自記住觀看進度）
   * @param {boolean} autoplay  換過去後是否直接播放（使用者點擊時為 true）
   */
  function switchTo(src, id, autoplay) {
    if (!src) return;
    saveTime();                             // 先記住目前這支看到哪裡
    if (id) currentId = String(id);

    // 已經是同一個來源（例如剛載入時就是第一支）就不用重新載入，避免多一次閃爍
    if (video.getAttribute('src') === src && video.readyState >= 1) {
      if (autoplay) video.play().catch(() => {});
      return;
    }

    metadataDone = false;                   // 讓新影片的 metadata 重新處理一次
    note('');                               // 清掉上一支的錯誤訊息
    frame.classList.remove('has-error');
    frame.classList.remove('is-started');   // 中央播放鈕回來
    if (factDur) factDur.textContent = '--:--';
    if (chip) chip.textContent = '0%';
    played.style.width = '0%';
    buffered.style.width = '0%';
    seek.value = '0';
    curEl.textContent = '0:00';
    durEl.textContent = '0:00';
    busy(true);

    video.src = src;
    video.load();
    if (autoplay) video.play().catch(() => {});
  }

  /* ------------------------------------------------------------- start-up */
  applyVolume(1, false);
  applyRate(1, false);
  paint();
  if (video.readyState >= 1) handleMetadata();   // metadata 在腳本執行前就載完的情況
  refreshPlayState();
  controls.dataset.state = 'shown';
  window.setTimeout(() => { if (video.paused) controls.dataset.state = 'hidden'; }, 4200);

  // 方便在 console 除錯的小把手
  window.LOLPlayer = {
    video,
    play: () => video.play(),
    pause: () => video.pause(),
    seek: (s) => seekTo(s, false),
    switchTo,
    currentId: () => currentId
  };
})();
