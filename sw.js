const CACHE_NAME = 'wealth-terminal-v2'; // 👈 อัปเดต Version เพื่อล้าง Cache เก่า
const ASSETS_TO_CACHE = [
  './',
  './index.html',
  './manifest.json',
  'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap',
  'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2',
  'https://cdn.jsdelivr.net/npm/chart.js'
];

// 1. Install Event - บันทึกไฟล์ Assets ลง Cache
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS_TO_CACHE);
    })
  );
  self.skipWaiting();
});

// 2. Activate Event - ลบ Cache เก่าออกอัตโนมัติ
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
      );
    })
  );
  self.clients.claim();
});

// 3. Fetch Event
self.addEventListener('fetch', (event) => {
  if (!event.request.url.startsWith('http')) return;

  // 🚫 1. API Calls (Supabase / Firebase) -> Network Only เสมอ (ห้าม Cache ตัวเลข)
  if (event.request.url.includes('supabase.co') || event.request.url.includes('firebasedatabase.app')) {
    event.respondWith(fetch(event.request));
    return;
  }

  // ⚡ 2. Static Assets (HTML, CSS, JS, Libraries) -> Stale-While-Revalidate
  event.respondWith(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.match(event.request).then((cachedResponse) => {
        // ดึงไฟล์ใหม่จาก Network มาอัปเดตลง Cache เบื้องหลัง
        const fetchPromise = fetch(event.request).then((networkResponse) => {
          if (networkResponse && networkResponse.status === 200) {
            cache.put(event.request, networkResponse.clone());
          }
          return networkResponse;
        }).catch(() => cachedResponse);

        // แสดงผลจาก Cache ทันที ถ้าไม่มีใน Cache ค่อยรอจาก Network
        return cachedResponse || fetchPromise;
      });
    })
  );
});
