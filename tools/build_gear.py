#!/usr/bin/env python3
"""
把「戰術商城」換成「裝備合成系統」（guides.html）。
資料來源：assets/lol/gear.json（由 build_extra.py 產生，含圖示、價格、官方說明、合成路徑）
功能：搜尋／類型篩選／價格排序、加入 6 格合成計畫、總金額、合成路徑（組件 → 成品）、四語。
"""
import io
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.environ.get('LOL_SITE') or (_HERE if os.path.exists(os.path.join(_HERE, 'index.html')) else os.path.dirname(_HERE))
ASSETS = os.path.join(SITE, 'assets', 'lol')

with io.open(os.path.join(ASSETS, 'gear.json'), encoding='utf-8') as fh:
    GEAR = json.load(fh)
ITEMS = GEAR['items']
VER = GEAR['version']

HTML = '''<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <meta name="color-scheme" content="dark light">
    <meta name="theme-color" content="#05080d">
    <title>LOL 攻略站 V6.0 - 裝備合成系統</title>
    <link rel="stylesheet" href="style.css">
    <link rel="stylesheet" href="guides.css">
</head>
<body class="bg-items">
    <header class="topbar">
        <div class="brand">SUMMONER'S <span>GUIDE</span><b>V6.0</b></div>
        <nav>
            <a href="index.html">首頁</a>
            <a href="champions.html">英雄攻略</a>
            <a href="items.html">裝備攻略</a>
            <a href="guides.html" style="color: #00d9ff; font-weight: 800;">裝備合成</a>
        </nav>
        <button class="icon-btn" id="themeBtn">☀️</button>
    </header>

    <main class="gb-wrap">
        <section class="gb-hero">
            <small>ITEM BUILDER &middot; PATCH __VER__</small>
            <h1>裝備合成 <em>系統</em></h1>
            <p>__COUNT__ 件可購買道具的價格、官方說明與<strong>合成路徑</strong>。點道具加入右側的合成計畫，
               會自動列出它的組件（合成來源）並計算總金額；純瀏覽器端計算，不需要連外。</p>
            <div class="gb-hero__pills">
                <span>__COUNT__ 件道具</span>
                <span>__RECIPES__ 件有合成路徑</span>
                <span>6 格合成計畫</span>
                <span>Patch __VER__</span>
            </div>
        </section>

        <div class="gb-layout">
            <section class="gb-list">
                <div class="gb-toolbar">
                    <div class="gb-searchbox">
                        <span class="gb-searchbox__icon" aria-hidden="true">🔍</span>
                        <input type="search" id="gbSearch" placeholder="搜尋道具名稱或說明" aria-label="搜尋道具" autocomplete="off">
                        <button type="button" id="gbFind" class="gb-find">搜尋</button>
                        <button type="button" id="gbReset" class="gb-reset" title="清除" aria-label="清除">✕</button>
                    </div>
                    <select id="gbType" aria-label="依類型篩選"></select>
                    <select id="gbSort" aria-label="排序">
                        <option value="gold-asc">價格：低到高</option>
                        <option value="gold-desc">價格：高到低</option>
                        <option value="name">名稱</option>
                    </select>
                </div>
                <p class="gb-count" id="gbCount">載入中…</p>
                <div class="gb-grid" id="gbGrid"></div>
                <p class="gb-empty" id="gbEmpty" hidden>沒有符合條件的道具。</p>
            </section>

            <aside class="gb-plan">
                <h2>合成計畫 <em id="gbPlanCount">0／6</em></h2>
                <div class="gb-slots" id="gbSlots"></div>
                <p class="gb-total">總金額 <b id="gbTotal">0</b> 金幣</p>
                <button type="button" class="gb-clear" id="gbClear">清空計畫</button>
                <div class="gb-paths" id="gbPaths"></div>
            </aside>
        </div>

        <div class="notice">
            📌 <b>資料說明：</b> 道具圖示、價格與官方說明取自 Riot 官方 Data Dragon <b>__VER__</b>（zh_TW），
            已下載到 <b>assets/lol/</b>。本頁為非商業的合成查詢工具，純瀏覽器端計算、不牽涉任何交易。
        </div>
    </main>

    <footer>
        <div>&copy; 2026 LOL 攻略站。LOL 攻略站是在 Riot Games 的「法律通則」方針下利用該公司擁有的資產所製作。Riot Games 不為此專案提供背書或贊助。</div>
        <div>資料基於 Patch __VER__（Riot 官方 Data Dragon）· 僅供遊戲參考 · 非官方粉絲網站</div>
        <div>本站為靜態攻略資料庫，未串接 Riot API，不提供即時戰績或牌位查詢。</div>
    </footer>

    <script src="script.js"></script>
    <script src="nav.js" defer></script>
    <script src="fx.js" defer></script>
    <script src="i18n.js" defer></script>
    <script src="state.js" defer></script>
    <script src="guides.js" defer></script>
    <!-- 讓更新立即生效：HTML 網路優先 -->
    <script>if('serviceWorker' in navigator){window.addEventListener('load',function(){navigator.serviceWorker.register('sw.js').catch(function(){});});}</script>
</body>
</html>
'''

CSS = '''/* 裝備合成系統（guides.html）— 由 tools/build_gear.py 產生 */
.gb-wrap { width: min(1240px, 92%); margin: 30px auto 0; }
.gb-hero { position: relative; overflow: hidden; padding: 32px; border: 1px solid #22323d; border-radius: 18px;
  background: radial-gradient(120% 140% at 10% 0%, rgba(0,217,255,.14), transparent 60%),
              radial-gradient(100% 120% at 90% 100%, rgba(200,170,110,.16), transparent 60%), #0b1117; }
.gb-hero small { color: #00d9ff; letter-spacing: 2.2px; font-weight: 800; font-size: 11px; }
.gb-hero h1 { margin: 10px 0 12px; font-size: clamp(30px, 4.4vw, 46px); color: #f0eadb; }
.gb-hero h1 em { font-style: normal; color: #c8aa6e; }
.gb-hero p { max-width: 74ch; margin: 0; color: #aab4bc; }
.gb-hero__pills { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 16px; }
.gb-hero__pills span { padding: 6px 12px; font-size: 12px; font-weight: 700; color: #9ddff0;
  background: rgba(9,20,28,.66); border: 1px solid rgba(98,170,190,.35); border-radius: 999px; }

.gb-layout { display: grid; grid-template-columns: minmax(0, 1fr) 320px; gap: 18px; margin-top: 22px; align-items: start; }
.gb-toolbar { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; margin-bottom: 8px; }
.gb-searchbox { flex: 1 1 260px; display: flex; align-items: center; gap: 6px; padding: 4px 4px 4px 12px;
  background: #080e14; border: 1px solid #2b3a45; border-radius: 12px; }
.gb-searchbox:focus-within { border-color: #00d9ff; box-shadow: 0 0 0 3px rgba(0,217,255,.12); }
.gb-searchbox__icon { font-size: 14px; opacity: .75; }
.gb-searchbox input[type="search"] { flex: 1 1 auto; min-width: 0; padding: 8px 2px; color: #e8e4d9;
  background: transparent; border: 0; outline: none; font: inherit; }
.gb-searchbox .gb-find { padding: 8px 16px; font-size: 13px; font-weight: 800; color: #071016;
  background: linear-gradient(180deg,#d8bd80,#c8aa6e); border: 0; border-radius: 9px; cursor: pointer; }
.gb-searchbox .gb-reset { display: none; padding: 8px 10px; font-size: 13px; color: #9da9b2;
  background: #111d26; border: 1px solid #2b3a45; border-radius: 9px; cursor: pointer; }
.gb-searchbox.has-query .gb-reset { display: inline-block; }
.gb-toolbar select { padding: 11px 14px; color: #e8e4d9; background: #080e14;
  border: 1px solid #2b3a45; border-radius: 10px; }
.gb-count { margin: 4px 0 14px; color: #8e9aa4; font-size: 13px; }
.gb-empty { text-align: center; padding: 26px; color: #76838d; }

.gb-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(232px, 1fr)); gap: 10px; }
.gb-item { display: flex; gap: 10px; padding: 10px; text-align: left; font: inherit; color: inherit;
  background: linear-gradient(180deg,#101922,#0b1117); border: 1px solid #253540; border-radius: 12px; cursor: pointer;
  transition: transform .18s ease, border-color .18s ease; }
.gb-item:hover { transform: translateY(-2px); border-color: #00d9ff; }
.gb-item.is-picked { border-color: #c8aa6e; box-shadow: inset 0 0 0 1px rgba(200,170,110,.35); }
.gb-item img { width: 44px; height: 44px; flex: 0 0 auto; border-radius: 10px; border: 1px solid #2b3a45; background: #0a1016; }
.gb-item b { display: block; font-size: 13.5px; color: #f0eadb; }
.gb-item .gold { color: #c8aa6e; font-weight: 800; font-size: 12.5px; }
.gb-item p { margin: 3px 0 0; font-size: 11.5px; line-height: 1.5; color: #8e9aa4; }
.gb-item .tags { margin-top: 5px; display: flex; flex-wrap: wrap; gap: 4px; }
.gb-item .tags .tag { font-size: 10px; padding: 2px 6px; margin: 0; }

.gb-plan { position: sticky; top: 130px; padding: 16px; background: linear-gradient(180deg,#101922,#0b1117);
  border: 1px solid #253540; border-radius: 16px; }
.gb-plan h2 { margin: 0 0 12px; font-size: 17px; color: #f0eadb; }
.gb-plan h2 em { font-style: normal; color: #c8aa6e; font-size: 13px; margin-left: 6px; }
.gb-slots { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }
.gb-slot { aspect-ratio: 1; display: grid; place-items: center; background: #0a1016;
  border: 1px dashed #2b3a45; border-radius: 10px; font-size: 11px; color: #56636d; }
.gb-slot img { width: 80%; height: 80%; border-radius: 8px; }
.gb-slot.filled { border-style: solid; border-color: #2f4d5c; }
.gb-slot button { all: unset; cursor: pointer; display: grid; place-items: center; width: 100%; height: 100%; }
.gb-total { margin: 14px 0 10px; font-size: 13px; color: #aab4bc; }
.gb-total b { color: #c8aa6e; font-size: 17px; }
.gb-clear { width: 100%; padding: 9px; font-size: 13px; color: #9da9b2; background: #111d26;
  border: 1px solid #2b3a45; border-radius: 9px; cursor: pointer; }
.gb-clear:hover { color: #fff; border-color: #00d9ff; }
.gb-paths { margin-top: 14px; }
.gb-path { padding: 10px; margin-bottom: 8px; background: rgba(0,217,255,.05);
  border-left: 3px solid #c8aa6e; border-radius: 0 10px 10px 0; }
.gb-path b { display: block; font-size: 12.5px; color: #e8cf9c; margin-bottom: 6px; }
.gb-path .parts { display: flex; flex-wrap: wrap; align-items: center; gap: 6px; font-size: 11px; color: #9da9b2; }
.gb-path .parts img { width: 26px; height: 26px; border-radius: 6px; border: 1px solid #2b3a45; background: #0a1016; }
.gb-path .parts span { display: inline-flex; align-items: center; gap: 4px; }
.gb-path .none { font-size: 11.5px; color: #6f7c86; }

@media (max-width: 900px) {
  .gb-layout { grid-template-columns: 1fr; }
  .gb-plan { position: static; }
  .gb-grid { grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); }
}
@media (max-width: 560px) {
  .gb-hero { padding: 20px; }
  .gb-grid { grid-template-columns: 1fr; }
  .gb-toolbar select, .gb-searchbox { flex: 1 1 100%; width: 100%; }
}
@media (hover: none) { .gb-item:hover { transform: none; } }
'''

JS = '''/* 裝備合成系統前端（guides.html）— 由 tools/build_gear.py 產生 */
(function () {
  'use strict';
  var ITEMS = __DATA__, DATA = ITEMS, plan = [], out = [];
  function $(id) { return document.getElementById(id); }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
    return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  var byName = {}, byId = {};
  ITEMS.forEach(function (it) { byName[(it.name || it.n)] = it; byId[it.id] = it; });

  function card(it) {
    var picked = plan.indexOf(it.id) >= 0;
    return '<button type="button" class="gb-item' + (picked ? ' is-picked' : '') + '" data-id="' + esc(it.id) + '"' +
      ' data-name="' + esc((it.name || it.n) + ' ' + (it.en || '') + ' ' + it.desc + ' ' + (it.tags || []).join(' ')) + '"' +
      ' data-tags="' + esc((it.tags || []).join(' ')) + '" data-gold="' + it.gold + '">' +
      '<img src="' + esc(it.icon) + '" alt="' + esc(it.name || it.n) + '" loading="lazy">' +
      '<span><b>' + esc(it.name || it.n) + '</b><span class="gold">' + it.gold + ' 金幣</span>' +
      '<p>' + esc(it.desc) + '</p>' +
      '<span class="tags">' + (it.tags || []).map(function (t) { return '<span class="tag">' + esc(t) + '</span>'; }).join('') + '</span>' +
      '</span></button>';
  }

  function render() {
    $('gbGrid').innerHTML = ITEMS.map(card).join('');
    var counts = {};
    ITEMS.forEach(function (it) { (it.tags || []).forEach(function (t) { counts[t] = (counts[t] || 0) + 1; }); });
    var keys = Object.keys(counts).sort(function (a, b) { return counts[b] - counts[a]; });
    $('gbType').innerHTML = '<option value="all">全部類型（' + keys.length + '）</option>' +
      keys.map(function (k) { return '<option value="' + esc(k) + '">' + esc(k) + '（' + counts[k] + '）</option>'; }).join('');
    $('gbSort').addEventListener('change', apply);
    $('gbType').addEventListener('change', apply);
    $('gbGrid').addEventListener('click', function (e) {
      var b = e.target.closest ? e.target.closest('.gb-item') : null;
      if (!b) return;
      toggle(b.dataset.id);
    });
    apply();
    renderPlan();
  }

  function apply() {
    var q = ($('gbSearch').value || '').toLowerCase().trim();
    var type = $('gbType').value;
    var sort = $('gbSort').value;
    var list = ITEMS.filter(function (it) {
      var okQ = !q || ((it.name || it.n) + ' ' + (it.en || '') + ' ' + it.desc + ' ' + (it.tags || []).join(' ')).toLowerCase().indexOf(q) >= 0;
      var okT = type === 'all' || (it.tags || []).indexOf(type) >= 0;
      return okQ && okT;
    });
    if (sort === 'gold-desc') list = list.slice().sort(function (a, b) { return b.gold - a.gold; });
    else if (sort === 'name') list = list.slice().sort(function (a, b) { return a.n.localeCompare(b.n); });
    else list = list.slice().sort(function (a, b) { return a.gold - b.gold; });
    $('gbGrid').innerHTML = list.map(card).join('');
    $('gbCount').textContent = '顯示 ' + list.length + ' 件道具（共 ' + ITEMS.length + ' 件）' + (q ? '（關鍵字：' + q + '）' : '');
    $('gbEmpty').hidden = list.length !== 0;
    var sb = document.querySelector('.gb-searchbox');
    if (sb) sb.classList.toggle('has-query', !!q);
  }

  function toggle(id) {
    if (!byId[id]) return;                      // 資料不存在就不加入
    var i = plan.indexOf(id);
    if (i >= 0) plan.splice(i, 1);
    else { if (plan.length >= 6) plan.shift(); plan.push(id); }
    Array.prototype.forEach.call(document.querySelectorAll('.gb-item'), function (b) {
      b.classList.toggle('is-picked', plan.indexOf(b.dataset.id) >= 0);
    });
    renderPlan();
  }

  function renderPlan() {
    // 防護：只保留查得到的道具，計數一律以實際渲染出的為準
    plan = plan.filter(function (id) { return !!byId[id]; });
    var slots = [];
    for (var i = 0; i < 6; i++) {
      var it = plan[i] ? byId[plan[i]] : null;
      slots.push('<div class="gb-slot' + (it ? ' filled' : '') + '">' +
        (it ? '<button type="button" data-remove="' + esc(it.id) + '" title="移除"><img src="' + esc(it.icon) + '" alt="' + esc(it.name || it.n) + '"></button>' : (i + 1)) + '</div>');
    }
    $('gbSlots').innerHTML = slots.join('');
    $('gbPlanCount').textContent = plan.length + '／6';
    var total = plan.reduce(function (n, id) { return n + (byId[id] ? byId[id].gold : 0); }, 0);
    $('gbTotal').textContent = total;
    var paths = plan.map(function (id) {
      var it = byId[id];
      if (!it) return '';
      var from = (it.from || []);
      var parts = from.length
        ? from.map(function (n) { var c = byName[n]; return '<span>' + (c ? '<img src="' + esc(c.icon) + '" alt="">' : '') + esc(n) + '</span>'; }).join('<i>＋</i>')
        : '<span class="none">此道具沒有合成組件（可直接購買）</span>';
      return '<div class="gb-path"><b>' + esc(it.name || it.n) + '（' + it.gold + '）</b><div class="parts">' + parts + '</div></div>';
    }).join('');
    $('gbPaths').innerHTML = paths;
  }

  document.addEventListener('DOMContentLoaded', function () {
    if (!$('gbGrid')) return;
    render();
    $('gbSearch').addEventListener('input', apply);
    $('gbSearch').addEventListener('keydown', function (e) { if (e.key === 'Enter') { e.preventDefault(); apply(); } });
    $('gbFind').addEventListener('click', apply);
    $('gbReset').addEventListener('click', function () { $('gbSearch').value = ''; apply(); });
    $('gbClear').addEventListener('click', function () { plan = []; renderPlan(); Array.prototype.forEach.call(document.querySelectorAll('.gb-item'), function (b) { b.classList.remove('is-picked'); }); });
    $('gbSlots').addEventListener('click', function (e) {
      var b = e.target.closest ? e.target.closest('[data-remove]') : null;
      if (b) toggle(b.dataset.remove);
    });
  });
})();
'''

def main():
    recipes = sum(1 for it in ITEMS if it.get('from'))
    html = (HTML.replace('__VER__', VER)
                .replace('__COUNT__', str(len(ITEMS)))
                .replace('__RECIPES__', str(recipes)))
    with io.open(os.path.join(SITE, 'guides.html'), 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(html)
    with io.open(os.path.join(SITE, 'guides.css'), 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(CSS)
    with io.open(os.path.join(SITE, 'guides.js'), 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(JS.replace('__DATA__', json.dumps(ITEMS, ensure_ascii=False, separators=(',', ':'))))
    print('  已寫入 guides.html（裝備合成系統，%d 件道具、%d 件有合成路徑）' % (len(ITEMS), recipes))
    print('  已寫入 guides.css / guides.js')


if __name__ == '__main__':
    sys.exit(main())
