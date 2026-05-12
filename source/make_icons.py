#!/usr/bin/env python3
"""
Génère toutes les icônes iOS/PWA à partir d'un fichier maître `source/master.png`.
Si master.png n'existe pas, fabrique d'abord une icône stylisée (placeholder).

Usage :
    python3 source/make_icons.py            # utilise master.png si présent
    python3 source/make_icons.py --rebuild  # régénère master.png stylisé

L'utilisateur peut remplacer source/master.png par une image au format carré
(idéalement 1024×1024) et relancer ce script pour rafraîchir toutes les tailles.
"""

import os, sys, math
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ICONS = os.path.abspath(os.path.join(HERE, '..', 'icons'))
MASTER = os.path.join(HERE, 'master.png')
os.makedirs(ICONS, exist_ok=True)

# ─── Palette du projet ──────────────────────────────────────────────────
CREAM     = (247, 243, 234)   # --bg          #f7f3ea
GOLD      = (180, 143,  70)   # --gold        #b48f46
GOLD_2    = (217, 184, 119)   # --gold-2      #d9b877
INK       = ( 31,  29,  46)   # --ink         #1f1d2e
ACCENT    = ( 62,  45,  94)   # --accent      #3e2d5e
COEUR     = (122,  62,  62)   # --coeur       #7a3e3e

# ─── Génération d'un icône stylisé (placeholder) ───────────────────────
def make_placeholder(size=1024):
    """Mandala stylisé : disque crème, soleil-étoile central doré, anneau
    de 24 étoilettes, anneau extérieur, dans l'esprit de la gravure
    fournie par l'utilisateur (mais bien plus simplifié)."""
    img = Image.new('RGB', (size, size), CREAM)
    d = ImageDraw.Draw(img, 'RGBA')
    cx, cy = size / 2, size / 2

    # Anneau extérieur (fin contour or)
    R_OUT = size * 0.485
    d.ellipse([cx - R_OUT, cy - R_OUT, cx + R_OUT, cy + R_OUT],
              outline=GOLD, width=max(2, size // 220))

    # Anneau interne (où vivent les étoilettes)
    R_RING = size * 0.42
    # Marquages d'étoilettes à 12 positions (sobre)
    N_STARS = 12
    for k in range(N_STARS):
        ang = (k / N_STARS) * 2 * math.pi - math.pi / 2
        sx = cx + R_RING * math.cos(ang)
        sy = cy + R_RING * math.sin(ang)
        draw_star(d, sx, sy, size * 0.025, ACCENT)

    # Anneau de laurier (suggéré par un cercle pointillé d'or)
    R_LAUREL = size * 0.36
    d.ellipse([cx - R_LAUREL, cy - R_LAUREL, cx + R_LAUREL, cy + R_LAUREL],
              outline=(*GOLD_2, 180), width=max(1, size // 320))

    # Disque central crème entouré d'or
    R_DISK = size * 0.30
    d.ellipse([cx - R_DISK, cy - R_DISK, cx + R_DISK, cy + R_DISK],
              fill=CREAM, outline=GOLD, width=max(2, size // 240))

    # Soleil central rayonnant
    draw_sun(d, cx, cy, R_DISK * 0.92, GOLD, COEUR, size)

    # Léger vieillissement (vignette douce)
    vignette = Image.new('L', (size, size), 255)
    vd = ImageDraw.Draw(vignette)
    vd.ellipse([-size * 0.1, -size * 0.1, size * 1.1, size * 1.1], fill=255)
    # ombre légère au bord
    border = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    bd = ImageDraw.Draw(border)
    bd.ellipse([0, 0, size, size], outline=(60, 50, 40, 40),
               width=int(size * 0.012))
    border = border.filter(ImageFilter.GaussianBlur(radius=size / 240))
    img = Image.alpha_composite(img.convert('RGBA'), border).convert('RGB')

    return img


def draw_star(d, cx, cy, r, color, points=5):
    """Étoilette simple à 5 branches."""
    inner = r * 0.45
    pts = []
    for k in range(points * 2):
        a = (k / (points * 2)) * 2 * math.pi - math.pi / 2
        rr = r if k % 2 == 0 else inner
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=color)


def draw_sun(d, cx, cy, r_disk, ray_color, face_color, size):
    """Soleil : 16 rayons triangulaires + disque + petits traits suggérant
    le visage (yeux, bouche)."""
    # Rayons : alternance longs/courts comme dans la gravure
    n_rays = 16
    for k in range(n_rays):
        a = (k / n_rays) * 2 * math.pi
        long_ray = (k % 2 == 0)
        r_tip = r_disk * (1.5 if long_ray else 1.18)
        r_base = r_disk * 0.78
        half = math.radians(360 / n_rays / 2.6)
        p_tip = (cx + r_tip * math.cos(a), cy + r_tip * math.sin(a))
        p_l = (cx + r_base * math.cos(a - half), cy + r_base * math.sin(a - half))
        p_r = (cx + r_base * math.cos(a + half), cy + r_base * math.sin(a + half))
        d.polygon([p_tip, p_l, p_r], fill=ray_color)
    # Disque solaire
    rd = r_disk * 0.78
    d.ellipse([cx - rd, cy - rd, cx + rd, cy + rd],
              fill=GOLD_2, outline=ray_color, width=max(2, size // 220))
    # Visage minimaliste (yeux et sourire suggérés)
    eye_r = rd * 0.08
    eye_dx = rd * 0.30
    eye_dy = rd * 0.12
    d.ellipse([cx - eye_dx - eye_r, cy - eye_dy - eye_r,
               cx - eye_dx + eye_r, cy - eye_dy + eye_r], fill=ray_color)
    d.ellipse([cx + eye_dx - eye_r, cy - eye_dy - eye_r,
               cx + eye_dx + eye_r, cy - eye_dy + eye_r], fill=ray_color)
    # Bouche : arc
    mw = rd * 0.42
    mh = rd * 0.30
    d.arc([cx - mw/2, cy + rd*0.05, cx + mw/2, cy + rd*0.05 + mh],
          start=10, end=170, fill=ray_color, width=max(2, size // 220))


# ─── Génération des tailles iOS/PWA à partir d'un master ───────────────
TARGETS = [
    # iOS Apple Touch
    ('apple-touch-icon.png',        180),
    ('apple-touch-icon-152.png',    152),
    ('apple-touch-icon-167.png',    167),
    ('apple-touch-icon-120.png',    120),
    # PWA manifest
    ('icon-192.png',                192),
    ('icon-256.png',                256),
    ('icon-384.png',                384),
    ('icon-512.png',                512),
    # Maskable (avec padding pour zone de sécurité)
    ('icon-512-maskable.png',       512),
    # Favicon
    ('favicon-32.png',               32),
    ('favicon-16.png',               16),
]


def make_maskable(src, size):
    """Pour icône maskable, ajouter un padding de 10% pour la safe area
    (Android peut crop jusqu'à 10% de chaque côté)."""
    pad = int(size * 0.1)
    inner = size - 2 * pad
    base = Image.new('RGB', (size, size), CREAM)
    scaled = src.resize((inner, inner), Image.LANCZOS)
    base.paste(scaled, (pad, pad))
    return base


def build_all():
    if not os.path.exists(MASTER):
        print('Pas de master.png — fabrication d\'un placeholder stylisé.')
        ph = make_placeholder(1024)
        ph.save(MASTER, 'PNG', optimize=True)
        print(f'  → {MASTER} (1024×1024)')
    # Ouvre RGBA puis compose sur fond crème — préserve les bords doux,
    # remplace les zones transparentes par la couleur de l'app au lieu de noir.
    raw = Image.open(MASTER).convert('RGBA')
    bg = Image.new('RGB', raw.size, CREAM)
    bg.paste(raw, mask=raw.split()[3])
    src = bg
    # Crop carré si besoin
    w, h = src.size
    if w != h:
        s = min(w, h)
        left = (w - s) // 2
        top = (h - s) // 2
        src = src.crop((left, top, left + s, top + s))
        print(f'Source recadrée en carré : {s}×{s}')
    print('Génération des tailles :')
    for name, size in TARGETS:
        if 'maskable' in name:
            img = make_maskable(src, size)
        else:
            img = src.resize((size, size), Image.LANCZOS)
        path = os.path.join(ICONS, name)
        img.save(path, 'PNG', optimize=True)
        print(f'  {name:<30s} {size}×{size}')

    # Splash screens iPhone classiques (cream fond + icône centrée)
    splashes = [
        ('apple-splash-1170-2532.png', 1170, 2532),  # iPhone 12/13/14 Pro
        ('apple-splash-1284-2778.png', 1284, 2778),  # iPhone 12/13/14 Pro Max
        ('apple-splash-1125-2436.png', 1125, 2436),  # iPhone X/XS/11 Pro
        ('apple-splash-828-1792.png',   828, 1792),  # iPhone XR/11
        ('apple-splash-750-1334.png',   750, 1334),  # iPhone 6/7/8/SE
    ]
    icon_size = 360  # taille de l'icône centrée sur le splash
    icon_for_splash = src.resize((icon_size, icon_size), Image.LANCZOS)
    print('Splash screens iOS :')
    for name, w, h in splashes:
        splash = Image.new('RGB', (w, h), CREAM)
        sx = (w - icon_size) // 2
        sy = (h - icon_size) // 2 - h // 16   # légèrement au-dessus du centre
        splash.paste(icon_for_splash, (sx, sy))
        path = os.path.join(ICONS, name)
        splash.save(path, 'PNG', optimize=True)
        print(f'  {name:<30s} {w}×{h}')

    print(f'\nTout généré dans : {ICONS}')


if __name__ == '__main__':
    if '--rebuild' in sys.argv and os.path.exists(MASTER):
        os.remove(MASTER)
        print('master.png supprimé — sera régénéré.')
    build_all()
