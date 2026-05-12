# Mandala-Mantra · Générateur PWA

Version **Progressive Web App** du générateur Shem72 : s'installe sur iPhone / iPad / Mac comme une vraie application, fonctionne hors-ligne, plein écran sans barre de navigation.

---

## Contenu du dossier

```
mandala_mantra_PWA/
├── index.html              ← l'app (version mobile/desktop unifiée)
├── manifest.json           ← métadonnées PWA (nom, couleurs, icônes)
├── service-worker.js       ← cache hors-ligne
├── serve_local.py          ← serveur Python pour test local Mac↔iPhone
├── README.md               ← ce fichier
├── icons/                  ← icônes générées (180, 192, 512… + splash)
├── source/
│   ├── master.png          ← icône-source 1024×1024 (à remplacer)
│   └── make_icons.py       ← script de régénération de toutes les tailles
└── fonts/                  ← (vide) — les fonts sont chargées via CDN
```

---

## 1. Tester en local sur votre iPhone (5 minutes)

Le Mac et l'iPhone doivent être sur le **même Wi-Fi**.

```bash
cdcd "/Users/yatsav-macbookpro/Documents/Claude/Projects/Shem72/mandala_mantra_PWA"
python3 serve_local.py --https
```

Le script affiche l'URL à ouvrir sur votre iPhone :

```
 iPhone (Wi-Fi)     : https://192.168.x.x:8443/
```

Sur l'iPhone :

1. Ouvrir cette URL dans **Safari** (pas Chrome).
2. Au 1ᵉʳ chargement, Safari affichera un avertissement de certificat auto-signé → **Détails** → **visiter ce site web**.
3. Une fois la page chargée, taper l'icône **Partager** (carré + flèche vers le haut) → **Sur l'écran d'accueil**.
4. Confirmer. L'icône Mandala-Mantra apparaît sur l'écran d'accueil.
5. **Lancer depuis l'écran d'accueil** : l'app s'ouvre plein écran, sans Safari visible. C'est officiellement installé.

> **Note** — le mode HTTP simple (`python3 serve_local.py`) fonctionne aussi mais sans service worker, donc pas de hors-ligne. Utiliser `--https` pour la vraie expérience PWA.

---

## 2. Déployer en ligne (recommandé pour partage à des proches)

### Option A · GitHub Pages (gratuit, \~5 min)

1. Créer un dépôt sur github.com (peut être public ou privé).
2. Téléverser tout le contenu de `mandala_mantra_PWA/` à la racine du dépôt.
3. Settings → Pages → Source : `main` branch / `/ (root)`.
4. URL fournie : `https://votre-pseudo.github.io/nom-du-depot/`.
5. Ouvrir cette URL sur iPhone → **Partager** → **Sur l'écran d'accueil**.

### Option B · Netlify Drop (gratuit, encore plus rapide)

1. Aller sur https://app.netlify.com/drop
2. **Glisser tout le dossier** `mandala_mantra_PWA/` sur la page.
3. URL fournie en \~30 secondes (`https://random-name.netlify.app`).
4. Même procédure côté iPhone.

### Option C · Vercel (gratuit, équivalent Netlify)

Idem Netlify via https://vercel.com.

---

## 3. Remplacer l'icône

L'icône actuelle est un placeholder. Pour la remplacer par votre vraie image :

1. Placer votre fichier image (idéalement 1024×1024 PNG ou JPG) sous le nom **`master.png`** dans le dossier `source/`.
2. Régénérer toutes les tailles :

```bash
cd "/Users/yatsav-macbookpro/Documents/Claude/Projects/Shem72/mandala_mantra_PWA"
python3 source/make_icons.py
```

3. Les fichiers dans `icons/` sont remplacés (180, 192, 512, splash, etc.).
4. Sur iPhone, supprimer l'app de l'écran d'accueil et la réinstaller pour voir la nouvelle icône (le cache d'icône iOS est tenace).

> Si vous voulez forcer la régénération de l'icône stylisée placeholder à partir de zéro : `python3 source/make_icons.py --rebuild`.

---

## 4. Mode hors-ligne — comment ça marche

- Le **service worker** met en cache l'HTML, le JS, les icônes et les fonts Google au **premier lancement en ligne**.
- À partir du 2ᵉ lancement, l'app fonctionne sans connexion (mode avion, sous-sol, en voyage…).
- Pour forcer une mise à jour de cache : sur iOS, fermer l'app, relancer en ligne, attendre 5 s, relancer.

---

## 5. Différences par rapport à la version bureau (`mandala_mantra_generateur.html`)

Cohabitation prudente : la version bureau d'origine n'a pas été modifiée.

La PWA inclut en plus :
- balises `apple-touch-icon`, `apple-mobile-web-app-*`, splash screens iOS
- `manifest.json` + service worker
- safe-area iPhone (notch / dynamic island)
- CSS responsive mobile (≤ 720 px) :
  - layout en pile, formulaire non sticky
  - cibles tactiles ≥ 44 px (Apple HIG)
  - inputs en 16 px pour éviter le zoom automatique iOS
  - boutons et toggles redimensionnés
- tooltips déclenchés au **tap** sur écran tactile (et auto-fermés au bout de 3,5 s)
- enregistrement automatique du service worker

Les calculs (gematria, séquences, mandala SVG, exports SVG/PNG) sont **identiques**.

---

## 6. Désinstaller

Sur iPhone : appui long sur l'icône → **Supprimer l'app**. Toutes les données cache disparaissent avec.

---

## 7. Dépannage

| Problème                                               | Solution                                                                                                                       |
| ------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------ |
| « Cette page ne peut pas être chargée » sur iPhone     | Vérifier que Mac et iPhone sont sur **le même Wi-Fi**, et que le firewall macOS autorise Python (Réglages → Réseau → Pare-feu) |
| L'icône ne se met pas à jour après remplacement        | Supprimer l'app de l'écran d'accueil et la réinstaller                                                                         |
| « Service worker registration failed » dans la console | Normal en `file://` — il faut servir en HTTP(S). Utiliser `serve_local.py`                                                     |
| Fonts pas chargées hors-ligne au 1er lancement offline | Faire un 1er lancement **en ligne** pour que le SW les mette en cache                                                          |
| Couleur de la barre de statut iOS mauvaise             | Modifier `apple-mobile-web-app-status-bar-style` (`default`, `black`, `black-translucent`)                                     |

---

*Projet Shem72 · Mandala-Mantra · Système Yatsav — Reboiser l'imaginaire*
