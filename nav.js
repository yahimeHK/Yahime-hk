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
    ['gallery.html', '圖片', '🖼️'],
    ['abilities.html', '技能圖片', '⚡'],
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


/* ================= 主導覽下拉選單（比照 Riot 官網分類選單） ================= */
(function () {
  var nav = document.querySelector('.topbar nav');
  if (!nav) return;
  var links = Array.prototype.slice.call(nav.querySelectorAll('a'));
  if (links.length < 2) return;

  var here = (location.pathname.split('/').pop() || 'index.html').toLowerCase();
  var cur = null;
  links.forEach(function (a) { if ((a.getAttribute('href') || '').toLowerCase() === here) cur = a; });
  if (!cur) cur = links[0];

  var label = (cur.textContent || '').replace(/\s+/g, ' ').trim();
  nav.classList.add('navdd');
  nav.setAttribute('aria-label', '主選單');
  nav.innerHTML = '';

  var btn = document.createElement('button');
  btn.type = 'button';
  btn.className = 'navdd__btn';
  btn.setAttribute('aria-haspopup', 'true');
  btn.setAttribute('aria-expanded', 'false');
  btn.innerHTML = '<span class="navdd__label"></span><i class="navdd__caret" aria-hidden="true">▾</i>';
  btn.querySelector('.navdd__label').textContent = label;

  var panel = document.createElement('div');
  panel.className = 'navdd__panel';
  panel.setAttribute('role', 'menu');
  links.forEach(function (a) {
    var b = document.createElement('a');
    b.href = a.getAttribute('href');
    b.textContent = (a.textContent || '').trim();
    b.setAttribute('role', 'menuitem');
    if (a === cur) { b.className = 'is-current'; b.setAttribute('aria-current', 'page'); }
    panel.appendChild(b);
  });

  nav.appendChild(btn);
  nav.appendChild(panel);

  function close() {
    nav.classList.remove('is-open');
    btn.setAttribute('aria-expanded', 'false');
  }
  function open() {
    nav.classList.add('is-open');
    btn.setAttribute('aria-expanded', 'true');
  }
  btn.addEventListener('click', function (e) {
    e.stopPropagation();
    if (nav.classList.contains('is-open')) close(); else open();
  });
  document.addEventListener('click', function (e) { if (!nav.contains(e.target)) close(); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') close(); });
  panel.addEventListener('click', function () { setTimeout(close, 60); });

  var st = document.createElement('style');
  st.textContent = [
    '.topbar nav.navdd{position:relative;display:flex;align-items:center;gap:0;overflow:visible}',
    '.navdd__btn{display:inline-flex;align-items:center;gap:7px;padding:9px 14px;font:inherit;font-size:14px;font-weight:800;',
    'color:#e8f4f8;background:linear-gradient(180deg,rgba(20,34,44,.95),rgba(11,17,23,.95));',
    'border:1px solid rgba(98,170,190,.4);border-radius:10px;cursor:pointer;transition:border-color .18s ease,color .18s ease}',
    '.navdd__btn:hover{border-color:#00d9ff;color:#fff}',
    '.navdd__caret{font-style:normal;font-size:10px;color:#c8aa6e;transition:transform .2s ease}',
    'nav.is-open .navdd__caret{transform:rotate(180deg)}',
    '.navdd__panel{display:none;position:absolute;top:calc(100% + 10px);right:0;min-width:196px;padding:8px;z-index:120;',
    'background:linear-gradient(180deg,#111c24,#0a1016);border:1px solid rgba(98,170,190,.4);border-radius:12px;',
    'box-shadow:0 26px 60px -30px rgba(0,0,0,1),0 0 0 1px rgba(0,0,0,.5);',
    'opacity:0;transform:translateY(-6px);transition:opacity .18s ease,transform .18s ease}',
    'nav.is-open .navdd__panel{display:block !important;visibility:visible !important;opacity:1 !important;transform:translateY(0)}',
    '.navdd__panel a{display:block;padding:11px 14px;font-size:14px;font-weight:600;color:#c9d6dd;text-decoration:none;border-radius:8px}',
    '.navdd__panel a:hover{color:#fff;background:rgba(0,217,255,.12)}',
    '.navdd__panel a.is-current{color:#00d9ff;background:rgba(0,217,255,.08)}',
    '.navdd__panel a.is-current::after{content:"●";float:right;font-size:8px;color:#c8aa6e;line-height:20px}',
    '@media (max-width:430px){.navdd__btn{padding:8px 11px;font-size:13px}.navdd__panel{min-width:176px}}',
    '@media (prefers-reduced-motion:reduce){.navdd__panel,.navdd__caret{transition:none}}'
  ].join('');
  document.head.appendChild(st);

  window.LOLNav = { open: open, close: close };
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