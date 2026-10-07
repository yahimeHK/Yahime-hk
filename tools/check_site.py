#!/usr/bin/env python3
"""
驗證 LOL_Guide_Offline：把整站跑起來，逐一檢查每個頁面與素材，
包含 Range(206) 支援、參照完整性、播放器 DOM 接線、CSS 作用域與影片規格。

用法：
    python _check_site.py <site_dir> <base_url> [node_exe]
"""
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request

PASS, FAIL, INFO = "PASS", "FAIL", "INFO"
results = []


def rec(state, area, msg):
    results.append((state, area, msg))
    print("[%s] %-9s %s" % (state, area, msg), flush=True)


def http(url, headers=None, method="GET", attempts=3):
    """本機 loopback 偶爾會有一個連線卡住，重試幾次即可。"""
    last = None
    for i in range(attempts):
        hd = dict(headers or {})
        hd["Connection"] = "close"
        req = urllib.request.Request(url, headers=hd, method=method)
        try:
            with urllib.request.urlopen(req, timeout=8) as r:
                return r.status, dict(r.headers), r.read()
        except urllib.error.HTTPError as e:
            return e.code, dict(e.headers), e.read()
        except Exception as e:                       # timeout / reset -> 重試
            last = e
    raise last


# --------------------------------------------------------------------------- refs
REF_RE_HTML = re.compile(r'(?:src|href)\s*=\s*["\']([^"\']+)["\']', re.I)
REF_RE_CSS = re.compile(r'url\(\s*["\']?([^"\')]+)["\']?\s*\)', re.I)
REF_RE_FETCH = re.compile(r'''(?:fetch|src)\(\s*["']([^"']+)["']''', re.I)


def local_refs(text, is_css=False):
    out = []
    for m in (REF_RE_CSS if is_css else REF_RE_HTML).finditer(text):
        raw = m.group(1).strip()
        if not raw or raw.startswith(("#", "http://", "https://", "//", "data:", "mailto:", "tel:", "javascript:")):
            continue
        out.append(raw.split("?")[0].split("#")[0])
    return out


def css_selector_audit(path):
    """回傳 (未作用域的選擇器清單, 規則總數)。"""
    src = open(path, encoding="utf-8").read()
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
    bad, total = [], 0
    buf, depth, ctx = "", 0, []
    for ch in src:
        if ch == "{":
            head = buf.strip()
            buf = ""
            total += 1
            if head.startswith("@"):
                ctx.append(depth)
                if head.startswith("@keyframes") or head.startswith("@-webkit-keyframes"):
                    ctx[-1] = "kf"
            elif ctx and ctx[-1] == "kf":
                pass                                   # keyframe 的 0%/to 步驟
            else:
                for sel in head.split(","):
                    sel = sel.strip()
                    if not sel:
                        continue
                    if not (sel.startswith(".salvation-player")
                            or sel.startswith(".video-card--feature")
                            or sel.startswith(".video-thumb")):
                        bad.append(sel)
            depth += 1
        elif ch == "}":
            depth -= 1
            if ctx and isinstance(ctx[-1], int) and depth == ctx[-1]:
                ctx.pop()
            elif ctx and ctx[-1] == "kf" and depth == 0:
                ctx.pop()
            buf = ""
        else:
            buf += ch
    return bad, total


# --------------------------------------------------------------------------- mp4
def mp4_video_spec(path):
    """從 tkhd / mvhd 取出影片寬高與片長（秒）。"""
    data = open(path, "rb").read()
    spec = {}
    mv = data.find(b"mvhd")
    if mv > 0:
        ver = data[mv + 4]
        off = mv + 8 + (16 if ver == 1 else 8)
        timescale = int.from_bytes(data[off:off + 4], "big")
        duration = int.from_bytes(data[off + 4:off + (12 if ver == 1 else 8)], "big")
        if timescale:
            spec["duration"] = duration / timescale
    # tkhd: 跳過 version/flags + creation + modification + track_ID + reserved
    # + duration，再跳 reserved/layer/group/volume/reserved/matrix，才輪到寬高。
    for m in re.finditer(b"tkhd", data):
        o = m.start() + 4
        ver = data[o]
        base = o + 4 + (32 if ver == 1 else 20)
        w = int.from_bytes(data[base + 52:base + 56], "big") / 65536
        h = int.from_bytes(data[base + 56:base + 60], "big") / 65536
        if w and h:
            spec["width"], spec["height"] = round(w), round(h)
    return spec


def main():
    site = os.path.abspath(sys.argv[1])
    base = sys.argv[2].rstrip("/") + "/"
    node = sys.argv[3] if len(sys.argv) > 3 else None

    # ---------------------------------------------------------------- 1. HTTP
    pages = ["index.html", "champions.html", "items.html", "guides.html"]
    for p in pages:
        st, hd, body = http(base + p)
        ok = st == 200 and "text/html" in hd.get("Content-Type", "")
        rec(PASS if ok else FAIL, "http", "%s -> %s %s (%d bytes)" % (
            p, st, hd.get("Content-Type"), len(body)))

    st, hd, _ = http(base)
    rec(PASS if st == 200 else FAIL, "http", "GET / -> %s (index 自動對應)" % st)

    # 每個檔案都能取得，且大小與磁碟一致
    files = []
    for dirpath, _dirs, names in os.walk(site):
        for n in names:
            files.append(os.path.relpath(os.path.join(dirpath, n), site).replace("\\", "/"))
    for rel in sorted(files):
        size = os.path.getsize(os.path.join(site, rel))
        if size > 1024 * 1024:
            st, hd, body = http(base + rel, {"Range": "bytes=0-2047"})
            ok = st == 206 and len(body) == 2048 and hd.get("Content-Range", "").endswith("/%d" % size)
        else:
            st, hd, body = http(base + rel)
            ok = st == 200 and len(body) == size
        rec(PASS if ok else FAIL, "asset", "%-32s %s  %s" % (rel, st, hd.get("Content-Type", "?")))

    # 不存在 -> 404，且不可穿越目錄
    st, _hd, _b = http(base + "definitely-missing.png")
    rec(PASS if st == 404 else FAIL, "http", "missing file -> %s (預期 404)" % st)
    st, _hd, _b = http(base + "%2e%2e/%2e%2e/serve.py")
    rec(PASS if st == 404 else FAIL, "http", "path traversal -> %s (預期 404)" % st)

    # ------------------------------------------------------- 2. 參照完整性
    for rel in sorted(files):
        low = rel.lower()
        if low.endswith(".html"):
            refs = local_refs(open(os.path.join(site, rel), encoding="utf-8").read())
        elif low.endswith(".css"):
            refs = local_refs(open(os.path.join(site, rel), encoding="utf-8").read(), is_css=True)
        else:
            continue
        for ref in refs:
            target = os.path.normpath(os.path.join(os.path.dirname(os.path.join(site, rel)), ref))
            exists = os.path.isfile(target)
            inside = os.path.abspath(target).startswith(site)
            ok = exists and inside
            rec(PASS if ok else FAIL, "ref", "%s -> %s%s" % (rel, ref, "" if ok else "  << 檔案不存在"))

    # ------------------------------------------------- 3. 播放器 DOM 接線
    idx = open(os.path.join(site, "index.html"), encoding="utf-8").read()
    pjs = open(os.path.join(site, "player.js"), encoding="utf-8").read()
    ids = set(re.findall(r'id\s*=\s*"([^"]+)"', idx))
    wanted = set(re.findall(r"\$\('([^']+)'\)", pjs)) | set(re.findall(r"getElementById\('([^']+)'\)", pjs))
    missing = sorted(wanted - ids)
    rec(PASS if not missing else FAIL, "dom", "player.js 需要的 id 全部存在於 index.html（%d 個）%s"
        % (len(wanted), "" if not missing else " 缺少: " + ", ".join(missing)))

    for sel in [".salvation-player", ".stage__frame", ".video-card--feature"]:
        rec(PASS if sel.strip(".") in idx else FAIL, "dom", "index.html 含 %s" % sel)

    # 播放器只掛在首頁
    others = [p for p in pages if p != "index.html"]
    strays = [p for p in others if "player.js" in open(os.path.join(site, p), encoding="utf-8").read()]
    rec(PASS if not strays else FAIL, "dom", "player.js 只載入首頁%s" % ("" if not strays else " 也出現在: " + ",".join(strays)))

    # 影片來源（自訂播放器用 src 屬性，player.js 會讀它）
    m = re.search(r'<video[^>]*id="video"[^>]*src="([^"]+)"', idx)
    src = m.group(1) if m else None
    ok = bool(src) and os.path.isfile(os.path.join(site, src))
    rec(PASS if ok else FAIL, "dom", "自訂播放器影片來源 %s%s" % (src, "" if ok else " 不存在"))

    # -------------------------------------------- 4. CSS 作用域 / JS 語法
    bad, total = css_selector_audit(os.path.join(site, "player.css"))
    rec(PASS if not bad else FAIL, "css", "player.css %d 條規則，未作用域的選擇器: %s"
        % (total, "無" if not bad else ", ".join(bad[:8])))

    for f in ["style.css", "player.css"]:
        t = open(os.path.join(site, f), encoding="utf-8").read()
        rec(PASS if t.count("{") == t.count("}") else FAIL, "css", "%s 大括號平衡 (%d/%d)"
            % (f, t.count("{"), t.count("}")))

    if node:
        for f in ["script.js", "player.js"]:
            r = subprocess.run([node, "--check", os.path.join(site, f)],
                               capture_output=True, text=True)
            rec(PASS if r.returncode == 0 else FAIL, "js", "node --check %s%s"
                % (f, "" if r.returncode == 0 else " :: " + r.stderr.strip()[:200]))

    # ------------------------------------------------------------ 5. 影片規格
    spec = mp4_video_spec(os.path.join(site, "assets/assetsvideo1.mp4"))
    if "width" in spec:
        rec(INFO, "video", "assetsvideo1.mp4 = %dx%d, %.1f 秒" % (spec["width"], spec["height"], spec.get("duration", 0)))
        rec(PASS if spec["width"] == 640 and spec["height"] == 272 else FAIL, "video",
            "CSS aspect-ratio 640/272 與實際解析度一致")
    else:
        rec(FAIL, "video", "無法解析 mp4 規格")

    # -------------------------------------------------------------- 總結
    fails = [r for r in results if r[0] == FAIL]
    print("\n" + "=" * 72)
    print("總計 %d 項：PASS %d / INFO %d / FAIL %d" % (
        len(results),
        sum(1 for r in results if r[0] == PASS),
        sum(1 for r in results if r[0] == INFO),
        len(fails)))
    for _s, area, msg in fails:
        print("  FAIL [%s] %s" % (area, msg))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
