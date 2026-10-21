#!/usr/bin/env python3
"""產生「賽季進度計算器」分頁（season.html / season.css / season.js）。
   輸入：目標、目前進度、每場獲得、剩餘天數、每天最多幾場
   輸出：還差多少、需要幾場、每天需幾場、是否能達標，並用明顯的顏色／大字回應。"""
import io
import json
import os
import sys

SITE = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
VER = '16.20.1'
gp = os.path.join(SITE, 'assets', 'lol', 'gear.json')
if os.path.exists(gp):
    with io.open(gp, encoding='utf-8') as fh:
        VER = json.load(fh).get('version', VER)

HTML = '''<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
    <meta name="color-scheme" content="dark light">
    <meta name="theme-color" content="#05080d">
    <title>LOL 攻略站 V6.0 - 賽季進度計算器</title>
    <link rel="stylesheet" href="style.css">
    <link rel="stylesheet" href="season.css">
</head>
<body class="bg-items">
    <header class="topbar">
        <div class="brand">SUMMONER'S <span>GUIDE</span><b>V6.0</b></div>
        <nav>
            <a href="index.html">首頁</a>
            <a href="guide.html">英雄攻略</a>
            <a href="budget.html">裝備預算</a>
            <a href="season.html" style="color:#00d9ff;font-weight:800">賽季進度</a>
        </nav>
        <button class="icon-btn" id="themeBtn">☀️</button>
    </header>

    <main class="items-wrap">
        <section class="items-hero">
            <small>SEASON TRACKER &middot; PATCH __VER__</small>
            <h1>賽季進度 <em>計算器</em></h1>
            <p>輸入你的目標與目前進度，算出還差多少、需要幾場、每天要打幾場，並直接告訴你能不能達標。
               通行證等級、積分、英雄專精都適用（公式相同）。</p>
            <div class="items-hero__pills">
                <span>即時計算</span>
                <span>通行證／積分／專精</span>
                <span>達標評估</span>
                <span>純前端、離線可用</span>
            </div>
        </section>

        <div class="sn-layout">
            <section class="sn-form">
                <div class="sn-field"><label>目標（例如通行證等級 50）</label>
                    <input type="number" id="snGoal" min="1" step="1" value="50" inputmode="numeric"></div>
                <div class="sn-field"><label>目前進度</label>
                    <input type="number" id="snCur" min="0" step="1" value="12" inputmode="numeric"></div>
                <div class="sn-field"><label>每場大約獲得</label>
                    <input type="number" id="snPer" min="1" step="1" value="1" inputmode="numeric"></div>
                <div class="sn-field"><label>賽季剩餘天數</label>
                    <input type="number" id="snDays" min="1" step="1" value="30" inputmode="numeric"></div>
                <div class="sn-field"><label>每天最多能打幾場</label>
                    <input type="number" id="snMax" min="1" step="1" value="6" inputmode="numeric"></div>
            </section>

            <aside class="sn-result">
                <div class="bd-reply idle" id="snReply"></div>
                <div class="sn-stats">
                    <div><span>還差</span><b id="snNeed">0</b></div>
                    <div><span>需要場數</span><b id="snGames">0</b></div>
                    <div><span>每天需要</span><b id="snPerDay">0</b></div>
                </div>
                <p class="sn-note">計算僅供參考：實際進度依遊戲內規則（勝場加成、任務、活動）而有所不同。</p>
            </aside>
        </div>

        <div class="notice">
            📌 <b>說明：</b> 本頁為純瀏覽器端試算工具，不涉及任何真實交易；不會上傳你的任何資料。
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
    <script src="season.js?v=1" defer></script>
</body>
</html>
'''

CSS = '''/* 賽季進度計算器（由 tools/build_season.py 產生） */
.sn-layout { display: grid; grid-template-columns: minmax(0, 1fr) 360px; gap: 18px; margin-top: 20px; align-items: start; }
.sn-form { display: grid; gap: 12px; padding: 18px; background: linear-gradient(180deg,#101922,#0b1117);
  border: 1px solid #253540; border-radius: 16px; }
.sn-field label { display: block; margin-bottom: 6px; font-size: 12.5px; color: #9da9b2; }
.sn-field input { width: 100%; padding: 11px 13px; font-size: 16px; font-weight: 800; color: #ffd98a;
  background: #0a1016; border: 1px solid #2b3a45; border-radius: 10px; text-align: center; }
.sn-field input:focus { outline: none; border-color: #00d9ff; box-shadow: 0 0 0 3px rgba(0,217,255,.12); }
.sn-result { padding: 16px; background: linear-gradient(180deg,#101922,#0b1117);
  border: 1px solid #253540; border-radius: 16px; position: sticky; top: 120px; }

/* 回應（與裝備預算一致的顯眼樣式） */
.bd-reply { margin: 0 0 12px; padding: 16px; border-radius: 14px; border-left: 6px solid #00d9ff;
  background: rgba(0,217,255,.08); color: #dff3fb; font-size: 14px; line-height: 1.65;
  display: flex; gap: 14px; align-items: center; }
.bd-reply .ico { flex: 0 0 auto; width: 46px; height: 46px; display: grid; place-items: center;
  font-size: 26px; border-radius: 50%; background: rgba(0,217,255,.14); }
.bd-reply .body { flex: 1 1 auto; min-width: 0; }
.bd-reply .main { font-size: 17px; font-weight: 900; }
.bd-reply .sub { font-size: 12.5px; font-weight: 600; opacity: .85; margin-top: 4px; }
.bd-reply .num { font-size: 26px; font-weight: 900; line-height: 1; }
.bd-reply.ok { border-left-color: #4ade80; background: linear-gradient(180deg,rgba(74,222,128,.16),rgba(74,222,128,.06));
  color: #d6ffe4; box-shadow: 0 0 24px -10px rgba(74,222,128,.9); animation: snPop .35s ease; }
.bd-reply.ok .ico { background: rgba(74,222,128,.22); }
.bd-reply.warn { border-left-color: #f87171; background: linear-gradient(180deg,rgba(248,113,113,.18),rgba(248,113,113,.06));
  color: #ffdede; box-shadow: 0 0 24px -10px rgba(248,113,113,.9); animation: snShake .4s ease; }
.bd-reply.warn .ico { background: rgba(248,113,113,.24); }
.bd-reply.idle { border-left-color: #62707a; background: rgba(98,112,122,.10); color: #b9c4cb; }
.bd-reply.idle .ico { background: rgba(98,112,122,.18); }
.bd-bar { height: 10px; margin-top: 10px; background: #0a1016; border: 1px solid #253540; border-radius: 999px; overflow: hidden; }
.bd-bar span { display: block; height: 100%; border-radius: 999px;
  background: linear-gradient(90deg,#4ade80,#00d9ff); transition: width .25s ease; }
.bd-reply.warn .bd-bar span { background: linear-gradient(90deg,#f87171,#fb923c); }
@keyframes snPop { 0% { transform: scale(.97); } 60% { transform: scale(1.01); } 100% { transform: scale(1); } }
@keyframes snShake { 0%,100% { transform: translateX(0); } 25% { transform: translateX(-4px); } 50% { transform: translateX(4px); } 75% { transform: translateX(-2px); } }
.sn-stats { display: flex; flex-wrap: wrap; gap: 10px; }
.sn-stats div { flex: 1 1 30%; min-width: 92px; padding: 12px; text-align: center;
  background: #0a1016; border: 1px solid #253540; border-radius: 10px; }
.sn-stats span { display: block; font-size: 11.5px; color: #8e9aa4; margin-bottom: 5px; }
.sn-stats b { font-size: 21px; color: #c8aa6e; }
.sn-note { margin: 12px 0 0; font-size: 11.5px; line-height: 1.6; color: #6f7c86; }
@media (max-width: 900px) { .sn-layout { grid-template-columns: 1fr; } .sn-result { position: static; } }
@media (prefers-reduced-motion: reduce) { .bd-reply.ok, .bd-reply.warn { animation: none; } }
'''

JS = '''/* 賽季進度計算器（由 tools/build_season.py 產生） */
(function () {
  'use strict';
  function $(id) { return document.getElementById(id); }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
    return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function n(id, def) { var v = parseInt($(id).value, 10); return isNaN(v) || v < 0 ? def : v; }

  function calc() {
    var goal = Math.max(1, n('snGoal', 1));
    var cur = n('snCur', 0);
    var per = Math.max(1, n('snPer', 1));
    var days = Math.max(1, n('snDays', 1));
    var maxPerDay = Math.max(1, n('snMax', 6));

    var need = Math.max(0, goal - cur);
    var games = Math.ceil(need / per);
    var perDay = Math.ceil(games / days);
    var pct = Math.min(100, Math.max(0, cur / goal * 100));

    $('snNeed').textContent = need;
    $('snGames').textContent = games;
    $('snPerDay').textContent = perDay;

    var el = $('snReply');
    if (need <= 0) {
      el.className = 'bd-reply ok';
      el.innerHTML = '<span class="ico">🏆</span><span class="body">' +
        '<div class="main">已達標！　<span class="num">100%</span></div>' +
        '<div class="sub">目前 ' + cur + ' ／ 目標 ' + goal + '。保持下去就好。</div>' +
        '<div class="bd-bar"><span style="width:100%"></span></div></span>';
      return;
    }
    if (perDay <= maxPerDay) {
      el.className = 'bd-reply ok';
      el.innerHTML = '<span class="ico">✓</span><span class="body">' +
        '<div class="main">可以達標！　<span class="num">每天 ' + perDay + ' 場</span></div>' +
        '<div class="sub">還差 ' + need + '，需要 ' + games + ' 場；剩下 ' + days + ' 天，每天 ' + perDay +
        ' 場（上限 ' + maxPerDay + ' 場）剛好來得及。</div>' +
        '<div class="bd-bar"><span style="width:' + pct.toFixed(1) + '%"></span></div></span>';
    } else {
      el.className = 'bd-reply warn';
      el.innerHTML = '<span class="ico">✗</span><span class="body">' +
        '<div class="main">時間不夠　<span class="num">每天要 ' + perDay + ' 場</span></div>' +
        '<div class="sub">還差 ' + need + '（' + games + ' 場），但每天只能打 ' + maxPerDay +
        ' 場 → ' + days + ' 天最多 ' + (days * maxPerDay) + ' 場，還差 ' + Math.max(0, games - days * maxPerDay) +
        ' 場。建議提高每場進度或增加天數。</div>' +
        '<div class="bd-bar"><span style="width:' + pct.toFixed(1) + '%"></span></div></span>';
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    if (!$('snGoal')) return;
    ['snGoal', 'snCur', 'snPer', 'snDays', 'snMax'].forEach(function (id) {
      var el = $(id);
      if (el) { el.addEventListener('input', calc); el.addEventListener('change', calc); }
    });
    calc();
  });
})();
'''


def main():
    html = HTML.replace('__VER__', VER)
    for name, content in (('season.html', html), ('season.css', CSS), ('season.js', JS)):
        with io.open(os.path.join(SITE, name), 'w', encoding='utf-8', newline='\n') as fh:
            fh.write(content)
    print('  已寫入 season.html / season.css / season.js')

    nav_p = os.path.join(SITE, 'nav.js')
    with io.open(nav_p, encoding='utf-8') as fh:
        nav = fh.read()
    if 'season.html' not in nav:
        nav = nav.replace("['budget.html', '裝備預算', '🧮'],",
                          "['budget.html', '裝備預算', '🧮'],\n    ['season.html', '賽季進度', '📈'],", 1)
        nav = nav.replace("'guides.html','budget.html'", "'guides.html','budget.html','season.html'", 1)
        with io.open(nav_p, 'w', encoding='utf-8', newline='') as fh:
            fh.write(nav)
        print('  分類列已加入「📈 賽季進度」')

    i18n_p = os.path.join(SITE, 'i18n.js')
    with io.open(i18n_p, encoding='utf-8') as fh:
        i18n = fh.read()
    if "'賽季進度':" not in i18n:
        i18n = i18n.replace("    '裝備預算': [", "    '賽季進度': ['Season Tracker', 'シーズン進捗', '시즌 진행도'],\n    '裝備預算': [", 1)
        with io.open(i18n_p, 'w', encoding='utf-8', newline='') as fh:
            fh.write(i18n)
        print('  i18n 已加入「賽季進度」')


if __name__ == '__main__':
    sys.exit(main())
