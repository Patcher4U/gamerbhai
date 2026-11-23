/* GamerBhai service worker: fast repeat visits + offline fallback. Never touches other sites (Supabase, YouTube…). */
const C = "gb-v1";
self.addEventListener("install", e => { e.waitUntil(caches.open(C).then(c => c.addAll(["/", "/guides", "/map", "/img/og.jpg"])).catch(() => {})); self.skipWaiting(); });
self.addEventListener("activate", e => { e.waitUntil(caches.keys().then(k => Promise.all(k.filter(x => x !== C).map(x => caches.delete(x)))).then(() => self.clients.claim())); });
self.addEventListener("fetch", e => {
  const r = e.request, u = new URL(r.url);
  if (r.method !== "GET" || u.origin !== location.origin || u.pathname === "/sw.js") return;
  if (r.mode === "navigate") {   // pages: always try the network first so content is fresh
    e.respondWith(fetch(r).then(res => { const cp = res.clone(); caches.open(C).then(c => c.put(r, cp)); return res; })
      .catch(() => caches.match(r).then(m => m || caches.match("/"))));
    return;
  }
  if (/\.(webp|png|jpg|glb|ico)$/.test(u.pathname) || u.search.includes("v=")) {   // versioned/static assets: cache first
    e.respondWith(caches.match(r).then(m => m || fetch(r).then(res => { if (res.ok) { const cp = res.clone(); caches.open(C).then(c => c.put(r, cp)); } return res; })));
  }
});
