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
