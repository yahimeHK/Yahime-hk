/* ==========================================================================
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
