#!/usr/bin/env python3
"""產生「裝備預算計算器」分頁（budget.html / budget.css / budget.js）。
   功能：輸入金幣 → 選裝備 → 設定數量（1–6）→ 即時計算總額、剩餘金幣、6 格使用量，
        並依情況給出回應（金幣不足／可以買／裝備欄已滿／核心裝成形／合成路徑）。
   資料來源：assets/lol/gear.json（220 件召喚峽谷現行裝備，已在本機）。"""
import io
import json
import os
import re
import sys

SITE = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
GEAR = os.path.join(SITE, 'assets', 'lol', 'gear.json')
with io.open(GEAR, encoding='utf-8') as fh:
    G = json.load(fh)
ITEMS = [{'id': str(i['id']), 'n': i['name'], 'en': i.get('en', ''), 'i': i['icon'],
          'g': i['gold'], 't': i.get('tags') or [], 'd': (i.get('desc') or '')[:60],
          'f': i.get('from') or []} for i in G['items']]

HTML = '''<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
    <meta name="color-scheme" content="dark light">
    <meta name="theme-color" content="#05080d">
    <title>LOL 攻略站 V6.0 - 裝備預算計算器</title>
    <link rel="stylesheet" href="style.css">
    <link rel="stylesheet" href="budget.css">
</head>
<body class="bg-items">
    <header class="topbar">
        <div class="brand">SUMMONER'S <span>GUIDE</span><b>V6.0</b></div>
        <nav>
            <a href="index.html">首頁</a>
            <a href="guide.html">英雄攻略</a>
            <a href="guides.html">裝備合成</a>
            <a href="budget.html" style="color:#00d9ff;font-weight:800">裝備預算</a>
        </nav>
        <button class="icon-btn" id="themeBtn">☀️</button>
    </header>

    <main class="items-wrap">
        <section class="items-hero">
            <small>BUILD BUDGET &middot; PATCH __VER__</small>
            <h1>裝備預算 <em>計算器</em></h1>
            <p>輸入你現在的金幣、挑選想買的裝備與數量，立即算出總額、剩餘金幣與 6 格使用量，
               並依情況告訴你可不可以買、還差多少、或是否已成形核心裝。</p>
            <div class="items-hero__pills">
                <span>__COUNT__ 件裝備</span>
                <span>即時計算</span>
                <span>數量 1–6</span>
                <span>純前端、離線可用</span>
            </div>
        </section>

        <div class="bd-layout">
            <section class="bd-pick">
                <div class="bd-toolbar">
                    <label class="bd-budget">
                        <span>我現在有</span>
                        <input type="number" id="bdGold" min="0" step="50" value="3000" inputmode="numeric">
                        <span>金幣</span>
                    </label>
                    <span class="bd-quick">
                        <button type="button" data-gold="-500">−500</button>
                        <button type="button" data-gold="+500">＋500</button>
                        <button type="button" data-gold="1000">1000</button>
                        <button type="button" data-gold="3000">3000</button>
                        <button type="button" data-gold="5000">5000</button>
                        <button type="button" data-gold="0" title="歸零">✕</button>
                    </span>
                    <input type="search" id="bdSearch" placeholder="搜尋裝備名稱或類型" autocomplete="off">
                    <select id="bdType" aria-label="依類型篩選"></select>
                    <select id="bdSort" aria-label="排序">
                        <option value="price-asc">價格：低到高</option>
                        <option value="price-desc">價格：高到低</option>
                        <option value="name">名稱</option>
                    </select>
                    <label class="bd-afford"><input type="checkbox" id="bdAfford"> 只顯示買得起</label>
                </div>
                <p class="bd-count" id="bdCount">載入中…</p>
                <div class="bd-grid" id="bdGrid"></div>
            </section>

            <aside class="bd-cart">
                <h2>已選裝備 <em id="bdSlots">0／6 格</em></h2>
                <div id="bdList" class="bd-list"></div>
                <div class="bd-total">
                    <div><span>總額</span><b id="bdSpent">0</b></div>
                    <div><span>剩餘</span><b id="bdLeft">0</b></div>
                    <div><span>裝備數量</span><b id="bdQty">0 件</b></div>
                </div>
                <div class="bd-reply idle" id="bdReply"></div>
                <button type="button" class="bd-clear" id="bdClear">清空</button>
            </aside>
        </div>

        <div class="notice">
            📌 <b>說明：</b> 本頁為<b>遊戲內金幣</b>的買裝試算工具，純瀏覽器端計算，不涉及任何真實交易。
            裝備資料取自 Riot 官方 Data Dragon <b>__VER__</b>（已下載到本機）。
        </div>
    </main>

    <footer>
        <div>&copy; 2026 LOL 攻略站。LOL 攻略站是在 Riot Games 的「法律通則」方針下利用該公司擁有的資產所製作。Riot Games 不為此專案提供背書或贊助。</div>
        <div>資料基於 Patch __VER__（Riot 官方 Data Dragon）· 僅供遊戲參考 · 非官方粉絲網站</div>
    </footer>

    <script src="nav.js?v=1" defer></script>
    <script src="fx.js?v=1" defer></script>
    <script src="i18n.js?v=1" defer></script>
    <script src="state.js?v=1" defer></script>
    <script src="budget.js?v=1" defer></script>
</body>
</html>
'''

CSS = '''/* 裝備預算計算器（由 tools/build_budget.py 產生） */
.bd-layout { display: grid; grid-template-columns: minmax(0, 1fr) 320px; gap: 18px; margin-top: 20px; align-items: start; }
.bd-toolbar { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; margin-bottom: 10px; }
.bd-budget { display: inline-flex; align-items: center; gap: 8px; padding: 8px 12px; font-size: 13px;
  color: #aab4bc; background: #080e14; border: 1px solid #2b3a45; border-radius: 12px; }
.bd-budget input { width: 92px; padding: 6px 8px; font-size: 15px; font-weight: 800; color: #ffd98a;
  background: #0e1720; border: 1px solid #2b3a45; border-radius: 8px; text-align: right; }
#bdSearch { flex: 1 1 200px; padding: 11px 14px; color: #e8e4d9; background: #080e14;
  border: 1px solid #2b3a45; border-radius: 10px; }

.bd-quick { display: inline-flex; flex-wrap: wrap; gap: 6px; align-items: center; }
.bd-quick button { padding: 8px 12px; font: inherit; font-size: 13px; font-weight: 700; cursor: pointer;
  color: #cfe7f0; background: linear-gradient(180deg,#16232d,#0e1720); border: 1px solid #2b3a45;
  border-radius: 999px; transition: border-color .16s ease, color .16s ease, transform .16s ease; }
.bd-quick button:hover { color: #fff; border-color: #00d9ff; transform: translateY(-1px); }
.bd-quick button:active { transform: translateY(0); }
@media (max-width: 560px) { .bd-quick { width: 100%; } .bd-quick button { flex: 1 1 auto; padding: 8px 6px; font-size: 12.5px; } }

.bd-toolbar select { padding: 11px 12px; color: #e8e4d9; background: #080e14; border: 1px solid #2b3a45; border-radius: 10px; }
.bd-afford { display: inline-flex; align-items: center; gap: 6px; padding: 9px 12px; font-size: 12.5px; font-weight: 700;
  color: #c9d6dd; background: #080e14; border: 1px solid #2b3a45; border-radius: 10px; cursor: pointer; user-select: none; }
.bd-afford input { accent-color: #00d9ff; width: 15px; height: 15px; }
.bd-afford:has(input:checked) { color: #9dffbf; border-color: rgba(74,222,128,.6); }
.bd-item { position: relative; }
.bd-item .have { position: absolute; top: 6px; right: 6px; min-width: 20px; height: 20px; padding: 0 5px;
  display: grid; place-items: center; font-size: 11px; font-weight: 900; color: #071016;
  background: linear-gradient(180deg,#d8bd80,#c8aa6e); border-radius: 999px; }
.bd-item.in-cart { border-color: rgba(200,170,110,.7); box-shadow: inset 0 0 0 1px rgba(200,170,110,.28); }
.bd-count { margin: 4px 0 12px; font-size: 12.5px; color: #8e9aa4; }
.bd-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(216px, 1fr)); gap: 10px; }
.bd-item { display: flex; gap: 10px; align-items: center; padding: 10px; text-align: left; font: inherit;
  color: inherit; background: linear-gradient(180deg,#101922,#0b1117); border: 1px solid #253540;
  border-radius: 12px; cursor: pointer; transition: border-color .16s ease, transform .16s ease; }
.bd-item:hover { border-color: #00d9ff; transform: translateY(-1px); }
.bd-item img { width: 42px; height: 42px; flex: 0 0 auto; border-radius: 9px; border: 1px solid #2b3a45; background: #0a1016; }
.bd-item b { display: block; font-size: 13px; color: #f0eadb; }
.bd-item .g { color: #c8aa6e; font-weight: 800; font-size: 12px; }
.bd-item small { color: #8e9aa4; font-size: 11px; }

.bd-cart { position: sticky; top: 120px; padding: 16px; background: linear-gradient(180deg,#101922,#0b1117);
  border: 1px solid #253540; border-radius: 16px; }
.bd-cart h2 { margin: 0 0 12px; font-size: 16px; color: #f0eadb; }
.bd-cart h2 em { font-style: normal; color: #c8aa6e; font-size: 12.5px; margin-left: 6px; }
.bd-list { display: grid; gap: 8px; max-height: 46vh; overflow: auto; }
.bd-row { display: flex; align-items: center; gap: 8px; padding: 8px; background: #0a1016;
  border: 1px solid #253540; border-radius: 10px; }
.bd-row img { width: 30px; height: 30px; border-radius: 7px; border: 1px solid #2b3a45; }
.bd-row .nm { flex: 1 1 auto; min-width: 0; font-size: 12.5px; color: #e8e4d9; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.bd-row .qty { display: inline-flex; align-items: center; gap: 4px; }
.bd-row .qty button { width: 24px; height: 24px; font-size: 14px; font-weight: 800; color: #cfe7f0;
  background: #16232d; border: 1px solid #2b3a45; border-radius: 7px; cursor: pointer; }
.bd-row .qty span { min-width: 18px; text-align: center; font-weight: 800; color: #fff; }
.bd-row .del { color: #8e9aa4; background: none; border: 0; cursor: pointer; font-size: 14px; }
.bd-total { display: flex; gap: 14px; margin: 14px 0 8px; }
.bd-total { flex-wrap: wrap; }
.bd-total div { flex: 1 1 30%; min-width: 92px; padding: 10px; text-align: center; background: #0a1016; border: 1px solid #253540; border-radius: 10px; }
.bd-total span { display: block; font-size: 11.5px; color: #8e9aa4; margin-bottom: 4px; }
.bd-total b { font-size: 18px; color: #c8aa6e; }
/* 回應：做大做明顯 */
.bd-reply { margin: 0 0 12px; padding: 16px; border-radius: 14px; border-left: 6px solid #00d9ff;
  background: rgba(0,217,255,.08); color: #dff3fb; font-size: 14px; line-height: 1.65;
  display: flex; gap: 14px; align-items: center; }
.bd-reply .ico { flex: 0 0 auto; width: 46px; height: 46px; display: grid; place-items: center;
  font-size: 26px; border-radius: 50%; background: rgba(0,217,255,.14); }
.bd-reply .body { flex: 1 1 auto; min-width: 0; }
.bd-reply .main { font-size: 17px; font-weight: 900; letter-spacing: .3px; }
.bd-reply .sub { font-size: 12.5px; font-weight: 600; opacity: .85; margin-top: 4px; }
.bd-reply .num { font-size: 26px; font-weight: 900; line-height: 1; }
.bd-reply.ok { border-left-color: #4ade80; background: linear-gradient(180deg,rgba(74,222,128,.16),rgba(74,222,128,.06));
  color: #d6ffe4; box-shadow: 0 0 24px -10px rgba(74,222,128,.9); animation: bdPop .35s ease; }
.bd-reply.ok .ico { background: rgba(74,222,128,.22); }
.bd-reply.warn { border-left-color: #f87171; background: linear-gradient(180deg,rgba(248,113,113,.18),rgba(248,113,113,.06));
  color: #ffdede; box-shadow: 0 0 24px -10px rgba(248,113,113,.9); animation: bdShake .4s ease; }
.bd-reply.warn .ico { background: rgba(248,113,113,.24); }
.bd-reply.idle { border-left-color: #62707a; background: rgba(98,112,122,.10); color: #b9c4cb; }
.bd-reply.idle .ico { background: rgba(98,112,122,.18); }
.bd-bar { height: 10px; margin-top: 10px; background: #0a1016; border: 1px solid #253540;
  border-radius: 999px; overflow: hidden; }
.bd-bar span { display: block; height: 100%; border-radius: 999px;
  background: linear-gradient(90deg,#4ade80,#00d9ff); transition: width .25s ease; }
.bd-reply.warn .bd-bar span { background: linear-gradient(90deg,#f87171,#fb923c); }
@keyframes bdPop { 0% { transform: scale(.97); } 60% { transform: scale(1.01); } 100% { transform: scale(1); } }
@keyframes bdShake { 0%,100% { transform: translateX(0); } 25% { transform: translateX(-4px); }
  50% { transform: translateX(4px); } 75% { transform: translateX(-2px); } }
@media (prefers-reduced-motion: reduce) { .bd-reply.ok, .bd-reply.warn { animation: none; } }
.bd-clear { width: 100%; padding: 9px; font-size: 13px; color: #9da9b2; background: #111d26;
  border: 1px solid #2b3a45; border-radius: 9px; cursor: pointer; }

/* 購物車狀態光暈 */
.bd-cart.is-ok { border-color: rgba(74,222,128,.75); box-shadow: 0 0 0 1px rgba(74,222,128,.45), 0 0 30px -14px rgba(74,222,128,.95); }
.bd-cart.is-warn { border-color: rgba(248,113,113,.8); box-shadow: 0 0 0 1px rgba(248,113,113,.5), 0 0 30px -14px rgba(248,113,113,.95); }
.bd-cart { transition: border-color .2s ease, box-shadow .2s ease; }
/* 音效開關 */
.bd-sound { margin-left: 8px; padding: 4px 9px; font: inherit; font-size: 11.5px; font-weight: 700; cursor: pointer;
  color: #9da9b2; background: #111d26; border: 1px solid #2b3a45; border-radius: 999px; }
.bd-sound.on { color: #ffd98a; border-color: rgba(200,170,110,.7); }
/* 替代建議 */
.bd-suggest { margin: 10px 0 0; padding: 12px; border-radius: 10px; font-size: 12.5px; line-height: 1.7;
  background: rgba(0,217,255,.06); border: 1px dashed rgba(0,217,255,.4); color: #cfe7f0; }
.bd-suggest b { color: #ffd98a; }
.bd-suggest .keep { color: #9dffbf; }
.bd-suggest .drop { color: #ffb4b4; }
@media (max-width: 900px) { .bd-layout { grid-template-columns: 1fr; } .bd-cart { position: static; } }
@media (max-width: 560px) { .bd-grid { grid-template-columns: 1fr; } .bd-toolbar > * { flex: 1 1 100%; } .bd-budget { justify-content: center; } }
'''

JS = '''/* 裝備預算計算器（由 tools/build_budget.py 產生） */
(function () {
  'use strict';
  var ITEMS = __DATA__;
  var byId = {}, cart = {};
  ITEMS.forEach(function (it) { byId[it.id] = it; });

  function $(id) { return document.getElementById(id); }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
    return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function num(v) { var n = parseInt(v, 10); return isNaN(n) || n < 0 ? 0 : n; }



  /* ---------------- 金幣輸入：快捷、常用金額、記住上次 ---------------- */
  function goldSet(v) {
    var el = $('bdGold');
    if (!el) return;
    el.value = String(Math.max(0, v));
    el.dispatchEvent(new Event('input', { bubbles: true }));
  }
  function goldQuick() {
    var wrap = document.querySelector('.bd-quick');
    if (wrap) {
      wrap.addEventListener('click', function (e) {
        var b = e.target.closest ? e.target.closest('[data-gold]') : null;
        if (!b) return;
        var op = b.getAttribute('data-gold');
        var cur = parseInt($('bdGold').value, 10) || 0;
        var val;
        if (op.charAt(0) === '+') val = cur + (parseInt(op.slice(1), 10) || 0);
        else if (op.charAt(0) === '-') val = cur - (parseInt(op.slice(1), 10) || 0);
        else val = parseInt(op, 10) || 0;
        goldSet(val);
        sfx('ok');
      });
    }
    var inp = $('bdGold');
    if (!inp) return;
    try {
      var saved = localStorage.getItem('bdGold');
      if (saved !== null && saved !== '') goldSet(parseInt(saved, 10) || 0);
    } catch (e) {}
    function remember() { try { localStorage.setItem('bdGold', inp.value); } catch (e) {} }
    inp.addEventListener('change', remember);
    inp.addEventListener('blur', remember);
  }

  /* ---------------- 音效（WebAudio，無需音檔；預設關閉） ---------------- */
  var soundOn = false;
  try { soundOn = localStorage.getItem('bdSound') === '1'; } catch (e) {}
  var ac = null;
  function sfx(kind) { beep(kind); }
  function beep(kind) {
    if (!soundOn) return;
    try {
      ac = ac || new (window.AudioContext || window.webkitAudioContext)();
      var t0 = ac.currentTime;
      var tones = kind === 'ok' ? [[660, 0], [880, 0.09]] : [[220, 0], [180, 0.12]];
      tones.forEach(function (tt) {
        var o = ac.createOscillator(), g = ac.createGain();
        o.type = kind === 'ok' ? 'sine' : 'square';
        o.frequency.value = tt[0];
        g.gain.setValueAtTime(0.0001, t0 + tt[1]);
        g.gain.exponentialRampToValueAtTime(kind === 'ok' ? 0.12 : 0.09, t0 + tt[1] + 0.01);
        g.gain.exponentialRampToValueAtTime(0.0001, t0 + tt[1] + 0.14);
        o.connect(g); g.connect(ac.destination);
        o.start(t0 + tt[1]); o.stop(t0 + tt[1] + 0.16);
      });
    } catch (e) {}
  }
  function soundBtn() {
    var h2 = document.querySelector('.bd-cart h2');
    if (!h2 || document.getElementById('bdSound')) return;
    var b = document.createElement('button');
    b.id = 'bdSound'; b.type = 'button';
    b.className = 'bd-sound' + (soundOn ? ' on' : '');
    b.textContent = soundOn ? '🔊 音效開' : '🔇 音效關';
    b.title = '點擊切換音效（預設關閉）';
    b.addEventListener('click', function () {
      soundOn = !soundOn;
      try { localStorage.setItem('bdSound', soundOn ? '1' : '0'); } catch (e) {}
      b.className = 'bd-sound' + (soundOn ? ' on' : '');
      b.textContent = soundOn ? '🔊 音效開' : '🔇 音效關';
      if (soundOn) beep('ok');
    });
    h2.appendChild(b);
  }

  /* ---------------- 替代建議：先買哪些、哪些先不要買 ---------------- */
  function suggest(t) {
    if (t.left >= 0) return '';
    var rows = t.rows.map(function (r) { return { n: r.it.n, unit: r.it.g, q: r.qty, total: r.it.g * r.qty }; })
      .sort(function (a, b) { return a.unit - b.unit; });
    var keep = [], drop = [], sum = 0;
    rows.forEach(function (r) {
      if (sum + r.unit <= t.budget) { keep.push(r); sum += r.unit; }
      else { drop.push(r); }
    });
    var html = '<div class="bd-suggest"><b>替代建議</b><br>';
    if (keep.length) {
      html += '<span class="keep">✓ 先買這些（共 ' + keep.length + ' 件，' + sum + ' 金幣）：</span>' +
        keep.map(function (r) { return r.n + '（' + r.unit + '）'; }).join('、') + '<br>';
    } else {
      html += '<span class="drop">✗ 目前金幣買不到任何一件，建議先賺金幣或多打幾波兵。</span><br>';
    }
    if (drop.length) {
      html += '<span class="drop">✗ 先不要買：</span>' +
        drop.map(function (r) { return r.n + '（' + r.unit + '，缺 ' + Math.max(0, r.unit - (t.budget - sum)) + '）'; }).join('、');
    }
    return html + '</div>';
  }

  function cartRows() { return Object.keys(cart).map(function (id) { return { it: byId[id], qty: cart[id] }; })
    .filter(function (r) { return r.it && r.qty > 0; }); }

  function totals() {
    var rows = cartRows(), spent = 0, slots = 0;
    rows.forEach(function (r) { spent += r.it.g * r.qty; slots += r.qty; });
    return { rows: rows, spent: spent, slots: slots, budget: num($('bdGold').value), left: num($('bdGold').value) - spent };
  }

  var lastCls = '';

  function reply(t) {
    var el = $('bdReply');
    if (!el) return;
    var oldSug = el.parentNode.querySelector('.bd-suggest');
    if (oldSug) oldSug.remove();
    if (!t.rows.length) {
      el.className = 'bd-reply idle';
      el.innerHTML = '<span class="ico">🛒</span><span class="body">' +
        '<div class="main">開始挑選裝備</div>' +
        '<div class="sub">輸入你有多少金幣，再點左邊的裝備加入清單。</div></span>';
      return;
    }
    var cls = 'ok', ico = '✓', main = '', num = '', sub = [];
    var pct = Math.max(0, Math.min(100, t.budget > 0 ? (t.spent / t.budget * 100) : 100));

    if (t.slots > 6) {
      cls = 'warn'; ico = '⚠';
      main = '裝備欄超過 6 格';
      num = t.slots + ' 件';
      sub.push('已選 ' + t.slots + ' 件，請減少數量（上限 6 件）。');
    } else if (t.left < 0) {
      cls = 'warn'; ico = '✗';
      main = '金幣不足';
      num = '還差 ' + (-t.left);
      sub.push('買這 ' + t.slots + ' 件裝備還差 ' + (-t.left) + ' 金幣。');
    } else {
      main = '可以買！';
      num = '剩 ' + t.left;
      sub.push('總額 ' + t.spent + ' 金幣 · 共 ' + t.slots + ' 件裝備' +
               (t.slots <= 6 ? '（' + t.slots + '／6 格）' : ''));
    }
    var comps = t.rows.filter(function (r) { return r.it.f && r.it.f.length; });
    if (comps.length) sub.push('合成來源：' + comps.map(function (r) {
      return r.it.n + '（' + r.it.f.join('＋') + '）'; }).join('；'));
    if (t.slots >= 3 && t.slots <= 6) sub.push('★ 已成形核心裝，可以直接參團。');

    el.className = 'bd-reply ' + cls;
    el.innerHTML = '<span class="ico">' + ico + '</span>' +
      '<span class="body"><div class="main">' + esc(main) + '　<span class="num">' + esc(num) + '</span></div>' +
      '<div class="sub">' + sub.map(esc).join('<br>') + '</div>' +
      '<div class="bd-bar"><span style="width:' + pct.toFixed(1) + '%"></span></div></span>';

    /* 購物車邊框光暈：可買＝綠、不足＝紅 */
    var cartBox = document.querySelector('.bd-cart');
    if (cartBox) {
      cartBox.classList.toggle('is-ok', cls === 'ok');
      cartBox.classList.toggle('is-warn', cls === 'warn');
    }
    /* 音效（預設關閉） */
    if (cls !== lastCls) { beep(cls === 'ok' ? 'ok' : 'err'); lastCls = cls; }
    /* 金幣不足 → 替代建議 */
    var sug = suggest(t);
    if (sug) el.insertAdjacentHTML('afterend', sug);
  }

  function renderCart() {
    var t = totals();
    $('bdSlots').textContent = t.slots + '／6 格';
    $('bdSpent').textContent = t.spent;
    $('bdLeft').textContent = t.left;
    if ($('bdQty')) $('bdQty').textContent = t.slots + ' 件';
    $('bdList').innerHTML = t.rows.map(function (r) {
      return '<div class="bd-row"><img src="' + esc(r.it.i) + '" alt=""><span class="nm" title="' + esc(r.it.n) +
        ' · ' + r.it.g + ' 金幣">' + esc(r.it.n) + '</span>' +
        '<span class="qty"><button type="button" data-dec="' + r.it.id + '">−</button><span>' + r.qty +
        '</span><button type="button" data-inc="' + r.it.id + '">＋</button></span>' +
        '<button type="button" class="del" data-del="' + r.it.id + '" title="移除">✕</button></div>';
    }).join('');
    reply(t);
  }

  function currentTotals() {
    var spent = 0;
    Object.keys(cart).forEach(function (id) { if (byId[id]) spent += byId[id].g * cart[id]; });
    return { spent: spent, left: num($('bdGold').value) - spent };
  }

  function renderGrid() {
    var q = ($('bdSearch').value || '').toLowerCase().trim();
    var type = $('bdType') ? $('bdType').value : 'all';
    var sort = $('bdSort') ? $('bdSort').value : 'price-asc';
    var affordOnly = $('bdAfford') && $('bdAfford').checked;
    var left = currentTotals().left;

    var list = ITEMS.filter(function (it) {
      var okQ = !q || (it.n + ' ' + it.en + ' ' + it.t.join(' ') + ' ' + it.d).toLowerCase().indexOf(q) >= 0;
      var okT = type === 'all' || (it.t || []).indexOf(type) >= 0;
      var okA = !affordOnly || (it.g <= left && (cart[it.id] || 0) < 6);
      return okQ && okT && okA;
    });
    if (sort === 'price-desc') list = list.slice().sort(function (a, b) { return b.g - a.g; });
    else if (sort === 'name') list = list.slice().sort(function (a, b) { return a.n.localeCompare(b.n); });
    else list = list.slice().sort(function (a, b) { return a.g - b.g; });

    var info = '顯示 ' + list.length + ' 件裝備（共 ' + ITEMS.length + ' 件）';
    if (type !== 'all') info += '｜類型：' + type;
    if (affordOnly) info += '｜只顯示買得起（剩 ' + left + '）';
    if (q) info += '｜關鍵字：' + q;
    $('bdCount').textContent = info;

    $('bdGrid').innerHTML = list.map(function (it) {
      var have = cart[it.id] || 0;
      return '<button type="button" class="bd-item' + (have ? ' in-cart' : '') + '" data-add="' + it.id + '">' +
        (have ? '<span class="have">' + have + '</span>' : '') +
        '<img src="' + esc(it.i) + '" alt="" loading="lazy">' +
        '<span><b>' + esc(it.n) + '</b><span class="g">' + it.g +
        ' 金幣</span><small>' + esc((it.t || []).join('、')) + '</small></span></button>';
    }).join('');
  }

  function initFilters() {
    var sel = $('bdType');
    if (sel) {
      var types = {};
      ITEMS.forEach(function (it) { (it.t || []).forEach(function (t) { types[t] = (types[t] || 0) + 1; }); });
      var keys = Object.keys(types).sort(function (a, b) { return types[b] - types[a]; });
      sel.innerHTML = '<option value="all">全部類型（' + keys.length + '）</option>' +
        keys.map(function (k) { return '<option value="' + esc(k) + '">' + esc(k) + '（' + types[k] + '）</option>'; }).join('');
      sel.addEventListener('change', renderGrid);
    }
    if ($('bdSort')) $('bdSort').addEventListener('change', renderGrid);
    if ($('bdAfford')) $('bdAfford').addEventListener('change', renderGrid);
  }

  function add(id) {
    if (!byId[id]) return;
    cart[id] = Math.min(6, (cart[id] || 0) + 1);
    renderGrid(); renderCart();
  }

  document.addEventListener('DOMContentLoaded', function () {
    if (!$('bdGrid')) return;
    initFilters(); renderGrid(); renderCart(); soundBtn(); goldQuick();
    $('bdSearch').addEventListener('input', renderGrid);
    $('bdGold').addEventListener('input', function () { renderGrid(); renderCart(); });
    $('bdGrid').addEventListener('click', function (e) {
      var b = e.target.closest ? e.target.closest('[data-add]') : null;
      if (b) add(b.getAttribute('data-add'));
    });
    $('bdList').addEventListener('click', function (e) {
      var t = e.target, id;
      if (!t) return;
      if ((id = t.getAttribute('data-inc'))) { add(id); }
      else if ((id = t.getAttribute('data-dec'))) { cart[id] = Math.max(0, (cart[id] || 0) - 1); if (!cart[id]) delete cart[id]; renderCart(); }
      else if ((id = t.getAttribute('data-del'))) { delete cart[id]; renderCart(); }
    });
    $('bdClear').addEventListener('click', function () { cart = {}; renderCart(); });
  });
})();
'''

def main():
    ver = G.get('version', '16.20.1')
    html = HTML.replace('__VER__', ver).replace('__COUNT__', str(len(ITEMS)))
    with io.open(os.path.join(SITE, 'budget.html'), 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(html)
    with io.open(os.path.join(SITE, 'budget.css'), 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(CSS)
    with io.open(os.path.join(SITE, 'budget.js'), 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(JS.replace('__DATA__', json.dumps(ITEMS, ensure_ascii=False, separators=(',', ':'))))
    print('  已寫入 budget.html / budget.css / budget.js（%d 件裝備）' % len(ITEMS))

    # 分類列加入「裝備預算」（放在裝備合成之後）
    nav_p = os.path.join(SITE, 'nav.js')
    with io.open(nav_p, encoding='utf-8') as fh:
        nav = fh.read()
    if 'budget.html' not in nav:
        nav = nav.replace("['guides.html', '裝備合成', '🧩'],",
                          "['guides.html', '裝備合成', '🧩'],\n    ['budget.html', '裝備預算', '🧮'],", 1)
        nav = nav.replace("var ORDER = ['guide.html','champions.html','items.html','guides.html'",
                          "var ORDER = ['guide.html','champions.html','items.html','guides.html','budget.html'", 1)
        with io.open(nav_p, 'w', encoding='utf-8', newline='') as fh:
            fh.write(nav)
        print('  分類列已加入「🧮 裝備預算」')
    else:
        print('  分類列已含 budget.html')

    # i18n 加入「裝備預算」
    i18n_p = os.path.join(SITE, 'i18n.js')
    with io.open(i18n_p, encoding='utf-8') as fh:
        i18n = fh.read()
    if "'裝備預算':" not in i18n:
        i18n = i18n.replace("    '裝備合成': [", "    '裝備預算': ['Build Budget', 'ビルド予算', '빌드 예산'],\n    '裝備合成': [", 1)
        with io.open(i18n_p, 'w', encoding='utf-8', newline='') as fh:
            fh.write(i18n)
        print('  i18n 已加入「裝備預算」')


if __name__ == '__main__':
    sys.exit(main())
