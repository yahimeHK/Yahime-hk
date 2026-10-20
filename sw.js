/* LOL 攻略站 Service Worker
   模式：保留快取機制，但「不自動更新」。
   - 頁面（HTML）：快取優先 → 固定使用你載入的版本，不會自己抓新版
   - 有 ?v= 版號的資源：快取優先（內容雜湊保證不變）
   - 只有當這個 SW 的 CACHE 版本被主動提升時，才會清舊快取並換成新版
   - 絕不快取失敗的回應（res.ok 檢查） */
const CACHE = 'lol-guide-v3';

self.addEventListener('install', () => self.skipWaiting());

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;
  let url;
  try { url = new URL(req.url); } catch (e) { return; }
  if (url.origin !== self.location.origin) return;

  const isDocument = req.mode === 'navigate' || (req.headers.get('accept') || '').indexOf('text/html') >= 0;

  function fromCacheFirst(fallbackToIndex) {
    return caches.match(req).then((hit) => {
      if (hit) return hit;                                    // 有快取就用，不連網（＝不自動更新）
      return fetch(req).then((res) => {
        if (res && res.ok) {
          const copy = res.clone();
          caches.open(CACHE).then((c) => c.put(req, copy)).catch(() => {});
        }
        return res;
      }).catch(() => fallbackToIndex ? caches.match('index.html') : undefined);
    });
  }

  if (isDocument) {
    event.respondWith(fromCacheFirst(true));
    return;
  }
  if (url.searchParams.has('v')) {
    event.respondWith(fromCacheFirst(false));
  }
});