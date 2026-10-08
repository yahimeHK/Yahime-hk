/* ==========================================================================
   LOL 攻略站 — 分類導覽列（七個分類分頁）
   --------------------------------------------------------------------------
   1. 由 JS 注入在 topbar 之後，所有頁面共用
   2. 樣式直接內嵌在這裡（不依賴 style.css），避免瀏覽器快取舊的 CSS 時
      只看得到文字、間距全擠在一起
   ========================================================================== */
(function () {
  'use strict';

  var PAGES = [
    ['skins.html', '角色造型', '🎨'],
    ['gallery.html', '美術圖', '🖼️'],
    ['champions.html', '英雄攻略', '🎯'],
    ['maps.html', '地圖', '🗺️'],
    ['runes.html', '符文', '🔯'],
    ['gear.html', '核心裝備', '🛡️'],
    ['tactics.html', '戰術解析', '🎯']
  ];

  var CSS = [
    '.subnav{position:sticky;top:64px;z-index:45;background:rgba(5,8,13,.94);border-bottom:1px solid #1d2a33;',
    'box-shadow:0 10px 24px -18px rgba(0,0,0,.95);backdrop-filter:blur(12px)}',
    '.subnav__inner{width:min(1200px,90%);margin:0 auto;display:flex;align-items:center;gap:8px;',
    'padding:10px 0;overflow-x:auto;flex-wrap:nowrap;scrollbar-width:none;-ms-overflow-style:none}',
    '.subnav__inner::-webkit-scrollbar{display:none}',
    '.subnav__label{flex:0 0 auto;display:inline-flex;align-items:center;gap:6px;margin-right:4px;',
    'padding:5px 11px;font-size:11px;font-weight:800;letter-spacing:1.4px;text-transform:uppercase;',
    'color:#9ddff0;background:rgba(0,217,255,.08);border:1px solid rgba(98,170,190,.35);border-radius:999px}',
    '.subnav a{flex:0 0 auto;display:inline-flex;align-items:center;gap:6px;padding:7px 14px;font-size:13.5px;',
    'line-height:1.2;color:#aab4be;text-decoration:none;white-space:nowrap;border:1px solid transparent;',
    'border-radius:999px;transition:color .18s,background .18s,border-color .18s}',
    '.subnav a i{font-style:normal;font-size:13px;line-height:1;opacity:.9}',
    '.subnav a:hover{color:#fff;background:#111d26;border-color:#2a4a58}',
    '.subnav a.is-here{color:#071016;background:#c8aa6e;border-color:#c8aa6e;font-weight:800}',
    '.subnav a.is-here i{opacity:1}',
    '@media (max-width:900px){.subnav__inner{gap:6px}.subnav a{padding:7px 12px;font-size:13px}}',
    '@media (max-width:700px){',
    '.subnav{top:56px}',
    '.subnav__inner{width:94%;gap:6px;padding:8px 0;',
    '-webkit-mask-image:linear-gradient(90deg,#000 88%,transparent);mask-image:linear-gradient(90deg,#000 88%,transparent)}',
    '.subnav__label{display:none}',
    '.subnav a{padding:6px 11px;font-size:12.5px}',
    '.subnav a i{font-size:12px}',
    '}'
  ].join('');

  function build() {
    if (document.querySelector('.subnav')) return;
    var top = document.querySelector('.topbar');
    if (!top) return;

    if (!document.getElementById('subnav-style')) {
      var style = document.createElement('style');
      style.id = 'subnav-style';
      style.textContent = CSS;
      document.head.appendChild(style);
    }

    var here = (location.pathname.split('/').pop() || 'index.html').toLowerCase();
    var links = PAGES.map(function (p) {
      var cls = (p[0] === here) ? ' class="is-here"' : '';
      return '<a href="' + p[0] + '"' + cls + '><i>' + p[2] + '</i>' + p[1] + '</a>';
    }).join('');

    var nav = document.createElement('nav');
    nav.className = 'subnav';
    nav.setAttribute('aria-label', '分類資料庫');
    nav.innerHTML = '<div class="subnav__inner"><span class="subnav__label">分類資料庫</span>' + links + '</div>';
    top.parentNode.insertBefore(nav, top.nextSibling);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', build);
  else build();
})();


/* ================= 主選單整併進「分類資料庫」那一列 ================= */
(function () {
  var nav = document.querySelector('.topbar nav');
  var sub = document.querySelector('.subnav__inner') || document.querySelector('.subnav');
  if (!nav || !sub) return;

  var here = (location.pathname.split('/').pop() || 'index.html').toLowerCase();
  var items = [];
  function push(href, label, icon) {
    if (!href) return;
    for (var k = 0; k < items.length; k++) { if (items[k].href.toLowerCase() === href.toLowerCase()) return; }
    items.push({ href: href, label: label, icon: icon });
  }

  // 1) 原本頂欄的四項
  Array.prototype.forEach.call(nav.querySelectorAll('a'), function (a) {
    if ((a.getAttribute('href') || '').toLowerCase() === 'index.html') return;   // 首頁已由品牌按鈕提供
    push(a.getAttribute('href'), (a.textContent || '').replace(/\s+/g, ' ').trim(), '');
  });
  // 2) 原本分類資料庫的各項（含圖示）
  Array.prototype.forEach.call(sub.querySelectorAll('a'), function (a) {
    var el = a.querySelector('i');
    var icon = el ? (el.textContent || '').trim() : '';
    var label = (a.textContent || '').replace(/\s+/g, ' ').trim();
    if (icon && label.indexOf(icon) === 0) label = label.slice(icon.length).trim();
    push(a.getAttribute('href'), label, icon);
  });

  // 3) 重建分類列（保留「分類資料庫」標題），主選單置前
    // 依指定順序排列（1 英雄攻略 2 裝備攻略 3 裝備合成 4 符文 5 核心裝備 6 戰術解析 7 地圖 8 角色造型 9 美術圖）
  var ORDER = ['champions.html','items.html','guides.html','runes.html','gear.html','tactics.html','maps.html','skins.html','gallery.html'];
  items.sort(function (x, y) {
    var ix = ORDER.indexOf(x.href.toLowerCase()), iy = ORDER.indexOf(y.href.toLowerCase());
    if (ix < 0) ix = 99; if (iy < 0) iy = 99;
    return ix - iy;
  });
  Array.prototype.forEach.call(sub.querySelectorAll('a'), function (a) { a.parentNode.removeChild(a); });
  sub.insertAdjacentHTML('beforeend', items.map(function (it) {
    var cur = it.href.toLowerCase() === here ? ' class="is-current"' : '';
    var icon = it.icon ? '<i aria-hidden="true">' + it.icon + '</i>' : '';
    return '<a href="' + it.href + '"' + cur + '>' + icon + it.label + '</a>';
  }).join(''));

  // 4) 頂欄選單已整併，隱藏避免重複
  nav.style.display = 'none';
  nav.setAttribute('aria-hidden', 'true');
})();

/* ================= 品牌字做成「回到首頁」按鈕 ================= */
(function () {
  var brand = document.querySelector('.topbar .brand');
  if (!brand || brand.tagName === 'A') return;
  var a = document.createElement('a');
  a.className = (brand.className || '') + ' brand--link';
  a.href = 'index.html';
  a.title = 'Home';
  a.setAttribute('aria-label', 'Home');
  a.innerHTML = brand.innerHTML;
  brand.parentNode.replaceChild(a, brand);

  var st = document.createElement('style');
  st.textContent = [
    '.brand--link{display:inline-flex;align-items:center;gap:8px;padding:7px 12px;text-decoration:none;cursor:pointer;',
    'border:1px solid rgba(98,170,190,.35);border-radius:10px;background:rgba(12,20,27,.6);',
    '-webkit-tap-highlight-color:rgba(0,217,255,.15);transition:background .18s ease,box-shadow .18s ease,border-color .18s ease}',
    '.brand--link:hover{background:rgba(0,217,255,.12);border-color:#00d9ff;box-shadow:0 0 18px -8px rgba(0,217,255,.7)}',
    '.brand--link:active{transform:translateY(1px)}',
    '.brand--link:focus-visible{outline:2px solid #00d9ff;outline-offset:2px}',
    '@media (max-width:430px){.brand--link{padding:5px 8px;gap:5px}}',
    '@media (prefers-reduced-motion:reduce){.brand--link{transition:none}}'
  ].join('');
  document.head.appendChild(st);
})();

/* ================= 把頂欄圖示鈕集中到最右側容器 ================= */
(function () {
  var ICON_SEL = '.icon-btn, #fxBtn, #langBtn, #themeBtn, #navBtn';
  function group() {
    var tb = document.querySelector('.topbar');
    if (!tb) return;
    var right = tb.querySelector('.topbar__right');
    if (!right) {
      right = document.createElement('div');
      right.className = 'topbar__right';
      tb.appendChild(right);
      var st = document.createElement('style');
      st.textContent = '.topbar{display:flex;align-items:center;flex-wrap:nowrap}'
        + '.topbar__right{margin-left:auto;display:flex;align-items:center;gap:8px;flex:0 0 auto}';
      document.head.appendChild(st);
    }
    Array.prototype.slice.call(tb.querySelectorAll(ICON_SEL)).forEach(function (el) {
      if (el.parentNode !== right) right.appendChild(el);
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', group);
  else group();
  [200, 600, 1500, 3000].forEach(function (ms) { setTimeout(group, ms); });
})();
/* ================= 分類列：外框與外框特效 ================= */
(function () {
  var st = document.createElement('style');
  st.textContent = [
    '.subnav__inner{display:flex;align-items:center;gap:8px;flex-wrap:nowrap;overflow-x:auto}',
    '.subnav__inner a{display:inline-flex;align-items:center;gap:6px;padding:8px 13px;white-space:nowrap;',
    'font-size:13.5px;font-weight:600;color:#c9d6dd;text-decoration:none;border:1px solid rgba(98,170,190,.30);',
    'border-radius:999px;background:linear-gradient(180deg,rgba(16,25,34,.92),rgba(9,14,20,.92));',
    'transition:border-color .18s ease,box-shadow .18s ease,transform .18s ease,color .18s ease,background .18s ease}',
    '.subnav__inner a i{font-style:normal;font-size:14px;line-height:1}',
    /* 外框特效：hover 青色光暈 ＋ 微微上浮 */
    '.subnav__inner a:hover{color:#fff;border-color:#00d9ff;transform:translateY(-1px);',
    'background:linear-gradient(180deg,rgba(12,32,42,.95),rgba(8,18,24,.95));',
    'box-shadow:0 0 0 1px rgba(0,217,255,.45),0 10px 26px -14px rgba(0,217,255,.75)}',
    '.subnav__inner a:active{transform:translateY(0)}',
    '.subnav__inner a:focus-visible{outline:2px solid #00d9ff;outline-offset:2px}',
    /* 目前頁面：金色外框 ＋ 內光 */
    '.subnav__inner a.is-current{color:#ffd98a;border-color:rgba(200,170,110,.75);',
    'background:linear-gradient(180deg,rgba(38,31,17,.95),rgba(19,15,8,.95));',
    'box-shadow:inset 0 0 0 1px rgba(200,170,110,.35),0 0 22px -12px rgba(200,170,110,.9)}',
    '@media (max-width:430px){.subnav__inner{gap:6px}.subnav__inner a{padding:6px 10px;font-size:12.5px}.subnav__inner a i{font-size:13px}}',
    '@media (prefers-reduced-motion:reduce){.subnav__inner a{transition:none}}'
  ].join('');
  document.head.appendChild(st);
})();
