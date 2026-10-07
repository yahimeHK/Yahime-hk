/* ==========================================================================
   LOL 攻略站 — 視覺特效層（框架特效 / 按鍵特效 / 滑鼠移動特效）
   --------------------------------------------------------------------------
   * 樣式直接由這支 JS 注入（不依賴外部 CSS，避免瀏覽器快取舊樣式時效果壞掉）
   * 只在「可用的裝置」預設開啟：桌機滑鼠預設開、觸控預設關、使用者要求減少動態時預設關
   * 右上角有一顆 ✨ 可以隨時開關，狀態存在 localStorage（lolFx）
   * 全部效果只改 transform / opacity / CSS 變數，pointermove 以 requestAnimationFrame 節流
   ========================================================================== */
(function () {
  'use strict';

  var KEY = 'lolFx';
  var root = document.documentElement;

  /* ------------------------------------------------------------ 環境判斷 */
  var reduced = false;
  var noHover = false;
  try {
    reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    noHover = window.matchMedia('(hover: none)').matches;
  } catch (e) { /* 舊瀏覽器：視為可開啟 */ }

  var saved = null;
  try { saved = localStorage.getItem(KEY); } catch (e) { saved = null; }

  // 預設值：桌機開、觸控關、減少動態關；使用者手動設定過就以他的選擇為準
  var enabled = saved ? (saved === 'on') : (!reduced && !noHover);

  /* ---------------------------------------------------------------- 樣式 */
  var CARDS = '.db-card,.ac-card,.skin-card,.ability-card,.gear-card,.tac-card,'
    + '.art-card,.map-card,.rune-card,.db-champ,.product-card,.quick,.counter-card';

  var BUTTONS = '.tab,.small-btn,.gold-btn,.ex-find,.ex-reset,.ext-link,.icon-btn,'
    + '.subnav a,.role-filters .tab,.ghost-btn,.gold-btn,.ac-card__foot .ext-link,'
    + '.db-link,.download-btn,.readArticle,.product-card';

  var CSS = [
    /* ---------- 滑鼠移動：整頁聚光 ---------- */
    '#lol-fx-spot{position:fixed;inset:0;z-index:1;pointer-events:none;opacity:0;transition:opacity .5s ease;',
    'background:radial-gradient(460px circle at var(--fx-mx,50%) var(--fx-my,50%),rgba(0,217,255,.062),transparent 62%)}',
    'html.fx-on #lol-fx-spot{opacity:1}',
    'html.fx-on #lol-fx-glow{position:fixed;z-index:1;pointer-events:none;width:280px;height:280px;border-radius:50%;',
    'left:var(--fx-mx,50%);top:var(--fx-my,50%);transform:translate(-50%,-50%);opacity:0;transition:opacity .5s ease;',
    'background:radial-gradient(circle,rgba(200,170,110,.075),transparent 65%);filter:blur(6px)}',
    'html.fx-on #lol-fx-glow{opacity:1}',

    /* ---------- 框架特效：面板流動邊框 ---------- */
    'html.fx-on :is(.items-hero,.champ-hero,.ex-hero,.shop-hero,.hero-card){position:relative}',
    'html.fx-on :is(.items-hero,.champ-hero,.ex-hero,.shop-hero,.hero-card)::before{',
    'content:"";position:absolute;inset:0;border-radius:inherit;padding:1px;pointer-events:none;z-index:2;',
    'background:linear-gradient(115deg,rgba(0,217,255,.65),rgba(200,170,110,.6),rgba(0,217,255,.12),rgba(200,170,110,.65));',
    'background-size:300% 300%;animation:fx-frame 9s linear infinite;',
    '-webkit-mask:linear-gradient(#000 0 0) content-box,linear-gradient(#000 0 0);',
    '-webkit-mask-composite:xor;mask:linear-gradient(#000 0 0) content-box,linear-gradient(#000 0 0);mask-composite:exclude}',
    '@keyframes fx-frame{0%{background-position:0% 50%}100%{background-position:300% 50%}}',

    /* ---------- 框架特效：卡片跟隨游標的光暈 ---------- */
    'html.fx-on :is(' + CARDS + '){position:relative}',
    'html.fx-on :is(' + CARDS + ')::after{content:"";position:absolute;inset:0;border-radius:inherit;pointer-events:none;',
    'opacity:0;transition:opacity .28s ease;z-index:3;',
    'background:radial-gradient(240px circle at var(--fx-x,50%) var(--fx-y,50%),rgba(0,217,255,.18),transparent 62%)}',
    'html.fx-on :is(' + CARDS + '):hover::after{opacity:1}',
    'html.fx-on :is(' + CARDS + '){transition:transform .22s cubic-bezier(.2,.7,.3,1),border-color .22s ease,box-shadow .28s ease}',
    'html.fx-on :is(' + CARDS + '):hover{transform:translateY(-2px);border-color:rgba(0,217,255,.45);',
    'box-shadow:0 14px 34px -18px rgba(0,217,255,.55),0 0 0 1px rgba(0,217,255,.10) inset}',

    /* ---------- 按鍵特效：浮起 / 按壓 / 漣漪 ---------- */
    'html.fx-on :is(' + BUTTONS + '){position:relative;overflow:hidden;isolation:isolate;',
    'transition:transform .16s cubic-bezier(.2,.7,.3,1),box-shadow .22s ease,border-color .22s ease,background-color .22s ease,color .22s ease}',
    'html.fx-on :is(' + BUTTONS + '):hover{transform:translateY(-1px);box-shadow:0 8px 20px -10px rgba(0,217,255,.6),0 0 0 1px rgba(0,217,255,.22)}',
    'html.fx-on :is(' + BUTTONS + '):active{transform:translateY(0) scale(.975)}',
    'html.fx-on :is(' + BUTTONS + '):focus-visible{box-shadow:0 0 0 3px rgba(0,217,255,.35)}',
    '.fx-ripple{position:absolute;left:0;top:0;width:12px;height:12px;margin:-6px 0 0 -6px;border-radius:50%;',
    'pointer-events:none;z-index:0;transform:scale(0);opacity:.9;',
    'background:radial-gradient(circle,rgba(255,255,255,.55),rgba(0,217,255,.35) 45%,transparent 70%);',
    'animation:fx-ripple .6s cubic-bezier(.2,.7,.3,1) forwards}',
    '@keyframes fx-ripple{60%{opacity:.45}100%{transform:scale(26);opacity:0}}',

    /* ---------- 開關按鈕 ---------- */
    '.fx-btn{font-size:14px;line-height:1}',
    '.fx-btn[aria-pressed="false"]{opacity:.45;filter:grayscale(1)}',

    /* ---------- 尊重系統設定 ---------- */
    '@media (prefers-reduced-motion: reduce){',
    'html.fx-on :is(' + CARDS + '),html.fx-on :is(' + BUTTONS + '){transition:none}',
    'html.fx-on :is(.items-hero,.champ-hero,.ex-hero,.shop-hero,.hero-card)::before{animation:none}',
    '.fx-ripple{display:none}',
    '}',
    '@media (hover: none){',
    'html.fx-on :is(' + CARDS + '):hover{transform:none}',
    'html.fx-on :is(' + BUTTONS + '):hover{transform:none;box-shadow:none}',
    'html.fx-on :is(' + CARDS + ')::after{display:none}',
    '#lol-fx-spot,#lol-fx-glow{display:none}',
    '}'
  ].join('');

  function injectStyle() {
    if (document.getElementById('lol-fx-style')) return;
    var st = document.createElement('style');
    st.id = 'lol-fx-style';
    st.textContent = CSS;
    document.head.appendChild(st);
  }

  /* ------------------------------------------------------------ 聚光圖層 */
  function injectLayers() {
    if (!document.getElementById('lol-fx-spot')) {
      var spot = document.createElement('div');
      spot.id = 'lol-fx-spot';
      spot.setAttribute('aria-hidden', 'true');
      document.body.appendChild(spot);
    }
    if (!document.getElementById('lol-fx-glow')) {
      var glow = document.createElement('div');
      glow.id = 'lol-fx-glow';
      glow.setAttribute('aria-hidden', 'true');
      document.body.appendChild(glow);
    }
  }

  /* ---------------------------------------------------------- 滑鼠移動特效 */
  var raf = null;
  var pending = null;

  function flush() {
    raf = null;
    if (!pending) return;
    root.style.setProperty('--fx-mx', pending.x + 'px');
    root.style.setProperty('--fx-my', pending.y + 'px');
    pending = null;
  }

  var lastMove = 0;

  function onMove(e) {
    if (!enabled) return;
    if (e.pointerType && e.pointerType !== 'mouse' && e.pointerType !== 'pen') return;
    var now = e.timeStamp || Date.now();
    // 第一個事件立刻生效（畫面上馬上看到），之後 16ms 內的連續事件合併到下一次畫面更新
    if (now - lastMove < 16) {
      pending = { x: e.clientX, y: e.clientY };
      if (!raf) raf = window.requestAnimationFrame(flush);
      return;
    }
    lastMove = now;
    pending = null;
    root.style.setProperty('--fx-mx', e.clientX + 'px');
    root.style.setProperty('--fx-my', e.clientY + 'px');
  }

  /* ------------------------------------------------------ 卡片光暈（跟隨游標） */
  var hoverCard = null;
  var cardRect = null;

  function cardMove(e) {
    if (!enabled || !hoverCard || !cardRect) return;
    var x = ((e.clientX - cardRect.left) / cardRect.width) * 100;
    var y = ((e.clientY - cardRect.top) / cardRect.height) * 100;
    hoverCard.style.setProperty('--fx-x', Math.max(0, Math.min(100, x)).toFixed(1) + '%');
    hoverCard.style.setProperty('--fx-y', Math.max(0, Math.min(100, y)).toFixed(1) + '%');
  }

  function bindCards() {
    document.addEventListener('pointerover', function (e) {
      if (!enabled) return;
      var el = e.target && e.target.closest ? e.target.closest(CARDS) : null;
      if (!el || el === hoverCard) return;
      hoverCard = el;
      cardRect = el.getBoundingClientRect();
    }, { passive: true });

    document.addEventListener('pointerout', function (e) {
      if (!hoverCard) return;
      if (e.relatedTarget && hoverCard.contains(e.relatedTarget)) return;
      hoverCard = null;
      cardRect = null;
    }, { passive: true });

    document.addEventListener('pointermove', cardMove, { passive: true });
  }

  /* ------------------------------------------------------------ 按鍵漣漪 */
  function bindRipple() {
    document.addEventListener('pointerdown', function (e) {
      if (!enabled) return;
      var el = e.target && e.target.closest ? e.target.closest(BUTTONS) : null;
      if (!el || el.disabled) return;
      if (noHover && e.pointerType === 'mouse') return;
      var rect = el.getBoundingClientRect();
      var dot = document.createElement('span');
      dot.className = 'fx-ripple';
      dot.style.left = (e.clientX - rect.left) + 'px';
      dot.style.top = (e.clientY - rect.top) + 'px';
      el.appendChild(dot);
      dot.addEventListener('animationend', function () {
        if (dot.parentNode) dot.parentNode.removeChild(dot);
      });
      window.setTimeout(function () {                     // 保險：動畫事件沒觸發時也要清掉
        if (dot.parentNode) dot.parentNode.removeChild(dot);
      }, 1200);
    }, { passive: true });
  }

  /* -------------------------------------------------------------- 開關按鈕 */
  function apply() {
    root.classList.toggle('fx-on', !!enabled);
    var btn = document.getElementById('fxBtn');
    if (btn) {
      btn.setAttribute('aria-pressed', enabled ? 'true' : 'false');
      btn.title = enabled ? '視覺特效：開（點一下關閉）' : '視覺特效：關（點一下開啟）';
      btn.textContent = enabled ? '✨' : '✦';
    }
    if (!enabled) {
      root.style.removeProperty('--fx-mx');
      root.style.removeProperty('--fx-my');
    }
  }

  function toggle() {
    enabled = !enabled;
    try { localStorage.setItem(KEY, enabled ? 'on' : 'off'); } catch (e) { /* 無痕模式 */ }
    apply();
  }

  function bindToggle() {
    var top = document.querySelector('.topbar');
    var theme = document.getElementById('themeBtn');
    if (!top || !theme || document.getElementById('fxBtn')) return;
    var btn = document.createElement('button');
    btn.id = 'fxBtn';
    btn.type = 'button';
    btn.className = 'icon-btn fx-btn';
    btn.setAttribute('aria-pressed', enabled ? 'true' : 'false');
    btn.addEventListener('click', toggle);
    theme.parentNode.insertBefore(btn, theme);
  }

  /* ------------------------------------------------------------------ 起始 */
  function init() {
    injectStyle();
    if (!document.querySelector('.topbar')) return;        // 不是網站頁面就安靜結束
    injectLayers();
    bindToggle();
    bindCards();
    bindRipple();
    document.addEventListener('pointermove', onMove, { passive: true });
    apply();
  }

  window.LOLFx = {                       // 方便在 console 或測試中使用
    get enabled() { return enabled; },
    on: function () { enabled = true; try { localStorage.setItem(KEY, 'on'); } catch (e) {} apply(); },
    off: function () { enabled = false; try { localStorage.setItem(KEY, 'off'); } catch (e) {} apply(); },
    toggle: toggle
  };

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
