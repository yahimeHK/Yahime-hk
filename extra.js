/* ==========================================================================
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
    maps: { file: 'maps.json', pick: function (d) { return d.maps; },
      intro: '官方遊戲內地圖素材（小地圖與各地形變化）與戰術重點：目標時間、地形、視野，點縮圖可放大。',
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

  // 各分類頁的下拉篩選：選項由畫面資料自動產生，不需要手寫清單
  var FILTERS = {
    skins:     { scope: '.skin-card',      attr: 'data-theme', label: '全部造型系列', nested: '.skin-champ' },
    gallery:   { scope: '[data-kind]',     attr: 'data-kind',  label: '全部類型' },
    abilities: { scope: '.ability-card',   attr: 'data-slot',  label: '全部技能' },
    maps:      { scope: '.map-card',       attr: 'data-map',   label: '全部地圖' },
    runes:     { scope: '.rune-tree-block', attr: 'data-tree', label: '全部符文樹' },
    gear:      { scope: '.gear-card',      attr: 'data-tags',  label: '全部類型' },
    tactics:   { scope: '.tac-card',       attr: 'data-diff',  label: '全部難度' }
  };

  function buildFilter() {
    var cfg = FILTERS[MODE];
    var sel = $('exSelect');
    if (!cfg || !sel) return;
    var counts = {}, total = 0;
    Array.prototype.forEach.call(document.querySelectorAll('#exBody ' + cfg.scope), function (el) {
      var raw = el.getAttribute(cfg.attr) || '';
      if (!raw) return;
      raw.split(/[ ]+/).forEach(function (v) {
        v = v.trim();
        if (!v) return;
        counts[v] = (counts[v] || 0) + 1;
        total++;
      });
    });
    var keys = Object.keys(counts).sort(function (a, b) { return counts[b] - counts[a] || a.localeCompare(b); });
    if (!keys.length) { sel.hidden = true; return; }
    var shown = keys.slice(0, 40);                     // 選項太多時只列前 40 個（其餘仍可用搜尋）
    sel.hidden = false;
    var allLabel = (window.LOLi18n && LOLi18n.t) ? LOLi18n.t(cfg.label) : cfg.label;
    sel.innerHTML = '<option value="all">' + esc(allLabel) + '（' + keys.length + '）</option>' +
      shown.map(function (k) {
        return '<option value="' + esc(k) + '">' + esc(k) + '（' + counts[k] + '）</option>';
      }).join('') +
      (keys.length > shown.length ? '<option value="__more__" disabled>…其餘 ' + (keys.length - shown.length) + ' 項請用搜尋</option>' : '');
    state.sel = 'all';
  }

  function sum(arr, key) { var n = 0; arr.forEach(function (x) { n += (x[key] || []).length; }); return n; }
  function sumTrees(trees) { var n = 0; trees.forEach(function (t) { t.slots.forEach(function (s) { n += s.runes.length; }); }); return n; }
  function $(id) { return document.getElementById(id); }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }

  var DATA = null, ITEMS = [], state = { role: '全部', q: '', sel: 'all' };

  function role(name) { return name ? '<span class="tag tag--role">' + esc(name) + '</span>' : ''; }

  // 搜尋索引：中文名、英文名、稱號、玩家稱呼、職業、額外文字都會被搜到
  function sText(c, extra) {
    if (!c) return String(extra || '');
    return [c.champ || c.name || '', c.en || '', c.title || '',
      (c.aliases || []).join(' '), (c.tags || []).join(' '), extra || ''].join(' ').replace(/[ ]+/g, ' ').trim();
  }

  /* ---------------------------------------------------------------- 各頁卡片 */
  function cardSkins(c) {
    var imgs = c.skins.map(function (s) {
      return '<button class="skin-card" type="button" data-theme="' + esc(s.theme || '') + '" data-big="' + esc(s.big) + '" data-name="' + esc(c.champ + ' ' + s.name) + '">' +
        '<img src="' + esc(s.img) + '" alt="' + esc(s.name) + '" loading="lazy">' +
        '<span>' + esc(s.name) + '</span></button>';
    }).join('');
    return '<section class="skin-champ" data-role="' + esc(c.role) + '" data-name="' + esc(sText(c, c.skins.map(function (s) { return s.name; }).join(' '))) + '">' +
      '<div class="skin-champ__head"><b>' + esc(c.champ) + '</b>' + role(c.role) +
      '<span>' + c.skins.length + ' 個造型</span></div><div class="skin-grid">' + imgs + '</div></section>';
  }

  function cardArt(c) {
    return '<figure class="art-card" data-role="' + esc(c.role) + '" data-kind="讀取圖" data-big="' + esc(c.big) + '" data-name="' + esc(sText(c)) + '">' +
      '<img src="' + esc(c.img) + '" alt="' + esc(c.champ) + '" loading="lazy">' +
      '<span>' + esc(c.champ) + ' <small>' + esc(c.title) + '</small></span></figure>';
  }

  function cardAbility(c, a) {
    return '<article class="ability-card" data-role="' + esc(c.role) + '" data-slot="' + esc(a.k) + '" data-name="' + esc(sText(c, a.n + ' ' + a.k + ' ' + a.d)) + '">' +
      '<img src="' + esc(a.i) + '" alt="' + esc(a.n) + '" loading="lazy">' +
      '<div><small>' + esc(c.name) + ' · ' + esc(a.k) + '</small>' +
      '<b>' + esc(a.n) + '</b><p>' + esc(a.d) + '</p></div></article>';
  }

  function cardMap(m) {
    var gal = (m.gallery && m.gallery.length) ? '<div class="map-gal">' + m.gallery.map(function (g) {
      return '<button type="button" class="map-gal__item" data-big="' + esc(g.img) + '" data-name="' + esc(m.name + ' ' + g.name) + '">' +
        '<img src="' + esc(g.img) + '" alt="' + esc(g.name) + '" loading="lazy"><span>' + esc(g.name) + '</span></button>';
    }).join('') + '</div>' : '';
    return '<article class="map-card" data-map="' + esc(m.name) + '" data-name="' + esc(m.name + ' ' + m.sub + ' ' + (m.notes || []).join(' ')) + '"><div><img src="' + esc(m.img) + '" alt="' + esc(m.name) + '" loading="lazy"></div>' +
      '<div><h2>' + esc(m.name) + '</h2><small>' + esc(m.sub) + '</small><ul>' +
      m.notes.map(function (n) { return '<li>' + esc(n) + '</li>'; }).join('') + '</ul>' + gal + '</div></article>';
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
    return '<section class="rune-tree-block" data-tree="' + esc(t.name) + '" data-name="' + esc(t.name) + '"><div class="rune-tree-head">' +
      '<img src="' + esc(t.icon) + '" alt="' + esc(t.name) + '"><b>' + esc(t.name) + '</b></div>' + slots + '</section>';
  }

  function cardGear(it) {
    var tags = (it.tags || []).map(function (x) { return '<span class="tag">' + esc(x) + '</span>'; }).join('');
    var path = (it.from && it.from.length) ? '<p>合成：' + esc(it.from.join(' + ')) + '</p>' : '';
    return '<article class="gear-card" data-tags="' + esc((it.tags || []).join(' ')) + '" data-name="' + esc([it.name, it.en || '', it.desc, (it.tags || []).join(' ')].join(' ')) + '">' +
      '<img src="' + esc(it.icon) + '" alt="' + esc(it.name) + '" loading="lazy">' +
      '<div><b>' + esc(it.name) + '</b><span class="gold">' + it.gold + ' 金幣</span>' +
      '<p>' + esc(it.desc) + '</p>' + path + '<div class="tags">' + tags + '</div></div></article>';
  }

  function cardTactic(c) {
    var t = c.tactic || {};
    var tips = (t.tips || []).map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('');
    var enemy = (t.enemy || []).map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('');
    var weak = (t.weak || []).join('、'), strong = (t.strong || []).join('、');
    return '<article class="tac-card" data-role="' + esc(c.role) + '" data-diff="' + esc(c.diffLabel || '') + '" data-name="' + esc(sText(c, (c.tactic || {}).style)) + '">' +
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
        return '<div class="wall-card" data-kind="桌布" data-name="' + esc(w.name) + '"><img src="' + esc(w.img) + '" alt="' + esc(w.name) + '" loading="lazy">' +
          '<span>' + esc(w.name) + '<a class="ex-dl" href="' + esc(w.img) + '" download>下載</a></span></div>';
      }).join('');
      body.innerHTML = '<h3 style="margin:0 0 12px;color:#00d9ff;font-size:12px;letter-spacing:1.6px;">頁面桌布（1920×1080）</h3>' +
        '<div class="wall-row">' + walls + '</div>' +
        '<h3 style="margin:0 0 12px;color:#00d9ff;font-size:12px;letter-spacing:1.6px;">英雄讀取圖</h3>' +
        '<div class="art-wall">' + DATA.map(cardArt).join('') + '</div>';
      // 桌布卡與讀取圖卡都要能被「類型」篩選（兩者都有 data-name／data-kind）
      ITEMS = [].slice.call(document.querySelectorAll('#exBody [data-name]')).filter(function (el) {
        return !el.classList.contains('rune-card') && !el.classList.contains('map-gal__item');
      });
      apply(); return;
    }
    else if (MODE === 'abilities') body.innerHTML = DATA.map(function (c) { return c.ability.map(function (a) { return cardAbility(c, a); }).join(''); }).join('');
    else if (MODE === 'maps') body.innerHTML = DATA.map(cardMap).join('');
    else if (MODE === 'runes') body.innerHTML = DATA.map(cardRuneTree).join('');
    else if (MODE === 'gear') body.innerHTML = DATA.map(cardGear).join('');
    else if (MODE === 'tactics') body.innerHTML = DATA.map(cardTactic).join('');

    ITEMS = [].slice.call(body.querySelectorAll('[data-name]')).filter(function (el) {
      return !el.classList.contains('rune-card') && !el.classList.contains('map-gal__item');
    });
    apply();
  }

  function apply() {
    var raw = state.q || '';
    var q = raw.toLowerCase().trim();
    var shown = 0;

    var FLT = FILTERS[MODE];
    ITEMS.forEach(function (el) {
      var okRole = (state.role === '全部' || el.dataset.role === state.role || !el.dataset.role);
      var okSel = (state.sel === 'all' || !FLT || (el.getAttribute(FLT.attr) || '').indexOf(state.sel) >= 0);
      var okQ = !q || (el.dataset.name || '').toLowerCase().indexOf(q) >= 0;
      var on = okRole && okSel && okQ;
      el.hidden = !on;
      if (on) shown++;
    });

    if (MODE === 'skins') {           // 造型頁以「英雄區塊」為單位
      var blocks = document.querySelectorAll('.skin-champ');
      shown = 0;
      Array.prototype.forEach.call(blocks, function (b) {
        var okRole = (state.role === '全部' || b.dataset.role === state.role);
        var okQ = !q || (b.dataset.name || '').toLowerCase().indexOf(q) >= 0;
        var anyCard = false;                            // 這個英雄是否還有符合篩選的造型
        Array.prototype.forEach.call(b.querySelectorAll('.skin-card'), function (sc) { if (!sc.hidden) anyCard = true; });
        var on = okRole && okQ && anyCard;
        b.hidden = !on;
        if (on) shown++;
      });
    } else if (MODE === 'maps') {      // 地圖頁只算地圖卡，縮圖不算一筆
      shown = 0;
      Array.prototype.forEach.call(document.querySelectorAll('.map-card'), function (cd) {
        if (!cd.hidden) shown++;
      });
    } else if (MODE === 'runes') {     // 符文頁以「符文樹」為單位（樹內文字都算）
      var trees = document.querySelectorAll('.rune-tree-block');
      shown = 0;
      Array.prototype.forEach.call(trees, function (tr) {
        var okTree = (state.sel === 'all' || (tr.getAttribute('data-tree') || '') === state.sel);
        var ok = okTree && (!q || (tr.textContent || '').toLowerCase().indexOf(q) >= 0);
        tr.hidden = !ok;
        if (ok) shown++;
      });
    }

    var suffix = q ? '（關鍵字：' + raw.trim() + '）' : '';
    if (MODE === 'skins') $('exCount').textContent = '顯示 ' + shown + ' 位英雄的造型' + suffix;
    else if (MODE === 'runes') $('exCount').textContent = '顯示 ' + shown + ' 條符文樹（共 ' + DATA.length + ' 條）' + suffix;
    else if (MODE === 'maps') $('exCount').textContent = '顯示 ' + shown + ' / 共 ' + DATA.length + ' 張地圖' + suffix;
    else $('exCount').textContent = '顯示 ' + shown + ' 筆資料（共 ' + DATA.length + ' 筆）' + suffix;

    $('exEmpty').hidden = shown !== 0;
    var sbox = document.querySelector('.ex-searchbox');
    if (sbox) sbox.classList.toggle('has-query', !!raw.trim());
  }
  /* ------------------------------------------------------------------ 事件 */
  function bind() {
    var box = $('exSearch');
    function run() {
      state.q = box ? box.value : '';
      apply();
    }
    if (box) {
      box.addEventListener('input', run);                       // 打字即時篩選
      box.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') { e.preventDefault(); run(); focusFirst(); }
        if (e.key === 'Escape') { box.value = ''; run(); }
      });
    }
    if ($('exFind')) $('exFind').addEventListener('click', function () { run(); focusFirst(); });
    if ($('exReset')) $('exReset').addEventListener('click', function () {
      if (box) { box.value = ''; box.focus(); }
      state.q = '';
      apply();
    });
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

  // 按下搜尋後捲到第一筆結果，讓使用者馬上看到變化
  function focusFirst() {
    var list = document.querySelectorAll('#exBody [data-name]');
    for (var i = 0; i < list.length; i++) {
      if (!list[i].hidden) {
        if (list[i].scrollIntoView) list[i].scrollIntoView({ behavior: 'smooth', block: 'center' });
        return;
      }
    }
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
        renderAll();
        buildFilter();          // 下拉篩選的選項由剛渲染出來的資料自動產生
        bind();
        var sel = $('exSelect');
        if (sel) sel.addEventListener('change', function () { state.sel = sel.value; apply(); });
        // 切換語言時重建下拉選項（標籤要跟著翻），並保留原本的選擇
        window.addEventListener('lol:lang', function () {
          var box = $('exSelect');
          if (!box) return;
          var keep = box.value;
          buildFilter();
          if (keep) { box.value = keep; state.sel = keep; }
          apply();
        });
      })
      .catch(function (err) {
        $('exCount').textContent = '資料載入失敗：' + err.message;
      });
  });
})();
