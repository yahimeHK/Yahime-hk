/* ==========================================================================
   LOL 攻略站 — 分類導覽列（七個分類分頁）
   注入在 topbar 之後，所有頁面共用；目前頁面會自動標記。
   ========================================================================== */
(function () {
  'use strict';
  var PAGES = [
    ['skins.html', '角色造型'],
    ['gallery.html', '圖片'],
    ['abilities.html', '技能圖片'],
    ['maps.html', '地圖'],
    ['runes.html', '符文'],
    ['gear.html', '核心裝備'],
    ['tactics.html', '戰術解析']
  ];
  function build() {
    if (document.querySelector('.subnav')) return;
    var top = document.querySelector('.topbar');
    if (!top) return;
    var here = location.pathname.split('/').pop() || 'index.html';
    var links = PAGES.map(function (p) {
      var on = (p[0] === here) ? ' class="is-here"' : '';
      return '<a href="' + p[0] + '"' + on + '>' + p[1] + '</a>';
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
