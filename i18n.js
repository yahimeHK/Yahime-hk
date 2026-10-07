/* ==========================================================================
   LOL 攻略站 — 語系切換（中文 / English / 日本語 / 한국어）
   --------------------------------------------------------------------------
   * 右上角新增 🌐 按鈕，可即時切換四種語言（存在 localStorage：lolLang）
   * 作法是「原地替換文字」：以中文原文為 key 對照譯文，
     所以不需要改動任何既有頁面與產生器，動態產生的卡片也能一起翻譯
   * 只翻譯介面文字（導覽、標題、按鈕、欄位、提示）；英雄／技能等資料內容
     仍以 Riot 官方繁中資料為準，選單內有註明
   * 用 MutationObserver 追蹤之後才渲染出來的內容（延遲 200ms 批次處理）
   ========================================================================== */
(function () {
  'use strict';

  var LANGS = [
    { code: 'zh-Hant', label: '中文', short: '中' },
    { code: 'en', label: 'English', short: 'EN' },
    { code: 'ja', label: '日本語', short: '日' },
    { code: 'ko', label: '한국어', short: '한' }
  ];
  var KEY = 'lolLang';

  // 以中文原文為 key： [en, ja, ko]
  var DICT = {
    // 導覽
    '首頁': ['Home', 'ホーム', '홈'],
    '英雄攻略': ['Champions', 'チャンピオン', '챔피언'],
    '裝備攻略': ['Items', 'アイテム', '아이템'],
    '戰術商城': ['Tactics', 'タクティクス', '전술'],
    '分類資料庫': ['Categories', 'カテゴリ', '카테고리'],
    '角色造型': ['Skins', 'スキン', '스킨'],
    '圖片': ['Art', 'アート', '아트'],
    '技能圖片': ['Abilities', 'スキル', '스킬'],
    '地圖': ['Maps', 'マップ', '맵'],
    '符文': ['Runes', 'ルーン', '룬'],
    '核心裝備': ['Core Items', 'コアアイテム', '핵심 아이템'],
    '戰術解析': ['Tactics', '戦術分析', '전술 분석'],
    // 通用
    '搜尋': ['Search', '検索', '검색'],
    '清除篩選': ['Clear filters', 'フィルター解除', '필터 초기화'],
    '全部職業': ['All classes', 'すべてのクラス', '모든 클래스'],
    '全部難度': ['All difficulties', 'すべての難易度', '모든 난이도'],
    '全部類型': ['All types', 'すべての種類', '모든 유형'],
    '全部技能': ['All abilities', 'すべてのスキル', '모든 스킬'],
    '全部地圖': ['All maps', 'すべてのマップ', '모든 맵'],
    '全部符文樹': ['All trees', 'すべてのツリー', '모든 룬 트리'],
    '全部造型系列': ['All skin lines', 'すべてのスキンシリーズ', '모든 스킨 시리즈'],
    '全部英雄': ['All champions', 'すべてのチャンピオン', '모든 챔피언'],
    '技能圖示與簡介': ['Abilities & descriptions', 'スキルと説明', '스킬 및 설명'],
    '建議符文': ['Recommended runes', 'おすすめルーン', '추천 룬'],
    '核心裝備': ['Core items', 'コアアイテム', '핵심 아이템'],
    '即時數據 ＆ 更多資料': ['Live stats & more', 'リアルタイム數據と詳細', '실시간 데이터 및 더 보기'],
    '玩家常用稱呼': ['Common nicknames', 'よく使われる呼称', '자주 쓰는 별칭'],
    '完整攻略 →': ['Full guide →', '詳しい攻略 →', '전체 공략 →'],
    '符文 ＆ 核心裝備 數據庫': ['Runes & Core Items Database', 'ルーン＆コアアイテム図鑑', '룬 & 핵심 아이템 데이터베이스'],
    '深度攻略卡': ['In-depth guides', '詳細ガイド', '심층 공략 카드'],
    '英雄資料庫': ['Champion Database', 'チャンピオン図鑑', '챔피언 도감'],
    '難度：簡單': ['Difficulty: Easy', '難易度：やさしい', '난이도: 쉬움'],
    '難度：中等': ['Difficulty: Medium', '難易度：ふつう', '난이도: 보통'],
    '難度：困難': ['Difficulty: Hard', '難易度：むずかしい', '난이도: 어려움'],
    '被動': ['Passive', 'パッシブ', '패시브'],
    '簡單': ['Easy', 'やさしい', '쉬움'],
    '中等': ['Medium', 'ふつう', '보통'],
    '困難': ['Hard', 'むずかしい', '어려움'],
    '上路': ['Top', 'トップ', '탑'],
    '打野': ['Jungle', 'ジャングル', '정글'],
    '中路': ['Mid', 'ミッド', '미드'],
    '下路': ['Bottom', 'ボット', '바텀'],
    '輔助': ['Support', 'サポート', '서포터'],
    '刺客': ['Assassin', 'アサシン', '암살자'],
    '鬥士': ['Fighter', 'ファイター', '전사'],
    '法師': ['Mage', 'メイジ', '마법사'],
    '射手': ['Marksman', 'マークスマン', '원거리 딜러'],
    '坦克': ['Tank', 'タンク', '탱커'],
    '全部': ['All', 'すべて', '전체'],
    // 首頁
    '完整 LOL 攻略資料庫': ['Complete LOL Guide Database', 'LOL 完全攻略データベース', 'LOL 완전 공략 데이터베이스'],
    '由對線到團戰 一站掌握': ['From laning to teamfights, all in one place', 'レーン戦からチームファイトまで', '라인전부터 한타까지 한 곳에서'],
    '瀏覽英雄資料庫': ['Browse champions', 'チャンピオン図鑑を見る', '챔피언 도감 보기'],
    '隨機英雄': ['Random champion', 'ランダムチャンピオン', '랜덤 챔피언'],
    '173 位英雄': ['173 champions', '173 チャンピオン', '챔피언 173명'],
    '5 條路線': ['5 roles', '5 ロール', '5개 포지션'],
    '6 種英雄類型': ['6 classes', '6 クラス', '6개 클래스'],
    '12 種玩法方向': ['12 playstyle builds', '12 のビルド方向', '12가지 빌드 방향'],
    '英雄總數': ['Champions', 'チャンピオン数', '챔피언 수'],
    '最新版本 (Patch)': ['Latest patch', '最新パッチ', '최신 패치'],
    '離線運行支援': ['Works offline', 'オフライン対応', '오프라인 지원'],
    '官方影片精選': ['Official videos', '公式動画', '공식 영상'],
    '現正播放': ['Now playing', '再生中', '재생 중'],
    '主畫面播放中': ['Playing on main screen', 'メイン画面で再生中', '메인 화면 재생 중'],
    '核心對線': ['Matchup lab', 'マッチアップラボ', '맞라인 연구소'],
    '前往戰術商城與分析 ⚔': ['Open tactics store ⚔', 'タクティクスへ ⚔', '전술 상점으로 ⚔'],
    // 提示
    '技能圖片及簡介': ['Abilities & descriptions', 'スキルと説明', '스킬 및 설명'],
    '完整攻略卡': ['Full guide cards', '詳細ガイドカード', '전체 공략 카드'],
    '沒有符合條件的英雄，換個條件試試。': ['No champions match these filters.', '条件に合うチャンピオンがありません。', '조건에 맞는 챔피언이 없습니다.'],
    '沒有符合條件的資料。': ['No matching data.', '該当するデータがありません。', '조건에 맞는 데이터가 없습니다.'],
    '技能加點 ＆ 召喚師技能': ['Skill order & summoner spells', 'スキルオーダーとサモナースペル', '스킬 순서 & 소환사 주문'],
    '📊 LeagueOfGraphs 符文勝率': ['📊 LeagueOfGraphs runes', '📊 LeagueOfGraphs ルーン', '📊 LeagueOfGraphs 룬'],
    '⚔ LeagueOfGraphs 對局': ['⚔ LeagueOfGraphs matchups', '⚔ LeagueOfGraphs 対面', '⚔ LeagueOfGraphs 상대'],
    '🧭 LaneLore 出裝與符文': ['🧭 LaneLore builds & runes', '🧭 LaneLore ビルドとルーン', '🧭 LaneLore 빌드 & 룬'],
    '📚 站內：克制／稱呼／技能': ['📚 In-site: counters / nicknames / skills', '📚 サイト内：カウンター／呼称／スキル', '📚 사이트 내: 카운터/별칭/스킬'],
    '版本玩法方向盤': ['Playstyle compass', 'プレイスタイル方位盤', '플레이스타일 나침반'],
    '符文資料': ['Rune data', 'ルーンデータ', '룬 데이터'],
    '裝備資料': ['Item data', 'アイテムデータ', '아이템 데이터'],
    '技能資料': ['Ability data', 'スキルデータ', '스킬 데이터'],
    'Counter資料': ['Counter data', 'カウンターデータ', '카운터 데이터'],
    '🧾 結帳試算': ['🧾 Checkout estimate', '🧾 会計シミュレーション', '🧾 결제 계산'],
    '⚡ 立即試算總金額': ['⚡ Calculate total', '⚡ 合計を計算', '⚡ 총액 계산'],
    '閱讀摘要': ['Read summary', '要約を読む', '요약 읽기'],
    '新手': ['Beginner', '初心者', '초보'],
    '團戰': ['Teamfight', 'チームファイト', '한타'],
    '頁面桌布（1920×1080）': ['Page wallpapers (1920×1080)', 'ページ壁紙（1920×1080）', '페이지 배경화면 (1920×1080)'],
    '下載': ['Download', 'ダウンロード', '다운로드'],
    '英雄讀取圖': ['Champion loading art', 'チャンピオン読込画像', '챔피언 로딩 아트'],
    'AI 推薦文摘': ['AI reading picks', 'AI おすすめ記事', 'AI 추천 글'],
    '對線重點': ['Laning notes', 'レーニングの要点', '라인전 포인트'],
    '玩法定位': ['Playstyle', 'プレイスタイル', '플레이 스타일'],
    '賽季核心數據': ['Season stats', 'シーズン統計', '시즌 통계'],
    '官方影片精選': ['Official videos', '公式動画', '공식 영상'],
    '瀏覽英雄資料庫': ['Browse champions', 'チャンピオン図鑑を見る', '챔피언 도감 보기'],
    '前往戰術商城與分析': ['Open tactics store', 'タクティクスへ', '전술 상점으로'],
    '現正播放': ['Now playing', '再生中', '재생 중'],
    '主畫面播放中': ['Playing on main screen', 'メイン画面で再生中', '메인 화면 재생 중'],
    '資料說明：': ['About the data: ', 'データについて：', '데이터 안내: '],
    '僅供參考': ['for reference only', '参考用', '참고용'],
    '資料基於 Patch': ['Data patch', 'データパッチ', '데이터 패치']
  };

  // 有數字的句子用規則處理
  var RULES = [
    [/^(\d+)\s*個技能$/, ['$1 abilities', '$1 スキル', '스킬 $1개']],
    [/^(\d+)\s*張造型縮圖$/, ['$1 skin thumbnails', 'スキン画像 $1 枚', '스킨 썸네일 $1개']],
    [/^(\d+)\s*張讀取圖$/, ['$1 loading art', 'ロード画面 $1 枚', '로딩 아트 $1개']],
    [/^(\d+)\s*件道具$/, ['$1 items', 'アイテム $1 点', '아이템 $1개']],
    [/^(\d+)\s*個符文$/, ['$1 runes', 'ルーン $1 個', '룬 $1개']],
    [/^(\d+)\s*條符文樹$/, ['$1 rune trees', 'ルーンツリー $1 本', '룬 트리 $1개']],
    [/^(\d+)\s*張地圖$/, ['$1 maps', 'マップ $1 枚', '맵 $1개']],
    [/^(\d+)\s*個技能圖示$/, ['$1 ability icons', 'スキルアイコン $1 個', '스킬 아이콘 $1개']],
    [/^(\d+)\s*件核心裝備$/, ['$1 core items', 'コアアイテム $1 点', '핵심 아이템 $1개']],
    [/^顯示\s*(\d+)\s*個技能（共\s*(\d+)\s*個）$/, ['Showing $1 of $2 abilities', '$2 スキル中 $1 を表示', '$2개 중 $1개 스킬 표시']],
    [/^…其餘\s*(\d+)\s*項請用搜尋$/, ['…$1 more — use search', '…残り $1 件は検索してください', '…나머지 $1개는 검색하세요']],
    [/^共\s*(\d+)\s*筆$/, ['$1 entries', '$1 件', '$1개']],
    [/顯示\s*(\d+)\s*位英雄（共\s*(\d+)\s*位）/, ['Showing $1 of $2 champions', '$2 人中 $1 人を表示', '$2명 중 $1명 표시']],
    [/顯示\s*(\d+)\s*位英雄的造型/, ['Showing skins for $1 champions', '$1 チャンピオンのスキンを表示', '$1명 챔피언의 스킨 표시']],
    [/顯示\s*(\d+)\s*筆資料（共\s*(\d+)\s*筆）/, ['Showing $1 of $2 entries', '$2 件中 $1 件を表示', '$2개 중 $1개 표시']],
    [/顯示\s*(\d+)\s*條符文樹（共\s*(\d+)\s*條）/, ['Showing $1 of $2 rune trees', '$2 ツリー中 $1 ツリーを表示', '$2개 중 $1개 룬 트리 표시']],
    [/顯示\s*(\d+)\s*\/\s*共\s*(\d+)\s*張地圖/, ['Showing $1 of $2 maps', '$2 マップ中 $1 を表示', '$2개 중 $1개 맵 표시']],
    [/顯示\s*(\d+)\s*筆資料/, ['Showing $1 entries', '$1 件を表示', '$1개 표시']],
    [/顯示\s*(\d+)\s*位英雄/, ['Showing $1 champions', '$1 チャンピオンを表示', '$1명 챔피언 표시']],
    [/共\s*(\d+)\s*張地圖/, ['$1 maps', '$1 マップ', '$1개 맵']],
    [/（關鍵字：([^）]*)）/, [' (keyword: $1)', '（キーワード：$1）', ' (검색어: $1)']],
    [/符合條件的英雄：/, ['Matching champions: ', '該当チャンピオン：', '조건에 맞는 챔피언: ']]
  ];

  var lang = 'zh-Hant';
  try { lang = localStorage.getItem(KEY) || 'zh-Hant'; } catch (e) { /* 無痕模式 */ }
  var idxOf = function (code) {
    for (var i = 0; i < LANGS.length; i++) if (LANGS[i].code === code) return i;
    return 0;
  };
  var LI = idxOf(lang);

  // 結尾的表情符號／箭頭等在翻譯時忽略（例：「瀏覽英雄資料庫 🎲」→ 以「瀏覽英雄資料庫」查表）
  var TAIL = /[\s\u2000-\u2BFF\u2190-\u21FF\u2600-\u27BF\uFE0F\uD800-\uDFFF]+$/;

  function stripTail(s) {
    return String(s || '').replace(TAIL, '').trim();
  }

  // 建立查表：原文與「去掉結尾符號」的版本都能查到
  var LOOKUP = {};
  Object.keys(DICT).forEach(function (k) {
    LOOKUP[k] = DICT[k];
    var core = stripTail(k);
    if (core && !LOOKUP[core]) LOOKUP[core] = DICT[k];
  });

  /* ---------------- 資料內容對照（英雄／技能／符文／裝備…） ---------------- */
  var dataMaps = {};        // code -> { 中文原文: 譯文 }
  var dataQueues = {};      // code -> [callback]

  function dataMap() {
    return dataMaps[lang] || {};
  }

  function dataHit(key) {
    var m = dataMap();
    return m[key] || m[stripTail(key)] || null;
  }

  function ensureData(code, done) {
    if (code === 'zh-Hant' || dataMaps[code]) { done(); return; }
    if (dataQueues[code]) { dataQueues[code].push(done); return; }
    dataQueues[code] = [done];
    var finish = function () {
      var list = dataQueues[code] || [];
      delete dataQueues[code];
      list.forEach(function (f) { try { f(); } catch (e) { /* 忽略 */ } });
    };
    fetch('assets/lol/i18n-' + code + '.json')
      .then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
      .then(function (d) { dataMaps[code] = d.map || {}; finish(); })
      ['catch'](function () { finish(); });          // 讀不到就用原文
  }

  function t(key) {
    var hit = LOOKUP[key] || LOOKUP[stripTail(key)] || dataHit(key);
    if (LI === 0 || !hit) return key;
    return hit[LI - 1] || key;
  }

  /* ---------------------------------------------------------------- 翻譯引擎 */
  var originals = new WeakMap();          // 節點 → 原文（切回中文時用）
  var SKIP = { SCRIPT: 1, STYLE: 1, NOSCRIPT: 1, TEXTAREA: 1, CODE: 1, PRE: 1 };

  function translateText(node) {
    if (!node || !node.nodeValue) return;
    var raw = originals.has(node) ? originals.get(node) : node.nodeValue;
    var key = raw.trim();
    if (!key) return;
    var out = null;
    var core = stripTail(key);
    var hit = LOOKUP[key] || (core !== key ? LOOKUP[core] : null) || dataHit(key);
    // DICT 是四語陣列、資料對照是單一譯文字串，這裡要分開處理
    var target = Array.isArray(hit) ? (hit[LI - 1] || null) : hit;
    if (LI === 0) {
      out = raw;
    } else if (target) {
      out = raw.replace(core || key, target);
    } else if (hit) {
      out = raw;                                  // 有對照但該語言沒有譯文，保持原文
    } else if (key.indexOf(' · ') > 0) {
      // 「英雄名 · 技能」／「稱號 · 位置」這類組合字串：每一段都查得到才翻譯
      var parts = key.split(' · ');
      var tr = [];
      var all = true;
      parts.forEach(function (p2) {
        var d1 = DICT[p2] ? DICT[p2][LI - 1] : null;
        var d2 = dataHit(p2);
        var v = d1 || d2;
        if (!v && !/^[A-Za-z0-9]+$/.test(p2)) all = false;   // Q/W/E/R 這種本來就是英文，允許直接沿用
        tr.push(v || p2);
      });
      if (all) out = raw.replace(key, tr.join(' · '));
    } else {
      for (var i = 0; i < RULES.length; i++) {
        var m = RULES[i][0].exec(key);
        if (m) {
          out = key.replace(RULES[i][0], RULES[i][1][LI - 1]);
          break;
        }
      }
    }
    if (out === null) return;
    if (!originals.has(node)) originals.set(node, raw);
    if (node.nodeValue !== out) node.nodeValue = out;
  }

  function walk(root) {
    if (!root) return;
    var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
      acceptNode: function (n) {
        if (n.parentNode && SKIP[n.parentNode.nodeName]) return NodeFilter.FILTER_REJECT;
        return NodeFilter.FILTER_ACCEPT;
      }
    });
    var nodes = [], n;
    while ((n = walker.nextNode())) nodes.push(n);
    nodes.forEach(translateText);
    // 屬性（placeholder / title / aria-label）
    var attrs = ['placeholder', 'title', 'aria-label'];
    var els = root.querySelectorAll ? root.querySelectorAll('[placeholder],[title],[aria-label]') : [];
    Array.prototype.forEach.call(els, function (el) {
      attrs.forEach(function (a) {
        var v = el.getAttribute(a);
        if (!v) return;
        // 注意：dataset 的 key 不能含連字號（aria-label 會丟錯），所以用一般屬性保存原文
        if (!el._i18nOrig) el._i18nOrig = {};
        if (!el._i18nOrig[a]) el._i18nOrig[a] = v;
        var orig = el._i18nOrig[a];
        var ok = LOOKUP[orig.trim()] || LOOKUP[stripTail(orig)] || dataHit(orig.trim());
        var okTarget = Array.isArray(ok) ? (ok[LI - 1] || null) : ok;
        var out = LI === 0 ? orig : okTarget;
        if (out && v !== out) el.setAttribute(a, out);
      });
    });
  }

  var timer = null;
  function schedule() {
    if (timer) return;
    timer = window.setTimeout(function () { timer = null; walk(document.body); }, 200);
  }

  /* ------------------------------------------------------------------ 介面 */
  var CSS = [
    '.lang{position:relative}',
    '.lang__menu{position:absolute;right:0;top:calc(100% + 8px);min-width:190px;padding:8px;z-index:60;',
    'background:#0b131b;border:1px solid #31505f;border-radius:12px;box-shadow:0 18px 40px -18px #000;display:none}',
    '.lang.open .lang__menu{display:block}',
    '.lang__menu button{display:block;width:100%;padding:8px 10px;text-align:left;font-size:13px;color:#cfd8de;',
    'background:none;border:0;border-radius:8px;cursor:pointer}',
    '.lang__menu button:hover{background:#111d26;color:#fff}',
    '.lang__menu button[aria-current="true"]{background:rgba(200,170,110,.16);color:#e8cf9c;font-weight:800}',
    '.lang__menu small{display:block;margin:6px 4px 2px;font-size:11px;line-height:1.5;color:#6f7c86}',
    '.lang__now{font-size:12px;font-weight:800;letter-spacing:.5px}'
  ].join('');

  function injectCss() {
    if (document.getElementById('lol-lang-style')) return;
    var st = document.createElement('style');
    st.id = 'lol-lang-style';
    st.textContent = CSS;
    document.head.appendChild(st);
  }

  function applyChrome() {
    var box = document.getElementById('langBtn');
    if (box) {
      var now = box.querySelector('.lang__now');
      if (now) now.textContent = LANGS[LI].short;
      box.setAttribute('title', t('語言') + '：' + LANGS[LI].label);
      Array.prototype.forEach.call(box.querySelectorAll('.lang__menu button[data-code]'), function (b) {
        b.setAttribute('aria-current', b.dataset.code === LANGS[LI].code ? 'true' : 'false');
      });
      var note = box.querySelector('.lang__menu small');
      if (note) note.textContent = ['資料內容（英雄、技能、符文等）以 Riot 官方繁中資料為準。',
        'Champion, ability and rune text stays in Traditional Chinese (Riot official data).',
        'チャンピオン・スキル・ルーンなどのデータは公式の繁体字中国語のままです。',
        '챔피언·스킬·룬 등의 데이터는 라이엇 공식 번체 중국어로 표시됩니다.'][LI];
    }
    document.documentElement.setAttribute('lang', LANGS[LI].code === 'zh-Hant' ? 'zh-Hant' : LANGS[LI].code);
  }

  function setLang(code) {
    LI = idxOf(code);
    lang = LANGS[LI].code;
    try { localStorage.setItem(KEY, lang); } catch (e) { /* 無痕模式 */ }
    walk(document.body);                       // 先翻介面（立即見效）
    applyChrome();
    window.dispatchEvent(new CustomEvent('lol:lang', { detail: { lang: lang } }));
    ensureData(lang, function () {             // 資料對照載入後再翻一次內容
      if (LANGS[LI].code === lang) {
        walk(document.body);
        applyChrome();
      }
    });
  }

  function build() {
    var top = document.querySelector('.topbar');
    var theme = document.getElementById('themeBtn');
    if (!top || !theme || document.getElementById('langBtn')) return;
    injectCss();

    var box = document.createElement('div');
    box.className = 'lang';
    box.id = 'langBtn';
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'icon-btn';
    btn.setAttribute('aria-haspopup', 'true');
    btn.innerHTML = '🌐 <span class="lang__now"></span>';
    var menu = document.createElement('div');
    menu.className = 'lang__menu';
    menu.setAttribute('role', 'menu');
    LANGS.forEach(function (l) {
      var b = document.createElement('button');
      b.type = 'button';
      b.dataset.code = l.code;
      b.setAttribute('role', 'menuitem');
      b.textContent = l.label;
      b.addEventListener('click', function () { setLang(l.code); box.classList.remove('open'); });
      menu.appendChild(b);
    });
    var note = document.createElement('small');
    menu.appendChild(note);
    box.appendChild(btn);
    box.appendChild(menu);
    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      box.classList.toggle('open');
    });
    document.addEventListener('click', function () { box.classList.remove('open'); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') box.classList.remove('open'); });

    theme.parentNode.insertBefore(box, theme);
    walk(document.body);
    applyChrome();
  }

  window.LOLi18n = {
    get lang() { return lang; },
    set: setLang,
    t: t,
    langs: LANGS
  };

  function init() {
    build();
    if (LI !== 0) ensureData(lang, function () { walk(document.body); });
    new MutationObserver(schedule).observe(document.body, { childList: true, subtree: true, characterData: true });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
