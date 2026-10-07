#!/usr/bin/env python3
"""
產生七個分類分頁（可重複執行、跟著 Riot 官方資料更新）：

  skins.html     角色造型（每位英雄的造型縮圖，已排除炫彩，最多 6 個）
  gallery.html   圖片（官方讀取圖牆 + 四張頁面桌布）
  abilities.html 技能圖片及簡介（全英雄被動與 Q/W/E/R）
  maps.html      地圖（召喚峽谷／嚎哭深淵等，含地圖重點）
  runes.html     符文 ＋ 符文簡介（五條符文樹全部符文與官方說明）
  gear.html      核心裝備（可購買道具、價格、說明、合成路徑）
  tactics.html   戰術解析（玩法定位、位置重點、Riot 官方提示、克制資料）

素材來源：Riot 官方 Data Dragon（zh_TW），圖片下載到 assets/lol/ 供離線使用。
造型縮圖與讀取圖會用 Pillow 縮小，避免 repo 過大。

執行：python tools/build_extra.py
"""
import html
import json
import os
import re
import sys
import time
import urllib.request

_HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.environ.get('LOL_SITE') or (_HERE if os.path.exists(os.path.join(_HERE, 'index.html')) else os.path.dirname(_HERE))
ASSETS = os.path.join(SITE, 'assets', 'lol')
CACHE = os.path.join(os.environ['TEMP'], 'lolcache')
os.makedirs(CACHE, exist_ok=True)
os.makedirs(ASSETS, exist_ok=True)

VER = None
IMG = {'n': 0, 'b': 0}
_LAST = [0.0]
MAX_SKINS = 6          # 每位英雄最多收錄幾個造型（不含炫彩）
SKIN_PX = 144          # 造型縮圖邊長
ART_PX = 260           # 讀取圖縮圖寬度

try:
    from PIL import Image
    import io as _io
    HAVE_PIL = True
except Exception:                                                 # noqa: BLE001
    HAVE_PIL = False


# --------------------------------------------------------------------- 工具
def polite(min_gap=0.1):
    wait = min_gap - (time.time() - _LAST[0])
    if wait > 0:
        time.sleep(wait)
    _LAST[0] = time.time()


def fetch(url, cache_name=None):
    path = os.path.join(CACHE, cache_name) if cache_name else None
    if path and os.path.exists(path) and os.path.getsize(path) > 500:
        with open(path, encoding='utf-8') as fh:
            return fh.read()
    polite()
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (lol-guide-build)'})
    with urllib.request.urlopen(req, timeout=180) as r:
        raw = r.read().decode('utf-8')
    if path:
        with open(path, 'w', encoding='utf-8') as fh:
            fh.write(raw)
    return raw


def ddragon(path, cache_name=None):
    return fetch('https://ddragon.leagueoflegends.com/cdn/%s' % path, cache_name)


def _download(url, rel_path, attempts=4):
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
            IMG['n'] += 1
            IMG['b'] += len(data)
            return 'assets/lol/' + rel_path.replace('\\', '/')
        except Exception as e:                                    # noqa: BLE001
            last = e
            time.sleep(1.0 * (attempt + 1))
    print('   ! 下載失敗 %s -> %s' % (url, last), file=sys.stderr)
    return ''


def save_image(url, rel_path, square_px=None, width_px=None):
    """下載圖片；指定尺寸且有 Pillow 時會縮小後才放進 assets（原始檔只留在快取，不佔 repo）。"""
    if (square_px or width_px) and HAVE_PIL:
        rel_path = re.sub(r'\.(jpg|jpeg|png)$', r'_s.\1', rel_path)
        dest = os.path.join(ASSETS, rel_path)
        if os.path.exists(dest) and os.path.getsize(dest) > 0:
            return 'assets/lol/' + rel_path.replace('\\', '/')
        tmp_src = os.path.join(CACHE, 'img_' + os.path.basename(rel_path).replace('_s.', '.'))
        if not (os.path.exists(tmp_src) and os.path.getsize(tmp_src) > 0):
            ok = False
            for attempt in range(4):
                polite()
                try:
                    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (lol-guide-build)'})
                    with urllib.request.urlopen(req, timeout=120) as r:
                        data = r.read()
                    with open(tmp_src, 'wb') as fh:
                        fh.write(data)
                    ok = True
                    break
                except Exception:                                 # noqa: BLE001
                    time.sleep(1.0 * (attempt + 1))
            if not ok:
                print('   ! 下載失敗 %s' % url, file=sys.stderr)
                return ''
        try:
            from PIL import Image as _Image
            im = _Image.open(tmp_src).convert('RGB')
            if square_px:
                side = min(im.size)
                left = (im.width - side) // 2
                top = max(0, int((im.height - side) * 0.28))
                im = im.crop((left, top, left + side, top + side)).resize((square_px, square_px), _Image.LANCZOS)
            else:
                h = max(1, round(im.height * width_px / im.width))
                im = im.resize((width_px, h), _Image.LANCZOS)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            im.save(dest, 'JPEG', quality=78, optimize=True)
            IMG['n'] += 1
            IMG['b'] += os.path.getsize(dest)
            return 'assets/lol/' + rel_path.replace('\\', '/')
        except Exception as e:                                    # noqa: BLE001
            print('   ! 縮圖失敗 %s -> %s' % (tmp_src, e), file=sys.stderr)
            return ''
    return _download(url, rel_path)

def clean(text, limit=140):
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


def esc(s):
    return html.escape(str(s if s is not None else ''), quote=True)


# ------------------------------------------------------------------ 主流程
def main():
    global VER
    versions = json.loads(fetch('https://ddragon.leagueoflegends.com/api/versions.json', 'versions.json'))
    VER = versions[0]
    print('Data Dragon 版本:', VER, '（Pillow:', HAVE_PIL, '）')

    champs = json.loads(ddragon('%s/data/zh_TW/championFull.json' % VER, 'champFull_%s.json' % VER))['data']
    items = json.loads(ddragon('%s/data/zh_TW/item.json' % VER, 'item_%s.json' % VER))['data']
    trees = json.loads(ddragon('%s/data/zh_TW/runesReforged.json' % VER, 'runes_%s.json' % VER))
    en = json.loads(ddragon('%s/data/en_US/champion.json' % VER, 'champEn_%s.json' % VER))['data']

    # 既有資料：位置與戰術解析沿用 build_champions.py 產生的 champions.json
    champ_json = os.path.join(ASSETS, 'champions.json')
    base = json.load(open(champ_json, encoding='utf-8')) if os.path.exists(champ_json) else {'champions': []}
    base_by_key = {c['key']: c for c in base.get('champions', [])}
    print('  讀到既有英雄資料:', len(base_by_key), '位')

    # ---------------------------------------------------- 1) 角色造型
    skins_out = []
    for key, c in sorted(champs.items(), key=lambda kv: kv[1]['name']):
        real = [s for s in (c.get('skins') or []) if '(' not in s['name'] and '（' not in s['name']]
        real = real[:MAX_SKINS]
        if not real:
            continue
        rows = []
        for s in real:
            img = save_image('https://ddragon.leagueoflegends.com/cdn/img/champion/tiles/%s_%d.jpg' % (key, s['num']),
                             os.path.join('skin', '%s_%d.jpg' % (key, s['num'])), square_px=SKIN_PX)
            if img:
                rows.append({'num': s['num'], 'name': '預設造型' if s['name'] == 'default' else s['name'],
                             'img': img,
                             'big': 'https://ddragon.leagueoflegends.com/cdn/img/champion/splash/%s_%d.jpg' % (key, s['num'])})
        if rows:
            skins_out.append({'key': key, 'champ': c['name'], 'role': (base_by_key.get(key) or {}).get('role', ''),
                              'skins': rows})
    write_json('skins.json', {'version': VER, 'champions': skins_out})
    print('  角色造型：%d 位英雄 / %d 張縮圖' % (len(skins_out), sum(len(x['skins']) for x in skins_out)))

    # ---------------------------------------------------- 2) 圖片（讀取圖牆＋桌布）
    art_out = []
    for key, c in sorted(champs.items(), key=lambda kv: kv[1]['name']):
        img = save_image('https://ddragon.leagueoflegends.com/cdn/img/champion/loading/%s_0.jpg' % key,
                         os.path.join('art', '%s.jpg' % key), width_px=ART_PX)
        if img:
            art_out.append({'key': key, 'champ': c['name'], 'title': c.get('title', ''),
                            'role': (base_by_key.get(key) or {}).get('role', ''), 'img': img,
                            'big': 'https://ddragon.leagueoflegends.com/cdn/img/champion/splash/%s_0.jpg' % key})
    write_json('gallery.json', {'version': VER, 'champions': art_out})
    print('  圖片：%d 張讀取圖' % len(art_out))

    # ---------------------------------------------------- 3) 地圖
    maps_meta = [
        ('map11', '召喚峽谷', '5 對 5 經典模式', [
            '三條路線＋野區，地圖目標決定勝負節奏。',
            '小龍 5:00 出生，之後每 5 分鐘重生；擊殺 4 條可獲得龍魂。',
            '預示者 8:00 出生、14:00 前要打完，可召喚撞塔。',
            '巴龍 20:00 出生，重生間隔 6 分鐘；拿到巴龍是推進與結束比賽的關鍵。',
            '視野重點：河道草叢、三角草、龍／巴龍區入口。',
        ]),
        ('map12', '嚎哭深淵', 'ARAM 單線大亂鬥', [
            '單線擠壓、無法回城，只能靠死亡或隊友治療補給。',
            '開場就是團戰，選角以消耗、開戰與清線能力為主。',
            '雪球（標記）是唯一的進場位移手段，請善用。',
            '血量低於一定程度才能買裝，記得把錢花在刀口上。',
        ]),
        ('map22', '競技場', 'Arena 雙人組合', [
            '多隊輪替對戰，回合制節奏。',
            '強化符文（Augment）決定流派走向，先看抽到的再決定買裝。',
            '與隊友的組合搭配比單卡強度重要。',
        ]),
        ('map30', '其他地圖', '特殊模式素材', [
            '官方輪替模式（如無限死鬥、終極法書等）會使用不同地圖素材。',
            '模式規則以遊戲內公告為準。',
        ]),
    ]
    maps_out = []
    for mid, name, sub, notes in maps_meta:
        img = save_image('https://ddragon.leagueoflegends.com/cdn/%s/img/map/%s.png' % (VER, mid),
                         os.path.join('map', '%s.png' % mid))
        if img:
            maps_out.append({'id': mid, 'name': name, 'sub': sub, 'img': img, 'notes': notes})
    write_json('maps.json', {'version': VER, 'maps': maps_out})
    print('  地圖：%d 張' % len(maps_out))

    # ---------------------------------------------------- 4) 符文（含簡介）
    def rune_icon(path):
        return save_image('https://ddragon.leagueoflegends.com/cdn/img/%s' % path,
                          os.path.join('rune', re.sub(r'[^A-Za-z0-9_.-]', '_', path)))

    runes_out = []
    for t in trees:
        slots = []
        for si, slot in enumerate(t['slots']):
            rows = []
            for r in slot['runes']:
                rows.append({'name': r['name'], 'icon': rune_icon(r['icon']),
                             'short': clean(r.get('shortDesc') or '', 150),
                             'long': clean(r.get('longDesc') or '', 320)})
            slots.append({'key': '基石' if si == 0 else '第 %d 層' % si, 'runes': rows})
        runes_out.append({'name': t['name'], 'key': t['key'], 'icon': rune_icon(t['icon']), 'slots': slots})
    write_json('runes.json', {'version': VER, 'trees': runes_out})
    print('  符文：%d 條樹 / %d 個符文' % (len(runes_out), sum(len(s['runes']) for t in runes_out for s in t['slots'])))

    # ---------------------------------------------------- 5) 核心裝備
    gear_out = []
    for iid, it in items.items():
        gold = it.get('gold') or {}
        if not gold.get('purchasable') or not gold.get('total'):
            continue
        if it.get('maps', {}).get('11') is False and it.get('maps', {}).get('12') is False:
            continue
        icon = save_image('https://ddragon.leagueoflegends.com/cdn/%s/img/item/%s.png' % (VER, iid),
                          os.path.join('gear', '%s.png' % iid))
        if not icon:
            continue
        gear_out.append({
            'id': iid, 'name': it['name'], 'icon': icon, 'gold': gold.get('total', 0),
            'tags': [TAG_ZH.get(x, x) for x in (it.get('tags') or [])],
            'desc': clean(it.get('plaintext') or it.get('description') or '', 170),
            'from': [items[str(x)]['name'] for x in (it.get('from') or []) if str(x) in items],
            'into': [items[str(x)]['name'] for x in (it.get('into') or []) if str(x) in items][:4],
        })
    gear_out.sort(key=lambda x: (x['gold'], x['name']))
    write_json('gear.json', {'version': VER, 'items': gear_out})
    print('  核心裝備：%d 件' % len(gear_out))

    print('  本次新下載：%d 張 / %.1f MB' % (IMG['n'], IMG['b'] / 1024 / 1024))

    write_css()
    write_js()
    write_nav()
    write_pages(base)
    return 0


TAG_ZH = {'Damage': '物理傷害', 'SpellDamage': '魔法傷害', 'Health': '生命', 'Armor': '物理防禦',
          'SpellBlock': '魔法防禦', 'Mana': '魔力', 'CriticalStrike': '暴擊', 'AttackSpeed': '攻速',
          'LifeSteal': '吸血', 'SpellVamp': '技能吸血', 'CooldownReduction': '技能急速',
          'MagicPenetration': '魔法穿透', 'ArmorPenetration': '物理穿透', 'Boots': '鞋子',
          'NonbootsMovement': '移動速度', 'Tenacity': '韌性', 'Slow': '減速', 'Active': '主動',
          'Aura': '光環', 'OnHit': '命中效果', 'HealthRegen': '生命回復', 'ManaRegen': '魔力回復',
          'AbilityHaste': '技能急速', 'MagicResist': '魔法防禦', 'Stealth': '潛行', 'Lane': '對線'}


def write_json(name, data):
    path = os.path.join(ASSETS, name)
    with open(path, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(data, fh, ensure_ascii=False, separators=(',', ':'))
    print('    已寫入 assets/lol/%s (%d KB)' % (name, os.path.getsize(path) // 1024))


PAGES = [
    ('skins.html', '角色造型', 'SKINS GALLERY', 'skins'),
    ('gallery.html', '圖片', 'ART GALLERY', 'gallery'),
    ('abilities.html', '技能圖片及簡介', 'ABILITIES', 'abilities'),
    ('maps.html', '地圖', 'MAPS', 'maps'),
    ('runes.html', '符文', 'RUNES', 'runes'),
    ('gear.html', '核心裝備', 'ITEMS', 'gear'),
    ('tactics.html', '戰術解析', 'TACTICS', 'tactics'),
]


def write_pages(base):
    for fname, title, kicker, mode in PAGES:
        doc = '''<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <meta name="color-scheme" content="dark light">
    <meta name="theme-color" content="#05080d">
    <title>LOL 攻略站 V6.0 - __TITLE__</title>
    <link rel="stylesheet" href="style.css">
    <link rel="stylesheet" href="extra.css">
</head>
<body class="bg-champions">
    <header class="topbar">
        <div class="brand">SUMMONER'S <span>GUIDE</span><b>V6.0</b></div>
        <nav>
            <a href="index.html">首頁</a>
            <a href="champions.html">英雄攻略</a>
            <a href="items.html">裝備攻略</a>
            <a href="guides.html">戰術商城</a>
        </nav>
        <button class="icon-btn" id="themeBtn">☀️</button>
    </header>

    <main class="ex-wrap" data-page="__MODE__">
        <section class="ex-hero">
            <small>__KICKER__ &middot; PATCH __VER__</small>
            <h1>__TITLE__ <em>分類資料庫</em></h1>
            <p data-role="intro"></p>
            <div class="ex-hero__pills" data-role="pills"></div>
        </section>

        <div class="ex-toolbar">
            <div class="role-filters" id="exRoles" hidden></div>
            <input type="search" id="exSearch" placeholder="搜尋…" aria-label="搜尋">
            <select id="exSelect" hidden></select>
            <span class="ex-count" id="exCount">載入中…</span>
        </div>

        <div class="ex-body" id="exBody"></div>
        <p class="ex-empty" id="exEmpty" hidden>沒有符合條件的資料。</p>

        <div class="notice">
            📌 <b>資料說明：</b> 內容與圖片取自 Riot 官方 Data Dragon <b>__VER__</b>（zh_TW），
            圖片已下載到 <b>assets/lol/</b>，開網站不需要連外。分類頁面由 <b>tools/build_extra.py</b> 產生，可重複更新。
        </div>
    </main>

    <div class="ex-modal" id="exModal" aria-hidden="true" role="dialog" aria-modal="true">
        <div class="ex-modal__box">
            <button class="ex-modal__close" id="exClose" aria-label="關閉">&times;</button>
            <div id="exModalBody"></div>
        </div>
    </div>

    <footer>
        <div>&copy; 2026 LOL 攻略站 &middot; 資料基於 Patch __VER__ &middot; 僅供參考</div>
    </footer>

    <script src="ui.js"></script>
    <script src="nav.js" defer></script>
    <script src="state.js" defer></script>
    <script src="extra.js" defer></script>
</body>
</html>
'''.replace('__TITLE__', title).replace('__KICKER__', kicker).replace('__MODE__', mode).replace('__VER__', VER)
        with open(os.path.join(SITE, fname), 'w', encoding='utf-8', newline='\n') as fh:
            fh.write(doc)
    print('  已寫入 7 個分類分頁:', ', '.join(p[0] for p in PAGES))


def write_css():
    css = '''/* ==========================================================================
   LOL 攻略站 — 七個分類分頁（由 tools/build_extra.py 產生）
   ========================================================================== */

.ex-wrap { width: min(1200px, 90%); margin: 30px auto 0; }

.ex-hero {
  position: relative; overflow: hidden; padding: 32px;
  border: 1px solid #22323d; border-radius: 18px;
  background:
    radial-gradient(120% 140% at 10% 0%, rgba(0, 217, 255, .14), transparent 60%),
    radial-gradient(100% 120% at 90% 100%, rgba(200, 170, 110, .16), transparent 60%),
    #0b1117;
}
.ex-hero small { color: #00d9ff; letter-spacing: 2.2px; font-weight: 800; font-size: 11px; }
.ex-hero h1 { margin: 10px 0 12px; font-size: clamp(28px, 4.2vw, 44px); line-height: 1.08; color: #f0eadb; }
.ex-hero h1 em { font-style: normal; color: #c8aa6e; }
.ex-hero p { max-width: 74ch; margin: 0; color: #aab4bc; }
.ex-hero__pills { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 16px; }
.ex-hero__pills span {
  padding: 6px 12px; font-size: 12px; font-weight: 700; color: #9ddff0;
  background: rgba(9, 20, 28, .66); border: 1px solid rgba(98, 170, 190, .35); border-radius: 999px;
}

.ex-toolbar { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; margin: 20px 0 8px; }
.ex-toolbar input[type="search"], .ex-toolbar select {
  flex: 0 1 260px; min-width: 180px; padding: 11px 14px; color: #e8e4d9;
  background: #080e14; border: 1px solid #2b3a45; border-radius: 10px;
}
.ex-toolbar input[type="search"] { flex: 1 1 260px; }
.ex-count { margin-left: auto; color: #8e9aa4; font-size: 13px; }
.ex-empty { text-align: center; padding: 30px; color: #76838d; }

/* ---- 角色造型 ---- */
.skin-champ { margin-bottom: 26px; }
.skin-champ__head { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; }
.skin-champ__head b { font-size: 18px; color: #f0eadb; }
.skin-champ__head span { font-size: 12px; color: #8e9aa4; }
.skin-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(144px, 1fr)); gap: 12px; }
.skin-card { padding: 0; border: 1px solid #253540; border-radius: 12px; overflow: hidden; background: #0d151d; cursor: pointer; transition: .2s; }
.skin-card:hover { transform: translateY(-3px); border-color: #00d9ff; }
.skin-card img { display: block; width: 100%; aspect-ratio: 1; object-fit: cover; }
.skin-card span { display: block; padding: 8px 10px; font-size: 12px; color: #c0c8cf; }

/* ---- 圖片牆 ---- */
.art-wall { column-count: 5; column-gap: 12px; }
.art-card { break-inside: avoid; margin: 0 0 12px; border: 1px solid #253540; border-radius: 12px; overflow: hidden; background: #0d151d; cursor: pointer; }
.art-card img { display: block; width: 100%; }
.art-card span { display: block; padding: 8px 10px; font-size: 12px; color: #c0c8cf; }
.wall-row { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; margin-bottom: 26px; }
.wall-card { border: 1px solid #253540; border-radius: 12px; overflow: hidden; background: #0d151d; }
.wall-card img { display: block; width: 100%; aspect-ratio: 16/9; object-fit: cover; }
.wall-card span { display: flex; justify-content: space-between; gap: 10px; padding: 10px 12px; font-size: 13px; color: #c0c8cf; }

/* ---- 技能 ---- */
.ability-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 14px; }
.ability-card { display: flex; gap: 12px; padding: 14px; background: linear-gradient(180deg, #101922, #0b1117); border: 1px solid #253540; border-radius: 14px; }
.ability-card img { width: 48px; height: 48px; flex: 0 0 auto; border-radius: 10px; border: 1px solid #2b3a45; background: #0a1016; }
.ability-card b { display: block; font-size: 14px; color: #f0eadb; margin-bottom: 3px; }
.ability-card small { display: block; margin-bottom: 5px; font-size: 11.5px; color: #00d9ff; }
.ability-card p { margin: 0; font-size: 12.5px; line-height: 1.6; color: #9da9b2; }

/* ---- 地圖 ---- */
.map-card { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 18px; padding: 18px; margin-bottom: 18px;
  background: linear-gradient(180deg, #101922, #0b1117); border: 1px solid #253540; border-radius: 16px; }
.map-card img { width: 100%; border-radius: 12px; border: 1px solid #2b3a45; background: #0a1016; }
.map-card h2 { margin: 0 0 4px; font-size: 22px; color: #f0eadb; }
.map-card small { display: block; margin-bottom: 10px; color: #00d9ff; font-weight: 700; letter-spacing: 1px; font-size: 11.5px; }
.map-card ul { margin: 0; padding-left: 18px; color: #c0c8cf; font-size: 13px; line-height: 1.75; }

/* ---- 符文 ---- */
.rune-tree-block { margin-bottom: 26px; }
.rune-tree-head { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; }
.rune-tree-head img { width: 34px; height: 34px; }
.rune-tree-head b { font-size: 20px; color: #f0eadb; }
.rune-slot { margin-bottom: 12px; }
.rune-slot > h4 { margin: 0 0 8px; font-size: 11.5px; letter-spacing: 1.6px; text-transform: uppercase; color: #76838d; }
.rune-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 10px; }
.rune-card { display: flex; gap: 10px; padding: 12px; background: #0f1a22; border: 1px solid #24333e; border-radius: 12px; }
.rune-card img { width: 40px; height: 40px; flex: 0 0 auto; border-radius: 50%; background: #0a1016; padding: 2px; border: 1px solid rgba(200,170,110,.35); }
.rune-card b { display: block; font-size: 13.5px; color: #e8cf9c; margin-bottom: 3px; }
.rune-card p { margin: 0; font-size: 12px; line-height: 1.6; color: #9da9b2; }
.rune-card--key { background: linear-gradient(180deg, rgba(200,170,110,.14), rgba(200,170,110,.03)), #0f1a22; border-color: rgba(200,170,110,.45); }

/* ---- 裝備 ---- */
.gear-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 12px; }
.gear-card { display: flex; gap: 12px; padding: 13px; background: linear-gradient(180deg, #101922, #0b1117); border: 1px solid #253540; border-radius: 13px; }
.gear-card img { width: 46px; height: 46px; flex: 0 0 auto; border-radius: 10px; border: 1px solid #2b3a45; background: #0a1016; }
.gear-card b { display: block; font-size: 14px; color: #f0eadb; }
.gear-card .gold { color: #c8aa6e; font-weight: 800; font-size: 13px; }
.gear-card p { margin: 4px 0 0; font-size: 12px; line-height: 1.6; color: #9da9b2; }
.gear-card .tags { margin-top: 6px; display: flex; flex-wrap: wrap; gap: 5px; }
.gear-card .tags .tag { font-size: 10.5px; padding: 2px 7px; margin-right: 0; }

/* ---- 戰術解析 ---- */
.tac-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(360px, 1fr)); gap: 14px; }
.tac-card { padding: 16px; background: linear-gradient(180deg, #101922, #0b1117); border: 1px solid #253540; border-radius: 14px; }
.tac-card__head { display: flex; gap: 10px; align-items: center; margin-bottom: 10px; }
.tac-card__head img { width: 48px; height: 48px; border-radius: 12px; border: 1px solid #2f4453; }
.tac-card__head b { font-size: 16px; color: #f0eadb; }
.tac-card__head small { display: block; font-size: 11.5px; color: #8e9aa4; }
.tac-card .box { padding: 10px 12px; margin-top: 8px; font-size: 12.5px; line-height: 1.65; color: #c0c8cf;
  background: rgba(0, 217, 255, .06); border-left: 3px solid #00d9ff; border-radius: 0 10px 10px 0; }
.tac-card .box--gold { background: linear-gradient(90deg, rgba(200,170,110,.12), rgba(0,217,255,.04)); border-left-color: #c8aa6e; color: #e0d8c8; }
.tac-card ul { margin: 4px 0 0; padding-left: 18px; }

/* ---- 彈窗 ---- */
.ex-modal { position: fixed; inset: 0; z-index: 130; display: none; place-items: center; padding: 20px; background: rgba(0,0,0,.8); backdrop-filter: blur(6px); }
.ex-modal.show { display: grid; }
.ex-modal__box { position: relative; width: min(760px, 100%); max-height: 88vh; overflow: auto; padding: 22px;
  background: #0b131b; border: 1px solid #31505f; border-radius: 16px; box-shadow: 0 25px 80px #000; }
.ex-modal__close { position: absolute; right: 14px; top: 10px; border: 0; background: none; color: #b9c2c8; font-size: 30px; cursor: pointer; }
.ex-modal__box img { width: 100%; border-radius: 12px; }
.ex-modal__box h2 { margin: 12px 0 6px; color: #c8aa6e; font-size: 24px; }
.ex-modal__box p { color: #aab4bc; font-size: 13px; }

@media (max-width: 1000px) { .art-wall { column-count: 4; } }
@media (max-width: 820px) { .map-card { grid-template-columns: 1fr; } }
@media (max-width: 700px) {
  .ex-hero { padding: 22px; }
  .art-wall { column-count: 3; }
  .wall-row { grid-template-columns: 1fr; }
  .ability-grid, .tac-grid, .gear-grid, .rune-grid { grid-template-columns: 1fr; }
  .ex-count { margin-left: 0; }
}
@media (max-width: 480px) {
  .art-wall { column-count: 2; }
  .skin-grid { grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); }
  .ex-modal { padding: 10px; }
  .ex-modal__box { padding: 16px; }
}
@media (hover: none) { .skin-card:hover { transform: none; } }
'''
    with open(os.path.join(SITE, 'extra.css'), 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(css)
    print('  已寫入 extra.css')


def write_js():
    js = '''/* ==========================================================================
   LOL 攻略站 — 分類分頁前端（由 tools/build_extra.py 產生）
   依 <main data-page="..."> 決定載入哪個 JSON 與版面
   ========================================================================== */
(function () {
  'use strict';
  var main = document.querySelector('.ex-wrap');
  if (!main) return;
  var MODE = main.dataset.page;

  var CFG = {
    skins: { file: 'skins.json', pick: function (d) { return d.champions; },
      intro: '收錄每位英雄的官方造型縮圖（已排除炫彩），點一下可以到官方大圖。造型名稱、數量都跟著 Data Dragon 更新。',
      pills: function (d) { return [d.champions.length + ' 位英雄', sum(d.champions, 'skins') + ' 張造型縮圖']; } },
    gallery: { file: 'gallery.json', pick: function (d) { return d.champions; },
      intro: '官方英雄讀取圖牆（loading art），加上四張分頁桌布。點圖可看較大版本或到官方大圖。',
      pills: function (d) { return [d.champions.length + ' 張讀取圖', '4 張桌布']; } },
    abilities: { file: 'champions.json', pick: function (d) { return d.champions; },
      intro: '全英雄的被動與 Q/W/E/R 圖示與官方技能說明，可用英雄、位置或技能名稱搜尋。',
      pills: function (d) { return [d.champions.length + ' 位英雄', sum(d.champions, 'ability') + ' 個技能']; } },
    maps: { file: 'maps.json', noSearch: true, pick: function (d) { return d.maps; },
      intro: '官方地圖素材與各地圖的戰術重點（目標時間、地形與視野）。',
      pills: function (d) { return [d.maps.length + ' 張地圖', 'Patch ' + d.version]; } },
    runes: { file: 'runes.json', pick: function (d) { return d.trees; },
      intro: '五條符文樹的完整符文清單：圖示、名稱與官方符文說明（shortDesc／longDesc）。',
      pills: function (d) { return [d.trees.length + ' 條符文樹', sumTrees(d.trees) + ' 個符文']; } },
    gear: { file: 'gear.json', pick: function (d) { return d.items; },
      intro: '可購買道具的圖示、價格、官方說明與合成路徑，可依類型或關鍵字篩選。',
      pills: function (d) { return [d.items.length + ' 件道具', 'Patch ' + d.version]; } },
    tactics: { file: 'champions.json', pick: function (d) { return d.champions; },
      intro: '每位英雄的戰術解析：玩法定位、各位置重點、Riot 官方提示與站內整理的克制資料。',
      pills: function (d) { return [d.champions.length + ' 位英雄', '含官方提示與克制']; } }
  };

  function sum(arr, key) { var n = 0; arr.forEach(function (x) { n += (x[key] || []).length; }); return n; }
  function sumTrees(trees) { var n = 0; trees.forEach(function (t) { t.slots.forEach(function (s) { n += s.runes.length; }); }); return n; }
  function $(id) { return document.getElementById(id); }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }

  var DATA = null, ITEMS = [], state = { role: '全部', q: '', sel: 'all' };

  function role(name) { return name ? '<span class="tag tag--role">' + esc(name) + '</span>' : ''; }

  /* ---------------------------------------------------------------- 各頁卡片 */
  function cardSkins(c) {
    var imgs = c.skins.map(function (s) {
      return '<button class="skin-card" type="button" data-big="' + esc(s.big) + '" data-name="' + esc(c.champ + ' ' + s.name) + '">' +
        '<img src="' + esc(s.img) + '" alt="' + esc(s.name) + '" loading="lazy">' +
        '<span>' + esc(s.name) + '</span></button>';
    }).join('');
    return '<section class="skin-champ" data-role="' + esc(c.role) + '" data-name="' + esc(c.champ + ' ' + c.skins.map(function (s) { return s.name; }).join(' ')) + '">' +
      '<div class="skin-champ__head"><b>' + esc(c.champ) + '</b>' + role(c.role) +
      '<span>' + c.skins.length + ' 個造型</span></div><div class="skin-grid">' + imgs + '</div></section>';
  }

  function cardArt(c) {
    return '<figure class="art-card" data-big="' + esc(c.big) + '" data-name="' + esc(c.champ + ' ' + c.title) + '">' +
      '<img src="' + esc(c.img) + '" alt="' + esc(c.champ) + '" loading="lazy">' +
      '<span>' + esc(c.champ) + ' <small>' + esc(c.title) + '</small></span></figure>';
  }

  function cardAbility(c, a) {
    return '<article class="ability-card" data-name="' + esc(c.name + ' ' + a.n + ' ' + a.k) + '">' +
      '<img src="' + esc(a.i) + '" alt="' + esc(a.n) + '" loading="lazy">' +
      '<div><small>' + esc(c.name) + ' · ' + esc(a.k) + '</small>' +
      '<b>' + esc(a.n) + '</b><p>' + esc(a.d) + '</p></div></article>';
  }

  function cardMap(m) {
    return '<article class="map-card"><div><img src="' + esc(m.img) + '" alt="' + esc(m.name) + '" loading="lazy"></div>' +
      '<div><h2>' + esc(m.name) + '</h2><small>' + esc(m.sub) + '</small><ul>' +
      m.notes.map(function (n) { return '<li>' + esc(n) + '</li>'; }).join('') + '</ul></div></article>';
  }

  function cardRuneTree(t) {
    var slots = t.slots.map(function (s) {
      var cards = s.runes.map(function (r) {
        return '<div class="rune-card' + (s.key === '基石' ? ' rune-card--key' : '') + '" data-name="' + esc(r.name + ' ' + r.short) + '" title="' + esc(r.long) + '">' +
          '<img src="' + esc(r.icon) + '" alt="' + esc(r.name) + '" loading="lazy">' +
          '<div><b>' + esc(r.name) + '</b><p>' + esc(r.short) + '</p></div></div>';
      }).join('');
      return '<div class="rune-slot"><h4>' + esc(s.key) + '</h4><div class="rune-grid">' + cards + '</div></div>';
    }).join('');
    return '<section class="rune-tree-block" data-name="' + esc(t.name) + '"><div class="rune-tree-head">' +
      '<img src="' + esc(t.icon) + '" alt="' + esc(t.name) + '"><b>' + esc(t.name) + '</b></div>' + slots + '</section>';
  }

  function cardGear(it) {
    var tags = (it.tags || []).map(function (x) { return '<span class="tag">' + esc(x) + '</span>'; }).join('');
    var path = (it.from && it.from.length) ? '<p>合成：' + esc(it.from.join(' + ')) + '</p>' : '';
    return '<article class="gear-card" data-tags="' + esc((it.tags || []).join(' ')) + '" data-name="' + esc(it.name + ' ' + it.desc) + '">' +
      '<img src="' + esc(it.icon) + '" alt="' + esc(it.name) + '" loading="lazy">' +
      '<div><b>' + esc(it.name) + '</b><span class="gold">' + it.gold + ' 金幣</span>' +
      '<p>' + esc(it.desc) + '</p>' + path + '<div class="tags">' + tags + '</div></div></article>';
  }

  function cardTactic(c) {
    var t = c.tactic || {};
    var tips = (t.tips || []).map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('');
    var enemy = (t.enemy || []).map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('');
    var weak = (t.weak || []).join('、'), strong = (t.strong || []).join('、');
    return '<article class="tac-card" data-role="' + esc(c.role) + '" data-name="' + esc(c.name + ' ' + c.title + ' ' + c.tags.join(' ')) + '">' +
      '<div class="tac-card__head"><img src="' + esc(c.avatar) + '" alt="' + esc(c.name) + '" loading="lazy">' +
      '<div><b>' + esc(c.name) + '</b><small>' + esc(c.title) + ' · ' + esc(c.role) + '</small></div></div>' +
      '<div class="box box--gold">' + esc(t.style || '') + '</div>' +
      (t.role ? '<div class="box">' + esc(t.role) + '</div>' : '') +
      (tips ? '<div class="box"><b>Riot 官方提示：</b><ul>' + tips + '</ul></div>' : '') +
      (enemy ? '<div class="box"><b>對手會怎麼打你：</b><ul>' + enemy + '</ul></div>' : '') +
      ((weak || strong) ? '<div class="box"><b>站內整理對局：</b>' + (weak ? '較怕：' + esc(weak) + '　' : '') + (strong ? '較好打：' + esc(strong) : '') + '</div>' : '') +
      '</article>';
  }

  /* ------------------------------------------------------------------ 渲染 */
  function renderAll() {
    var body = $('exBody');
    if (MODE === 'skins') body.innerHTML = DATA.map(cardSkins).join('');
    else if (MODE === 'gallery') {
      var walls = [
        { img: 'assets/bg-home.jpg', name: '首頁桌布（蒂瑪西亞）' },
        { img: 'assets/bg-champions.jpg', name: '英雄攻略桌布' },
        { img: 'assets/bg-items.jpg', name: '裝備攻略桌布' },
        { img: 'assets/bg-guides.jpg', name: '戰術商城桌布' }
      ].map(function (w) {
        return '<div class="wall-card"><img src="' + esc(w.img) + '" alt="' + esc(w.name) + '" loading="lazy">' +
          '<span>' + esc(w.name) + '<a class="ex-dl" href="' + esc(w.img) + '" download>下載</a></span></div>';
      }).join('');
      body.innerHTML = '<h3 style="margin:0 0 12px;color:#00d9ff;font-size:12px;letter-spacing:1.6px;">頁面桌布（1920×1080）</h3>' +
        '<div class="wall-row">' + walls + '</div>' +
        '<h3 style="margin:0 0 12px;color:#00d9ff;font-size:12px;letter-spacing:1.6px;">英雄讀取圖</h3>' +
        '<div class="art-wall">' + DATA.map(cardArt).join('') + '</div>';
      ITEMS = [].slice.call(document.querySelectorAll('.art-card'));
      apply(); return;
    }
    else if (MODE === 'abilities') body.innerHTML = DATA.map(function (c) { return c.ability.map(function (a) { return cardAbility(c, a); }).join(''); }).join('');
    else if (MODE === 'maps') body.innerHTML = DATA.map(cardMap).join('');
    else if (MODE === 'runes') body.innerHTML = DATA.map(cardRuneTree).join('');
    else if (MODE === 'gear') body.innerHTML = DATA.map(cardGear).join('');
    else if (MODE === 'tactics') body.innerHTML = DATA.map(cardTactic).join('');

    ITEMS = [].slice.call(body.querySelectorAll('[data-name]'));
    apply();
  }

  function apply() {
    var q = (state.q || '').toLowerCase().trim();
    var shown = 0;
    ITEMS.forEach(function (el) {
      var okRole = (state.role === '全部' || el.dataset.role === state.role || !el.dataset.role);
      var okSel = (state.sel === 'all' || (el.dataset.tags || '').indexOf(state.sel) >= 0 || !el.dataset.tags);
      var okQ = !q || (el.dataset.name || '').toLowerCase().indexOf(q) >= 0;
      var on = okRole && okSel && okQ;
      el.hidden = !on;
      if (on) shown++;
    });
    if (MODE === 'skins') {   // 造型頁以「英雄區塊」為單位過濾
      var blocks = document.querySelectorAll('.skin-champ');
      shown = 0;
      Array.prototype.forEach.call(blocks, function (b) {
        var okRole = (state.role === '全部' || b.dataset.role === state.role);
        var okQ = !q || (b.dataset.name || '').toLowerCase().indexOf(q) >= 0;
        var on = okRole && okQ;
        b.hidden = !on;
        if (on) shown++;
      });
      $('exCount').textContent = '顯示 ' + shown + ' 位英雄的造型';
    } else if (MODE === 'runes') {
      var trees = document.querySelectorAll('.rune-tree-block');
      var n = 0;
      Array.prototype.forEach.call(trees, function (t) {
        var ok = !q || (t.dataset.name || '').toLowerCase().indexOf(q) >= 0 || t.textContent.toLowerCase().indexOf(q) >= 0;
        t.hidden = !ok;
        if (ok) n++;
      });
      $('exCount').textContent = '顯示 ' + n + ' 條符文樹（共 ' + trees.length + ' 條）';
    } else {
      if (MODE === 'maps') $('exCount').textContent = '共 ' + DATA.length + ' 張地圖';
      else $('exCount').textContent = '顯示 ' + shown + ' 筆資料';
    }
    $('exEmpty').hidden = (MODE === 'skins' || MODE === 'runes') ? true : shown !== 0;
  }

  /* ------------------------------------------------------------------ 事件 */
  function bind() {
    var box = $('exSearch');
    if (box) {
      if (CFG[MODE].noSearch) box.hidden = true;
      box.addEventListener('input', function () { state.q = box.value; apply(); });
    }
    var sel = $('exSelect');
    if (sel) sel.addEventListener('change', function () { state.sel = sel.value; apply(); });
    var modal = $('exModal');
    document.addEventListener('click', function (e) {
      var card = e.target.closest ? e.target.closest('[data-big]') : null;
      if (card) {
        $('exModalBody').innerHTML = '<img src="' + esc(card.dataset.big) + '" alt="">' +
          '<h2>' + esc((card.dataset.name || '').split(' ')[0]) + '</h2>' +
          '<p>' + esc(card.dataset.name || '') + '</p>' +
          '<p><a class="gold-btn" style="display:inline-block;margin-top:8px;" href="' + esc(card.dataset.big) + '" target="_blank" rel="noopener">開官方大圖</a></p>';
        modal.classList.add('show');
        modal.setAttribute('aria-hidden', 'false');
        document.querySelector('.ex-modal__box').scrollTop = 0;
      }
    });
    if ($('exClose')) $('exClose').addEventListener('click', closeModal);
    if (modal) modal.addEventListener('click', function (e) { if (e.target === modal) closeModal(); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && modal.classList.contains('show')) closeModal(); });
  }
  function closeModal() {
    $('exModal').classList.remove('show');
    $('exModal').setAttribute('aria-hidden', 'true');
  }

  /* ------------------------------------------------------------------ 起始 */
  document.addEventListener('DOMContentLoaded', function () {
    var cfg = CFG[MODE];
    if (!cfg) return;
    fetch('assets/lol/' + cfg.file)
      .then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
      .then(function (d) {
        DATA = cfg.pick(d);
        document.querySelector('.ex-hero p[data-role="intro"]').textContent = cfg.intro;
        document.querySelector('.ex-hero__pills').innerHTML =
          cfg.pills(d).map(function (x) { return '<span>' + esc(x) + '</span>'; }).join('');

        // 位置篩選（造型、技能、戰術解析有位置資料）
        var needRole = DATA.length && DATA[0] && DATA[0].role;
        var host = $('exRoles');
        if (needRole) {
          var counts = { '全部': DATA.length };
          DATA.forEach(function (x) { if (x.role) counts[x.role] = (counts[x.role] || 0) + 1; });
          host.hidden = false;
          host.innerHTML = ['全部', '上路', '打野', '中路', '下路', '輔助'].map(function (r) {
            if (r !== '全部' && !counts[r]) return '';
            return '<button type="button" class="tab' + (r === '全部' ? ' active' : '') + '" data-role="' + esc(r) + '">' +
              esc(r) + ' <b>' + (counts[r] || 0) + '</b></button>';
          }).join('');
          Array.prototype.forEach.call(host.querySelectorAll('.tab'), function (t) {
            t.addEventListener('click', function () {
              Array.prototype.forEach.call(host.querySelectorAll('.tab'), function (x) { x.classList.remove('active'); });
              t.classList.add('active');
              state.role = t.dataset.role;
              apply();
            });
          });
        }
        // 裝備類型篩選
        var sel = $('exSelect');
        if (MODE === 'gear') {
          var tags = {};
          DATA.forEach(function (it) { (it.tags || []).forEach(function (t) { tags[t] = (tags[t] || 0) + 1; }); });
          var list = Object.keys(tags).sort(function (a, b) { return tags[b] - tags[a]; });
          sel.hidden = false;
          sel.innerHTML = '<option value="all">全部類型</option>' +
            list.map(function (t) { return '<option value="' + esc(t) + '">' + esc(t) + '（' + tags[t] + '）</option>'; }).join('');
        }
        renderAll();
        bind();
      })
      .catch(function (err) {
        $('exCount').textContent = '資料載入失敗：' + err.message;
      });
  });
})();
'''
    with open(os.path.join(SITE, 'extra.js'), 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(js)
    print('  已寫入 extra.js')


def write_nav():
    """分類導覽列（nav.js）已經改成手動維護：樣式內嵌在 nav.js 裡，
    避免瀏覽器快取舊的 style.css 時導覽列變成沒有間距的純文字。
    這裡只確認檔案存在，不覆蓋它。"""
    nav = os.path.join(SITE, 'nav.js')
    if not os.path.exists(nav):
        print('   ! 找不到 nav.js（分類導覽列），請確認檔案存在', file=sys.stderr)
    else:
        print('  nav.js 存在（樣式內嵌，不覆蓋）')

if __name__ == '__main__':
    sys.exit(main())
