#!/usr/bin/env python3
"""
產生資料內容的四語對照表（中文原文 → 英文／日文／韓文）。

輸出：assets/lol/i18n-en.json、i18n-ja.json、i18n-ko.json
格式：{ "lang": "en", "map": { "蓋倫": "Garen", "致命打擊": "Decisive Strike", ... } }

來源：Riot 官方 Data Dragon 的 en_US／ja_JP／ko_KR 資料（與站上 zh_TW 資料以 key 對應）
      另外加上站上自己撰寫的少量文字（玩法定位、地圖重點）的人工翻譯。
"""
import html
import io
import json
import os
import re
import sys
import urllib.request

_HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.environ.get('LOL_SITE') or (_HERE if os.path.exists(os.path.join(_HERE, 'index.html')) else os.path.dirname(_HERE))
ASSETS = os.path.join(SITE, 'assets', 'lol')
CACHE = os.path.join(os.environ.get('TEMP', '/tmp'), 'lolcache')
TARGETS = [('en', 'en_US'), ('ja', 'ja_JP'), ('ko', 'ko_KR')]


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


def fetch(url, cache_name):
    path = os.path.join(CACHE, cache_name)
    if os.path.exists(path) and os.path.getsize(path) > 500:
        with io.open(path, encoding='utf-8') as fh:
            return fh.read()
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (lol-guide-build)'})
    with urllib.request.urlopen(req, timeout=180) as r:
        raw = r.read().decode('utf-8')
    with io.open(path, 'w', encoding='utf-8') as fh:
        fh.write(raw)
    return raw


def load_site_json(name):
    path = os.path.join(ASSETS, name)
    if not os.path.exists(path):
        return None
    with io.open(path, encoding='utf-8') as fh:
        return json.load(fh)


# 站上自己寫的文字（Data Dragon 沒有）：玩法定位、各位置重點、地圖名稱與重點
MANUAL = {
    'en': {
        '刺客爆發／側翼切入：靠技能連段在短時間內收掉關鍵目標，進場與退場路線要事先想好。':
            'Assassin burst / flanking: delete key targets with a quick combo, and plan your entry and exit route.',
        '遠程持續輸出／安全站位：傷害來自持續普攻，站位比操作更重要，注意對面的開戰技能。':
            'Ranged sustained damage / safe positioning: damage comes from auto attacks, so positioning matters more than mechanics.',
        '前排承傷／開戰或保護：用控制與坦度替隊友創造空間，開戰前先確認隊友跟得上。':
            'Front line / engage or peel: create space with crowd control and durability, and check your team can follow.',
        '控制／保護／團隊功能：視野、保護與開團是你的主要價值，人頭不是。':
            'Control / peel / utility: vision, protection and engages are your value — not kills.',
        '技能消耗／控場／爆發：用技能距離與冷卻換取優勢，團戰負責範圍傷害與控場。':
            'Poke / zone / burst: trade with spell range and cooldowns, and bring area damage in teamfights.',
        '戰士近戰／持續作戰：換血與兵線掌控是核心，注意進場時機與隊友位置。':
            'Melee fighter / extended trades: trading and wave control are key — watch your entry timing.',
        '上路重點：兵線與單帶節奏，注意河道視野與對手的打野動向。':
            'Top: wave and split-push tempo, plus river vision and jungle tracking.',
        '打野重點：以 Gank 與河道／預示者建立節奏，路線要配合線上兵線狀態。':
            'Jungle: build tempo with ganks and river objectives; route around lane states.',
        '中路重點：控線與支援邊線，六級後配合打野抓時間差。':
            'Mid: control the wave and roam; after level 6 look for jungle timings.',
        '下路重點：發育與站位，前期以穩定吃兵與換血為主，避免被包夾。':
            'Bottom: farm and position; focus on safe CS and trades, avoid being collapsed on.',
        '輔助重點：視野佈置與保護／開團，注意幫打野做河道視野。':
            'Support: vision plus peel or engage, and help your jungler with river vision.',
        '5 對 5 經典模式（map11）': 'Classic 5v5 (map11)',
        '3 條路線＋野區，地圖目標決定勝負節奏。': 'Three lanes plus jungle; objectives set the tempo.',
        '小龍 5:00 出生，之後每 5 分鐘重生；擊殺 4 條可獲得龍魂。':
            'Dragons spawn at 5:00 and every 5 minutes after; four drakes grant a soul.',
        '預示者 8:00 出生、14:00 前要打完，可召喚撞塔。':
            'Rift Herald spawns at 8:00 and must be used before 14:00 to damage towers.',
        '巴龍 20:00 出生，重生間隔 6 分鐘；拿到巴龍是推進與結束比賽的關鍵。':
            'Baron spawns at 20:00 and respawns every 6 minutes — key to closing games.',
        '拿到元素龍之後地形會改變（下方五張就是各地形的小地圖）。':
            'Drakes change the terrain (the five maps below show each variant).',
        '視野重點：河道草叢、三角草、龍／巴龍區入口。':
            'Vision: river brush, tri-brush and the entrances to dragon / Baron pits.',
        '單線擠壓、無法回城，只能靠死亡或隊友治療補給。':
            'One lane, no recalls — you only heal by dying or with ally heals.',
        '開場就是團戰，選角以消耗、開戰與清線能力為主。':
            'Teamfights from the start; pick for poke, engage and wave clear.',
        '雪球（標記）是唯一的進場位移手段，請善用。':
            'Snowball (Mark) is your only gap closer — use it well.',
        '血量低於一定程度才能買裝，記得把錢花在刀口上。':
            'You can only shop below a health threshold, so spend wisely.',
        '活動期間地圖會有不同主題（下方為歷來的主題版本）。':
            'The map gets event themes (below are past versions).',
        '多隊輪替對戰、回合制節奏，每回合會在不同場地進行。':
            'Multi-team rounds; each round takes place on a different arena.',
        '強化符文（Augment）決定流派走向，先看抽到的再決定買裝。':
            'Augments decide your build direction — pick items after you see them.',
        '與隊友的組合搭配比單卡強度重要。':
            'Team composition matters more than individual power.',
        '場地會影響走位與開戰方式，圓環邊緣與草叢是關鍵。':
            'Arena layout changes spacing and engages; ring edges and brush are key.',
        '下方是全部八個場地（點圖可放大）。': 'All eight arenas are below (click to enlarge).',
        '嚎哭深淵': 'Howling Abyss', '競技場': 'Arena', '召喚峽谷': "Summoner's Rift",
        '5 對 5 經典模式': 'Classic 5v5', 'ARAM 單線大亂鬥': 'ARAM', 'Arena 雙人組合': 'Arena duos',
        '預設造型': 'Default', '全部造型系列': 'All skin lines', '全部類型': 'All types',
        '全部技能': 'All abilities', '全部地圖': 'All maps', '全部符文樹': 'All rune trees',
        '全部難度': 'All difficulties', '全部英雄': 'All champions', '讀取圖': 'Loading art', '桌布': 'Wallpaper',
    },
    'ja': {
        '刺客爆發／側翼切入：靠技能連段在短時間內收掉關鍵目標，進場與退場路線要事先想好。':
            'アサシンのバースト／側面攻撃。コンボで主要ターゲットを落とし、進入と離脱の動線を先に決めておく。',
        '遠程持續輸出／安全站位：傷害來自持續普攻，站位比操作更重要，注意對面的開戰技能。':
            '遠距離の継続ダメージ／安全な立ち位置。AA が主な火力なので立ち位置が最も重要。',
        '前排承傷／開戰或保護：用控制與坦度替隊友創造空間，開戰前先確認隊友跟得上。':
            '前衛／エンゲージまたはピール。CC と耐久で味方のスペースを作る。',
        '控制／保護／團隊功能：視野、保護與開團是你的主要價值，人頭不是。':
            'CC／ピール／ユーティリティ。視界・保護・エンゲージが仕事でキルではない。',
        '技能消耗／控場／爆發：用技能距離與冷卻換取優勢，團戰負責範圍傷害與控場。':
            'ポーク／ゾーニング／バースト。射程と CD で優位を作り、集団戦では範囲火力を担当。',
        '戰士近戰／持續作戰：換血與兵線掌控是核心，注意進場時機與隊友位置。':
            '近接ファイター／長期戦。トレードとウェーブ管理が要。',
        '上路重點：兵線與單帶節奏，注意河道視野與對手的打野動向。':
            'トップ：ウェーブとスプリットのテンポ、河の視界とジャングルの位置。',
        '打野重點：以 Gank 與河道／預示者建立節奏，路線要配合線上兵線狀態。':
            'ジャングル：ガンクと河オブジェクトでテンポを作る。',
        '中路重點：控線與支援邊線，六級後配合打野抓時間差。':
            'ミッド：ウェーブ管理とローム。レベル 6 以降はジャングルと合わせる。',
        '下路重點：發育與站位，前期以穩定吃兵與換血為主，避免被包夾。':
            'ボット：ファームと立ち位置。安全な CS とトレードを優先。',
        '輔助重點：視野佈置與保護／開團，注意幫打野做河道視野。':
            'サポート：視界とピール／エンゲージ。河の視界を手伝う。',
        '5 對 5 經典模式（map11）': 'クラシック 5v5（map11）',
        '3 條路線＋野區，地圖目標決定勝負節奏。': '3 レーン＋ジャングル。オブジェクトがテンポを決める。',
        '小龍 5:00 出生，之後每 5 分鐘重生；擊殺 4 條可獲得龍魂。':
            'ドラゴンは 5:00 に出現、以降 5 分ごと。4 体でソウル獲得。',
        '預示者 8:00 出生、14:00 前要打完，可召喚撞塔。':
            'ヘラルドは 8:00 出現、14:00 までに使うとタワーを攻撃できる。',
        '巴龍 20:00 出生，重生間隔 6 分鐘；拿到巴龍是推進與結束比賽的關鍵。':
            'バロンは 20:00 出現、以降 6 分ごと。試合を決める鍵。',
        '拿到元素龍之後地形會改變（下方五張就是各地形的小地圖）。':
            'ドラゴンを取ると地形が変化します（下の 5 枚が各地形）。',
        '視野重點：河道草叢、三角草、龍／巴龍區入口。':
            '視界：河のブッシュ、トライブッシュ、ドラゴン／バロンの入口。',
        '單線擠壓、無法回城，只能靠死亡或隊友治療補給。':
            '1 レーンでリコール不可。死亡か味方の回復でのみ回復。',
        '開場就是團戰，選角以消耗、開戰與清線能力為主。':
            '開始から集団戦。ポーク・エンゲージ・ウェーブクリアを優先。',
        '雪球（標記）是唯一的進場位移手段，請善用。':
            'スノーボール（マーク）が唯一の接近手段。',
        '血量低於一定程度才能買裝，記得把錢花在刀口上。':
            '一定 HP 以下でしか購入できない。使い所に注意。',
        '活動期間地圖會有不同主題（下方為歷來的主題版本）。':
            'イベント期間はマップのテーマが変わります（下は過去の版）。',
        '多隊輪替對戰、回合制節奏，每回合會在不同場地進行。':
            '多チームのラウンド制。毎ラウンド会場が変わる。',
        '強化符文（Augment）決定流派走向，先看抽到的再決定買裝。':
            'オーグメントでビルドが決まる。引いてからアイテムを選ぶ。',
        '與隊友的組合搭配比單卡強度重要。': '単体の強さより味方との組み合わせが重要。',
        '場地會影響走位與開戰方式，圓環邊緣與草叢是關鍵。':
            '会場で立ち回りが変わる。縁とブッシュが鍵。',
        '下方是全部八個場地（點圖可放大）。': '下に 8 会場すべて（クリックで拡大）。',
        '嚎哭深淵': '嘆きの淵', '競技場': 'アリーナ', '召喚峽谷': 'サモナーズリフト',
        '5 對 5 經典模式': 'クラシック 5v5', 'ARAM 單線大亂鬥': 'ARAM', 'Arena 雙人組合': 'アリーナ（デュオ）',
        '預設造型': 'デフォルト', '全部造型系列': 'すべてのスキンシリーズ', '全部類型': 'すべての種類',
        '全部技能': 'すべてのスキル', '全部地圖': 'すべてのマップ', '全部符文樹': 'すべてのツリー',
        '全部難度': 'すべての難易度', '全部英雄': 'すべてのチャンピオン', '讀取圖': 'ロード画面', '桌布': '壁紙',
    },
    'ko': {
        '刺客爆發／側翼切入：靠技能連段在短時間內收掉關鍵目標，進場與退場路線要事先想好。':
            '암살자 폭딜/측면 진입. 콤보로 핵심 대상를 처치하고 진입·이탈 경로를 미리 정하세요.',
        '遠程持續輸出／安全站位：傷害來自持續普攻，站位比操作更重要，注意對面的開戰技能。':
            '원거리 지속딜/안전한 위치. 평타가 주 딜이므로 위치가 가장 중요합니다.',
        '前排承傷／開戰或保護：用控制與坦度替隊友創造空間，開戰前先確認隊友跟得上。':
            '전방/이니시 또는 보호. CC와 탱킹으로 아군 공간을 만드세요.',
        '控制／保護／團隊功能：視野、保護與開團是你的主要價值，人頭不是。':
            'CC/보호/유틸. 시야·보호·이니시가 역할이며 킬이 아닙니다.',
        '技能消耗／控場／爆發：用技能距離與冷卻換取優勢，團戰負責範圍傷害與控場。':
            '견제/지역 장악/폭딜. 사거리와 쿨다운으로 이득을 보고 한타에서 광역딜을 담당.',
        '戰士近戰／持續作戰：換血與兵線掌控是核心，注意進場時機與隊友位置。':
            '근접 전사/지속 교전. 딜교와 웨이브 관리가 핵심.',
        '上路重點：兵線與單帶節奏，注意河道視野與對手的打野動向。':
            '탑: 웨이브와 스플릿 템포, 강 시야와 정글 위치.',
        '打野重點：以 Gank 與河道／預示者建立節奏，路線要配合線上兵線狀態。':
            '정글: 갱과 강 오브젝트로 템포를 만드세요.',
        '中路重點：控線與支援邊線，六級後配合打野抓時間差。':
            '미드: 웨이브 관리와 로밍, 6레벨 이후 정글과 합류.',
        '下路重點：發育與站位，前期以穩定吃兵與換血為主，避免被包夾。':
            '바텀: 파밍과 위치. 안전한 CS와 딜교 우선.',
        '輔助重點：視野佈置與保護／開團，注意幫打野做河道視野。':
            '서포터: 시야와 보호/이니시, 정글의 강 시야를 도와주세요.',
        '5 對 5 經典模式（map11）': '클래식 5v5 (map11)',
        '3 條路線＋野區，地圖目標決定勝負節奏。': '3개 라인+정글. 오브젝트가 템포를 결정합니다.',
        '小龍 5:00 出生，之後每 5 分鐘重生；擊殺 4 條可獲得龍魂。':
            '드래곤은 5:00 등장, 이후 5분마다. 4마리 처치 시 영혼 획득.',
        '預示者 8:00 出生、14:00 前要打完，可召喚撞塔。':
            '전령은 8:00 등장, 14:00 이전에 사용해 타워를 공격.',
        '巴龍 20:00 出生，重生間隔 6 分鐘；拿到巴龍是推進與結束比賽的關鍵。':
            '바론은 20:00 등장, 이후 6분마다. 게임을 끝내는 핵심.',
        '拿到元素龍之後地形會改變（下方五張就是各地形的小地圖）。':
            '드래곤을 먹으면 지형이 바뀝니다(아래 5장이 각 지형).',
        '視野重點：河道草叢、三角草、龍／巴龍區入口。':
            '시야: 강 부쉬, 삼각 부쉬, 드래곤/바론 입구.',
        '單線擠壓、無法回城，只能靠死亡或隊友治療補給。':
            '한 라인, 귀환 불가. 죽거나 아군 회복으로만 회복.',
        '開場就是團戰，選角以消耗、開戰與清線能力為主。':
            '시작부터 한타. 견제·이니시·푸시 위주로 픽.',
        '雪球（標記）是唯一的進場位移手段，請善用。':
            '스노우볼(표식)이 유일한 진입기입니다.',
        '血量低於一定程度才能買裝，記得把錢花在刀口上。':
            '체력이 일정 이하일 때만 상점 이용 가능. 신중하게 사용하세요.',
        '活動期間地圖會有不同主題（下方為歷來的主題版本）。':
            '이벤트 기간에는 맵 테마가 바뀝니다(아래는 과거 버전).',
        '多隊輪替對戰、回合制節奏，每回合會在不同場地進行。':
            '다중 팀 라운드제. 라운드마다 다른 경기장.',
        '強化符文（Augment）決定流派走向，先看抽到的再決定買裝。':
            '증강체가 빌드 방향을 결정합니다. 확인 후 아이템 구매.',
        '與隊友的組合搭配比單卡強度重要。': '개별 성능보다 아군 조합이 중요합니다.',
        '場地會影響走位與開戰方式，圓環邊緣與草叢是關鍵。':
            '경기장에 따라 위치 선정이 달라집니다. 가장자리와 부쉬가 핵심.',
        '下方是全部八個場地（點圖可放大）。': '아래에 8개 경기장 전부(클릭하면 확대).',
        '嚎哭深淵': '울부짖는 심연', '競技場': '아레나', '召喚峽谷': '소환사의 협곡',
        '5 對 5 經典模式': '클래식 5v5', 'ARAM 單線大亂鬥': 'ARAM', 'Arena 雙人組合': '아레나 듀오',
        '預設造型': '기본', '全部造型系列': '모든 스킨 시리즈', '全部類型': '모든 유형',
        '全部技能': '모든 스킬', '全部地圖': '모든 맵', '全部符文樹': '모든 룬 트리',
        '全部難度': '모든 난이도', '全部英雄': '모든 챔피언', '讀取圖': '로딩 아트', '桌布': '배경화면',
    },
}


def main():
    with io.open(os.path.join(CACHE, 'versions.json'), encoding='utf-8') as fh:
        VER = json.load(fh)[0]
    print('Data Dragon 版本:', VER)

    zh_champs = json.loads(fetch('https://ddragon.leagueoflegends.com/cdn/%s/data/zh_TW/championFull.json' % VER,
                                 'champFull_%s.json' % VER))['data']
    zh_items = json.loads(fetch('https://ddragon.leagueoflegends.com/cdn/%s/data/zh_TW/item.json' % VER,
                                'item_%s.json' % VER))['data']
    zh_runes = json.loads(fetch('https://ddragon.leagueoflegends.com/cdn/%s/data/zh_TW/runesReforged.json' % VER,
                                'runes_%s.json' % VER))
    site = load_site_json('champions.json') or {'champions': []}
    skins = load_site_json('skins.json') or {'champions': []}

    for code, dd in TARGETS:
        tg_champs = json.loads(fetch('https://ddragon.leagueoflegends.com/cdn/%s/data/%s/championFull.json' % (VER, dd),
                                     'champFull_%s_%s.json' % (dd, VER)))['data']
        tg_items = json.loads(fetch('https://ddragon.leagueoflegends.com/cdn/%s/data/%s/item.json' % (VER, dd),
                                    'item_%s_%s.json' % (dd, VER)))['data']
        tg_runes = json.loads(fetch('https://ddragon.leagueoflegends.com/cdn/%s/data/%s/runesReforged.json' % (VER, dd),
                                    'runes_%s_%s.json' % (dd, VER)))
        m = {}

        # 英雄名稱、稱號、技能名稱與簡介、官方提示
        for key, zc in zh_champs.items():
            tc = tg_champs.get(key)
            if not tc:
                continue
            if zc['name'] != tc['name']:
                m[zc['name']] = tc['name']
            if zc.get('title') and tc.get('title') and zc['title'] != tc['title']:
                m[zc['title']] = tc['title']
            # 被動
            zp, tp = zc.get('passive') or {}, tc.get('passive') or {}
            if zp.get('name') and tp.get('name'):
                m[zp['name']] = tp['name']
            if zp.get('description') and tp.get('description'):
                m[clean(zp['description'])] = clean(tp['description'])
            # Q/W/E/R
            for zs, ts in zip(zc.get('spells') or [], tc.get('spells') or []):
                if zs['name'] != ts['name']:
                    m[zs['name']] = ts['name']
                d1, d2 = clean(zs.get('description', '')), clean(ts.get('description', ''))
                if d1 and d2 and d1 != d2:
                    m[d1] = d2
            # 官方提示（戰術解析頁用到）
            for a, b in zip(zc.get('allytips') or [], tc.get('allytips') or []):
                a1, b1 = clean(a, 90), clean(b, 90)
                if a1 and b1:
                    m[a1] = b1
            for a, b in zip(zc.get('enemytips') or [], tc.get('enemytips') or []):
                a1, b1 = clean(a, 90), clean(b, 90)
                if a1 and b1:
                    m[a1] = b1

        # 造型名稱（以英雄 key + 號碼對應）
        for c in skins.get('champions', []):
            zc, tc = zh_champs.get(c['key']), tg_champs.get(c['key'])
            if not zc or not tc:
                continue
            zsk = {s['num']: s['name'] for s in (zc.get('skins') or [])}
            tsk = {s['num']: s['name'] for s in (tc.get('skins') or [])}
            for num, name in zsk.items():
                tname = tsk.get(num)
                if tname and name != tname:
                    m[name] = tname

        # 道具名稱與說明
        for iid, zi in zh_items.items():
            ti = tg_items.get(iid)
            if not ti:
                continue
            if zi['name'] != ti['name']:
                m[zi['name']] = ti['name']
            for field, limit in (('plaintext', 170), ('description', 170)):
                z1, t1 = clean(zi.get(field, ''), limit), clean(ti.get(field, ''), limit)
                if z1 and t1 and z1 != t1:
                    m[z1] = t1

        # 符文樹與符文
        for zt, tt in zip(zh_runes, tg_runes):
            if zt['name'] != tt['name']:
                m[zt['name']] = tt['name']
            for zs, ts in zip(zt['slots'], tt['slots']):
                for zr, tr in zip(zs['runes'], ts['runes']):
                    if zr['name'] != tr['name']:
                        m[zr['name']] = tr['name']
                    z1 = clean(zr.get('shortDesc', ''), 150)
                    t1 = clean(tr.get('shortDesc', ''), 150)
                    if z1 and t1 and z1 != t1:
                        m[z1] = t1

        # 站上自己寫的文字
        for k, v in MANUAL.get(code, {}).items():
            m[k] = v

        out = os.path.join(ASSETS, 'i18n-%s.json' % code)
        with io.open(out, 'w', encoding='utf-8', newline='') as fh:
            json.dump({'lang': code, 'version': VER, 'map': m}, fh, ensure_ascii=False, separators=(',', ':'))
        print('  已寫入 assets/lol/i18n-%s.json（%d 條對照，%d KB）' % (code, len(m), os.path.getsize(out) // 1024))
    return 0


if __name__ == '__main__':
    sys.exit(main())
