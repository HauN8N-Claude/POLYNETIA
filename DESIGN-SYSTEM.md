# PolynetIA — Design System « Lagoon »

> **Version 1.1 — Direction artistique de la landing page Local Partner.**
> Inspiré du design system de Stripe (structure, rythme, crédibilité) et calibré
> sur les screenshots de référence fournis (hero + section produits stripe.com),
> adapté à l'identité PolynetIA et à une cible d'artisans du fenua peu digitaux.
> Ce fichier est la source de vérité : la LP consomme ces tokens tels quels.

---

## 1. Principes (ce qu'on prend de Stripe, ce qu'on adapte)

| Principe Stripe | Application PolynetIA |
|---|---|
| **Fond clair dominant** — le produit est sérieux, la page est lumineuse | Fond blanc chaud. Le sombre est réservé à 2–3 sections d'impact (coût des fuites, investissement) |
| **Ruban dégradé en diagonale** — l'aurora traverse le coin du hero, le fond reste blanc *(screenshot hero)* | Ruban « lagon » incliné dans le coin supérieur droit du hero, jamais en fond pleine page |
| **Titre bicolore** — première phrase navy, suite en ardoise plus claire, dans le même Hn *(les 2 screenshots)* | Le H1 à deux phrases du brief est fait pour ça : phrase 1 en `--ink`, phrase 2 en `--body` |
| **Sections alternées clair / navy** | Rythme : clair → clair → navy → clair… le navy marque les moments décisifs |
| **Séparateurs diagonaux** (sections inclinées) | Bandes inclinées `skewY(-6deg)` entre grandes parties — la signature visuelle Stripe |
| **Typo énorme, interlettrage serré, poids contrastés** | H1 ~64px desktop, letter-spacing négatif, graisse 800 vs texte 400 |
| **Eyebrows colorés** au-dessus des titres | Label uppercase couleur primaire, jamais de bordure |
| **Boutons pillule avec flèche** `→` | CTA pillule, flèche qui glisse au hover |
| **Ombres en couches** (double ombre douce) | Ombres « stripe-like » à 2 niveaux, jamais d'ombre dure |
| **Schémas produits intégrés** (pas de stock photos) | Le seau, la timeline et le système sont des schémas SVG dans le style du système |
| **Densité maîtrisée** — beaucoup d'air, largeur de lecture courte | 72ch max pour le texte, sections ≥ 96px de respiration |

**Ce qu'on ne copie pas :** le violet « blurple » de Stripe (on garde une identité
lagon), les animations mesh WebGL (trop lourdes), la densité d'information
développeur (notre cible lit sur téléphone, fatiguée, le soir).

---

## 2. Design tokens (CSS)

À coller tel quel dans `:root` de la LP. Tout dérive de là.

```css
:root {
  /* ---------------------------------------------------------- */
  /* COULEURS — remplacer ici pour re-brander toute la page      */
  /* ---------------------------------------------------------- */

  /* Marque */
  --blue:        #4f5eda;   /* Primaire — bleu profond électrique (rôle du blurple Stripe) */
  --blue-dark:   #3a46b8;
  --lagoon:      #00b3c6;   /* Secondaire — cyan lagon PolynetIA */
  --coral:       #ff6b4a;   /* Accent chaud — alertes, fuites, points d'attention */
  --navy:        #0a2540;   /* Navy Stripe-like — sections sombres, titres sur clair */

  /* Dégradés signature « lagon » */
  /* Aurora : le ruban diagonal du hero (cf. screenshot stripe.com —
     bande inclinée dans le coin, PAS un fond pleine page) */
  --grad-aurora: linear-gradient(115deg, #4f5eda 0%, #00b3c6 40%, #7ee0d2 65%, #ffb199 100%);
  --grad-text:   linear-gradient(92deg, #4f5eda 0%, #00a8c0 100%);
  --grad-cta:    linear-gradient(135deg, #4f5eda 0%, #5b6cf0 100%);
  /* Jauge / meter (cf. screenshot "Usage meter" : barre fine en dégradé) */
  --grad-meter:  linear-gradient(90deg, #4f5eda 0%, #00b3c6 60%, #ff6b4a 100%);
  /* Fond chaud des visuels DANS les cartes-démo (cf. screenshot section produits) */
  --grad-card:   linear-gradient(160deg, #fff7f3 0%, #ffd9c2 60%, #ffb98f 100%);

  /* Surfaces */
  --bg:          #ffffff;
  --bg-soft:     #f6f9fc;   /* gris-bleu très clair (le "cloud" Stripe) */
  --bg-navy:     #0a2540;
  --bg-navy-2:   #10365c;   /* navy éclairci pour cartes sur fond navy */

  /* Texte */
  --ink:         #0a2540;   /* titres */
  --body:        #425466;   /* texte courant (le slate Stripe) */
  --muted:       #6b7f95;
  --ink-inv:     #ffffff;
  --body-inv:    #adbdcc;   /* texte courant sur navy */

  /* Sémantique */
  --ok:          #15803d;
  --ok-soft:     #e6f6ec;
  --bad:         #d43d2a;
  --bad-soft:    #fdeeea;

  /* Bordures */
  --line:        #e6ebf1;
  --line-navy:   rgba(255,255,255,.14);

  /* ---------------------------------------------------------- */
  /* TYPOGRAPHIE                                                 */
  /* ---------------------------------------------------------- */
  --font: "Segoe UI", system-ui, -apple-system, "Helvetica Neue", Arial, sans-serif;

  --fs-h1:    clamp(2.2rem, 6vw, 4rem);       /* 64px desktop */
  --fs-h2:    clamp(1.7rem, 4.4vw, 2.6rem);   /* 42px */
  --fs-h3:    clamp(1.15rem, 2.4vw, 1.4rem);  /* 22px */
  --fs-body:  1.0625rem;                      /* 17px */
  --fs-lede:  clamp(1.1rem, 2vw, 1.25rem);    /* 20px — intro de section */
  --fs-small: .92rem;
  --fs-eyebrow: .8rem;

  --lh-tight: 1.08;   /* H1 */
  --lh-head:  1.18;   /* H2-H3 */
  --lh-body:  1.65;

  --ls-tight: -0.025em;  /* titres */
  --ls-wide:  0.12em;    /* eyebrows uppercase */

  --w-hair: 400; --w-med: 600; --w-bold: 700; --w-black: 800;

  /* ---------------------------------------------------------- */
  /* ESPACE — échelle de 8, rythme Stripe                        */
  /* ---------------------------------------------------------- */
  --s1: 8px;  --s2: 16px; --s3: 24px; --s4: 32px;
  --s5: 48px; --s6: 64px; --s7: 96px; --s8: 128px;

  --section-y: clamp(var(--s7), 10vw, var(--s8));  /* respiration verticale */
  --wrap:      1080px;
  --wrap-text: 72ch;

  /* ---------------------------------------------------------- */
  /* FORME                                                       */
  /* ---------------------------------------------------------- */
  --r-sm: 8px; --r-md: 16px; --r-pill: 999px;

  /* Ombres en couches (signature Stripe : 2 ombres superposées) */
  --shadow-sm: 0 2px 5px -1px rgba(50,50,93,.12), 0 1px 3px -1px rgba(0,0,0,.08);
  --shadow-md: 0 6px 12px -2px rgba(50,50,93,.14), 0 3px 7px -3px rgba(0,0,0,.12);
  --shadow-lg: 0 13px 27px -5px rgba(50,50,93,.18), 0 8px 16px -8px rgba(0,0,0,.16);

  /* Diagonale signature */
  --skew: -6deg;

  /* Mouvement */
  --ease: cubic-bezier(.215,.61,.355,1);
  --t-fast: .15s; --t-med: .3s;
}
```

---

## 3. Typographie — règles d'usage

| Rôle | Taille | Graisse | Couleur | Notes |
|---|---|---|---|---|
| **H1 (hero uniquement)** | `--fs-h1` | 800 | **bicolore** : phrase 1 `--ink`, phrase 2 `--body` | Signature Stripe observée sur les screenshots. `line-height: var(--lh-tight)`, `letter-spacing: var(--ls-tight)`, `text-wrap: balance` |
| **H2 bicolore (optionnel)** | `--fs-h2` | 800 | idem H1 | Réservé aux sections à 2 phrases (titre + promesse). Max 2 par page |
| **H2 (titre de section)** | `--fs-h2` | 800 | `--ink` / blanc sur navy | idem tracking serré |
| **H3 (carte, sous-partie)** | `--fs-h3` | 700 | `--ink` | |
| **Eyebrow** | `--fs-eyebrow` | 700 | `--blue` (ou `--lagoon` sur navy) | UPPERCASE, `letter-spacing: var(--ls-wide)`, **sans bordure ni fond** — juste le mot coloré (style Stripe) |
| **Lede (intro de section)** | `--fs-lede` | 400 | `--body` | max `--wrap-text` |
| **Corps** | `--fs-body` | 400 | `--body` | jamais de gris < `--muted` pour du texte utile |
| **Chiffres (calculateur, F CFP)** | — | 800 | `--ink` | `font-variant-numeric: tabular-nums` |

**Interdits :** texte en italique long, plus de 2 graisses par bloc, titres centrés
sur plus de 2 lignes mobile.

---

## 4. Composants

### 4.1 Boutons

```css
/* CTA principal — pillule Stripe avec flèche */
.btn-primary {
  background: var(--grad-cta);
  color: #fff;
  font-weight: var(--w-bold);
  padding: 14px 28px;
  border-radius: var(--r-pill);
  box-shadow: var(--shadow-md);
  transition: transform var(--t-fast) var(--ease), box-shadow var(--t-fast) var(--ease);
}
.btn-primary .arrow { transition: transform var(--t-fast) var(--ease); }
.btn-primary:hover { transform: translateY(-1px); box-shadow: var(--shadow-lg); }
.btn-primary:hover .arrow { transform: translateX(3px); }

/* Secondaire — ghost pillule */
.btn-ghost {
  background: transparent; color: var(--blue);
  border: 1.5px solid var(--line); border-radius: var(--r-pill);
}
.btn-ghost:hover { border-color: var(--blue); }
```

- Le CTA principal contient **toujours** une flèche `→` (span `.arrow`).
- Un seul CTA principal visible par écran. Le ghost ne cohabite qu'au hero.
- Sur navy : CTA identique (le dégradé bleu tient sur navy), ghost en blanc.
- Tap target ≥ 48px. Sur mobile, CTA pleine largeur dans les sections.

### 4.2 Sections & séparateurs diagonaux

```css
section { padding: var(--section-y) 0; }

/* Bande inclinée signature — englobe une section navy ou soft */
.slant {
  position: relative;
  transform: skewY(var(----skew));   /* -6deg */
}
.slant > .unslant { transform: skewY(calc(-1 * var(--skew))); }
```

- **Rythme de la page** : `bg` → `bg-soft` → **navy incliné** → `bg` → …
- Maximum **3 sections navy** par page (coût, investissement, CTA final).
- La diagonale ne s'applique qu'aux **transitions majeures** (2–3 par page),
  jamais entre deux sections claires consécutives.
- Le contenu à l'intérieur est toujours contre-incliné (`.unslant`).

### 4.3 Cartes

```css
.card {
  background: #fff;
  border-radius: var(--r-md);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--line);
  padding: var(--s4);
  transition: box-shadow var(--t-med) var(--ease), transform var(--t-med) var(--ease);
}
.card:hover { box-shadow: var(--shadow-md); transform: translateY(-2px); }

/* Sur navy */
.card-navy { background: var(--bg-navy-2); border-color: var(--line-navy); }
```

- Pas de bordure colorée à gauche, pas d'icônes surdimensionnées.
- Une carte = un titre H3 + 1–3 lignes. Jamais de mur de texte en carte.
- L'icône (si présente) : 20–24px, monochrome `--blue` ou `--lagoon`, trait 2px.

### 4.3 bis Cartes-démo (signature screenshot « section produits »)

Grandes cartes blanches contenant un **visuel de démonstration posé sur un fond
dégradé chaud** — c'est le composant Stripe le plus reconnaissable des captures.

```css
.card-demo {
  background: #fff; border-radius: 20px;
  box-shadow: var(--shadow-lg); border: 1px solid var(--line);
  padding: var(--s5) var(--s4) 0;   /* le visuel touche le bas de la carte */
  overflow: hidden;
}
.card-demo .visual {
  background: var(--grad-card);      /* fond pêche dégradé derrière le mockup */
  border-radius: var(--r-md) var(--r-md) 0 0;
  padding: var(--s4) var(--s4) 0;
}
```

- Usage PolynetIA : **le seau** (hero), les **preuves** (mockup téléphone WhatsApp,
  fausse fenêtre navigateur avec barre d'URL pour la capture de site — cadre
  « browser chrome » comme sur le screenshot), le **schéma du système**.
- Titre H3 dans la carte, en haut à gauche. Icône « agrandir » optionnelle en
  haut à droite (carré lilas doux `--bg-soft`, 40px).
- Max 2 cartes-démo côte à côte desktop, empilées mobile.

### 4.3 ter Jauge dégradée (screenshot « Usage meter »)

Barre fine (8px, `--r-pill`) remplie avec `--grad-meter`.
Usage PolynetIA : le **résultat du calculateur** (la jauge s'allonge avec le
montant estimé) et les étapes de progression du process. Toujours accompagnée
du chiffre en clair — jamais d'info portée par la barre seule.

### 4.4 Schémas & visuels (seau, timeline, système)

- **Style unifié « schéma produit Stripe »** : fond blanc ou `--bg-soft`,
  traits `--navy` 2px, remplissages plats aux couleurs de marque, ombre `--shadow-lg`
  sur le cadre.
- L'eau / le flux : `--lagoon`. Les fuites / alertes : `--coral`.
- Étiquettes de schéma : pillules blanches, bordure `--line`, texte `--navy` 12–13px.
- Jamais de photo stock. Les emplacements de preuves réelles gardent le style
  placeholder (bordure pointillée `--blue`, tag « À REMPLACER »).

### 4.5 Formulaire

```css
.input {
  border: 1.5px solid var(--line); border-radius: var(--r-sm);
  padding: 13px 14px; background: #fff;
  transition: border-color var(--t-fast), box-shadow var(--t-fast);
}
.input:focus {
  border-color: var(--blue);
  box-shadow: 0 0 0 4px rgba(79,94,218,.12);   /* halo focus Stripe */
  outline: none;
}
.input.invalid { border-color: var(--bad); background: var(--bad-soft); }
```

- Labels au-dessus, gras 700, jamais de placeholder seul comme label.
- Messages d'erreur : `--bad`, 14px, sous le champ, en français.
- Radios en cartes cliquables (bordure qui passe `--blue` quand cochée).
- Le bouton submit = CTA principal pleine largeur.

### 4.6 FAQ (accordéon)

- Trait séparateur `--line`, question 700, chevron `+` couleur `--blue`
  qui pivote à 45°, `aria-expanded` obligatoire.
- Réponse en `--body`, jamais plus de 4 lignes.

### 4.7 Chiffres & calculateur

- Résultat : `--fs-h2`, 800, `--ink`, `tabular-nums`.
- Devise **F CFP** toujours après le montant, espace insécable.
- Le disclaimer (« estimation, pas une promesse ») reste attaché visuellement
  au résultat — même carte, `--muted`.

---

### 4.8 Anatomie du hero (calquée sur le screenshot stripe.com)

De haut en bas :

1. **Nav** : blanche, fine (64px), logo à gauche, liens simples, pas de CTA
   surdimensionné — le hero porte le CTA.
2. **Ruban aurora** : bande `--grad-aurora` inclinée (~30°) qui entre par le
   coin supérieur droit, floutée légèrement (`filter: blur(0–20px)` selon la
   couche), **derrière** le contenu. Le reste du fond est blanc.
3. **Ligne factuelle** au-dessus du H1 (l'équivalent du « Global GDP running
   on Stripe ») : petite ligne `--muted` avec une donnée **vraie** du brief —
   ex. « Réponse en moins d'une minute • 7 j/7, dimanche compris ».
   ⚠️ Jamais de statistique inventée ici.
4. **H1 bicolore** (cf. typographie) — les deux phrases du brief.
5. **Paire de CTA** : pillule `--grad-cta` avec flèche + bouton blanc bordé
   (secondaire), alignés à gauche.
6. **Bande logos clients** sous le hero *(pattern Stripe)* : uniquement si de
   vrais logos clients existent un jour. En attendant : **omise** — pas de
   placeholder visible sur cette zone, une rangée de faux logos détruirait la
   confiance.

## 5. Motion

| Élément | Animation | Durée |
|---|---|---|
| Reveal au scroll | fade + translateY(12px) | 0.5s `--ease`, 1 fois |
| Hover CTA | translateY(-1px) + flèche +3px | 0.15s |
| Hover carte | ombre sm→md + translateY(-2px) | 0.3s |
| FAQ | max-height | 0.28s |
| Hero | **statique** (pas de mesh animé — perf mobile) | — |

- `prefers-reduced-motion: reduce` → tout à zéro, contenu visible d'office.
- Aucune animation en boucle infinie sauf les gouttes du seau (2.6s, opacité seule).

---

## 6. Accessibilité (non négociable)

- Contraste : `--body` sur `--bg` = 8.6:1 ✓ · `--body-inv` sur `--bg-navy` ≥ 7:1 ✓
  · jamais de texte utile sous 4.5:1.
- Focus visible : halo 4px `rgba(79,94,218,.35)` sur tout élément interactif.
- L'information n'est jamais portée par la couleur seule (✓/✕ accompagnent
  toujours vert/rouge).
- HTML sémantique, un seul H1, `aria-expanded` sur la FAQ, labels reliés aux champs.

---

## 7. Anti-patterns (ce que ce système interdit)

- ❌ Dégradé sur plus d'un élément par écran (le dégradé est un événement, pas un fond).
- ❌ Fond sombre généralisé (le navy est un accent de rythme, pas la base).
- ❌ Grille/circuits/néons « tech » — exclus par le brief.
- ❌ Émojis comme icônes de section.
- ❌ Ombres dures, bordures noires, coins carrés.
- ❌ Plus de 2 couleurs de marque visibles simultanément.
- ❌ Texte sur le dégradé hero sans vérification de contraste.

---

## 8. Application au copy existant (rappel)

Le design system n'absout pas le copy : les corrections de jargon identifiées
dans l'analyse (Convertir, trafic, parcours, mobile-first, Google Business
Profile, preuve sociale, acquisition, composant, qualification, périmètre…)
s'appliquent lors de la reconstruction de la page.
```
Hiérarchie de décision : brief High Ticket > ce design system > goût du moment.
```
