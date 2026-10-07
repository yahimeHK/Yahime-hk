#!/usr/bin/env python3
"""
下載 4 張 LOL 官方美術，處理成網站要用的頁面背景圖。

來源用 Riot 自己的 CDN：
  1. CommunityDragon 的 centered splash art（專為橫幅／背景裁切，解析度最高）
  2. 失敗時退回 Data Dragon 的 champion splash
兩者都是 Riot 官方提供給第三方開發者使用的素材，網站本來就已經在用 Data Dragon。

輸出：assets/bg-*.jpg（寬 1920、輕微柔化、JPEG 壓縮）
"""
import io
import os
import sys
import urllib.request

from PIL import Image, ImageFilter

# 網站根目錄：優先用環境變數，其次自動判斷（產生器放 tools/ 時，上一層就是網站根目錄）
_HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.environ.get('LOL_SITE') or (_HERE if os.path.exists(os.path.join(_HERE, 'index.html')) else os.path.dirname(_HERE))
ASSETS = os.path.join(SITE, 'assets')

JOBS = [
    ('bg-home.jpg',      'Garen',       '蒂瑪西亞，呼應首頁《救贖》開幕動畫'),
    ('bg-champions.jpg', 'Yasuo',       '英雄攻略：經典英雄'),
    ('bg-items.jpg',     'Ezreal',      '裝備攻略：靠裝備成形的射手'),
    ('bg-guides.jpg',    'MissFortune', '戰術商城：賞金獵人'),
]


def fetch(url):
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (LOL guide site background fetch)'
    })
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def main():
    ok = 0
    for name, champ, why in JOBS:
        urls = [
            'https://cdn.communitydragon.org/latest/champion/%s/splash-art/centered' % champ,
            'https://ddragon.leagueoflegends.com/cdn/img/champion/splash/%s_0.jpg' % champ,
        ]
        data, used = None, None
        for u in urls:
            try:
                data = fetch(u)
                used = u
                break
            except Exception as e:                      # noqa: BLE001
                print('   ! 失敗 %s -> %s' % (u, e), file=sys.stderr)

        if data is None:
            print('   x %s：兩個來源都抓不到' % name)
            continue

        im = Image.open(io.BytesIO(data)).convert('RGB')
        w, h = im.size
        if w != 1920:
            im = im.resize((1920, max(1, round(h * 1920 / w))), Image.LANCZOS)
        im = im.filter(ImageFilter.GaussianBlur(0.8))    # 放大後柔化一點，當背景更順
        out = os.path.join(ASSETS, name)
        im.save(out, 'JPEG', quality=80, optimize=True, progressive=True)
        print('   + %-18s %sx%s  %5.0f KB  來源：%s（%s）' % (
            name, im.size[0], im.size[1], os.path.getsize(out) / 1024,
            used.split('/')[2], why))
        ok += 1

    print('\n完成 %d/%d 張，總計 %.1f MB' % (
        ok, len(JOBS),
        sum(os.path.getsize(os.path.join(ASSETS, n)) for n, _c, _w in JOBS
            if os.path.exists(os.path.join(ASSETS, n))) / 1024 / 1024))
    return 0 if ok == len(JOBS) else 1


if __name__ == '__main__':
    sys.exit(main())
