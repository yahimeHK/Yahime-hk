#!/usr/bin/env python3
"""把「英雄攻略」與「裝備攻略」合併成一頁 guide.html，並把分類列兩顆換成一顆 📖 攻略。

作法：讀取現成的 champions.html 與 items.html 骨架重新組裝（不改動既有產生器），
      並自動處理 id 衝突（roleFilters → champRoleFilters，champions-db.js 同步兼容）。
可重複執行：每次都會依最新的 champions.html / items.html 重新產生 guide.html。
"""
import io
import os
import re
import sys

SITE = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.join(SITE, 'tools')


def read(rel):
    with io.open(os.path.join(SITE, rel), encoding='utf-8') as fh:
        return fh.read()


def write(rel, text):
    with io.open(os.path.join(SITE, rel), 'w', encoding='utf-8', newline='') as fh:
        fh.write(text)


# ---------------------------------------------------------------- 1) 取出兩邊的 <main>
ch = read('champions.html')
it = read('items.html')
m_ch = re.search(r'(?s)\n?<main\b.*?</main>', ch)
m_it = re.search(r'(?s)\n?<main\b.*?</main>', it)
if not m_ch or not m_it:
    print('  !! 找不到 <main> 區塊')
    sys.exit(1)
main_ch, main_it = m_ch.group(0), m_it.group(0)

# 英雄頁的彈窗（#dbModal 等）位於 </main> 之後、<footer> 之前，必須一併帶過來，
# 否則 champions-db.js 的 render() 取不到彈窗會整段失敗（實測：英雄卡 0 張）
_tail = ch[m_ch.end():]
_fi = _tail.find('<footer')
if _fi >= 0:
    _tail = _tail[:_fi]
main_ch = main_ch + '\n' + _tail
print('  英雄區塊 = %.1f KB（含彈窗 %.1f KB）' % (len(main_ch.encode('utf-8')) / 1024, len(_tail.encode('utf-8')) / 1024))

# id 衝突：英雄區的 roleFilters 改名（items 的行內腳本仍使用原名，不能改）
main_ch = main_ch.replace('id="roleFilters"', 'id="champRoleFilters"')
main_ch = main_ch.replace('aria-controls="roleFilters"', 'aria-controls="champRoleFilters"')

# ---------------------------------------------------------------- 2) 以 items.html 為底組裝
guide = it[:m_it.start()] + main_ch + '\n' + main_it + it[m_it.end():]

# 標題與頁面模式
guide = re.sub(r'<title>[^<]*</title>', '<title>LOL 攻略站 V6.0 - 攻略</title>', guide, count=1)
guide = guide.replace('data-page="items"', 'data-page="items"')   # 保留 items 模式（行內腳本需要）

# 加入英雄頁的渲染腳本（放在 state.js 之後，確保 DOM 已就緒）
if 'champions-db.js' not in guide:
    guide = guide.replace('<script src="state.js',
                          '<script src="champions-db.js?v=1" defer></script>\n    <script src="state.js', 1)

# 英雄區塊的標題說明（置於最前，讓使用者知道這頁有兩部分）
guide = guide.replace('<body class="bg-items">',
                      '<body class="bg-items">\n    <!-- 合併頁：英雄攻略 ＋ 裝備攻略（由 tools/build_guide_merge.py 產生） -->', 1)

# 英雄卡的樣式表（champions.html 使用；合併頁若漏載，卡片會沒有樣式、頭像浮在文字上）
if 'champions-db.css' not in guide:
    guide = guide.replace('</head>', '    <link rel="stylesheet" href="champions-db.css">\n</head>', 1)
    print('  已加入 champions-db.css')

# ---------------------------------------------------------------- 編排整合：區塊切換列
SWITCH = '''<div class="guide-switch" id="guideSwitch">
        <a href="#champSection" data-sec="champSection">&#9876;&#65039; 英雄攻略</a>
    </div>
    <style>
    .guide-switch{position:sticky;top:0;z-index:60;display:flex;gap:8px;justify-content:center;padding:10px;
      background:linear-gradient(180deg,rgba(5,8,13,.97),rgba(5,8,13,.78));backdrop-filter:blur(8px);
      border-bottom:1px solid rgba(98,170,190,.25)}
    .guide-switch a{display:inline-flex;align-items:center;gap:6px;padding:8px 18px;font-size:14px;font-weight:700;
      color:#c9d6dd;text-decoration:none;border:1px solid rgba(98,170,190,.35);border-radius:999px;
      background:linear-gradient(180deg,rgba(16,25,34,.92),rgba(9,14,20,.92));
      transition:color .18s ease,border-color .18s ease,box-shadow .18s ease,background .18s ease}
    .guide-switch a:hover{color:#fff;border-color:#00d9ff;
      box-shadow:0 0 0 1px rgba(0,217,255,.4),0 8px 20px -12px rgba(0,217,255,.8)}
    .guide-switch a.is-active{color:#ffd98a;border-color:rgba(200,170,110,.8);
      background:linear-gradient(180deg,#332915,#1a140b);
      box-shadow:inset 0 1px 0 rgba(255,231,170,.3),0 0 0 1px rgba(0,0,0,.5)}
    @media (max-width:430px){.guide-switch{padding:8px;gap:6px}.guide-switch a{padding:7px 13px;font-size:13px}}
    </style>
    <script>
    (function () {
      var bar = document.getElementById('guideSwitch');
      if (!bar) return;
      if (bar.querySelectorAll('a').length < 2) { bar.style.display = 'none'; return; }   // 只剩一個按鈕就沒有切換意義
      var secs = ['champSection', 'itemsSection'];
      function update() {
        var y = window.scrollY + 160, best = secs[0];
        secs.forEach(function (id) {
          var el = document.getElementById(id);
          if (el && el.offsetTop <= y) best = id;
        });
        Array.prototype.forEach.call(bar.querySelectorAll('a'), function (a) {
          a.classList.toggle('is-active', a.getAttribute('data-sec') === best);
        });
      }
      window.addEventListener('scroll', update, { passive: true });
      window.addEventListener('resize', update);
      update();
    })();
    </script>
'''
if 'guide-switch' not in guide:
    guide = guide.replace('<body class="bg-items">', '<body class="bg-items">\n    ' + SWITCH, 1)
    if 'id="champSection"' not in guide:
        guide = guide.replace('<main class="champ-wrap"', '<main class="champ-wrap" id="champSection"', 1)
    if 'id="itemsSection"' not in guide:
        guide = guide.replace('<main class="items-wrap"', '<main class="items-wrap" id="itemsSection"', 1)
    print('  已加入區塊切換列（英雄攻略／裝備攻略）')

# ---------------------------------------------------------------- 統一網格（方案 A）
HIDE_CSS = '''<style>
    #itemsSection .items-hero,
    #itemsSection .items-toolbar,
    #itemsSection .items-count,
    #itemsSection #allchampSection,
    #itemsSection #allchamp,
    #itemsSection .build-block,
    #itemsSection #buildCards,
    #itemsSection #buildGrid { display: none !important; }
    .card-build { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin-top: 8px;
      padding-top: 8px; border-top: 1px solid rgba(98,170,190,.18); }
    .card-build .cb-rune { display: inline-flex; align-items: center; gap: 5px; padding: 4px 9px; font-size: 11.5px;
      font-weight: 700; color: #ffd98a; background: rgba(200,170,110,.10);
      border: 1px solid rgba(200,170,110,.45); border-radius: 999px; }
    .card-build .cb-rune img { width: 18px; height: 18px; border-radius: 50%; }
    .card-build .cb-items { display: inline-flex; gap: 4px; }
    .card-build .cb-items img { width: 26px; height: 26px; border-radius: 6px;
      border: 1px solid rgba(98,170,190,.45); background: #0a1016; }
    .card-build .cb-items img:hover { border-color: #00d9ff; }
    @media (max-width:430px) { .card-build .cb-items img { width: 22px; height: 22px; } }
    </style>'''

CARD_JS = '''<script>
    (function () {
      var host = document.getElementById('champSection');
      if (!host) return;
      fetch('assets/lol/champions.json').then(function (r) { return r.json(); }).then(function (d) {
        var byKey = {};
        (d.champions || []).forEach(function (c) { byKey[c.key] = c; });
        var n = 0;
        Array.prototype.forEach.call(host.querySelectorAll('.db-champ'), function (card) {
          if (card.querySelector('.card-build')) return;
          var im = card.querySelector('img');
          if (!im) return;
          var file = (im.getAttribute('src') || '').split('/').pop().split('?')[0].replace('.jpg', '');
          var c = byKey[file];
          if (!c) { var b = card.querySelector('b'); c = b ? byName[(b.textContent || '').trim()] : null; }
          if (!c) return;
          var r = c.rune || {}, its = c.items || [];
          var html = '<div class="card-build">';
          if (r.keystone) {
            html += '<span class="cb-rune" title="' + (r.desc || '') + '">' +
              (r.icon ? '<img src="' + r.icon + '" alt="">' : '') + r.keystone + '</span>';
          }
          if (its.length) {
            html += '<span class="cb-items">' + its.map(function (it) {
              return '<img src="' + it.i + '" alt="' + it.n + '" title="' + it.n + ' · ' + it.g + ' 金幣">';
            }).join('') + '</span>';
          }
          html += '</div>';
          card.insertAdjacentHTML('beforeend', html);
          n++;
        });
      })['catch'](function () {});
    })();
    </script>'''

if 'card-build' not in guide:
    guide = guide.replace('</body>', HIDE_CSS + '\n    ' + CARD_JS + '\n</body>', 1)
    print('  已加入統一網格（隱藏重複區塊 ＋ 卡片顯示基石符文與核心裝備）')

# ---------------------------------------------------------------- 卡片擴充（修正時序）＋ 召喚師技能
CARD_JS2 = """<style>
    .card-build .cb-spells { display: inline-flex; gap: 4px; }
    .card-build .cb-spells img { width: 26px; height: 26px; border-radius: 6px;
      border: 1px solid rgba(98,170,190,.45); background: #0a1016; }
    .card-build .cb-spells img:hover { border-color: #00d9ff; }
    @media (max-width:430px) { .card-build .cb-spells img { width: 22px; height: 22px; } }
    </style>
    <script>
    (function () {
      var host = document.getElementById('champSection');
      if (!host) return;
      var SPELL = { 'Flash': '閃現', 'Smite': '重擊', 'Teleport': '傳送', 'Ignite': '點燃',
                    'Heal': '治癒', 'Exhaust': '虛弱', 'Barrier': '光盾', 'Cleanse': '淨化', 'Ghost': '鬼步' };
      var BY_ROLE = { '上路': ['Flash', 'Teleport'], '中路': ['Flash', 'Ignite'], '打野': ['Flash', 'Smite'],
                      '下路': ['Flash', 'Heal'], '輔助': ['Flash', 'Ignite'] };
      var byKey = null, tries = 0;
      function enrich() {
        var cards = host.querySelectorAll('.db-champ');
        if (!cards.length) { if (tries++ < 25) setTimeout(enrich, 400); return; }
        if (!byKey) { if (tries++ < 25) setTimeout(enrich, 400); return; }
        var n = 0;
        Array.prototype.forEach.call(cards, function (card) {
          if (card.querySelector('.card-build')) return;
          var im = card.querySelector('img');
          if (!im) return;
          var file = (im.getAttribute('src') || '').split('/').pop().split('?')[0].replace('.jpg', '');
          var c = byKey[file];
          if (!c) { var b = card.querySelector('b'); c = b ? byName[(b.textContent || '').trim()] : null; }
          if (!c) return;
          var r = c.rune || {}, its = c.items || [];
          var spells = (BY_ROLE[c.role] || ['Flash', 'Ignite']);
          var html = '<div class="card-build">';
          if (its.length) {
            html += '<span class="cb-items">' + its.map(function (it) {
              return '<img src="' + it.i + '" alt="' + it.n + '" title="' + it.n + ' · ' + it.g + ' 金幣">';
            }).join('') + '</span>';
          }
          if (r.keystone) {
            html += '<span class="cb-rune" title="' + (r.desc || '') + '">' +
              (r.icon ? '<img src="' + r.icon + '" alt="">' : '') + r.keystone + '</span>';
          }
          html += '<span class="cb-spells">' + spells.map(function (sp) {
            return '<img src="assets/lol/spell/' + sp + '.png" alt="' + (SPELL[sp] || sp) + '" title="' +
              (SPELL[sp] || sp) + '（站內依定位建議）">';
          }).join('') + '</span>';
          html += '</div>';
          card.insertAdjacentHTML('beforeend', html);
          n++;
        });
      }
      fetch('assets/lol/champions.json').then(function (r) { return r.json(); }).then(function (d) {
        byKey = {};
        (d.champions || []).forEach(function (c) { byKey[c.key] = c; });
        enrich();
      })['catch'](function () {});
    })();
    </script>"""

if 'cb-spells' not in guide:
    guide = guide.replace('</body>', CARD_JS2 + '\n</body>', 1)
    print('  已加入卡片擴充（重試機制）＋ 召喚師技能')

# ---------------------------------------------------------------- 移除殘留的深度攻略卡區塊
HIDE_JS = """<script>
    (function () {
      function hideByHeading(text) {
        var nodes = document.querySelectorAll('h1, h2, h3, .db-heading, .heading, small, b');
        Array.prototype.forEach.call(nodes, function (el) {
          var t = (el.textContent || '').trim();
          if (!t || t.indexOf(text) < 0 || t.length > 40) return;   // 只比對標題本身，不誤抓整個容器
          var node = el, guard = 0;
          while (node.parentElement && node.parentElement !== document.body && guard++ < 10) {
            var par = node.parentElement;
            if (par.tagName === 'MAIN' || (par.classList && (par.classList.contains('items-wrap') || par.classList.contains('champ-wrap')))) break;
            node = par;
          }
          if (node !== document.body) node.style.display = 'none';
        });
      }
      ['深度攻略卡', '版本玩法方向盤'].forEach(hideByHeading);
    })();
    </script>"""

if 'hideByHeading' not in guide:
    guide = guide.replace('</body>', HIDE_JS + '\n</body>', 1)
    print('  已加入移除深度攻略卡與版本玩法方向盤的腳本')

write('guide.html', guide)
print('  已寫入 guide.html（%.1f KB）' % (len(guide.encode('utf-8')) / 1024))

# ---------------------------------------------------------------- 3) champions-db.js 兼容新 id
db = read('champions-db.js')
if 'champRoleFilters' not in db:
    db2 = db.replace("document.getElementById('roleFilters')",
                     "(document.getElementById('roleFilters') || document.getElementById('champRoleFilters'))")
    if db2 != db:
        write('champions-db.js', db2)
        print('  champions-db.js：已兼容 champRoleFilters')

# ---------------------------------------------------------------- 4) 分類列：兩顆換一顆
nav = read('nav.js')
if 'guide.html' not in nav:
    # 4a. 排序表加入 guide.html（放在最前）
    nav = nav.replace("var ORDER = ['champions.html','items.html'",
                      "var ORDER = ['guide.html','champions.html','items.html'", 1)
    # 4b. 排序後把兩顆合併成一顆
    anchor = "  Array.prototype.forEach.call(sub.querySelectorAll('a'), function (a) { a.parentNode.removeChild(a); });"
    merge_js = (
        "  // 合併：英雄攻略 + 裝備攻略 → 單一「📖 攻略」\n"
        "  (function () {\n"
        "    var out = [], added = false;\n"
        "    items.forEach(function (it) {\n"
        "      var h = it.href.toLowerCase();\n"
        "      if (h === 'champions.html' || h === 'items.html') {\n"
        "        if (!added) { out.push({ href: 'guide.html', label: '攻略', icon: '\\uD83D\\uDCD6' }); added = true; }\n"
        "        return;\n"
        "      }\n"
        "      out.push(it);\n"
        "    });\n"
        "    items = out;\n"
        "  })();\n\n")
    if anchor in nav:
        nav = nav.replace(anchor, merge_js + anchor, 1)
        write('nav.js', nav)
        print('  nav.js：分類列已改為單一「📖 攻略」')
    else:
        print('  !! nav.js 找不到重建錨點')
else:
    print('  nav.js 已含合併邏輯')

# ---------------------------------------------------------------- 5) i18n：新增「攻略」
i18n = read('i18n.js')
if "'攻略': [" not in i18n:
    i18n = i18n.replace("    '首頁': [", "    '攻略': ['Guide', 'ガイド', '공략'],\n    '首頁': [", 1)
    write('i18n.js', i18n)
    print('  i18n.js：已加入「攻略」四語')
