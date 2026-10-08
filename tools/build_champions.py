#!/usr/bin/env python3
"""
自動產生英雄資料庫（champions.html）。

內容全部來自 Riot 官方 Data Dragon（zh_TW），圖片下載到 assets/lol/ 供離線使用：
  角色頭像、被動與 Q/W/E/R 技能圖示＋簡介、位置（沿用 script.js 的 roleGroups 對照）、
  建議符文（基石＋符文說明＋主／副樹）、核心裝備（圖示＋名稱）、戰術解析
  （玩法定位＋各位置重點＋Riot 官方對戰提示＋站內整理的克制資料）。

所有英雄（173 位）都會產生，之後重跑就能跟上最新版本：
    python _build_champions.py
"""
import html
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

# 網站根目錄：優先用環境變數，其次自動判斷（產生器放 tools/ 時，上一層就是網站根目錄）
_HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.environ.get('LOL_SITE') or (_HERE if os.path.exists(os.path.join(_HERE, 'index.html')) else os.path.dirname(_HERE))
ASSETS = os.path.join(SITE, 'assets', 'lol')
CACHE = os.path.join(os.environ['TEMP'], 'lolcache')
os.makedirs(CACHE, exist_ok=True)
os.makedirs(ASSETS, exist_ok=True)

VER = None
IMG = {}

ROLE_SLUG = {'上路': 'top', '打野': 'jungle', '中路': 'middle', '下路': 'adc', '輔助': 'support'}
ROLES = ['上路', '打野', '中路', '下路', '輔助']
LANELORE_BASE = 'https://lanelore.com/champions/'
LOGRAPH_RUNES = 'https://www.leagueofgraphs.com/champions/runes/'
LOGRAPH_COUNTERS = 'https://www.leagueofgraphs.com/champions/counters/'

TAG_ZH = {'Assassin': '刺客', 'Fighter': '鬥士', 'Mage': '法師',
          'Marksman': '射手', 'Support': '輔助', 'Tank': '坦克'}

# ---------------------------------------------------------------- 規則表
# 依「職業 + 位置」決定建議符文（基石名稱皆為 16.20.1 zh_TW 官方譯名）
RUNE_RULES = {
    'Tank':    ('裂地衝擊', '意志', '精準'),
    'Support': ('召喚艾莉', '巫術', '啟示'),
    'Marksman': ('致命節奏', '精準', '征服'),
    'Assassin': ('死亡電刑', '征服', '精準'),
    'Mage':    ('奧術彗星', '巫術', '啟示'),
    'Fighter': ('征服者', '精準', '意志'),
}
# 進戰型輔助（坦克輔助）改用裂地衝擊
ENGAGE_SUPPORT = ('裂地衝擊', '意志', '啟示')
# 持續作戰型鬥士 / 坦克的替代基石
TANKY_FIGHTER = ('征服者', '精準', '意志')

# 核心裝備池（16.20.1 的 22xxxx / 現行裝備 ID）
ITEM_POOL = {
    'Fighter':  [223006, 226631, 226692, 226333, 223053],
    'FighterAP': [223020, 223100, 223157, 223089, 224637],
    'Tank':     [3174, 223084, 223110, 223065, 224401],
    'Mage':     [223020, 226655, 222503, 223089, 223157],
    'AssassinAD': [223142, 226693, 226691, 226696, 223026],
    'AssassinAP': [223020, 223100, 223157, 224637, 223089],
    'Marksman': [223006, 222523, 223085, 223031, 223036],
    'SupportEnc': [223158, 226620, 223222, 226617, 223190],
    'SupportEng': [3174, 223109, 223050, 223190, 226665],
}

PLAYSTYLE = {
    'Assassin': '刺客爆發／側翼切入：靠技能連段在短時間內收掉關鍵目標，進場與退場路線要事先想好。',
    'Marksman': '遠程持續輸出／安全站位：傷害來自持續普攻，站位比操作更重要，注意對面的開戰技能。',
    'Tank': '前排承傷／開戰或保護：用控制與坦度替隊友創造空間，開戰前先確認隊友跟得上。',
    'Support': '控制／保護／團隊功能：視野、保護與開團是你的主要價值，人頭不是。',
    'Mage': '技能消耗／控場／爆發：用技能距離與冷卻換取優勢，團戰負責範圍傷害與控場。',
    'Fighter': '戰士近戰／持續作戰：換血與兵線掌控是核心，注意進場時機與隊友位置。',
}
ROLE_BY_TAG = {'Tank': '上路', 'Support': '輔助', 'Marksman': '下路', 'Assassin': '中路', 'Mage': '中路', 'Fighter': '上路'}
ROLE_OVERRIDE = {'Janna': '輔助'}

ROLE_NOTE = {
    '上路': '上路重點：兵線與單帶節奏，注意河道視野與對手的打野動向。',
    '打野': '打野重點：以 Gank 與河道／預示者建立節奏，路線要配合線上兵線狀態。',
    '中路': '中路重點：控線與支援邊線，六級後配合打野抓時間差。',
    '下路': '下路重點：發育與站位，前期以穩定吃兵與換血為主，避免被包夾。',
    '輔助': '輔助重點：視野佈置與保護／開團，注意幫打野做河道視野。',
}


def slugify(name):
    s = str(name or '').lower().replace('&', '')
    s = re.sub(r"[.'’]", '', s)
    return re.sub(r'[^a-z0-9]+', '', s)


def log_slug(english_name):
    s = str(english_name or '').lower()
    s = re.sub(r"[.'’]", '-', s)
    s = re.sub(r'[^a-z0-9]+', '-', s)
    return s.strip('-')


def fetch(url, cache_name=None):
    path = os.path.join(CACHE, cache_name) if cache_name else None
    if path and os.path.exists(path) and os.path.getsize(path) > 500:
        with open(path, 'r', encoding='utf-8') as fh:
            return fh.read()
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (lol-guide-build)'})
    with urllib.request.urlopen(req, timeout=180) as r:
        raw = r.read().decode('utf-8')
    if path:
        with open(path, 'w', encoding='utf-8') as fh:
            fh.write(raw)
    return raw


def ddragon(path, cache_name=None):
    return fetch('https://ddragon.leagueoflegends.com/cdn/%s' % path, cache_name)


_LAST = [0.0]


def polite(min_gap=0.12):
    """Riot CDN 短時間內大量請求會回 403，這裡放慢一點並在失敗時退避重試。"""
    wait = min_gap - (time.time() - _LAST[0])
    if wait > 0:
        time.sleep(wait)
    _LAST[0] = time.time()


def _download(url, rel_path, attempts=5):
    dest = os.path.join(ASSETS, rel_path)
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        return 'assets/lol/' + rel_path.replace('\\', '/')
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    last = None
    for attempt in range(attempts):
        polite()
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (lol-guide-build)'})
            with urllib.request.urlopen(req, timeout=120) as r:
                data = r.read()
            with open(dest, 'wb') as fh:
                fh.write(data)
            IMG['count'] = IMG.get('count', 0) + 1
            IMG['bytes'] = IMG.get('bytes', 0) + len(data)
            return 'assets/lol/' + rel_path.replace('\\', '/')
        except Exception as e:                                    # noqa: BLE001
            last = e
            time.sleep(1.2 * (attempt + 1))                       # 退避
    print('   ! 圖片下載失敗 %s -> %s' % (url, last), file=sys.stderr)
    return ''


def save_image(url, rel_path, fallback=None):
    rel = _download(url, rel_path)
    if rel:
        return rel
    if fallback:
        return _download(fallback[0], fallback[1])
    return ''


def clean(text, limit=110):
    if not text:
        return ''
    t = re.sub(r'<br\s*/?>', '｜', text)
    t = re.sub(r'<[^>]+>', '', t)
    t = html.unescape(t)
    t = re.sub(r'\s+', ' ', t).strip()
    if len(t) <= limit:
        return t
    cut = t[:limit]
    for mark in ('。', '；', '，', '｜'):
        i = cut.rfind(mark)
        if i > limit * 0.5:
            return cut[:i + 1] + '…'
    return cut + '…'


def parse_js_object(source, var_name):
    """從 script.js 抓出簡單的 JS 物件（只用到字串／字串陣列，不倚賴完整 JS 解析）。"""
    m = re.search(re.escape(var_name) + r'\s*=\s*\{', source)
    if not m:
        return {}
    i = m.end() - 1
    depth = 0
    for j in range(i, len(source)):
        if source[j] == '{':
            depth += 1
        elif source[j] == '}':
            depth -= 1
            if depth == 0:
                body = source[i:j + 1]
                break
    else:
        return {}
    body = re.sub(r'//[^\n]*', '', body)
    body = re.sub(r',\s*([}\]])', r'\1', body)      # 去掉結尾多餘的逗號
    body = re.sub(r'([{,]\s*)([A-Za-z_][A-Za-z0-9_]*)\s*:', r'\1"\2":', body)   # 補上沒加引號的 key，才能當 JSON 解析
    try:
        return json.loads(body)
    except Exception:                                             # noqa: BLE001
        return {}


def main():
    global VER
    versions = json.loads(fetch('https://ddragon.leagueoflegends.com/api/versions.json', 'versions.json'))
    VER = versions[0]
    print('Data Dragon 版本:', VER)

    champs = json.loads(ddragon('%s/data/zh_TW/championFull.json' % VER, 'champFull_%s.json' % VER))['data']
    items = json.loads(ddragon('%s/data/zh_TW/item.json' % VER, 'item_%s.json' % VER))['data']
    trees = json.loads(ddragon('%s/data/zh_TW/runesReforged.json' % VER, 'runes_%s.json' % VER))
    en = json.loads(ddragon('%s/data/en_US/champion.json' % VER, 'champEn_%s.json' % VER))['data']

    tree_by_name = {t['name']: t for t in trees}
    keystone_by_name = {}
    for t in trees:
        for r in t['slots'][0]['runes']:
            keystone_by_name[r['name']] = (t, r)

    # 位置對照：沿用 script.js 的 roleGroups（英文名 -> 中文名 -> key）
    script_src = ''
    sp = os.path.join(SITE, 'script.js?v=223fd8d6fd')
    if os.path.exists(sp):
        with open(sp, 'r', encoding='utf-8') as fh:
            script_src = fh.read()
    role_groups = parse_js_object(script_src, 'roleGroups')
    english_name = {k: v.get('name', k) for k, v in en.items()}
    name_to_key = {v.get('name', k): k for k, v in en.items()}
    role_of = {}
    for role, names in role_groups.items():
        for n in names:
            key = name_to_key.get(n) or name_to_key.get(n.replace('’', "'"))
            if key:
                role_of.setdefault(key, []).append(role)
    counters = parse_js_object(script_src, 'championCounters')
    aliases = parse_js_object(script_src, 'championAliases')
    quotes = parse_js_object(script_src, 'championQuotes')

    def rune_icon(path):
        return save_image('https://ddragon.leagueoflegends.com/cdn/img/%s' % path,
                          os.path.join('rune', re.sub(r'[^A-Za-z0-9_.-]', '_', path)))

    out = []
    missing_role = []
    for key, c in sorted(champs.items(), key=lambda kv: kv[1]['name']):
        tags = c.get('tags', [])
        # 職業判斷：先看輔助／射手，再看刺客與法師（帶坦克標籤的不算），
        # 最後才用坦克與鬥士區分（防禦成長高的才算純坦克）
        if 'Support' in tags:
            cls = 'Support'
        elif 'Marksman' in tags:
            cls = 'Marksman'
        elif 'Assassin' in tags and 'Fighter' in tags and 'Tank' not in tags:
            cls = 'Fighter'          # 犽宿、伊瑞莉雅這類「鬥士＋刺客」當鬥士處理比較合理
        elif 'Assassin' in tags and 'Tank' not in tags:
            cls = 'Assassin'
        elif 'Mage' in tags and 'Tank' not in tags:
            cls = 'Mage'
        elif 'Tank' in tags and ((c.get('info', {}) or {}).get('defense', 0) or 0) >= 7:
            cls = 'Tank'
        elif 'Fighter' in tags:
            cls = 'Fighter'
        elif 'Tank' in tags:
            cls = 'Tank'
        else:
            cls = 'Fighter'
        roles = role_of.get(key) or []
        if not roles:
            missing_role.append(key)
            roles = [ROLE_OVERRIDE.get(key) or ROLE_BY_TAG.get(cls, '中路')]
        role = roles[0]

        info = c.get('info', {}) or {}
        ap = (info.get('magic', 0) or 0) > (info.get('attack', 0) or 0)
        diff = info.get('difficulty', 5) or 5

        # 建議符文
        if cls == 'Support' and 'Tank' in tags:
            ks_name, main_tree, sub_tree = ENGAGE_SUPPORT
        else:
            ks_name, main_tree, sub_tree = RUNE_RULES.get(cls, TANKY_FIGHTER)
        _tree, ks = keystone_by_name[ks_name]

        # 核心裝備
        pool_key = cls
        if cls in ('Assassin', 'Fighter'):
            pool_key = cls + ('AP' if ap else 'AD') if (cls + ('AP' if ap else 'AD')) in ITEM_POOL else cls
        elif cls == 'Support':
            pool_key = 'SupportEng' if 'Tank' in tags else 'SupportEnc'
        item_list = []
        for iid in ITEM_POOL.get(pool_key, ITEM_POOL['Fighter']):
            it = items.get(str(iid))
            if not it:
                continue
            icon = save_image('https://ddragon.leagueoflegends.com/cdn/%s/img/item/%s.png' % (VER, iid),
                              os.path.join('item', '%s.png' % iid))
            item_list.append({'n': it['name'], 'i': icon, 'g': (it.get('gold') or {}).get('total', 0)})

        # 技能
        ability = []
        pas = c.get('passive') or {}
        if pas.get('image'):
            ability.append({'k': '被動', 'n': pas.get('name', ''), 'd': clean(pas.get('description', '')),
                            'i': save_image('https://ddragon.leagueoflegends.com/cdn/%s/img/passive/%s' % (VER, pas['image']['full']),
                                            os.path.join('ability', pas['image']['full']))})
        for letter, sp2 in zip('QWER', c.get('spells', [])[:4]):
            ability.append({'k': letter, 'n': sp2.get('name', ''), 'd': clean(sp2.get('description', '')),
                            'i': save_image('https://ddragon.leagueoflegends.com/cdn/%s/img/spell/%s' % (VER, sp2['image']['full']),
                                            os.path.join('ability', sp2['image']['full']))})

        tips = [clean(t, 90) for t in (c.get('allytips') or [])[:2] if t]
        enemy = [clean(t, 90) for t in (c.get('enemytips') or [])[:2] if t]
        cnt = counters.get(english_name.get(key, key)) or counters.get(key) or {}

        out.append({
            'key': key,
            'name': c['name'],
            'title': c.get('title', ''),
            'en': english_name.get(key, key),
            'aliases': (aliases.get(key) or [])[:4],
            'quote': quotes.get(key, ''),
            'roles': roles,
            'role': role,
            'tags': [TAG_ZH.get(t, t) for t in tags],
            'cls': cls,
            'diff': diff,
            'diffLabel': '簡單' if diff <= 4 else ('中等' if diff <= 7 else '困難'),
            'avatar': save_image('https://ddragon.leagueoflegends.com/cdn/img/champion/tiles/%s_0.jpg' % key,
                                 os.path.join('champ', '%s.jpg' % key),
                                 fallback=('https://ddragon.leagueoflegends.com/cdn/%s/img/champion/%s.png' % (VER, key),
                                           os.path.join('champ', '%s.png' % key))),
            'ability': ability,
            'rune': {
                'keystone': ks['name'],
                'desc': clean(ks.get('shortDesc') or ks.get('longDesc', ''), 130),
                'icon': rune_icon(ks['icon']),
                'tree': main_tree,
                'treeIcon': rune_icon(tree_by_name[main_tree]['icon']),
                'sub': sub_tree,
                'subIcon': rune_icon(tree_by_name[sub_tree]['icon']),
            },
            'items': item_list,
            'tactic': {
                'style': PLAYSTYLE.get(cls, PLAYSTYLE['Fighter']),
                'role': ROLE_NOTE.get(role, ''),
                'tips': tips,
                'enemy': enemy,
                'weak': cnt.get('weakAgainst', [])[:5],
                'strong': cnt.get('strongAgainst', [])[:5],
            },
            'url': {
                'lanelore': LANELORE_BASE + slugify(key),
                'logRunes': LOGRAPH_RUNES + log_slug(english_name.get(key, key)) + '/' + ROLE_SLUG.get(role, 'middle'),
                'logCounters': LOGRAPH_COUNTERS + log_slug(english_name.get(key, key)) + '/' + ROLE_SLUG.get(role, 'middle'),
            },
        })

    print('  圖片下載：%d 張 / %.1f MB' % (IMG.get('count', 0), IMG.get('bytes', 0) / 1024 / 1024))
    print('  英雄：%d 位' % len(out))
    if missing_role:
        print('  沒有位置對照（改用職業推斷）：%d 位 -> %s' % (len(missing_role), ', '.join(missing_role[:8])))

    data = {'version': VER, 'count': len(out), 'roles': ROLES, 'champions': out}
    jpath = os.path.join(ASSETS, 'champions.json')
    with open(jpath, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(data, fh, ensure_ascii=False, separators=(',', ':'))
    print('  已寫入 assets/lol/champions.json (%d KB)' % (os.path.getsize(jpath) // 1024))

    write_html(len(out))
    write_css()
    write_js()
    write_ui()
    return 0


def write_html(count):
    doc = '''<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <meta name="color-scheme" content="dark light">
    <meta name="theme-color" content="#05080d">
    <title>LOL 攻略站 V6.0 - 英雄資料庫</title>
    <link rel="stylesheet" href="style.css?v=edc69e60b9">
    <link rel="stylesheet" href="champions-db.css?v=c552231cd3">
</head>
<body class="bg-champions">
    <header class="topbar">
        <div class="brand">SUMMONER'S <span>GUIDE</span><b>V6.0</b></div>
        <nav>
            <a href="index.html">首頁</a>
            <a href="champions.html" style="color: #00d9ff; font-weight: 800;">英雄攻略</a>
            <a href="items.html">裝備攻略</a>
            <a href="guides.html">裝備合成</a>
        </nav>
        <button class="icon-btn" id="themeBtn">☀️</button>
    </header>

    <main class="champ-wrap">
        <section class="champ-hero">
            <small>CHAMPION DATABASE &middot; PATCH __VER__</small>
            <h1>英雄資料庫 <em>完整攻略卡</em></h1>
            <p>__COUNT__ 位英雄，每位都有角色頭像、技能圖示與簡介、位置、建議符文（含符文說明）、核心裝備與戰術解析。
               內容與圖片自動取自 Riot 官方 Data Dragon <b>__VER__</b>（zh_TW），並已下載到本機，離線也能看。</p>
            <div class="champ-hero__pills">
                <span>__COUNT__ 位英雄</span>
                <span>5 條路線</span>
                <span>被動＋Q/W/E/R 技能</span>
                <span>符文／裝備／戰術解析</span>
            </div>
        </section>

        <div class="champ-toolbar">
            <div class="role-filters" id="roleFilters">
                <button type="button" class="tab active" data-role="全部">全部 <b>__COUNT__</b></button>
__ROLETABS__
            </div>
            <div class="champ-selects">
                <select id="dbClass" aria-label="依職業篩選">
                    <option value="all">全部職業</option>
__CLASSOPS__
                </select>
                <select id="dbDiff" aria-label="依難度篩選">
                    <option value="all">全部難度</option>
                    <option value="簡單">簡單</option>
                    <option value="中等">中等</option>
                    <option value="困難">困難</option>
                </select>
                <input type="search" id="dbSearch" placeholder="搜尋英雄名稱、稱號或技能…" aria-label="搜尋英雄">
                <button type="button" class="small-btn" id="dbClear">清除篩選</button>
            </div>
        </div>

        <p class="champ-count" id="dbCount">載入中…</p>
        <div class="champ-grid" id="dbGrid"></div>
        <p class="champ-empty" id="dbEmpty" hidden>沒有符合條件的英雄，換個條件試試。</p>

        <div class="notice">
            📌 <b>資料說明：</b> 英雄、技能、符文與裝備資料及圖片皆取自 Riot 官方 Data Dragon <b>__VER__</b>（zh_TW），
            圖片已下載到 <b>assets/lol/</b>，開網站不需要連外。位置對照沿用站內既有設定；
            符文與核心裝備為依職業／位置整理的建議方向，實戰請依對局與對手調整。
        </div>
    </main>

    <div class="db-modal" id="dbModal" aria-hidden="true" role="dialog" aria-modal="true">
        <div class="db-modal__box" role="document">
            <button class="db-modal__close" id="dbClose" aria-label="關閉">&times;</button>
            <div id="dbModalBody"></div>
        </div>
    </div>

    <footer>
        <div>&copy; 2026 LOL 攻略站。LOL 攻略站是在 Riot Games 的「法律通則」方針下利用該公司擁有的資產所製作。Riot Games 不為此專案提供背書或贊助。</div>
        <div>資料基於 Patch ''' + esc(VER) + '''（Riot 官方 Data Dragon）· 僅供遊戲參考 · 非官方粉絲網站</div>
        <div>本站為靜態攻略資料庫，未串接 Riot API，不提供即時戰績或牌位查詢。</div>
    </footer>

    <script src="ui.js?v=d39d73f5a8"></script>
    <script src="nav.js?v=d667269d21" defer></script>`n    <script src="fx.js?v=1754a5f26d" defer></script>`n    <script src="i18n.js?v=dfd29133cb" defer></script>`n    <script src="state.js?v=51487b7398" defer></script>
    <script src="champions-db.js?v=3009f3a66f" defer></script>
</body>
</html>
'''
    role_tabs = []
    # 位置分頁的人數由 JS 以資料即時計算，這裡先給空殼
    for r in ROLES:
        role_tabs.append('                <button type="button" class="tab" data-role="%s">%s <b data-count="%s">0</b></button>'
                         % (r, r, r))
    class_ops = '\n'.join('                    <option value="%s">%s</option>' % (k, v)
                          for k, v in [('刺客', '刺客'), ('鬥士', '鬥士'), ('法師', '法師'),
                                       ('射手', '射手'), ('輔助', '輔助'), ('坦克', '坦克')])
    doc = doc.replace('__VER__', VER).replace('__COUNT__', str(count))
    doc = doc.replace('__ROLETABS__', '\n'.join(role_tabs)).replace('__CLASSOPS__', class_ops)
    path = os.path.join(SITE, 'champions.html')
    for _ in range(5):
        try:
            with open(path, 'w', encoding='utf-8', newline='\n') as fh:
                fh.write(doc)
            break
        except PermissionError:
            import time
            time.sleep(0.7)
    print('  已寫入 champions.html (%d bytes)' % os.path.getsize(path))


def write_css():
    css = '''/* ==========================================================================
   LOL 攻略站 — 英雄資料庫（champions.html）
   由 _build_champions.py 產生，圖片全部來自本機 assets/lol/。
   ========================================================================== */

/* 篩選用：.db-champ 有 display:grid，會蓋掉 [hidden]，所以這裡強制生效 */
[hidden] { display: none !important; }

.champ-wrap { width: min(1200px, 90%); margin: 30px auto 0; }

.champ-hero {
  position: relative; overflow: hidden; padding: 34px;
  border: 1px solid #22323d; border-radius: 18px;
  background:
    radial-gradient(120% 140% at 12% 0%, rgba(0, 217, 255, .14), transparent 60%),
    radial-gradient(100% 120% at 88% 100%, rgba(200, 170, 110, .16), transparent 60%),
    #0b1117;
}
.champ-hero small { color: #00d9ff; letter-spacing: 2.2px; font-weight: 800; font-size: 11px; }
.champ-hero h1 { margin: 10px 0 12px; font-size: clamp(30px, 4.4vw, 46px); line-height: 1.08; color: #f0eadb; }
.champ-hero h1 em { font-style: normal; color: #c8aa6e; }
.champ-hero p { max-width: 72ch; margin: 0; color: #aab4bc; }
.champ-hero__pills { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 18px; }
.champ-hero__pills span {
  padding: 6px 12px; font-size: 12px; font-weight: 700; color: #9ddff0;
  background: rgba(9, 20, 28, .66); border: 1px solid rgba(98, 170, 190, .35);
  border-radius: 999px; backdrop-filter: blur(8px);
}

.champ-toolbar { display: grid; gap: 12px; margin: 22px 0 6px; }
.role-filters { display: flex; flex-wrap: wrap; gap: 8px; }
.role-filters .tab b { color: #00d9ff; font-size: 11px; margin-left: 4px; }
.role-filters .tab.active b { color: #071016; }
.champ-selects { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; }
.champ-selects select, .champ-selects input[type="search"] {
  padding: 11px 14px; color: #e8e4d9; background: #080e14;
  border: 1px solid #2b3a45; border-radius: 10px;
}
.champ-selects input[type="search"] { flex: 1 1 240px; min-width: 180px; }
.champ-selects select:focus, .champ-selects input[type="search"]:focus { outline: 2px solid #00d9ff; outline-offset: 1px; }
.champ-count { margin: 4px 0 18px; color: #8e9aa4; font-size: 13px; }
.champ-empty { text-align: center; padding: 30px; color: #76838d; }

.champ-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; }
.champ-grid[hidden] { display: none; }

.db-champ {
  display: grid; gap: 10px; padding: 12px; text-align: left; font: inherit; color: inherit;
  background: linear-gradient(180deg, #101922, #0c141b);
  border: 1px solid #253540; border-radius: 14px; cursor: pointer;
  transition: transform .2s ease, border-color .2s ease, box-shadow .2s ease;
}
.db-champ:hover { transform: translateY(-3px); border-color: #00d9ff; box-shadow: 0 12px 28px rgba(0, 217, 255, .12); }
.db-champ:focus-visible { outline: 2px solid #00d9ff; outline-offset: 2px; }
.db-champ[hidden] { display: none; }
.db-champ__head { display: flex; gap: 10px; align-items: center; }
.db-champ__avatar {
  width: 52px; height: 52px; flex: 0 0 auto; border-radius: 12px;
  border: 1px solid #2f4453; background: #0a1016; object-fit: cover;
}
.db-champ__name { display: block; font-size: 15px; font-weight: 800; color: #f0eadb; }
.db-champ__title { display: block; font-size: 11.5px; color: #8e9aa4; }
.db-champ__tags { display: flex; flex-wrap: wrap; gap: 5px; }
.db-champ__tags .tag { margin-right: 0; font-size: 11px; padding: 3px 8px; }
.tag--role { background: rgba(200, 170, 110, .16); border-color: rgba(200, 170, 110, .45); color: #e8cf9c; }
.db-champ__hint { font-size: 11.5px; color: #6f7c86; }

/* ---------- 詳細彈窗 ---------- */
.db-modal {
  position: fixed; inset: 0; z-index: 120; display: none; place-items: center;
  padding: 20px; background: rgba(0, 0, 0, .78); backdrop-filter: blur(6px);
}
.db-modal.show { display: grid; }
.db-modal__box {
  position: relative; width: min(760px, 100%); max-height: 88vh; overflow: auto;
  padding: 26px; background: #0b131b; border: 1px solid #31505f; border-radius: 16px;
  box-shadow: 0 25px 80px #000;
}
.db-modal__close {
  position: absolute; right: 14px; top: 10px; z-index: 2;
  border: 0; background: none; color: #b9c2c8; font-size: 30px; line-height: 1; cursor: pointer;
}
.db-modal__close:hover { color: #fff; }

.db-head { display: flex; gap: 16px; align-items: center; margin-bottom: 6px; }
.db-head img { width: 72px; height: 72px; border-radius: 14px; border: 1px solid #2f4453; }
.db-head h2 { margin: 0 0 6px; font-size: 30px; color: #c8aa6e; }
.db-head h2 small { font-size: 13px; font-weight: 700; color: #8e9aa4; margin-left: 8px; }
.db-head__tags { display: flex; flex-wrap: wrap; gap: 6px; }

.db-alias { margin: 10px 0 6px; font-size: 12.5px; color: #9ddff0; }
.db-alias .tag { margin-right: 4px; background: #0f1a22; border-color: #2a4a58; }
.db-quote {
  margin: 10px 0 0; padding: 10px 14px; font-size: 13px; font-style: italic; color: #e0d8c8;
  background: linear-gradient(90deg, rgba(200, 170, 110, .1), rgba(0, 217, 255, .04));
  border-left: 3px solid #c8aa6e; border-radius: 0 10px 10px 0;
}

.db-section { padding-top: 14px; margin-top: 14px; border-top: 1px solid rgba(37, 53, 64, .9); }
.db-section > h3 {
  margin: 0 0 10px; font-size: 12px; font-weight: 800; letter-spacing: 1.6px;
  text-transform: uppercase; color: #00d9ff;
}

.db-abilities { display: grid; gap: 10px; }
.db-ability { display: flex; gap: 10px; align-items: flex-start; }
.db-ability img { width: 42px; height: 42px; flex: 0 0 auto; border-radius: 9px; border: 1px solid #2b3a45; background: #0a1016; }
.db-ability b { display: block; margin-bottom: 3px; font-size: 13.5px; color: #f0eadb; }
.db-ability p { margin: 0; font-size: 12.5px; line-height: 1.6; color: #9da9b2; }

.db-rune { display: flex; gap: 12px; align-items: flex-start; }
.db-rune > img {
  width: 52px; height: 52px; flex: 0 0 auto; border-radius: 50%; padding: 3px;
  border: 1px solid rgba(200, 170, 110, .55); background: #0a1016;
}
.db-rune b { display: block; font-size: 16px; color: #e8cf9c; }
.db-rune span { display: inline-flex; align-items: center; gap: 6px; margin: 4px 0 6px; font-size: 12px; color: #9ddff0; }
.db-rune span img { width: 18px; height: 18px; }
.db-rune p { margin: 0; font-size: 12.5px; line-height: 1.6; color: #9da9b2; }
.db-rune-sub { display: flex; align-items: center; gap: 6px; margin: 12px 0 0; font-size: 12.5px; color: #aab4bc; }
.db-rune-sub img { width: 20px; height: 20px; }
.db-rune-sub b { color: #e8cf9c; }
.db-rune-note { color: #6f7c86; font-size: 11.5px; }

.db-items { display: flex; flex-wrap: wrap; gap: 12px; }
.db-items figure { display: grid; justify-items: center; gap: 5px; width: 74px; margin: 0; text-align: center; }
.db-items img { width: 46px; height: 46px; border-radius: 10px; border: 1px solid #2b3a45; background: #0a1016; }
.db-items figcaption { font-size: 11px; line-height: 1.35; color: #aab4bc; }

.db-tactic { display: grid; gap: 10px; }
.db-tactic .box {
  padding: 11px 13px; font-size: 12.5px; line-height: 1.7; color: #c0c8cf;
  background: rgba(0, 217, 255, .06); border-left: 3px solid #00d9ff; border-radius: 0 10px 10px 0;
}
.db-tactic .box--gold {
  background: linear-gradient(90deg, rgba(200, 170, 110, .12), rgba(0, 217, 255, .04));
  border-left-color: #c8aa6e; color: #e0d8c8;
}
.db-tactic ul { margin: 4px 0 0; padding-left: 18px; }
.db-tactic li { margin: 2px 0; }
.db-tactic b { color: #f0eadb; }

.db-links { display: flex; flex-wrap: wrap; gap: 8px; }
.db-link {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 8px 12px; font-size: 12.5px; font-weight: 700; color: #cfe9f2;
  background: #0f1c25; border: 1px solid #2a4a58; border-radius: 999px;
  transition: border-color .18s, color .18s, background .18s;
}
.db-link:hover { color: #fff; background: #142934; border-color: #00d9ff; }
.db-link--local { color: #f0e2bd; background: #221c10; border-color: rgba(200, 170, 110, .45); }
.db-link--local:hover { border-color: #c8aa6e; color: #fff; }
.db-note { margin: 10px 0 0; font-size: 11.5px; line-height: 1.6; color: #6f7c86; }

@media (max-width: 1100px) { .champ-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); } }
@media (max-width: 900px)  { .champ-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 560px) {
  .champ-hero { padding: 20px; }
  .champ-grid { grid-template-columns: 1fr; gap: 10px; }
  .champ-selects input[type="search"], .champ-selects select { flex: 1 1 100%; width: 100%; }
  .db-modal { padding: 10px; }
  .db-modal__box { padding: 18px; max-height: 92vh; }
  .db-head img { width: 56px; height: 56px; }
  .db-head h2 { font-size: 24px; }
  .db-ability img { width: 36px; height: 36px; }
  .db-items figure { width: 62px; }
  .db-items img { width: 40px; height: 40px; }
}
@media (hover: none) {
  .db-champ:hover { transform: none; }
}
'''
    path = os.path.join(SITE, 'champions-db.css?v=c552231cd3')
    with open(path, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(css)
    print('  已寫入 champions-db.css (%d bytes)' % os.path.getsize(path))


def write_js():
    js = '''/* ==========================================================================
   LOL 攻略站 — 英雄資料庫前端
   資料來源：本機 assets/lol/champions.json（由 _build_champions.py 產生）
   ========================================================================== */
(function () {
  'use strict';

  var DATA = null;
  var byKey = {};
  var state = { role: '全部', cls: 'all', diff: 'all', q: '' };

  function $(id) { return document.getElementById(id); }
  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function cardHTML(c) {
    var tags = c.tags.map(function (t) { return '<span class="tag">' + esc(t) + '</span>'; }).join('');
    return '<button class="db-champ" type="button" data-key="' + esc(c.key) + '" data-role="' + esc(c.role) +
      '" data-cls="' + esc(c.tags.join(' ')) + '" data-diff="' + esc(c.diffLabel) +
      '" data-name="' + esc(c.name + ' ' + c.title + ' ' + c.tags.join(' ') + ' ' + (c.en || '') + ' ' + (c.aliases || []).join(' ')) + '">' +
      '<span class="db-champ__head">' +
      '<img class="db-champ__avatar" src="' + esc(c.avatar) + '" alt="' + esc(c.name) + '" loading="lazy" width="52" height="52">' +
      '<span><span class="db-champ__name">' + esc(c.name) + '</span>' +
      '<span class="db-champ__title">' + esc(c.title) + '</span></span></span>' +
      '<span class="db-champ__tags"><span class="tag tag--role">' + esc(c.role) + '</span>' + tags +
      '<span class="tag">難度：' + esc(c.diffLabel) + '</span></span>' +
      '<span class="db-champ__hint">點開看技能／符文／裝備／戰術解析 →</span>' +
      '</button>';
  }

  function detailHTML(c) {
    var abil = c.ability.map(function (a) {
      return '<div class="db-ability"><img src="' + esc(a.i) + '" alt="' + esc(a.n) + '" loading="lazy">' +
        '<div><b>' + esc(a.k) + '｜' + esc(a.n) + '</b><p>' + esc(a.d) + '</p></div></div>';
    }).join('');

    var items = c.items.map(function (it) {
      return '<figure><img src="' + esc(it.i) + '" alt="' + esc(it.n) + '" loading="lazy"><figcaption>' + esc(it.n) + '</figcaption></figure>';
    }).join('');

    var tips = (c.tactic.tips || []).map(function (t) { return '<li>' + esc(t) + '</li>'; }).join('');
    var enemy = (c.tactic.enemy || []).map(function (t) { return '<li>' + esc(t) + '</li>'; }).join('');
    var weak = (c.tactic.weak || []).join('、');
    var strong = (c.tactic.strong || []).join('、');

    return '<div class="db-head">' +
      '<img src="' + esc(c.avatar) + '" alt="' + esc(c.name) + '">' +
      '<div><h2>' + esc(c.name) + ' <small>' + esc(c.title) + '</small></h2>' +
      '<div class="db-head__tags"><span class="tag tag--role">' + esc(c.role) + '</span>' +
      c.tags.map(function (t) { return '<span class="tag">' + esc(t) + '</span>'; }).join('') +
      '<span class="tag">難度：' + esc(c.diffLabel) + '</span></div>' +
      ((c.aliases && c.aliases.length) ? '<p class="db-alias">🏷️ 玩家常用稱呼：' + c.aliases.map(function (a) { return '<span class="tag">' + esc(a) + '</span>'; }).join('') + '</p>' : '') +
      (c.quote ? '<blockquote class="db-quote">「' + esc(c.quote) + '」</blockquote>' : '') +
      '</div></div>' +

      '<section class="db-section"><h3>技能圖示與簡介</h3><div class="db-abilities">' + abil + '</div></section>' +

      '<section class="db-section"><h3>建議符文</h3><div class="db-rune">' +
      '<img src="' + esc(c.rune.icon) + '" alt="' + esc(c.rune.keystone) + '">' +
      '<div><b>' + esc(c.rune.keystone) + '</b>' +
      '<span><img src="' + esc(c.rune.treeIcon) + '" alt="">主樹：' + esc(c.rune.tree) + '</span>' +
      '<p>' + esc(c.rune.desc) + '</p></div></div>' +
      '<p class="db-rune-sub"><img src="' + esc(c.rune.subIcon) + '" alt="">副樹：<b>' + esc(c.rune.sub) + '</b>' +
      '<span class="db-rune-note">符文請依對局與對手調整，這裡是依職業／位置整理的建議方向。</span></p></section>' +

      '<section class="db-section"><h3>核心裝備</h3><div class="db-items">' + items + '</div></section>' +

      '<section class="db-section"><h3>戰術解析</h3><div class="db-tactic">' +
      '<div class="box box--gold">' + esc(c.tactic.style) + '</div>' +
      (c.tactic.role ? '<div class="box">' + esc(c.tactic.role) + '</div>' : '') +
      (tips ? '<div class="box"><b>Riot 官方提示：</b><ul>' + tips + '</ul></div>' : '') +
      (enemy ? '<div class="box"><b>對手會怎麼打你：</b><ul>' + enemy + '</ul></div>' : '') +
      ((weak || strong) ? '<div class="box"><b>站內整理對局：</b>' +
        (weak ? '較怕：' + esc(weak) + '　' : '') + (strong ? '較好打：' + esc(strong) : '') + '</div>' : '') +
      '</div></section>' +

      '<section class="db-section"><h3>即時數據 ＆ 更多資料</h3><div class="db-links">' +
      '<a class="db-link" href="' + esc(c.url.logRunes) + '" target="_blank" rel="noopener">📊 LeagueOfGraphs 符文勝率</a>' +
      '<a class="db-link" href="' + esc(c.url.logCounters) + '" target="_blank" rel="noopener">⚔ LeagueOfGraphs 對局</a>' +
      '<a class="db-link" href="' + esc(c.url.lanelore) + '" target="_blank" rel="noopener">🧭 LaneLore 出裝與符文</a>' +
      '<a class="db-link db-link--local" href="items.html">📚 站內裝備攻略</a></div>' +
      '<p class="db-note">勝率、選用率等即時統計請看上面兩個外部網站；本頁提供的是整理後的建議方向。</p></section>';
  }

  function open(key, push) {
    var c = byKey[key];
    if (!c) { return; }
    $('dbModalBody').innerHTML = detailHTML(c);
    $('dbModal').classList.add('show');
    $('dbModal').setAttribute('aria-hidden', 'false');
    if (push && history.replaceState) {
      history.replaceState(null, '', '#champ=' + encodeURIComponent(c.name));
    }
    document.querySelector('.db-modal__box').scrollTop = 0;      // 開窗後捲回頂端
  }

  function close() {
    $('dbModal').classList.remove('show');
    $('dbModal').setAttribute('aria-hidden', 'true');
    if (history.replaceState) history.replaceState(null, '', location.pathname + location.search);
  }

  function apply() {
    var grid = $('dbGrid');
    var q = (state.q || '').toLowerCase().trim();
    var shown = 0;
    var cards = grid.children;
    for (var i = 0; i < cards.length; i++) {
      var el = cards[i];
      var okRole = (state.role === '全部' || el.dataset.role === state.role);
      var okCls = (state.cls === 'all' || el.dataset.cls.indexOf(state.cls) >= 0);
      var okDiff = (state.diff === 'all' || el.dataset.diff === state.diff);
      var okQ = !q || (el.dataset.name || '').toLowerCase().indexOf(q) >= 0;
      var on = okRole && okCls && okDiff && okQ;
      el.hidden = !on;
      if (on) shown++;
    }
    $('dbCount').textContent = '顯示 ' + shown + ' 位英雄（共 ' + DATA.count + ' 位）';
    $('dbEmpty').hidden = shown !== 0;
  }

  function render() {
    var grid = $('dbGrid');
    grid.innerHTML = DATA.champions.map(cardHTML).join('');

    // 各位置人數
    var counts = { '全部': DATA.count };
    DATA.roles.forEach(function (r) { counts[r] = 0; });
    DATA.champions.forEach(function (c) { counts[c.role] = (counts[c.role] || 0) + 1; });
    Array.prototype.forEach.call(document.querySelectorAll('#roleFilters .tab'), function (tab) {
      var b = tab.querySelector('b');
      if (b) b.textContent = counts[tab.dataset.role] || 0;
    });

    grid.addEventListener('click', function (e) {
      var btn = e.target.closest ? e.target.closest('.db-champ') : null;
      if (btn) open(btn.dataset.key, true);
    });

    // 篩選
    Array.prototype.forEach.call(document.querySelectorAll('#roleFilters .tab'), function (tab) {
      tab.addEventListener('click', function () {
        Array.prototype.forEach.call(document.querySelectorAll('#roleFilters .tab'), function (t) { t.classList.remove('active'); });
        tab.classList.add('active');
        state.role = tab.dataset.role;
        apply();
      });
    });
    ['dbClass', 'dbDiff'].forEach(function (id) {
      var el = $(id);
      if (el) el.addEventListener('change', function () {
        if (id === 'dbClass') state.cls = el.value; else state.diff = el.value;
        apply();
      });
    });
    var box = $('dbSearch');
    if (box) box.addEventListener('input', function () { state.q = box.value; apply(); });
    var clr = $('dbClear');
    if (clr) clr.addEventListener('click', function () {
      var s = $('dbSearch'); if (s) s.value = '';
      var c1 = $('dbClass'); if (c1) c1.value = 'all';
      var c2 = $('dbDiff'); if (c2) c2.value = 'all';
      state = { role: '全部', cls: 'all', diff: 'all', q: '' };
      Array.prototype.forEach.call(document.querySelectorAll('#roleFilters .tab'), function (t) {
        t.classList.toggle('active', t.dataset.role === '全部');
      });
      apply();
    });

    $('dbClose').addEventListener('click', close);
    $('dbModal').addEventListener('click', function (e) { if (e.target === $('dbModal')) close(); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && $('dbModal').classList.contains('show')) close(); });

    apply();

    // 深層連結：#champ=英雄名（items.html 的站內連結會用到）
    var m = /^#champ=(.*)$/.exec(location.hash);
    if (m) {
      var name = m[1];
      try { name = decodeURIComponent(m[1]); } catch (e) { /* 保持原樣 */ }
      var hit = DATA.champions.filter(function (c) { return c.name === name; })[0];
      if (hit) setTimeout(function () { open(hit.key, false); }, 120);
    }

    // ?random=1：隨機抽一位英雄（首頁「隨機英雄」在資料還沒載入時會導到這裡）
    if (/[?&]random=1/.test(location.search) && DATA.champions.length) {
      var pick = DATA.champions[Math.floor(Math.random() * DATA.champions.length)];
      if (pick) setTimeout(function () { open(pick.key, true); }, 150);
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    var grid = $('dbGrid');
    if (!grid) return;
    fetch('assets/lol/champions.json')
      .then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
      .then(function (data) {
        DATA = data;
        data.champions.forEach(function (c) { byKey[c.key] = c; });
        render();
      })
      .catch(function (err) {
        grid.innerHTML = '';
        $('dbCount').textContent = '資料載入失敗：' + err.message + '（請確認 assets/lol/champions.json 存在）';
      });
  });
})();
'''
    path = os.path.join(SITE, 'champions-db.js?v=3009f3a66f')
    with open(path, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(js)
    print('  已寫入 champions-db.js (%d bytes)' % os.path.getsize(path))


def write_ui():
    """不載入 script.js 的頁面（英雄資料庫）用的小工具：主題切換。"""
    path = os.path.join(SITE, 'ui.js?v=d39d73f5a8')
    if os.path.exists(path):
        return
    js = '''/* ==========================================================================
   全站小工具：主題切換（給不載入 script.js 的頁面用，例如英雄資料庫）
   ========================================================================== */
(function () {
  'use strict';
  function init() {
    var btn = document.getElementById('themeBtn');
    if (!btn) return;
    var saved = null;
    try { saved = localStorage.getItem('lolTheme'); } catch (e) { /* 忽略 */ }
    if (saved === 'light') {
      document.body.classList.add('light');
      btn.textContent = '🌙';
    }
    btn.addEventListener('click', function () {
      document.body.classList.toggle('light');
      var light = document.body.classList.contains('light');
      btn.textContent = light ? '🌙' : '☀️';
      try { localStorage.setItem('lolTheme', light ? 'light' : 'dark'); } catch (e) { /* 忽略 */ }
    });
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
'''
    with open(path, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(js)
    print('  已寫入 ui.js (%d bytes)' % os.path.getsize(path))


if __name__ == '__main__':
    sys.exit(main())
