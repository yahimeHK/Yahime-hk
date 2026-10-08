#!/usr/bin/env python3
"""
自動版號（cache busting）：用「檔案內容的雜湊」當版本號，寫進所有頁面的資源網址。

用法：
    python tools/bust_cache.py <站台資料夾>         # 檢查並自動更新版號
    python tools/bust_cache.py <站台資料夾> --check # 只檢查，不修改（不一致時結束碼 1）

為什麼要這樣做：
    只要有人改了 nav.js／fx.js／style.css…，網址就會跟著變，瀏覽器非重新下載不可。
    不需要（也不可能忘記）手動改版號，因此不會再出現「明明更新了卻看不到」。
"""
import hashlib
import io
import os
import re
import sys

# 需要版號的資源（依副檔名判斷，涵蓋所有共用資源）
ASSET_EXT = ('.js', '.css')
SKIP_DIRS = {'.git', 'assets', 'tools', 'node_modules'}


def asset_hash(path, length=10):
    with open(path, 'rb') as fh:
        return hashlib.sha1(fh.read()).hexdigest()[:length]


def collect_assets(site):
    out = {}
    for f in sorted(os.listdir(site)):
        if f.endswith(ASSET_EXT) and os.path.isfile(os.path.join(site, f)):
            out[f] = asset_hash(os.path.join(site, f))
    return out


def targets(site):
    """所有要改的檔案：頁面 ＋ 產生器樣板"""
    files = [os.path.join(site, f) for f in sorted(os.listdir(site))
             if f.endswith('.html') and not f.startswith('_t_')]
    # 只處理 HTML：產生器（tools/*.py）內的 asset 字串同時用於檔名，加上 ?v= 會讓產生器崩潰
    return files


def rewrite(site, assets, check_only):
    # 找出所有 <script src> / <link href> 指向本機資源的引用
    ref = re.compile(r'(["\'(])((?:\./)?)([A-Za-z0-9_.\-]+\.(?:js|css))(?:\?v=[A-Za-z0-9._\-]+)?(["\')])')
    changes, mismatches = [], []
    for path in targets(site):
        try:
            with io.open(path, encoding='utf-8') as fh:
                src = fh.read()
        except (UnicodeDecodeError, OSError):
            continue
        out = src

        def sub(m):
            quote, prefix, name, quote2 = m.group(1), m.group(2), m.group(3), m.group(4)
            h = assets.get(name)
            if not h:
                return m.group(0)          # 外部資源或不存在 → 不動
            want = '%s%s?v=%s%s' % (quote, name, h, quote2)
            if m.group(0) != want:
                mismatches.append((os.path.relpath(path, site), name, m.group(0), want))
            return want

        out = ref.sub(sub, out)
        if out != src and not check_only:
            with io.open(path, 'w', encoding='utf-8', newline='') as fh:
                fh.write(out)
            changes.append(os.path.relpath(path, site))
    return changes, mismatches


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    site = os.path.abspath(args[0]) if args else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    check_only = '--check' in sys.argv
    assets = collect_assets(site)
    changes, mismatches = rewrite(site, assets, check_only)
    if check_only:
        if mismatches:
            print('  ✗ 版號與內容不一致（%d 處）：' % len(mismatches))
            for f, n, old, new in mismatches[:10]:
                print('     %-22s %-18s %s → %s' % (f, n, old, new))
            print('  → 執行 python tools/bust_cache.py 可自動修正')
            return 1
        print('  ✓ 版號全部與內容一致（%d 個資源 × %d 個檔案）' % (len(assets), len(targets(site))))
        return 0
    if mismatches:
        print('  已更新 %d 個檔案的版號（依內容雜湊）：' % len(changes))
        for c in changes[:12]:
            print('     ' + c)
        print('  資源雜湊：' + ', '.join('%s=%s' % (k, v) for k, v in list(assets.items())[:6]) + ' …')
    else:
        print('  版號已是最新，無需更新（%d 個資源）' % len(assets))
    return 0


if __name__ == '__main__':
    sys.exit(main())
