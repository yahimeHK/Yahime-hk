/* LOL 攻略站：本機使用者檔案（暱稱 ＋ 等級 ＋ 經驗值）
   設計原則：
   - 純本機（localStorage），沒有密碼、沒有 Email、不連網、不上傳任何資料
   - 只在這台裝置／這個瀏覽器有效（換裝置就沒有，屬預期行為）
   - 等級：每 100 XP 升一級；XP 來源：首次造訪某頁 +5、每日簽到 +20
   對外介面：window.LOLUser = { get, create, rename, addXP, checkIn, reset, level, need } */
(function () {
  'use strict';
  var KEY = 'lolUser';
  var XP_PER_LEVEL = 100;
  var PAGES_KEY = 'lolUserPages';

  function read(k, def) {
    try { var v = localStorage.getItem(k); return v ? JSON.parse(v) : def; } catch (e) { return def; }
  }
  function write(k, v) {
    try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* 無痕模式 */ }
  }
  function today() { var d = new Date(); return d.getFullYear() + '-' + (d.getMonth() + 1) + '-' + d.getDate(); }

  function get() {
    var u = read(KEY, null);
    if (!u || typeof u !== 'object' || !u.name) return null;
    if (typeof u.xp !== 'number' || u.xp < 0) u.xp = 0;
    return u;
  }
  function save(u) { write(KEY, u); render(); return u; }
  function level(xp) { return Math.floor((xp || 0) / XP_PER_LEVEL) + 1; }
  function need(xp) { return XP_PER_LEVEL - ((xp || 0) % XP_PER_LEVEL); }
  function progress(xp) { return ((xp || 0) % XP_PER_LEVEL) / XP_PER_LEVEL * 100; }

  function create(name) {
    name = String(name || '').trim().slice(0, 16);
    if (!name) return null;
    var u = get() || { created: Date.now(), xp: 0, pages: [], lastCheckIn: '' };
    u.name = name;
    return save(u);
  }

  function addXP(n) {
    var u = get();
    if (!u) return null;
    u.xp = Math.max(0, (u.xp || 0) + (parseInt(n, 10) || 0));
    u.history = u.history || {};
    u.history[today()] = (u.history[today()] || 0) + (parseInt(n, 10) || 0);
    return save(u);
  }

  function checkIn() {
    var u = get();
    if (!u) return { ok: false, msg: '請先建立檔案' };
    if (u.lastCheckIn === today()) return { ok: false, msg: '今天已簽到（明天再來）' };
    u.lastCheckIn = today();
    save(u);
    addXP(20);
    return { ok: true, msg: '簽到成功！+20 XP' };
  }

  /* 首次造訪某頁 +5 XP（同一頁只給一次） */
  function visitXP() {
    var u = get();
    if (!u) return;
    var page = (location.pathname.split('/').pop() || 'index.html').toLowerCase();
    var seen = read(PAGES_KEY, {}) || {};
    if (seen[page]) return;
    seen[page] = 1;
    write(PAGES_KEY, seen);
    addXP(5);
  }

  /* ---------------- UI ---------------- */
  var styleInjected = false;
  function injectStyle() {
    if (styleInjected) return;
    styleInjected = true;
    var st = document.createElement('style');
    st.textContent = [
      '.lu-badge{display:inline-flex;align-items:center;gap:7px;padding:7px 12px;cursor:pointer;',
      'font:inherit;font-size:13px;font-weight:800;color:#ffd98a;border:1px solid rgba(200,170,110,.55);',
      'border-radius:999px;background:linear-gradient(180deg,#332915,#1a140b);white-space:nowrap;',
      'box-shadow:inset 0 1px 0 rgba(255,231,170,.28),0 0 0 1px rgba(0,0,0,.5);transition:box-shadow .18s ease,transform .18s ease}',
      '.lu-badge:hover{transform:translateY(-1px);box-shadow:inset 0 1px 0 rgba(255,231,170,.35),0 0 18px -8px rgba(214,184,120,.9)}',
      '.lu-badge i{font-style:normal;font-size:11px;color:#00d9ff}',
      '.lu-panel{position:fixed;right:16px;top:64px;z-index:300;width:min(320px,92vw);padding:16px;',
      'background:linear-gradient(180deg,#111c24,#0a1016);border:1px solid rgba(98,170,190,.45);border-radius:16px;',
      'box-shadow:0 30px 70px -40px rgba(0,0,0,1);color:#c9d6dd;font-size:13px;display:none}',
      '.lu-panel.open{display:block}',
      '.lu-panel h3{margin:0 0 10px;font-size:15px;color:#f0eadb}',
      '.lu-panel input{width:100%;padding:9px 11px;margin:0 0 8px;color:#e8e4d9;background:#0a1016;',
      'border:1px solid #2b3a45;border-radius:9px;font:inherit}',
      '.lu-row{display:flex;gap:8px;margin:8px 0}',
      '.lu-btn{flex:1;padding:9px;font:inherit;font-size:13px;font-weight:700;color:#071016;cursor:pointer;',
      'background:linear-gradient(180deg,#d8bd80,#c8aa6e);border:0;border-radius:9px}',
      '.lu-btn.ghost{color:#9da9b2;background:#111d26;border:1px solid #2b3a45}',
      '.lu-bar{height:8px;margin:8px 0;background:#0a1016;border:1px solid #253540;border-radius:999px;overflow:hidden}',
      '.lu-bar span{display:block;height:100%;background:linear-gradient(90deg,#c8aa6e,#00d9ff)}',
      '.lu-meta{display:flex;justify-content:space-between;font-size:11.5px;color:#8e9aa4}',
      '.lu-msg{margin:8px 0 0;font-size:12px;color:#9ddff0;min-height:16px}',
      '@media (max-width:430px){.lu-badge{font-size:12px;padding:6px 9px;gap:5px}}'
    ].join('');
    document.head.appendChild(st);
  }

  function render() {
    var u = get();
    var host = document.querySelector('.topbar__right') || document.querySelector('.topbar');
    if (!host) return;
    var btn = document.getElementById('luBadge');
    if (!btn) {
      btn = document.createElement('button');
      btn.id = 'luBadge';
      btn.type = 'button';
      btn.className = 'lu-badge';
      host.appendChild(btn);
      btn.addEventListener('click', function (e) { e.stopPropagation(); toggle(); });
    }
    if (u) {
      btn.innerHTML = 'Lv.' + level(u.xp) + ' <i>' + (u.name || '') + '</i>';
      btn.title = '經驗值 ' + (u.xp || 0) + ' · 升級還需 ' + need(u.xp) + ' XP';
    } else {
      btn.innerHTML = '👤 建立檔案';
      btn.title = '建立本機使用者檔案（只存在這台裝置）';
    }
  }

  function panel() {
    var el = document.getElementById('luPanel');
    if (el) return el;
    el = document.createElement('div');
    el.id = 'luPanel';
    el.className = 'lu-panel';
    document.body.appendChild(el);
    el.addEventListener('click', function (e) { e.stopPropagation(); });
    return el;
  }

  function draw() {
    var u = get(), el = panel();
    if (!u) {
      el.innerHTML = '<h3>建立使用者檔案</h3>' +
        '<input id="luName" maxlength="16" placeholder="輸入暱稱（例如：小明）" autocomplete="off">' +
        '<div class="lu-row"><button class="lu-btn" id="luCreate">建立</button>' +
        '<button class="lu-btn ghost" id="luClose">關閉</button></div>' +
        '<p class="lu-msg">只存在這台裝置的瀏覽器，沒有密碼、不會上傳任何資料。</p>';
      el.querySelector('#luCreate').onclick = function () {
        if (create(el.querySelector('#luName').value)) { draw(); msg('檔案已建立 ✓'); }
        else msg('請輸入暱稱');
      };
      el.querySelector('#luClose').onclick = close;
    } else {
      el.innerHTML = '<h3>Lv.' + level(u.xp) + '　' + u.name + '</h3>' +
        '<div class="lu-bar"><span style="width:' + progress(u.xp).toFixed(1) + '%"></span></div>' +
        '<div class="lu-meta"><span>經驗值 ' + (u.xp || 0) + '</span><span>升級還需 ' + need(u.xp) + ' XP</span></div>' +
        '<div class="lu-row"><button class="lu-btn" id="luSign">每日簽到 +20</button></div>' +
        '<div class="lu-row"><button class="lu-btn ghost" id="luRen">改暱稱</button>' +
        '<button class="lu-btn ghost" id="luReset">重置</button>' +
        '<button class="lu-btn ghost" id="luClose">關閉</button></div>' +
        '<p class="lu-msg" id="luMsg"></p>' +
        '<p class="lu-msg" style="color:#6f7c86">XP 來源：首次造訪某頁 +5、每日簽到 +20。資料只在這台裝置。</p>';
      el.querySelector('#luSign').onclick = function () { var r = checkIn(); msg(r.msg); draw(); };
      el.querySelector('#luRen').onclick = function () {
        var n = prompt('新的暱稱（1–16 字）', u.name);
        if (n && create(n)) { draw(); msg('暱稱已更新 ✓'); }
      };
      el.querySelector('#luReset').onclick = function () {
        if (!confirm('確定要刪除這個本機檔案？經驗值與等級都會清除。')) return;
        try { localStorage.removeItem(KEY); localStorage.removeItem(PAGES_KEY); } catch (e) {}
        render(); draw(); msg('已重置');
      };
      el.querySelector('#luClose').onclick = close;
    }
  }

  function msg(t) { var m = document.getElementById('luMsg'); if (m) m.textContent = t || ''; }
  function open() { injectStyle(); draw(); panel().classList.add('open'); }
  function close() { var el = document.getElementById('luPanel'); if (el) el.classList.remove('open'); }
  function toggle() { var el = document.getElementById('luPanel'); if (el && el.classList.contains('open')) close(); else open(); }

  function boot() {
    injectStyle();
    render();
    if (get()) visitXP();
    document.addEventListener('click', function (e) {
      var el = document.getElementById('luPanel');
      if (el && el.classList.contains('open') && !el.contains(e.target)) close();
    });
    /* 其他頁面可呼叫 window.LOLUser.addXP(10) 給獎勵 */
    window.LOLUser = { get: get, create: create, addXP: addXP, checkIn: checkIn, level: level, need: need, open: open };
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
