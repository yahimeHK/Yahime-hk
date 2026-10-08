/* LOL 攻略站 Service Worker
   目的：讓「更新後卻看到舊版」不再發生。
   - 頁面（HTML）：網路優先 → 永遠拿最新，離線才用快取
   - 有 ?v= 版號的資源：內容雜湊保證內容不變 → 快取優先（開站更快）
   注意：不主動干預其他請求，避免造成新的快取問題。 */
const CACHE = 'lol-guide-v1';

self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', (e) => e.waitUntil(self.clients.claim()));

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;
  let url;
  try { url = new URL(req.url); } catch (e) { return; }
  if (url.origin !== self.location.origin) return;          // 外部資源不介入

  const accept = req.headers.get('accept') || '';
  const isDocument = req.mode === 'navigate' || accept.indexOf('text/html') >= 0;

  if (isDocument) {
    // HTML：網路優先（必要時略過 HTTP 快取），成功就順手更新離線副本
    event.respondWith(
      fetch(req, { cache: 'no-cache' })
        .then((res) => {
          const copy = res.clone();
          caches.open(CACHE).then((c) => c.put(req, copy)).catch(() => {});
          return res;
        })
        .catch(() => caches.match(req).then((hit) => hit || caches.match('index.html')))
    );
    return;
  }

  if (url.searchParams.has('v')) {
    // 有版號的資源：先快取，沒有才連網（並存起來）
    event.respondWith(
      caches.match(req).then((hit) => hit || fetch(req).then((res) => {
        const copy = res.clone();
        caches.open(CACHE).then((c) => c.put(req, copy)).catch(() => {});
        return res;
      }))
    );
  }
});
