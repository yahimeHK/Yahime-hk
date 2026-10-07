LOL攻略站 V4｜完全離線版素材

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

=== V5.1 追加說明 ===

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
