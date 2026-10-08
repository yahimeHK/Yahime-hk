#!/usr/bin/env python3
"""
Riot API 資料收集器：抓取真實對戰的「出裝順序」與「技能加點」，產生 assets/lol/builds.json

設計原則（依 Riot 開發者政策）：
  1. API Key 一律從環境變數讀取，絕不寫進檔案、絕不進前端
  2. 只在「建置時間」抓資料並彙整成統計結果，網站本身仍是純靜態（離線可用）
  3. 只輸出彙整後的建議（最常見的出裝順序），不保存任何玩家個資（不含 Riot ID／PUUID）
  4. 遵守速率限制：預設每次請求間隔 1.3 秒，遇 429 自動退避重試

用法：
    set RIOT_API_KEY=RGAPI-xxxxxxxx      （Windows cmd）
    $env:RIOT_API_KEY='RGAPI-xxxxxxxx'   （PowerShell）
    python tools/fetch_builds_api.py --region asia --platform tw2 --players 40 --matches 12 --out assets/lol/builds.json

參數：
    --region    區域路由（match-v5）：asia / europe / americas / sea
    --platform  平台路由（聯盟資料）：tw2 / kr / na1 / euw1 ...
    --players   取前 N 位菁英玩家（來自 Challenger 聯盟）
    --matches   每位玩家抓幾場積分對戰
    --out       輸出檔路徑（預設 assets/lol/builds.json）
"""
import argparse
import collections
import io
import json
import os
import sys
import time
import urllib.error
import urllib.request

SKILL_SLOT = {1: 'Q', 2: 'W', 3: 'E', 4: 'R'}


def api_get(url, key, tries=4):
    """GET JSON，遇 429/5xx 自動退避重試。"""
    delay = 2.0
    for attempt in range(tries):
        req = urllib.request.Request(url, headers={
            'X-Riot-Token': key,
            'User-Agent': 'lol-guide-home-build-collector/1.0',
        })
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.loads(r.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if e.code in (429, 500, 502, 503, 504) and attempt < tries - 1:
                wait = delay if e.code != 429 else float(e.headers.get('Retry-After', delay))
                print('    HTTP %d，等待 %.1fs 後重試…' % (e.code, wait))
                time.sleep(wait)
                delay *= 2
                continue
            print('    HTTP %d：%s' % (e.code, url[:96]))
            return None
        except Exception as e:                                   # 網路問題
            if attempt < tries - 1:
                time.sleep(delay)
                delay *= 2
                continue
            print('    失敗：%s' % str(e)[:80])
            return None
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--region', default='asia')
    ap.add_argument('--platform', default='tw2')
    ap.add_argument('--players', type=int, default=40)
    ap.add_argument('--matches', type=int, default=12)
    ap.add_argument('--out', default=os.path.join('assets', 'lol', 'builds.json'))
    ap.add_argument('--sleep', type=float, default=1.3)
    args = ap.parse_args()

    key = os.environ.get('RIOT_API_KEY')
    if not key:
        print('  錯誤：請先設定環境變數 RIOT_API_KEY（金鑰只放在環境變數，不會寫入檔案）')
        print('  PowerShell：  $env:RIOT_API_KEY=\'RGAPI-xxxx\'')
        return 2

    plat = 'https://%s.api.riotgames.com' % args.platform
    reg = 'https://%s.api.riotgames.com' % args.region

    # 1) 菁英玩家（只取 PUUID，不保存任何識別資訊）
    print('  取得 Challenger 名單（%s）…' % args.platform)
    league = api_get('%s/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5' % plat, key)
    if not league or not league.get('entries'):
        print('  錯誤：取不到 Challenger 名單（可能是金鑰過期或區域錯誤）')
        return 1
    entries = sorted(league['entries'], key=lambda e: e.get('leaguePoints', 0), reverse=True)
    puuids = [e['puuid'] for e in entries if e.get('puuid')][:args.players]
    print('  玩家數 = %d（只使用 PUUID，用完即丟）' % len(puuids))

    # 統計容器：champion + 位置 → 資料
    starts = collections.defaultdict(collections.Counter)      # 起手裝組合
    cores = collections.defaultdict(collections.Counter)       # 核心裝組合（前 3 件）
    skills = collections.defaultdict(collections.Counter)      # 技能加點順序
    keystones = collections.defaultdict(collections.Counter)   # 基石符文
    seen_matches = 0

    for pi, puuid in enumerate(puuids, 1):
        ids = api_get('%s/lol/match/v5/matches/by-puuid/%s/ids?queue=420&count=%d' % (reg, puuid, args.matches), key)
        time.sleep(args.sleep)
        if not ids:
            continue
        for mid in ids:
            match = api_get('%s/lol/match/v5/matches/%s' % (reg, mid), key)
            time.sleep(args.sleep)
            if not match:
                continue
            tl = api_get('%s/lol/match/v5/matches/%s/timeline' % (reg, mid), key)
            time.sleep(args.sleep)
            if not tl:
                continue
            seen_matches += 1
            parts = {p['participantId']: p for p in match['info']['participants']}
            events = [ev for f in tl['info']['frames'] for ev in f.get('events', [])]
            for pid, p in parts.items():
                champ = p.get('championName')
                role = (p.get('teamPosition') or '').lower()
                if not champ or not role:
                    continue
                key2 = '%s|%s' % (champ, role)
                buys = [ev['itemId'] for ev in events
                        if ev.get('type') == 'ITEM_PURCHASED' and ev.get('participantId') == pid]
                if len(buys) >= 4:
                    starts[key2][tuple(sorted(buys[:2]))] += 1
                    cores[key2][tuple(buys[2:5])] += 1
                ups = [SKILL_SLOT.get(ev.get('skillSlot')) for ev in events
                       if ev.get('type') == 'SKILL_LEVEL_UP' and ev.get('participantId') == pid]
                ups = [u for u in ups if u]
                if len(ups) >= 9:
                    skills[key2][''.join(ups[:9])] += 1
                ks = ((p.get('perks') or {}).get('styles') or [{}])[0].get('selections') or []
                if ks:
                    keystones[key2][str(ks[0].get('perk'))] += 1
        print('  [%d/%d] 已彙整 %d 場' % (pi, len(puuids), seen_matches))

    # 2) 輸出（只留最常見的組合，不含任何玩家資訊）
    out = {}
    for k in set(list(starts) + list(cores) + list(skills) + list(keystones)):
        e = {}
        if starts[k]:
            e['start'] = list(starts[k].most_common(1)[0][0])
        if cores[k]:
            e['core'] = list(cores[k].most_common(1)[0][0])
        if skills[k]:
            e['skill'] = skills[k].most_common(1)[0][0]
        if keystones[k]:
            e['keystone'] = keystones[k].most_common(1)[0][0]
        e['games'] = max(starts[k].total(), cores[k].total(), skills[k].total())
        if e.get('start') or e.get('core'):
            out[k] = e

    path = args.out if os.path.isabs(args.out) else os.path.join(os.getcwd(), args.out)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, 'w', encoding='utf-8', newline='') as fh:
        json.dump({
            'source': 'Riot Match-V5（建置時間彙整，僅存統計結果，不含玩家資訊）',
            'region': args.region, 'platform': args.platform,
            'matches': seen_matches, 'players': len(puuids),
            'builds': out,
        }, fh, ensure_ascii=False, separators=(',', ':'))
    print('  完成：%d 場、%d 位玩家、%d 種英雄×位置組合 → %s' % (seen_matches, len(puuids), len(out), path))
    return 0


if __name__ == '__main__':
    sys.exit(main())
