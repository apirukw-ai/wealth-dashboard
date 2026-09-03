const CACHE_NAME = 'wealth-terminal-v1';
const ASSETS_TO_CACHE = [
  './',
  './index.html',
  './manifest.json',
  'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap',
  'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2',
  'https://cdn.jsdelivr.net/npm/chart.js'
];

// Install Event - โหลดไฟล์พื้นฐานลง Cache
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS_TO_CACHE);
    })
  );
  self.skipWaiting();
});

// Activate Event - ลบ Cache เก่า
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

// Fetch Event - ดึงจาก Network ก่อน ถ้าไม่มีเน็ตค่อยดึงจาก Cache
self.addEventListener('fetch', (event) => {
  // กรองข้าม Request ที่มาจาก Extension ให้ทำงานเฉพาะ HTTP/HTTPS
  if (!event.request.url.startsWith('http')) return;

  // 1. ถ้าเป็นการเรียก API ไปยัง Supabase หรือ Firebase ไม่ต้อง Cache ให้ดึงข้อมูลสดจาก Network เสมอ
  if (event.request.url.includes('supabase.co') || event.request.url.includes('firebasedatabase.app')) {
    event.respondWith(fetch(event.request));
    return;
  }

  // 2. สำหรับไฟล์อื่นๆ (HTML, JS, CSS) ให้พยายามดึงจาก Network ก่อน (Network First)
  event.respondWith(
    fetch(event.request)
      .then((networkResponse) => {
        // บันทึกลง Cache เฉพาะ Request ที่สำเร็จ
        if (networkResponse && networkResponse.status === 200 && networkResponse.type === 'basic') {
          const responseToCache = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseToCache);
          });
        }
        return networkResponse;
      })
      .catch(() => {
        // ถ้าไม่มีสัญญาณอินเทอร์เน็ต ค่อยไปดึงไฟล์จาก Cache มาแสดงแทน
        return caches.match(event.request);
      })
  );
});
