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
        <a href="#itemsSection" data-sec="itemsSection">&#127890; 裝備攻略</a>
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
