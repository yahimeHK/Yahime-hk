#!/usr/bin/env python3
"""
產生 items.html（符文 ＆ 核心裝備數據庫）。

資料與圖片來源：Riot 官方 Data Dragon（zh_TW），圖片下載到 assets/lol/ 供離線使用。
即時統計（勝率／選用率／對局）不轉載，改為連到本站既有的兩個外部資料來源：
  LeagueOfGraphs  https://www.leagueofgraphs.com/champions/runes/<slug>/<role>
  LaneLore        https://lanelore.com/champions/<slug>
（與 script.js 的 LiveGuideBase／CounterBase 使用同一套網址規則）

執行：python _build_items.py
"""
import html
import json
import os
import re
import sys
import urllib.parse
import urllib.request

# 網站根目錄：優先用環境變數，其次自動判斷（產生器放 tools/ 時，上一層就是網站根目錄）
_HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.environ.get('LOL_SITE') or (_HERE if os.path.exists(os.path.join(_HERE, 'index.html')) else os.path.dirname(_HERE))
ASSETS = os.path.join(SITE, 'assets', 'lol')
CACHE = os.path.join(os.environ['TEMP'], 'lolcache')
os.makedirs(CACHE, exist_ok=True)

VER = None
IMG = {}

# 與 script.js 相同的規則
ROLE_SLUG = {'上路': 'top', '打野': 'jungle', '中路': 'middle', '下路': 'adc', '輔助': 'support'}
SLUG_OVERRIDES = {'Nunu & Willump': 'nunu', 'Dr. Mundo': 'drmundo'}
# LeagueOfGraphs 少數英雄的網址是單一詞（LaneLore 用不到這組）
LOG_SLUG_OVERRIDES = {'Kaisa': 'kaisa'}
LANELORE_BASE = 'https://lanelore.com/champions/'
LOGRAPH_RUNES = 'https://www.leagueofgraphs.com/champions/runes/'
LOGRAPH_COUNTERS = 'https://www.leagueofgraphs.com/champions/counters/'


def slugify(name):
    s = str(name or '').lower().replace('&', '')
    s = re.sub(r"[.'’]", '', s)
    return re.sub(r'[^a-z0-9]+', '', s)


def log_slug(english_name):
    """LeagueOfGraphs 用的是英文名的連字號 slug：Jarvan IV -> jarvan-iv、Cho'Gath -> cho-gath。"""
    s = str(english_name or '').lower()
    # 空格、句點與撇號都當成分隔（Cho'Gath -> cho-gath、Jarvan IV -> jarvan-iv）
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


def save_image(url, rel_path):
    dest = os.path.join(ASSETS, rel_path)
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        return 'assets/lol/' + rel_path.replace('\\', '/')
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    for attempt in range(3):
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
            if attempt == 2:
                print('   ! 圖片下載失敗 %s -> %s' % (url, e), file=sys.stderr)
                return ''
    return ''


def clean(text, limit=118):
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
        if i > limit * 0.55:
            return cut[:i + 1] + '…'
    return cut + '…'


# ---------------------------------------------------------------------------
# (key, 位置, 基石符文, 主樹, 副樹, [核心裝備 id], 戰術解析, 技能加點, 召喚師技能, 對線重點)
CHAMPS = [
    ('Garen', '上路', '征服者', '精準', '意志', [223006, 226631, 223046, 223053, 223065],
     '用 E 疊征服者，Q 沉默後接 R 收頭；分推時留意對手控場，別把 W 減傷提前交掉。',
     'R > E > Q > W', '閃現 ＋ 點燃（也可帶傳送）',
     '一級用 Q 上前換血、E 轉圈清線；被遠程角壓時先補防禦，靠被動回血慢慢耗。'),
    ('Aatrox', '上路', '征服者', '精準', '意志', [223006, 226692, 223074, 226333, 223065],
     'Q 邊緣命中才有擊飛與增傷，E 位移用來修正 Q2／Q3 落點；被動印記在換血時會回血。',
     'R > Q > E > W', '閃現 ＋ 傳送',
     '前期用 Q1／Q2 消耗，Q3 命中才進場；注意 W 的施放距離，被動印記是換血本錢。'),
    ('Ambessa', '上路', '征服者', '精準', '意志', [3174, 226692, 223074, 223026, 223053],
     '靠位移疊層與能量管理打消耗，W 檔招、E 拉開距離；R 留給殘血追擊或強開。',
     'R > Q > E > W', '閃現 ＋ 傳送',
     '用位移吃兵兼消耗，能量不夠就退開；被壓時用 W 檔招，等六級再找反打機會。'),
    ('Kalista', '上路', '致命節奏', '精準', '征服', [223006, 223153, 223124, 223085, 223046],
     '普攻疊矛再 E 引爆，對線壓制力極強；R 能救被綁定的隊友，也能直接開團。',
     'R > E > Q > W', '閃現 ＋ 治癒',
     '普攻疊矛逼對手退，E 引爆要算斬殺線；R 可配合綁定的輔助硬開或救人。'),
    ('Chogath', '打野', '不死之握', '意志', '精準', [3174, 223084, 223110, 223065, 224401],
     'R 疊層永久增加生命，後期坦度驚人；Q 命中後接 W 沉默再進場，避免空大。',
     'R > Q > W > E', '閃現 ＋ 重擊',
     '以 Q 命中為主再進場，六級後 R 吃龍與疊層；對線型對手先出防禦再考慮傷害。'),
    ('JarvanIV', '打野', '征服者', '精準', '意志', [223111, 226631, 223071, 226333, 223053],
     'EQ 連段是開團核心，R 圈住對面關鍵輸出；前期節奏靠 Gank 與河道控制建立。',
     'R > Q > E > W', '閃現 ＋ 重擊',
     '三級後找機會 EQ 進場，配合線上隊友拿首殺；沒 Gank 就做河道視野與河蟹。'),
    ('Lillia', '打野', '征服者', '精準', '巫術', [223020, 224633, 223157, 224637, 223065],
     'W 中心命中傷害最高，靠被動移速拉扯；R 睡到多人再開團，Q 疊層別中斷。',
     'R > Q > W > E', '閃現 ＋ 重擊',
     '清野速度快，用 Q 疊層換血；W 中心命中是關鍵，對手有位移先用 E 減速。'),
    ('Viego', '打野', '征服者', '精準', '征服', [223006, 223153, 223074, 226333, 223026],
     '擊殺後佔據對手身體重置技能，團戰要挑時機進場收割；E 潛行繞後找關鍵目標。',
     'R > Q > E > W', '閃現 ＋ 重擊',
     '用 Q 消耗搭配 E 進出，六級後 R 進場收割；注意被動佔據的時機與血量。'),
    ('Vladimir', '中路', '風暴浪湧', '巫術', '啟示', [223020, 223089, 223040, 223100, 223157],
     '紅怒 Q 換血、W 既是保命也是進場；R 先手放大隊友傷害，注意血量換傷害的節奏。',
     'R > Q > E > W', '閃現 ＋ 傳送',
     '用 Q 換血，紅怒 Q 才上前；W 不要隨意交，留給對面的關鍵技能。'),
    ('Galio', '中路', '裂地衝擊', '意志', '巫術', [223020, 228020, 223157, 224401, 223190],
     'W 嘲諷是開團核心，R 可全球支援；對線用 Q 清線兼消耗，被動普攻範圍傷害別浪費。',
     'R > Q > W > E', '閃現 ＋ 傳送',
     'Q 清線兼消耗，W 嘲諷配合打野；R 全圖支援邊線，出手前先看隊友位置。'),
    ('Mel', '中路', '奧術彗星', '巫術', '啟示', [223020, 226655, 222503, 223089, 223157],
     '遠程消耗型法師，W 反彈技能要抓時機；保持距離疊加被動，靠 Q 持續騷擾。',
     'R > Q > E > W', '閃現 ＋ 點燃',
     '遠程消耗為主，W 反彈對面關鍵技能；保持距離，別讓近戰貼上身。'),
    ('Ahri', '中路', '奧術彗星', '巫術', '啟示', [223020, 226655, 222503, 223089, 223157],
     'Q 消耗、E 魅惑帶節奏；R 三段位移可進可退，永遠留一段當逃生。',
     'R > Q > W > E', '閃現 ＋ 點燃',
     'Q 兩段消耗，E 命中後接 QW 打爆發；R 進場或撤退都行，但別一次用完。'),
    ('Jinx', '下路', '致命節奏', '精準', '征服', [223006, 222523, 223085, 223031, 223036],
     '被動疊起來後攻速爆走，團戰靠走位站位；E 陷阱自保，R 收殘血與搶龍。',
     'R > Q > W > E', '閃現 ＋ 治癒',
     '前期用火箭筒騷擾，E 陷阱放自己腳下防近戰；六級後 R 可遠距離收頭。'),
    ('Varus', '下路', '強攻', '精準', '巫術', [223020, 223115, 223124, 223085, 226653],
     'AP 攻速流普攻附帶魔法傷害，W 主動強化爆發；R 綁人開團或反開都很強。',
     'R > Q > E > W', '閃現 ＋ 治癒',
     '普攻疊被動換血，E 減治療對抗吸血角；R 綁人配合打野最穩。'),
    ('Kaisa', '下路', '致命節奏', '精準', '征服', [223006, 223124, 223115, 223153, 223089],
     '靠堆疊被動觸發電漿爆發，進化後期傷害驚人；R 進場要算好護盾與隊友位置。',
     'R > Q > E > W', '閃現 ＋ 治癒',
     '用 Q 清兵兼疊被動，進化後再積極換血；R 留給隊友開戰時進場。'),
    ('Ezreal', '下路', '強攻', '精準', '啟示', [223158, 223078, 223004, 226675, 223146],
     'Q 命中疊攻速，E 既是位移也是保命；裝備成形後爆發與拉扯能力都極高。',
     'R > Q > E > W', '閃現 ＋ 治癒',
     'Q 命中疊攻速兼消耗，E 不要隨意交；對線偏保守，等核心裝成形再發力。'),
    ('Karma', '輔助', '召喚艾莉', '巫術', '啟示', [223158, 226620, 223222, 223050, 223190],
     'R 強化 Q 消耗或 E 給盾，對線期壓制力強；Q 減速配合射手換血最有效。',
     'R > Q > E > W', '閃現 ＋ 點燃',
     'R+Q 消耗、E 給盾換血；對線期是卡瑪最強的階段，前期就要打出優勢。'),
    ('Nami', '輔助', '召喚艾莉', '巫術', '啟示', [223158, 226617, 223222, 222065, 223190],
     'W 彈跳換血兼治療，Q 氣泡命中決定團戰；E 附魔給射手強化普攻，R 大範圍開團。',
     'R > W > E > Q', '閃現 ＋ 治癒',
     'W 彈跳換血兼治療，Q 氣泡配合射手；E 附魔讓射手普攻更痛。'),
    ('Leona', '輔助', '裂地衝擊', '意志', '啟示', [3174, 223109, 223050, 223190, 226665],
     'E 進場接 Q 暈眩，W 減傷扛傷；R 中心命中會暈眩，配合射手強開最有效。',
     'R > W > E > Q', '閃現 ＋ 點燃',
     '一級靠被動配合射手換血，E 進場接 Q 暈眩；W 先開再進場才能減傷。'),
    ('Thresh', '輔助', '裂地衝擊', '意志', '啟示', [223158, 223109, 223050, 223190, 223143],
     'Q 鉤中決定開戰節奏，W 燈籠救人與位移；E 拉回或推走都能改變戰局。',
     'R > Q > E > W', '閃現 ＋ 點燃',
     'Q 鉤中後 E 拉回，W 燈籠給隊友撤退或進攻；普攻騷擾但不要硬換。'),
]

ROLES = ['上路', '打野', '中路', '下路', '輔助']

TAG_ZH = {'Assassin': '刺客', 'Fighter': '鬥士', 'Mage': '法師',
          'Marksman': '射手', 'Support': '輔助', 'Tank': '坦克'}


def esc(s):
    return html.escape(str(s if s is not None else ''), quote=True)


def main():
    global VER
    versions = json.loads(fetch('https://ddragon.leagueoflegends.com/api/versions.json', 'versions.json'))
    VER = versions[0]
    print('Data Dragon 版本:', VER)

    champs = json.loads(ddragon('%s/data/zh_TW/championFull.json' % VER, 'champFull_%s.json' % VER))['data']
    items = json.loads(ddragon('%s/data/zh_TW/item.json' % VER, 'item_%s.json' % VER))['data']
    trees = json.loads(ddragon('%s/data/zh_TW/runesReforged.json' % VER, 'runes_%s.json' % VER))
    en = json.loads(ddragon('%s/data/en_US/champion.json' % VER, 'champEn_%s.json' % VER))['data']
    en_names = {k: v.get('name', k) for k, v in en.items()}
    tree_by_name = {t['name']: t for t in trees}
    keystone_by_name = {}
    for t in trees:
        for r in t['slots'][0]['runes']:
            keystone_by_name[r['name']] = (t, r)

    cards, problems = [], []
    for key, role, keystone, main_tree, sub_tree, item_ids, note, skill, spells, lane in CHAMPS:
        c = champs.get(key)
        if not c:
            problems.append('英雄不存在：%s' % key)
            continue
        if keystone not in keystone_by_name:
            problems.append('基石不存在：%s / %s' % (key, keystone))
            continue
        if main_tree not in tree_by_name or sub_tree not in tree_by_name:
            problems.append('符文樹不存在：%s' % key)
            continue

        tree, ks = keystone_by_name[keystone]
        avatar = save_image('https://ddragon.leagueoflegends.com/cdn/img/champion/tiles/%s_0.jpg' % key,
                            os.path.join('champ', '%s.jpg' % key))
        abilities = []
        pas = c.get('passive') or {}
        if pas.get('image'):
            abilities.append(('被動', pas.get('name', ''), pas.get('description', ''),
                              save_image('https://ddragon.leagueoflegends.com/cdn/%s/img/passive/%s' % (VER, pas['image']['full']),
                                         os.path.join('ability', pas['image']['full']))))
        for letter, sp in zip('QWER', c.get('spells', [])[:4]):
            abilities.append((letter, sp.get('name', ''), sp.get('description', ''),
                              save_image('https://ddragon.leagueoflegends.com/cdn/%s/img/spell/%s' % (VER, sp['image']['full']),
                                         os.path.join('ability', sp['image']['full']))))

        def rune_icon(path):
            return save_image('https://ddragon.leagueoflegends.com/cdn/img/%s' % path,
                              os.path.join('rune', re.sub(r'[^A-Za-z0-9_.-]', '_', path)))

        item_html = []
        for iid in item_ids:
            it = items.get(str(iid))
            if not it:
                problems.append('道具不存在：%s / %s' % (key, iid))
                continue
            icon = save_image('https://ddragon.leagueoflegends.com/cdn/%s/img/item/%s.png' % (VER, iid),
                              os.path.join('item', '%s.png' % iid))
            item_html.append((icon, it['name']))

        slug = SLUG_OVERRIDES.get(key, slugify(key))
        rslug = ROLE_SLUG.get(role, 'middle')
        lslug = LOG_SLUG_OVERRIDES.get(key, log_slug(en_names.get(key, key)))
        diff = (c.get('info') or {}).get('difficulty', 5)
        cards.append({
            'key': key, 'name': c['name'], 'title': c.get('title', ''), 'role': role,
            'tags': c.get('tags', []), 'avatar': avatar, 'abilities': abilities,
            'keystone': ks['name'], 'keystone_desc': clean(ks.get('shortDesc') or ks.get('longDesc', ''), 150),
            'rune_icon': rune_icon(ks['icon']), 'main_tree': main_tree, 'main_icon': rune_icon(tree['icon']),
            'sub_tree': sub_tree, 'sub_icon': rune_icon(tree_by_name[sub_tree]['icon']),
            'items': item_html, 'note': note,
            'skill': skill, 'spells': spells, 'lane': lane,
            'diff': '簡單' if diff <= 4 else ('中等' if diff <= 7 else '困難'),
            'url_lanelore': LANELORE_BASE + slug,
            'url_log_runes': LOGRAPH_RUNES + lslug + '/' + rslug,
            'url_log_counters': LOGRAPH_COUNTERS + lslug + '/' + rslug,
            'url_modal': 'champions.html#champ=' + urllib.parse.quote(c['name']),
        })

    if problems:
        print('\n有問題需要修正：')
        for pr in problems:
            print('  X', pr)
        return 1

    print('  圖片下載：%d 張 / %.1f MB' % (IMG.get('count', 0), IMG.get('bytes', 0) / 1024 / 1024))
    print('  英雄卡片：%d 張（含技能加點、召喚師技能、對線重點、外部數據連結）' % len(cards))
    write_html(cards)
    write_css()
    return 0


def write_html(cards):
    total_abilities = sum(len(c['abilities']) for c in cards)
    total_items = sum(len(c['items']) for c in cards)
    # 全英雄符文＆核心裝備數據庫（資料由 build_champions.py 產生）
    all_count = 0
    try:
        with open(os.path.join(ASSETS, 'champions.json'), encoding='utf-8') as fh:
            all_count = len(json.load(fh).get('champions', []))
    except Exception:                                             # noqa: BLE001
        all_count = 0
    p = []
    p.append('''<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LOL 攻略站 V6.0 - 裝備與符文數據庫</title>
    <link rel="stylesheet" href="style.css?v=edc69e60b9">
    <link rel="stylesheet" href="items.css?v=e5dfd4398b">
</head>
<body class="bg-items">
    <header class="topbar">
        <div class="brand">SUMMONER'S <span>GUIDE</span><b>V6.0</b></div>
        <nav>
            <a href="index.html">首頁</a>
            <a href="champions.html">英雄攻略</a>
            <a href="items.html" style="color: #00d9ff; font-weight: 800;">裝備攻略</a>
            <a href="guides.html">裝備合成</a>
        </nav>
        <button class="icon-btn" id="themeBtn">☀️</button>
    </header>

    <main class="items-wrap">
        <section class="items-hero">
            <small>BUILD LAB &middot; PATCH ''' + esc(VER) + '''</small>
            <h1>符文 ＆ 核心裝備 <em>數據庫</em></h1>
            <p>上方是<b>全英雄符文 ＆ 核心裝備資料庫</b>（''' + str(all_count) + ''' 位，建議基石含符文說明、主副符文樹與五件核心裝備），
               下方是深度攻略卡：技能加點、召喚師技能、對線重點與戰術解析。資料與圖片取自 Riot 官方 Data Dragon <b>''' + esc(VER) + '''</b> 並已下載到本機，離線可用。</p>
            <div class="items-hero__pills">
                <span>''' + str(all_count) + ''' 位英雄符文＆裝備</span>
                <span>''' + str(len(cards)) + ''' 張深度攻略卡</span>
                <span>''' + str(total_abilities) + ''' 個技能圖示</span>
                <span>''' + str(total_items) + ''' 件核心裝備</span>
                <span>5 條路線</span>
                <span>附即時數據連結</span>
            </div>
        </section>

        <section class="allchamp" id="allchampSection">
            <div class="db-heading">
                <small>RUNES &amp; CORE ITEMS &middot; 全英雄</small>
                <h2>符文 ＆ 核心裝備 數據庫 <em id="allTotal">載入中…</em></h2>
                <p>收錄全部英雄的建議基石（含官方符文說明）、主／副符文樹與五件核心裝備，點「完整攻略」可看技能與戰術解析。</p>
            </div>
            <div class="items-toolbar">
                <div class="role-filters" id="allRoleFilters"></div>
                <div class="ex-searchbox">
                    <span class="ex-searchbox__icon" aria-hidden="true">🔍</span>
                    <input type="search" id="allChampFilter" placeholder="輸入英雄名稱（中文或英文都可以）" aria-label="搜尋英雄" autocomplete="off">
                    <button type="button" id="allFind" class="ex-find">搜尋</button>
                    <button type="button" id="allReset" class="ex-reset" title="清除關鍵字" aria-label="清除關鍵字">✕</button>
                </div>
            </div>
            <p class="items-count" id="allCount">載入中…</p>
            <div class="allchamp-grid" id="allChampsGrid"></div>
            <p class="allchamp-empty" id="allEmpty" hidden>找不到符合的英雄，換個關鍵字試試。</p>
        </section>

        <div class="db-heading db-heading--deep">
            <small>DEEP DIVE</small>
            <h2>深度攻略卡 <em>''' + str(len(cards)) + ''' 位英雄</em></h2>
            <p>技能加點、召喚師技能、對線重點與戰術解析的完整版。</p>
        </div>

        <div class="items-toolbar">
            <div class="role-filters" id="roleFilters">
''')
    for i, r in enumerate(['全部'] + ROLES):
        n = len(cards) if r == '全部' else len([c for c in cards if c['role'] == r])
        p.append('                <button type="button" class="tab%s" data-role="%s">%s <b>%d</b></button>\n'
                 % (' active' if i == 0 else '', esc(r), esc(r), n))
    p.append('''            </div>
            <input type="search" id="champFilter" placeholder="搜尋英雄名稱、稱號或職業…" aria-label="搜尋英雄">
        </div>

        <p class="items-count" id="itemsCount">顯示 ''' + str(len(cards)) + ''' 位英雄</p>

        <div class="db-cards" id="buildCards">
''')

    for c in cards:
        p.append('''            <article class="db-card" data-role="%s" data-name="%s %s %s">
                <header class="db-card__head">
                    <img class="db-card__avatar" src="%s" alt="%s" loading="lazy">
                    <div class="db-card__id">
                        <h2>%s <small>%s</small></h2>
                        <div class="db-card__tags">
                            <span class="tag tag--role">%s</span>
%s                            <span class="tag">難度：%s</span>
                        </div>
                    </div>
                </header>

                <section class="build-block">
                    <h3>技能圖示與簡介</h3>
                    <ul class="ability-list">
''' % (esc(c['role']), esc(c['name']), esc(c['title']),
       ' '.join(TAG_ZH.get(t, t) for t in c['tags']),
       esc(c['avatar']), esc(c['name']), esc(c['name']), esc(c['title']), esc(c['role']),
       ''.join('                            <span class="tag">%s</span>\n' % esc(TAG_ZH.get(t, t)) for t in c['tags']),
       esc(c['diff'])))
        for letter, aname, adesc, icon in c['abilities']:
            p.append('''                        <li>
                            <img src="%s" alt="%s" loading="lazy">
                            <div><b>%s｜%s</b><p>%s</p></div>
                        </li>
''' % (esc(icon), esc(aname), esc(letter), esc(aname), esc(clean(adesc))))
        p.append('''                    </ul>
                </section>

                <section class="build-block">
                    <h3>技能加點 ＆ 召喚師技能</h3>
                    <div class="quick-grid">
                        <div class="quick"><span>技能加點順序</span><b>%s</b></div>
                        <div class="quick"><span>召喚師技能</span><b>%s</b></div>
                    </div>
                    <p class="lane-tip"><b>對線重點</b>%s</p>
                </section>

                <section class="build-block">
                    <h3>建議符文</h3>
                    <div class="rune-keystone">
                        <img src="%s" alt="%s" loading="lazy">
                        <div>
                            <b>%s</b>
                            <span class="rune-tree"><img src="%s" alt="">主樹：%s</span>
                            <p>%s</p>
                        </div>
                    </div>
                    <p class="rune-sub">
                        <img src="%s" alt="">副樹：<b>%s</b>
                        <span class="rune-note">符文請依對局與對手調整，這裡是當前主流方向。</span>
                    </p>
                </section>

                <section class="build-block">
                    <h3>核心裝備</h3>
                    <ul class="item-row">
''' % (esc(c['skill']), esc(c['spells']), esc(c['lane']),
       esc(c['rune_icon']), esc(c['keystone']), esc(c['keystone']), esc(c['main_icon']),
       esc(c['main_tree']), esc(c['keystone_desc']), esc(c['sub_icon']), esc(c['sub_tree'])))
        for icon, iname in c['items']:
            p.append('''                        <li><img src="%s" alt="%s" loading="lazy"><span>%s</span></li>
''' % (esc(icon), esc(iname), esc(iname)))
        p.append('''                    </ul>
                </section>

                <section class="build-block">
                    <h3>戰術解析</h3>
                    <p class="tactic">%s</p>
                </section>

                <section class="build-block build-block--links">
                    <h3>即時數據 ＆ 更多資料</h3>
                    <div class="ext-links">
                        <a class="ext-link" href="%s" target="_blank" rel="noopener">📊 LeagueOfGraphs 符文勝率</a>
                        <a class="ext-link" href="%s" target="_blank" rel="noopener">⚔ LeagueOfGraphs 對局</a>
                        <a class="ext-link" href="%s" target="_blank" rel="noopener">🧭 LaneLore 出裝與符文</a>
                        <a class="ext-link ext-link--local" href="%s">📚 站內：克制／稱呼／技能</a>
                    </div>
                    <p class="ext-note">勝率、選用率等即時統計請看上面兩個外部網站（本站既有的資料來源）；本頁提供的是整理後的建議方向。</p>
                </section>
            </article>
''' % (esc(c['note']), esc(c['url_log_runes']), esc(c['url_log_counters']),
       esc(c['url_lanelore']), esc(c['url_modal'])))

    p.append('''        </div>

        <section class="section dark" style="margin-top: 40px;">
            <div class="heading">
                <small>PRESETS DIRECTION</small>
                <h2>版本玩法方向盤</h2>
                <p>不知道從哪開始？先挑一個方向，再回到上面的卡片找對應英雄。</p>
            </div>
            <div class="build-grid" id="buildGrid" style="margin-top: 20px;"></div>
        </section>

        <div class="notice">
            📌 <b>資料說明：</b> 英雄、技能、符文與裝備資料及圖片皆取自 Riot 官方 Data Dragon <b>''' + esc(VER) + '''</b>（zh_TW），
            圖片已下載到 <b>assets/lol/</b>，開網站不需要連外。技能加點、召喚師技能、對線重點與戰術解析為整理後的建議方向；
            即時勝率與對局統計請點各卡片下方的 <b>LeagueOfGraphs</b> 與 <b>LaneLore</b> 連結。
        </div>
    </main>

    <div class="toast" id="toast"></div>
    <footer>
        <div>&copy; 2026 LOL 攻略站。LOL 攻略站是在 Riot Games 的「法律通則」方針下利用該公司擁有的資產所製作。Riot Games 不為此專案提供背書或贊助。</div>
        <div>資料基於 Patch ''' + esc(VER) + '''（Riot 官方 Data Dragon）· 僅供遊戲參考 · 非官方粉絲網站</div>
        <div>本站為靜態攻略資料庫，未串接 Riot API，不提供即時戰績或牌位查詢。</div>
    </footer>

    <script src="script.js?v=223fd8d6fd"></script>
    <script src="nav.js?v=e15ca57726" defer></script>`n    <script src="fx.js?v=beba14d08e" defer></script>`n    <script src="i18n.js?v=dfd29133cb" defer></script>`n    <script src="state.js?v=51487b7398" defer></script>
    <script>
        document.addEventListener('DOMContentLoaded', function () {
            var cards = Array.prototype.slice.call(document.querySelectorAll('#buildCards .db-card'));
            var tabs = Array.prototype.slice.call(document.querySelectorAll('#roleFilters .tab'));
            var box = document.getElementById('champFilter');
            var count = document.getElementById('itemsCount');
            var role = '全部';

            function apply() {
                var q = (box && box.value || '').toLowerCase().trim();
                var shown = 0;
                cards.forEach(function (card) {
                    var okRole = (role === '全部' || card.dataset.role === role);
                    var okText = !q || (card.dataset.name || '').toLowerCase().indexOf(q) >= 0;
                    var on = okRole && okText;
                    card.hidden = !on;
                    if (on) shown++;
                });
                if (count) count.textContent = '顯示 ' + shown + ' 位英雄';
            }

            tabs.forEach(function (tab) {
                tab.addEventListener('click', function () {
                    tabs.forEach(function (t) { t.classList.remove('active'); });
                    tab.classList.add('active');
                    role = tab.dataset.role;
                    apply();
                });
            });
            if (box) box.addEventListener('input', apply);
            apply();
        });
    </script>
    <script>
    /* 全英雄符文＆核心裝備數據庫（資料來源：assets/lol/champions.json，由 build_champions.py 產生） */
    (function () {
        'use strict';
        var ALL = [], role = '全部';
        function $(id) { return document.getElementById(id); }
        function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }

        function card(c) {
            var rune = c.rune || {};
            var its = c.items || [];
            var items = its.map(function (it) {
                return '<span class="ac-item" title="' + esc(it.n) + '"><img src="' + esc(it.i) + '" alt="' + esc(it.n) + '" loading="lazy"><i>' + esc(it.n) + '</i></span>';
            }).join('');
            var gold = its.reduce(function (n, it) { return n + (it.g || 0); }, 0);
            return '<article class="ac-card" data-role="' + esc(c.role) + '" data-name="' +
                esc([c.name, c.en, c.title, (c.aliases || []).join(' '), (c.tags || []).join(' ')].join(' ')) + '">' +
                '<header class="ac-card__head">' +
                '<img class="ac-card__avatar" src="' + esc(c.avatar) + '" alt="' + esc(c.name) + '" loading="lazy">' +
                '<div><b>' + esc(c.name) + '</b><small>' + esc(c.title) + '</small>' +
                '<span class="tag tag--role">' + esc(c.role) + '</span>' +
                (c.tags || []).map(function (x) { return '<span class="tag">' + esc(x) + '</span>'; }).join('') +
                '</div></header>' +
                '<div class="ac-rune"><img src="' + esc(rune.icon || '') + '" alt="">' +
                '<div><b>' + esc(rune.keystone || '') + '</b>' +
                '<span>主樹 ' + esc(rune.tree || '') + ' ／ 副樹 ' + esc(rune.sub || '') + '</span>' +
                '<p>' + esc(rune.desc || '') + '</p></div></div>' +
                '<div class="ac-items">' + items + '</div>' +
                '<footer class="ac-card__foot"><span>' + (gold ? '核心裝備共 ' + gold + ' 金幣' : '核心裝備 ' + its.length + ' 件') + '</span>' +
                '<a class="ext-link ext-link--local" href="champions.html#champ=' + encodeURIComponent(c.name) + '">完整攻略 →</a></footer>' +
                '</article>';
        }

        function apply() {
            var box = $('allChampFilter');
            var q = ((box && box.value) || '').toLowerCase().trim();
            var shown = 0;
            Array.prototype.forEach.call(document.querySelectorAll('#allChampsGrid .ac-card'), function (el) {
                var okRole = (role === '全部' || el.dataset.role === role);
                var okQ = !q || (el.dataset.name || '').toLowerCase().indexOf(q) >= 0;
                var on = okRole && okQ;
                el.hidden = !on;
                if (on) shown++;
            });
            $('allCount').textContent = '顯示 ' + shown + ' 位英雄（共 ' + ALL.length + ' 位）' + (q ? '（關鍵字：' + box.value.trim() + '）' : '');
            $('allEmpty').hidden = shown !== 0;
            var sb = document.querySelector('#allchampSection .ex-searchbox');
            if (sb) sb.classList.toggle('has-query', !!q);
        }

        function firstVisible() {
            var list = document.querySelectorAll('#allChampsGrid .ac-card');
            for (var i = 0; i < list.length; i++) { if (!list[i].hidden) return list[i]; }
            return null;
        }

        function build() {
            var grid = $('allChampsGrid');
            if (!grid) return;
            fetch('assets/lol/champions.json').then(function (r) {
                if (!r.ok) throw new Error('HTTP ' + r.status);
                return r.json();
            }).then(function (d) {
                ALL = d.champions || [];
                grid.innerHTML = ALL.map(card).join('');

                var counts = { '全部': ALL.length };
                ALL.forEach(function (c) { counts[c.role] = (counts[c.role] || 0) + 1; });
                $('allRoleFilters').innerHTML = ['全部', '上路', '打野', '中路', '下路', '輔助'].map(function (r) {
                    return '<button type="button" class="tab' + (r === '全部' ? ' active' : '') + '" data-role="' + r + '">' +
                        r + ' <b>' + (counts[r] || 0) + '</b></button>';
                }).join('');
                Array.prototype.forEach.call(document.querySelectorAll('#allRoleFilters .tab'), function (t) {
                    t.addEventListener('click', function () {
                        Array.prototype.forEach.call(document.querySelectorAll('#allRoleFilters .tab'), function (x) { x.classList.remove('active'); });
                        t.classList.add('active');
                        role = t.dataset.role;
                        apply();
                    });
                });

                var box = $('allChampFilter');
                if (box) {
                    box.addEventListener('input', apply);
                    box.addEventListener('keydown', function (e) {
                        if (e.key === 'Enter') { e.preventDefault(); apply(); var c = firstVisible(); if (c && c.scrollIntoView) c.scrollIntoView({ behavior: 'smooth', block: 'center' }); }
                        if (e.key === 'Escape') { box.value = ''; apply(); }
                    });
                }
                if ($('allFind')) $('allFind').addEventListener('click', function () {
                    apply();
                    var c = firstVisible();
                    if (c && c.scrollIntoView) c.scrollIntoView({ behavior: 'smooth', block: 'center' });
                });
                if ($('allReset')) $('allReset').addEventListener('click', function () {
                    if (box) { box.value = ''; box.focus(); }
                    apply();
                });

                $('allTotal').textContent = ALL.length + ' 位英雄';
                apply();
            }).catch(function (err) {
                $('allCount').textContent = '資料載入失敗：' + err.message;
            });
        }

        if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', build);
        else build();
    })();
    </script>
</body>
</html>
''')
    out = os.path.join(SITE, 'items.html')
    for attempt in range(5):
        try:
            with open(out, 'w', encoding='utf-8', newline='\n') as fh:
                fh.write(''.join(p))
            break
        except PermissionError:
            import time
            time.sleep(0.7)
    print('  已寫入 items.html (%d bytes)' % os.path.getsize(out))


def write_css():
    css = '''/* ==========================================================================
   LOL 攻略站 — 符文 ＆ 核心裝備數據庫（items.html）
   由 _build_items.py 產生，圖片全部來自本機 assets/lol/。
   ========================================================================== */

.items-wrap { width: min(1200px, 90%); margin: 30px auto 0; }

.items-hero {
  position: relative; overflow: hidden; padding: 34px;
  border: 1px solid #22323d; border-radius: 18px;
  background:
    radial-gradient(120% 140% at 10% 0%, rgba(200, 170, 110, .16), transparent 60%),
    radial-gradient(100% 120% at 92% 100%, rgba(0, 217, 255, .12), transparent 60%),
    #0b1117;
}
.items-hero small { color: #00d9ff; letter-spacing: 2.2px; font-weight: 800; font-size: 11px; }
.items-hero h1 { margin: 10px 0 12px; font-size: clamp(30px, 4.4vw, 46px); line-height: 1.08; color: #f0eadb; }
.items-hero h1 em { font-style: normal; color: #c8aa6e; }
.items-hero p { max-width: 72ch; margin: 0; color: #aab4bc; }
.items-hero__pills { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 18px; }
.items-hero__pills span {
  padding: 6px 12px; font-size: 12px; font-weight: 700; color: #9ddff0;
  background: rgba(9, 20, 28, .66); border: 1px solid rgba(98, 170, 190, .35);
  border-radius: 999px; backdrop-filter: blur(8px);
}

.items-toolbar { display: flex; flex-wrap: wrap; gap: 12px; align-items: center; justify-content: space-between; margin: 22px 0 6px; }
.role-filters { display: flex; flex-wrap: wrap; gap: 8px; }
.role-filters .tab b { color: #00d9ff; font-size: 11px; margin-left: 4px; }
.role-filters .tab.active b { color: #071016; }
.items-toolbar input[type="search"] {
  flex: 1 1 240px; min-width: 200px; padding: 11px 14px;
  color: #e8e4d9; background: #080e14; border: 1px solid #2b3a45; border-radius: 10px;
}
.items-toolbar input[type="search"]:focus { outline: 2px solid #00d9ff; outline-offset: 1px; }
.items-count { margin: 4px 0 18px; color: #8e9aa4; font-size: 13px; }

.db-cards { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px; }
.db-card {
  display: grid; gap: 14px; padding: 18px;
  background: linear-gradient(180deg, #101922, #0b1117);
  border: 1px solid #253540; border-radius: 16px;
  box-shadow: 0 16px 40px rgba(0, 0, 0, .22);
}
.db-card[hidden] { display: none; }

.db-card__head { display: flex; gap: 14px; align-items: center; }
.db-card__avatar {
  width: 64px; height: 64px; flex: 0 0 auto; border-radius: 14px;
  border: 1px solid #2f4453; object-fit: cover; background: #0a1016;
}
.db-card__id h2 { margin: 0 0 6px; font-size: 21px; color: #f0eadb; }
.db-card__id h2 small { font-size: 12px; font-weight: 700; color: #8e9aa4; margin-left: 6px; }
.db-card__tags { display: flex; flex-wrap: wrap; gap: 6px; }
.db-card__tags .tag { margin-right: 0; }
.tag--role { background: rgba(200, 170, 110, .16); border-color: rgba(200, 170, 110, .45); color: #e8cf9c; }

.build-block { padding-top: 12px; border-top: 1px solid rgba(37, 53, 64, .9); }
.build-block h3 {
  margin: 0 0 10px; font-size: 12px; font-weight: 800; letter-spacing: 1.6px;
  text-transform: uppercase; color: #00d9ff;
}

.ability-list { display: grid; gap: 10px; margin: 0; padding: 0; list-style: none; }
.ability-list li { display: flex; gap: 10px; align-items: flex-start; }
.ability-list img { width: 42px; height: 42px; flex: 0 0 auto; border-radius: 9px; border: 1px solid #2b3a45; background: #0a1016; }
.ability-list b { display: block; margin-bottom: 3px; font-size: 13.5px; color: #f0eadb; }
.ability-list p { margin: 0; font-size: 12.5px; line-height: 1.6; color: #9da9b2; }

.quick-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }
.quick { padding: 10px 12px; background: #0d151d; border: 1px solid #22323d; border-radius: 10px; }
.quick span { display: block; margin-bottom: 4px; font-size: 11px; letter-spacing: 1px; font-weight: 800; color: #76838d; }
.quick b { font-size: 14px; color: #e8cf9c; }
.lane-tip {
  margin: 12px 0 0; padding: 10px 12px; font-size: 12.5px; line-height: 1.65; color: #c0c8cf;
  background: rgba(0, 217, 255, .06); border-left: 3px solid #00d9ff; border-radius: 0 10px 10px 0;
}
.lane-tip b { display: block; margin-bottom: 3px; color: #9ddff0; font-size: 11px; letter-spacing: 1px; }

.rune-keystone { display: flex; gap: 12px; align-items: flex-start; }
.rune-keystone > img {
  width: 52px; height: 52px; flex: 0 0 auto; border-radius: 50%;
  border: 1px solid rgba(200, 170, 110, .55); background: #0a1016; padding: 3px;
}
.rune-keystone b { display: block; font-size: 16px; color: #e8cf9c; }
.rune-tree { display: inline-flex; align-items: center; gap: 6px; margin: 4px 0 6px; font-size: 12px; color: #9ddff0; }
.rune-tree img { width: 18px; height: 18px; }
.rune-keystone p { margin: 0; font-size: 12.5px; line-height: 1.6; color: #9da9b2; }
.rune-sub { display: flex; align-items: center; flex-wrap: wrap; gap: 6px; margin: 12px 0 0; font-size: 12.5px; color: #aab4bc; }
.rune-sub img { width: 20px; height: 20px; }
.rune-sub b { color: #e8cf9c; }
.rune-note { color: #6f7c86; font-size: 11.5px; }

.item-row { display: flex; flex-wrap: wrap; gap: 12px; margin: 0; padding: 0; list-style: none; }
.item-row li { display: grid; justify-items: center; gap: 5px; width: 74px; text-align: center; }
.item-row img { width: 46px; height: 46px; border-radius: 10px; border: 1px solid #2b3a45; background: #0a1016; }
.item-row span { font-size: 11px; line-height: 1.35; color: #aab4bc; }

.tactic {
  margin: 0; padding: 12px 14px; font-size: 13px; line-height: 1.7; color: #e0d8c8;
  background: linear-gradient(90deg, rgba(200, 170, 110, .1), rgba(0, 217, 255, .04));
  border-left: 3px solid #c8aa6e; border-radius: 0 10px 10px 0;
}

.ext-links { display: flex; flex-wrap: wrap; gap: 8px; }
.ext-link {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 8px 12px; font-size: 12.5px; font-weight: 700; color: #cfe9f2;
  background: #0f1c25; border: 1px solid #2a4a58; border-radius: 999px;
  transition: border-color .18s, color .18s, background .18s;
}
.ext-link:hover { color: #fff; background: #142934; border-color: #00d9ff; }
.ext-link--local { color: #f0e2bd; background: #221c10; border-color: rgba(200, 170, 110, .45); }
.ext-link--local:hover { border-color: #c8aa6e; color: #fff; }
.ext-note { margin: 10px 0 0; font-size: 11.5px; line-height: 1.6; color: #6f7c86; }

@media (max-width: 1000px) { .db-cards { grid-template-columns: 1fr; } }
@media (max-width: 700px) {
  .items-hero { padding: 22px; }
  .db-card { padding: 14px; }
  .db-card__avatar { width: 54px; height: 54px; }
  .item-row li { width: 62px; }
  .item-row img { width: 40px; height: 40px; }
  .quick-grid { grid-template-columns: 1fr; }
}

/* ===== 裝置相容（V6.0） ===== */
@media (hover: none) {
  .db-card:hover, .ext-link:hover { transform: none; }
}
@media (max-width: 480px) {
  .items-hero { padding: 18px; }
  .items-hero__pills span { font-size: 11px; padding: 5px 10px; }
  .items-toolbar input[type="search"] { flex: 1 1 100%; }
  .role-filters .tab { padding: 8px 12px; font-size: 13px; }
  .db-card { padding: 12px; gap: 12px; }
  .db-card__avatar { width: 48px; height: 48px; border-radius: 12px; }
  .db-card__id h2 { font-size: 18px; }
  .ability-list img { width: 36px; height: 36px; }
  .ability-list p { font-size: 12px; }
  .quick b { font-size: 13px; }
  .rune-keystone > img { width: 44px; height: 44px; }
  .item-row { gap: 8px; }
  .item-row li { width: 58px; }
  .item-row img { width: 40px; height: 40px; }
  .item-row span { font-size: 10.5px; }
  .ext-link { font-size: 12px; padding: 7px 10px; }
}
'''
    # 全英雄符文＆核心裝備數據庫
    css += '''

/* ===== 全英雄符文 ＆ 核心裝備 數據庫 ===== */
[hidden] { display: none !important; }          /* 卡片有 display:flex／grid，會蓋掉 [hidden] */
.db-heading { margin: 6px 0 16px; }
.db-heading--deep { margin-top: 44px; padding-top: 24px; border-top: 1px solid #1d2a33; }
.db-heading small { color: #00d9ff; letter-spacing: 2.2px; font-weight: 800; font-size: 11px; }
.db-heading h2 { margin: 8px 0 10px; font-size: clamp(23px, 3.2vw, 32px); color: #f0eadb; }
.db-heading h2 em { font-style: normal; color: #c8aa6e; font-size: .64em; margin-left: 8px; }
.db-heading p { margin: 0; color: #aab4bc; max-width: 74ch; }

.allchamp { margin: 30px 0 6px; }
.allchamp-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(292px, 1fr)); gap: 14px; }
.allchamp-empty { text-align: center; padding: 24px; color: #76838d; }

.ac-card {
  padding: 14px; background: linear-gradient(180deg, #101922, #0b1117);
  border: 1px solid #253540; border-radius: 14px;
  transition: transform .2s ease, border-color .2s ease;
}
.ac-card:hover { transform: translateY(-3px); border-color: #2f4d5c; }
.ac-card__head { display: flex; gap: 10px; align-items: center; margin-bottom: 10px; }
.ac-card__avatar { width: 52px; height: 52px; border-radius: 12px; border: 1px solid #2f4453; background: #0a1016; }
.ac-card__head b { display: block; font-size: 15.5px; color: #f0eadb; }
.ac-card__head small { display: block; margin: 1px 0 5px; font-size: 11.5px; color: #8e9aa4; }
.ac-card__head .tag { margin-right: 4px; font-size: 10.5px; padding: 2px 7px; }

.ac-rune {
  display: flex; gap: 10px; padding: 10px 11px;
  background: linear-gradient(90deg, rgba(200, 170, 110, .12), rgba(0, 217, 255, .04));
  border-left: 3px solid #c8aa6e; border-radius: 0 10px 10px 0;
}
.ac-rune > img { width: 42px; height: 42px; flex: 0 0 auto; border-radius: 50%; background: #0a1016; padding: 2px; border: 1px solid rgba(200, 170, 110, .45); }
.ac-rune b { display: block; font-size: 14px; color: #e8cf9c; }
.ac-rune span { display: block; margin: 2px 0 4px; font-size: 11.5px; color: #9ddff0; }
.ac-rune p { margin: 0; font-size: 11.5px; line-height: 1.55; color: #9da9b2; }

.ac-items { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; }
.ac-item { display: grid; justify-items: center; width: 52px; }
.ac-item img { width: 40px; height: 40px; border-radius: 9px; border: 1px solid #2b3a45; background: #0a1016; }
.ac-item i { font-style: normal; margin-top: 3px; font-size: 9.5px; line-height: 1.25; color: #8e9aa4; text-align: center; }

.ac-card__foot { display: flex; align-items: center; justify-content: space-between; gap: 8px; margin-top: 12px; padding-top: 10px; border-top: 1px solid #22323d; font-size: 11.5px; color: #c8aa6e; }
.ac-card__foot .ext-link { font-size: 11.5px; padding: 6px 10px; }

/* 搜尋框（含圖示、搜尋鈕、清除鈕） */
.ex-searchbox {
  flex: 1 1 300px; display: flex; align-items: center; gap: 6px;
  padding: 4px 4px 4px 12px; background: #080e14;
  border: 1px solid #2b3a45; border-radius: 12px; transition: border-color .18s, box-shadow .18s;
}
.ex-searchbox:focus-within { border-color: #00d9ff; box-shadow: 0 0 0 3px rgba(0, 217, 255, .12); }
.ex-searchbox__icon { font-size: 14px; opacity: .75; }
.ex-searchbox input[type="search"] {
  flex: 1 1 auto; min-width: 0; padding: 8px 2px; color: #e8e4d9;
  background: transparent; border: 0; font: inherit;
}
.ex-searchbox input[type="search"]:focus { outline: none; }
.ex-searchbox input[type="search"]::-webkit-search-cancel-button { display: none; }
.ex-searchbox .ex-find {
  flex: 0 0 auto; padding: 8px 16px; font-size: 13px; font-weight: 800; color: #071016;
  background: linear-gradient(180deg, #d8bd80, #c8aa6e); border: 0; border-radius: 9px; cursor: pointer;
}
.ex-searchbox .ex-find:hover { filter: brightness(1.08); }
.ex-searchbox .ex-reset {
  flex: 0 0 auto; display: none; padding: 8px 10px; font-size: 13px; color: #9da9b2;
  background: #111d26; border: 1px solid #2b3a45; border-radius: 9px; cursor: pointer;
}
.ex-searchbox.has-query .ex-reset { display: inline-block; }
.ex-searchbox .ex-reset:hover { color: #fff; border-color: #00d9ff; }

@media (max-width: 1000px) { .allchamp-grid { grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); } }
@media (max-width: 700px) {
  .allchamp-grid { grid-template-columns: 1fr; }
  .ac-card__head .tag { font-size: 10px; }
}
@media (hover: none) { .ac-card:hover { transform: none; } }
'''
    out = os.path.join(SITE, 'items.css?v=e5dfd4398b')
    with open(out, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(css)
    print('  已寫入 items.css (%d bytes)' % os.path.getsize(out))


if __name__ == '__main__':
    sys.exit(main())
