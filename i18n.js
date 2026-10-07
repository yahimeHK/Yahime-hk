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
    '裝備合成': ['Item builder', 'アイテム合成', '아이템 조합'],
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
    '本站為靜態攻略資料庫，未串接 Riot API，不提供即時戰績或牌位查詢。': ['This is a static guide database. It does not use the Riot API and provides no live match or rank lookup.', '本サイトは静的な攻略データベースです。Riot API は使用しておらず、リアルタイムの戦績やランク検索は提供していません。', '이 사이트는 정적 공략 데이터베이스입니다. Riot API를 사용하지 않으며 실시간 전적이나 랭크 조회를 제공하지 않습니다.'],
    '© 2026 LOL 攻略站。LOL 攻略站是在 Riot Games 的「法律通則」方針下利用該公司擁有的資產所製作。Riot Games 不為此專案提供背書或贊助。': [
        '© 2026 LOL Guide Site. LOL Guide Site was created under Riot Games\' "Legal Jibber Jabber" policy using assets owned by Riot Games. Riot Games does not endorse or sponsor this project.',
        '© 2026 LOL 攻略サイト。LOL 攻略サイトは Riot Games の「Legal Jibber Jabber」ポリシーに基づき、Riot Games が所有するアセットを使用して制作されています。Riot Games は本プロジェクトを推奨または後援していません。',
        '© 2026 LOL 공략 사이트. LOL 공략 사이트는 Riot Games의 "Legal Jibber Jabber" 정책에 따라 Riot Games가 소유한 자산을 사용하여 제작되었습니다. Riot Games는 이 프로젝트를 보증하거나 후원하지 않습니다.'],
    '資料基於 Patch': ['Data patch', 'データパッチ', '데이터 패치'],
    '僅供遊戲參考': ['for reference only', '参考用', '참고용'],
    '非官方粉絲網站': ['unofficial fan site', '非公式ファンサイト', '비공식 팬 사이트'],
    // 各頁說明文字（由 build_extra.py 的 CFG 取出，key 一定對得上）
    '收錄每位英雄的官方造型縮圖（已排除炫彩），點一下可以到官方大圖。造型名稱、數量都跟著 Data Dragon 更新。': ['Browse official skin thumbnails for every champion (chromas excluded); click for the official splash art. Names and counts follow Data Dragon.', '全チャンピオンの公式スキン画像（クロマ除く）。クリックで公式スプラッシュアートへ。名前と数は Data Dragon に追従します。', '모든 챔피언의 공식 스킨 썸네일(크로마 제외). 클릭하면 공식 스플래시 아트로 이동합니다.'],
    '官方英雄讀取圖牆（loading art），加上四張分頁桌布。點圖可看較大版本或到官方大圖。': ['Official champion loading art plus four page wallpapers. Click an image for a larger version or the official splash art.', '公式チャンピオンロード画面と4枚の壁紙。クリックで拡大または公式スプラッシュアートへ。', '공식 챔피언 로딩 아트와 배경화면 4장. 클릭하면 크게 보거나 공식 스플래시 아트로 이동합니다.'],
    '全英雄的被動與 Q/W/E/R 圖示與官方技能說明，可用英雄、位置或技能名稱搜尋。': ['Passive and Q/W/E/R icons with official descriptions for every champion. Search by champion, role or ability name.', '全チャンピオンのパッシブと Q/W/E/R のアイコンと公式説明。チャンピオン・ロール・スキル名で検索できます。', '모든 챔피언의 패시브와 Q/W/E/R 아이콘 및 공식 설명. 챔피언·포지션·스킬 이름으로 검색하세요.'],
    '官方遊戲內地圖素材（小地圖與各地形變化）與戰術重點：目標時間、地形、視野，點縮圖可放大。': ['In-game map assets (minimaps and terrain variants) with tactical notes: objective timers, terrain and vision. Click a thumbnail to enlarge.', 'ゲーム内マップ素材（ミニマップと地形変化）と戦術ポイント：オブジェクト時間・地形・視界。クリックで拡大。', '게임 내 맵 자료(미니맵과 지형 변화)와 전술 포인트: 오브젝트 시간, 지형, 시야. 클릭하면 확대됩니다.'],
    '五條符文樹的完整符文清單：圖示、名稱與官方符文說明（shortDesc／longDesc）。': ['Every rune of the five trees: icon, name and the official description (shortDesc / longDesc).', '5つのルーツリーの全ルーン：アイコン・名前・公式説明（shortDesc / longDesc）。', '5개 룬 트리의 모든 룬: 아이콘, 이름, 공식 설명(shortDesc / longDesc).'],
    '可購買道具的圖示、價格、官方說明與合成路徑，可依類型或關鍵字篩選。': ['Icons, prices, official descriptions and build paths for purchasable items. Filter by type or keyword.', '購入可能アイテムのアイコン・価格・公式説明・合成経路。種類やキーワードで絞り込めます。', '구매 가능 아이템의 아이콘, 가격, 공식 설명, 조합 경로. 유형이나 키워드로 필터링하세요.'],
    '每位英雄的戰術解析：玩法定位、各位置重點、Riot 官方提示與站內整理的克制資料。': ['Tactical breakdown per champion: playstyle, role focus, official Riot tips and the site’s curated counter data.', 'チャンピオンごとの戦術分析：プレイスタイル・ロールの要点・公式ヒント・独自のカウンター情報。', '챔피언별 전술 분석: 플레이 스타일, 포지션 핵심, 라이엇 공식 팁, 사이트 자체 카운터 데이터.'],
    // 其他頁面說明文字
    '收錄 Riot Games 官方頻道的賽季動畫、英雄 spotlight 與賽事精華。點下面的小圖，就能把那支影片換到上面的主畫面播放。': ['Season cinematics, champion spotlights and esports highlights from Riot Games’ official channel. Click a thumbnail below to play it on the main screen above.', 'Riot Games 公式チャンネルのシーズンシネマティック・チャンピオンスポットライト・大会ハイライト。下のサムネイルをクリックすると上のメイン画面で再生されます。', '라이엇 공식 채널의 시즌 시네마틱, 챔피언 스포트라이트, 대회 하이라이트. 아래 썸네일을 클릭하면 위 메인 화면에서 재생됩니다.'],
    '先點一下播放器或把滑鼠移上去，快捷鍵才會生效：': ['Click the player or hover it first — then the shortcuts work:', 'プレイヤーをクリックするかマウスを乗せるとショートカットが有効になります：', '플레이어를 클릭하거나 마우스를 올려야 단축키가 작동합니다:'],
    '跳到百分比位置': ['Jump to a percentage', 'パーセント位置へ移動', '퍼센트 위치로 이동'],
    '以蒂瑪西亞為主題的官方動畫，揭開新賽季序幕。這張卡片搭載自訂播放器：可拖曳時間軸預覽、鍵盤快捷鍵、0.5×–2× 變速、子母畫面與全螢幕，並記住上次的觀看進度。': ['A Demacia-themed official cinematic opening the new season. This card has a custom player: draggable scrub preview, keyboard shortcuts, 0.5×–2× speed, picture-in-picture and fullscreen — and it remembers where you stopped.', 'デマーシアをテーマにした新シーズン開幕の公式シネマティック。カスタムプレイヤー（ドラッグ可能なシーク、キーボードショートカット、0.5×〜2× 速度、ピクチャインピクチャ、全画面、再生位置の記憶）付き。', '데마시아 테마의 신 시즌 개막 공식 시네마틱. 드래그 탐색, 키보드 단축키, 0.5×~2× 배속, PIP, 전체화면, 재생 위치 기억을 지원하는 커스텀 플레이어가 있습니다.'],
    '輸入你的對手英雄，網站會從站內整理的克制資料與定位／玩法標籤，整理出一組「對線思考方向」，並附上 LeagueOfGraphs 與 LaneLore 的即時對局連結，讓你在載入畫面時就建立下一場的思路。': ['Enter your lane opponent and the site builds a “laning game plan” from its curated counter data and role/playstyle tags, plus live matchup links from LeagueOfGraphs and LaneLore.', '対面チャンピオンを入力すると、サイト内のカウンター情報とロール／プレイスタイルから「レーニングの考え方」を整理し、LeagueOfGraphs と LaneLore の最新マッチアップへのリンクも表示します。', '상대 챔피언을 입력하면 사이트의 카운터 데이터와 포지션/플레이스타일 태그로 “라인전 사고 방향”을 정리하고 LeagueOfGraphs·LaneLore 실시간 링크를 함께 보여줍니다.'],
    '選一個你現在最想修練的方向、輸入數量，系統會即時試算金額並發放數位序號。滿 1000 RP 另外解鎖 AI 加贈的『峽谷心理戰小冊』。': ['Pick the area you most want to improve and set a quantity — the total is calculated instantly and a digital code is issued. Orders of 1000 RP or more also unlock the bonus booklet.', '伸ばしたい分野を選んで数量を入力すると、金額を即時計算してデジタルコードを発行します。1000 RP 以上で特典冊子も解放。', '키우고 싶은 분야를 고르고 수량을 입력하면 금액이 즉시 계산되고 디지털 코드가 발급됩니다. 1000 RP 이상은 보너스 소책자도 해금됩니다.'],
    '改數量、換貨物，總額與滿額進度條立刻跟著變，不用按任何按鈕。': ['Change the quantity or the item — the total and the progress bar update instantly, no button needed.', '数量や商品を変えると、合計と進捗バーが即座に更新されます（ボタン不要）。', '수량이나 상품을 바꾸면 합계와 진행 바가 즉시 바뀝니다(버튼 불필요).'],
    '總額滿 1000 RP 就贈送『峽谷心理戰小冊』，序號會一起給你。': ['Reach 1000 RP and the bonus booklet unlocks — the code is included.', '合計 1000 RP で特典冊子が解放され、コードも一緒に発行されます。', '합계 1000 RP를 넘기면 보너스 소책자가 해금되고 코드도 함께 제공됩니다.'],
    '所有計算都在你的瀏覽器完成，不會送出任何資料，離線也能用。': ['All calculation happens in your browser — nothing is sent anywhere, and it works offline.', '計算はすべてブラウザ内で完結し、データは送信されません。オフラインでも使えます。', '모든 계산은 브라우저에서 이루어지며 아무 데이터도 전송되지 않습니다. 오프라인에서도 동작합니다.'],
    '下單前先看幾篇，挑一個最符合你現在瓶頸的方向。': ['Read a few before ordering, and pick the one that fits your current bottleneck.', '注文前にいくつか読んで、今の課題に合うものを選びましょう。', '주문 전에 몇 편 읽고 지금 병목에 맞는 방향을 고르세요.'],
    '再購買 500 RP 即可獲得贈品！': ['Buy 500 RP more to unlock the bonus!', 'あと 500 RP で特典が解放されます！', '500 RP만 더 구매하면 보너스가 해금됩니다!'],
    '巴龍 Buff 團戰全攻略包': ['Baron Buff teamfight pack', 'バロンバフ集団戦パック', '바론 버프 한타 팩'],
    '菁英級走位與對線技巧講義': ['Elite positioning & laning guide', 'エリート級の立ち回りとレーニング講義', '엘리트 위치 선정·라인전 강의'],
    '野區開局與高效 Gank 路線圖': ['Jungle pathing & efficient gank map', 'ジャングル開幕と効率的ガンクの地図', '정글 초반 동선과 효율 갱킹 지도'],
    '從集結、視野到巴龍爭奪的完整時間軸，含 5 種逆風開團腳本。': ['A full timeline from grouping and vision to Baron fights, with five comeback engage scripts.', '集結・視界からバロン争奪までの完全タイムライン。逆転用のエンゲージ台本 5 種付き。', '집결·시야부터 바론 싸움까지의 전체 타임라인, 역전 이니시 5가지 포함.'],
    '換血節奏、兵線控制與走位細節，用圖解拆給你看。': ['Trade patterns, wave control and positioning details explained with diagrams.', 'トレードのテンポ・ウェーブ管理・立ち位置の詳細を図解で解説。', '딜교 템포, 웨이브 관리, 위치 선정 디테일을 그림으로 설명.'],
    '三種開局路線、河蟹與預示者的取捨，跟著地圖走就對了。': ['Three opening routes plus how to choose between scuttle and Herald — just follow the map.', '3つの開幕ルートとカニ・ヘラルドの取捨選択。マップ通りに動けばOK。', '세 가지 초반 동선과 강 crab·전령 선택 기준을 지도로 정리.'],
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
    '推薦文摘': ['AI reading picks', 'AI おすすめ記事', 'AI 추천 글'],
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
