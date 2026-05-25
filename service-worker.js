/* ════════════════════════════════════════════════════════════════════
   Service Worker — Mandala-Mantra Générateur (PWA)
   Stratégie : cache-first pour les ressources statiques, network-first
   pour les fonts Google (fallback cache si hors-ligne).
   ════════════════════════════════════════════════════════════════════ */

const CACHE_VERSION = 'mandala-mantra-v1.1.3';
const STATIC_CACHE  = `${CACHE_VERSION}-static`;
const FONTS_CACHE   = `${CACHE_VERSION}-fonts`;

// Ressources mises en cache à l'installation
const PRECACHE_URLS = [
  './',
  './index.html',
  './manifest.json',
  './icons/apple-touch-icon.png',
  './icons/apple-touch-icon-152.png',
  './icons/apple-touch-icon-167.png',
  './icons/apple-touch-icon-120.png',
  './icons/icon-192.png',
  './icons/icon-256.png',
  './icons/icon-384.png',
  './icons/icon-512.png',
  './icons/icon-512-maskable.png',
  './icons/favicon-32.png',
  './icons/favicon-16.png',
  './icons/apple-splash-1170-2532.png',
  './icons/apple-splash-1284-2778.png',
  './icons/apple-splash-1125-2436.png',
  './icons/apple-splash-828-1792.png',
  './icons/apple-splash-750-1334.png'
];
// Le moteur (vendor/swisseph/*) n'est PAS pré-caché : le .data fait 12 Mo et ferait
// échouer l'installation du SW. Il est servi par le réseau (et caché à la demande par le navigateur).

// ─── Installation : pré-cache des ressources statiques ─────────────────
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then((cache) => cache.addAll(PRECACHE_URLS))
      .then(() => self.skipWaiting())
  );
});

// ─── Activation : nettoyer les anciens caches ──────────────────────────
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => Promise.all(
      keys
        .filter((k) => !k.startsWith(CACHE_VERSION))
        .map((k) => caches.delete(k))
    )).then(() => self.clients.claim())
  );
});

// ─── Stratégies de fetch ───────────────────────────────────────────────
self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;

  const url = new URL(req.url);

  // Fonts Google : network-first, fallback cache, mise en cache à la volée
  if (url.host === 'fonts.googleapis.com' || url.host === 'fonts.gstatic.com') {
    event.respondWith(
      caches.open(FONTS_CACHE).then(async (cache) => {
        const cached = await cache.match(req);
        try {
          const fresh = await fetch(req);
          if (fresh && fresh.status === 200) {
            cache.put(req, fresh.clone());
          }
          return fresh;
        } catch (_) {
          if (cached) return cached;
          throw _;
        }
      })
    );
    return;
  }

  // Ressources locales : cache-first, fallback réseau
  event.respondWith(
    caches.match(req).then((cached) => {
      if (cached) return cached;
      return fetch(req).then((resp) => {
        // Met en cache à la volée les nouvelles ressources locales
        if (resp && resp.status === 200 && url.origin === self.location.origin) {
          const clone = resp.clone();
          caches.open(STATIC_CACHE).then((cache) => cache.put(req, clone));
        }
        return resp;
      }).catch(() => {
        // Hors-ligne et pas en cache : retourner la page d'accueil pour la
        // navigation, sinon une erreur transparente.
        if (req.mode === 'navigate') {
          return caches.match('./index.html');
        }
      });
    })
  );
});

// ─── Message handler pour skipWaiting manuel ───────────────────────────
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});
