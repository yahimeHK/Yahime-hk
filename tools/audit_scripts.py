#!/usr/bin/env python3
"""檢查全站 JavaScript：語法、元素參考、重複 id、常見地雷。

用法：
    python tools/audit_scripts.py [網站根目錄] [node 執行檔]

檢查項目
  1. 每個 .js 的語法（node --check）
  2. JS 取用的元素 id 是否存在於「有載入這支 JS 的頁面」上（找不到就是死碼或打錯 id）
  3. 同一頁是否有重複 id（會讓 getElementById 抓到錯的元素）
  4. 常見地雷：console.log 殘留、setInterval 沒清、空 catch 吞錯、todo/TODO 註解
"""
import io
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.dirname(HERE)
NODE = sys.argv[2] if len(sys.argv) > 2 else 'node'

JS_ID_RE = [
    re.compile(r"""getElementById\(\s*['"]([A-Za-z0-9_\-]+)['"]"""),
    re.compile(r"""\$\(\s*['"]([A-Za-z0-9_\-]+)['"]\s*\)"""),
    re.compile(r"""querySelector(?:All)?\(\s*['"]#([A-Za-z0-9_\-]+)"""),
]
SCRIPT_SRC_RE = re.compile(r"""<script[^>]+src\s*=\s*["']([^"']+)["']""", re.I)
ID_ATTR_RE = re.compile(r"""\bid\s*=\s*["']([A-Za-z0-9_\-]+)["']""")
JS_CREATED_ID_RE = re.compile(r"""\.id\s*=\s*['"]([A-Za-z0-9_\-]+)['"]""")

results = []


def add(level, area, msg):
    results.append((level, area, msg))
    print("[%s] %-10s %s" % (level, area, msg), flush=True)


def read(path):
    with io.open(path, encoding='utf-8') as fh:
        return fh.read()


def main():
    js_files = sorted(f for f in os.listdir(SITE) if f.endswith('.js'))
    html_files = sorted(f for f in os.listdir(SITE) if f.endswith('.html'))

    # ---------------------------------------------------------------- 1. 語法
    if not js_files:
        add('FAIL', 'syntax', '找不到任何 .js')
    for f in js_files:
        path = os.path.join(SITE, f)
        try:
            p = subprocess.run([NODE, '--check', path], capture_output=True, text=True, timeout=60)
            if p.returncode == 0:
                add('PASS', 'syntax', '%s 語法正確' % f)
            else:
                add('FAIL', 'syntax', '%s 語法錯誤：%s' % (f, (p.stderr or '').strip().split('\n')[-3:]))
        except Exception as e:                                    # noqa: BLE001
            add('INFO', 'syntax', '%s 無法檢查（%s）' % (f, e))

    # ------------------------------------------------- 2. 每頁的 id 與載入的 JS
    page_ids = {}
    page_scripts = {}
    for page in html_files:
        text = read(os.path.join(SITE, page))
        ids = {}
        for m in ID_ATTR_RE.finditer(text):
            ids[m.group(1)] = ids.get(m.group(1), 0) + 1
        page_ids[page] = ids
        page_scripts[page] = [s.split('?')[0] for s in SCRIPT_SRC_RE.findall(text)]

    # JS 自行建立的 id 也算存在（例如動態插入的節點）
    created_ids = set()
    for f in js_files:
        created_ids |= set(JS_CREATED_ID_RE.findall(read(os.path.join(SITE, f))))

    # ------------------------------------------------- 3. 重複 id
    for page, ids in page_ids.items():
        dups = sorted(k for k, v in ids.items() if v > 1)
        if dups:
            add('FAIL', 'dup-id', '%s 有重複 id：%s' % (page, dups))
        else:
            add('PASS', 'dup-id', '%s 沒有重複 id（%d 個）' % (page, len(ids)))

    # ------------------------------------------------- 4. JS 取用的元素是否存在
    problems = 0
    for f in js_files:
        src = read(os.path.join(SITE, f))
        refs = set()
        for rx in JS_ID_RE:
            refs |= set(rx.findall(src))
        if not refs:
            add('INFO', 'refs', '%s 沒有取用特定 id（用 class 或動態查詢）' % f)
            continue
        # 這支 JS 被哪些頁面載入
        users = [p for p, s in page_scripts.items() if f in s]
        if not users:
            add('INFO', 'refs', '%s 沒有被任何頁面載入' % f)
            continue
        missing_all = []
        for ref in sorted(refs):
            if ref in created_ids:
                continue
            if not any(ref in page_ids[p] for p in users):
                missing_all.append(ref)
        if missing_all:
            problems += len(missing_all)
            add('INFO', 'refs', '%s 取用的 id 不在任何載入它的頁面上：%s（這些程式碼會安静跳過）'
                % (f, ', '.join(missing_all[:8])))
        else:
            add('PASS', 'refs', '%s 取用的 %d 個 id 都存在' % (f, len(refs)))

    # ------------------------------------------------- 5. 常見地雷
    for f in js_files:
        src = read(os.path.join(SITE, f))
        logs = len(re.findall(r'\bconsole\.(log|debug)\(', src))
        if logs:
            add('INFO', 'smell', '%s 有 %d 個 console.log（上線前建議清掉）' % (f, logs))
        intervals = len(re.findall(r'\bsetInterval\(', src))
        cleared = len(re.findall(r'\bclearInterval\(', src))
        if intervals and intervals > cleared:
            add('INFO', 'smell', '%s setInterval %d 次、clearInterval %d 次（確認會停止）' % (f, intervals, cleared))
        empty_catch = len(re.findall(r'catch\s*\([^)]*\)\s*\{\s*\}', src))
        if empty_catch:
            add('INFO', 'smell', '%s 有 %d 個空的 catch（會吞掉錯誤）' % (f, empty_catch))
        if re.search(r'\bTODO\b|\bFIXME\b', src):
            add('INFO', 'smell', '%s 還有 TODO／FIXME' % f)

    fails = [r for r in results if r[0] == 'FAIL']
    print('\n總計 %d 項：PASS %d / INFO %d / FAIL %d'
          % (len(results), len([r for r in results if r[0] == 'PASS']),
             len([r for r in results if r[0] == 'INFO']), len(fails)))
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
