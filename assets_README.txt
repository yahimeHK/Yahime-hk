LOL攻略站 V6.0｜完全離線版素材

本版本所有主頁背景素材均已放在 assets/，開啟 index.html 時不需要網絡。

assets/home-bg.jpg
- 主頁背景圖

assets/home-bg.mp4
- 本機背景影片（MP4）
- 12 秒循環、靜音、自動播放
- 由本機背景視覺製作，避免網站依賴 YouTube / 外部 CDN

assets/home-bottom.jpg
- 首頁底部大型主視覺

注意：上一版使用 Riot/YouTube 外部素材；因目前執行環境無法直接取得外網二進位檔案，今次離線包改用本機素材，確保真正斷網都能開啟。Riot Data Dragon 官方文件確認 Champion Splash Assets 可供第三方開發者使用；如日後你想換回指定 Riot 官方圖片，可把對應圖片下載後覆蓋上述 JPG。

=== V5.1 追加說明（現為 V6.0）===

首頁「官方影片精選」主打開幕動畫卡片已改用自訂播放器（player.js / player.css）：
- 可拖曳時間軸並即時預覽時間、鍵盤快捷鍵（Space、←→、J/L、↑↓、M、F、0–9）
- 0.5×–2× 變速、子母畫面、全螢幕、記住上次觀看進度
- 播放器樣式全部收在 .salvation-player 之內，不會影響攻略站原有版面

以下三個 MP4 已隨這個 repo 一起上傳（合計約 63 MB），開啟網站即可直接播放：

assets/assetsvideo1.mp4
- 《救贖》開幕動畫，640×272、4:54，約 20.6 MB
assets/assetsvideo2.mp4
- Worlds 2026 主題曲，約 8.5 MB
assets/assetsvideo3.mp4
- 英雄 Spotlight 精選，約 33.9 MB

本機開發時，在本資料夾執行以下其中一種即可觀看：
- 雙擊 start.bat（會自動開瀏覽器）
- python serve.py 然後開 http://127.0.0.1:8099/

serve.py 是本機靜態伺服器，會回應 byte range（206 Partial Content）；
少了它（例如用 python -m http.server）拖曳時間軸會卡住，因為瀏覽器需要
分段請求才能 seek。直接以 file:// 開啟時，播放器也會自行提示這個限制。

=== 16.20.1 追加：裝備攻略頁的圖片素材 ===

assets/lol/ 內的圖片全部由 Riot Data Dragon 16.20.1（zh_TW）下載後存到本機，
所以裝備攻略頁（items.html）離線也能正常顯示，不會像以前連外失敗就整頁變純文字。

assets/lol/champ/    英雄頭像（20 張）
assets/lol/ability/  被動與 Q/W/E/R 技能圖示（100 張）
assets/lol/item/     核心裝備圖示（47 張）
assets/lol/rune/     符文樹與基石圖示（13 張）

要更新到最新版本時，在專案根目錄執行：
    python _build_items.py
它會抓最新版本的 Data Dragon 資料與圖片，重新產生 items.html 與 items.css。
（英雄清單、建議符文與核心裝備的配置寫在 _build_items.py 最上面的 CHAMPS 清單裡。）

=== V6.0 ===

版本號更新為 V6.0，並補強各裝置（手機／平板／桌機／超寬螢幕）的顯示：
- 瀏海安全區（viewport-fit=cover + safe-area-inset）
- 平板直立時背景圖改用 scroll（避免行動瀏覽器 fixed 背景異常）
- 手機／小手機（<=700 / <=400）版面、彈窗、卡片與按鈕尺寸調整
- 橫向手機（高度 <=520）縮短首頁高度
- 觸控裝置取消 hover 位移效果
- 超寬螢幕（>=1600）內容寬度由 1200 放大到 1320

=== V6.0 自動更新 ===

tools/ 內放的是產生器（可重複執行、跟著 Riot 官方資料更新）：

tools/build_champions.py   重新產生英雄資料庫：champions.html、champions-db.css/js、assets/lol/champions.json
                           （173 位英雄的頭像、被動與 Q/W/E/R 技能圖示＋簡介、位置、建議符文＋符文說明、
                             核心裝備、戰術解析，以及 LeagueOfGraphs／LaneLore 即時數據連結）
tools/build_items.py       重新產生裝備攻略：items.html、items.css（20 位英雄的完整攻略卡）
tools/fetch_backgrounds.py 重新下載四個分頁的背景美術（需要 Pillow）
tools/check_site.py        整站檢查（頁面、素材、參照、CSS 作用域、JS 語法、影片規格）

自動更新方式（Windows 排程工作）：
- 「LOL 攻略站 更新資料」每週一 09:00 執行 tools/update-lol-data.ps1，重新產生上面兩個頁面
- 「LOL 攻略站 自動推送」每 5 分鐘檢查變更，有變更就 commit + push，GitHub Pages 約 1 分鐘後更新
- 也可以雙擊桌面上的「立即更新資料.bat」手動更新
- 記錄檔：%LOCALAPPDATA%\LOLGuideAutoPush\update-data.log（更新）與 auto-push.log（推送）

=== V6.0 七個分類分頁 ===

由 tools/build_extra.py 產生（可重複執行，跟著 Data Dragon 更新）：

skins.html      角色造型：172 位英雄、996 張造型縮圖（已排除炫彩，每位最多 6 個）→ assets/lol/skin/
gallery.html    圖片：173 張官方讀取圖牆 + 4 張頁面桌布（可下載）→ assets/lol/art/
abilities.html  技能圖片及簡介：865 個被動與 Q/W/E/R（圖示＋官方說明）
maps.html       地圖：召喚峽谷／嚎哭深淵等素材與地圖重點 → assets/lol/map/
runes.html      符文＋符文簡介：5 條符文樹、62 個符文（shortDesc／longDesc）
gear.html       核心裝備：402 件可購買道具（圖示、價格、官方說明、合成路徑）→ assets/lol/gear/
tactics.html    戰術解析：173 位英雄的玩法定位、位置重點、Riot 官方提示與克制資料

共用檔案：
  nav.js      分類導覽列（注入在 topbar 之後，所有頁面共用，會標記目前頁面）
  extra.css   七個分頁的樣式
  extra.js    七個分頁的前端（依 <main data-page="…"> 決定載入哪個 JSON）
  assets/lol/{skins,gallery,maps,runes,gear}.json  各分頁的資料

造型縮圖（144px）與讀取圖（260px 寬）由 Pillow 縮小後才存入 assets，原始大圖只留在快取，
所以 2,737 張圖片總共只有約 27 MB。