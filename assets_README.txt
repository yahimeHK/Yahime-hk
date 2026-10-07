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
