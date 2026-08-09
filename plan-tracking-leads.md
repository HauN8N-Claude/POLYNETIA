# Plan de tracking — suivre les leads & rendre les pubs rentables

> **But :** savoir combien de personnes passent à chaque étape du tunnel, où elles décrochent, et quelle pub ramène de vrais clients — puis laisser Facebook optimiser pour l'achat, pas pour le clic.

---

## 1. Comment ça marche (en simple)

Ton tunnel est un tuyau : **pub → test → guide → achat → diagnostic**. On pose un « compteur » à chaque étape. Deux usages :

- **Suivre tes leads un par un (pour les rappeler).** Chaque personne qui fait le test ou demande un diagnostic arrive dans ton **Google Sheet** avec nom, téléphone, fuite principale, étape. C'est ta liste d'appels.
- **Mesurer et optimiser.** Les compteurs sont reliés à **Facebook (Pixel)** et à un **tableau de bord (Google Analytics)**. Facebook apprend à trouver des acheteurs ; toi, tu vois où ça fuit.

**Un seul outil pour tout relier : Google Tag Manager (GTM).** Le tunnel envoie déjà chaque étape dans une « boîte aux lettres » du navigateur (le `dataLayer`). GTM lit cette boîte et prévient Facebook et Google Analytics. On ne retouche presque pas le code.

---

## 2. Ce qui est DÉJÀ en place ✅

- **Les compteurs (événements)** sont déjà émis par le code à chaque étape (fonction `trackFunnel`, envoyée au `dataLayer` du navigateur + PostHog si présent).
- **La base de données** journalise chaque étape (`FunnelEvent`).
- **Le Google Sheet** reçoit chaque lead (upsert par email) — c'est ta liste de suivi/rappel.

Il reste donc surtout à **brancher GTM + Pixel Facebook + Google Analytics** (côté outils, peu de code).

---

## 3. Le plan — les étapes à compter

| Événement (dans le code) | Ce que ça veut dire | Événement Facebook (Pixel) | Événement GA4 | Valeur |
|---|---|---|---|---|
| `view_test_lp` | Quelqu'un ouvre le test | `PageView` (auto) | `page_view` | — |
| `start_test` | Il répond à la 1re question | *(custom)* `StartTest` | `start_test` | — |
| `complete_test` | Il finit le test + laisse son email | **`Lead`** | `generate_lead` | — |
| `view_result` | Il voit son résultat | `ViewContent` | `view_result` | — |
| `click_guide_offer` | Il clique vers le guide | *(custom)* `ClickGuide` | `select_content` | — |
| `view_guide_lp` | Il ouvre la page du guide | `ViewContent` | `view_item` | — |
| `start_checkout` | Il lance le paiement | **`InitiateCheckout`** | `begin_checkout` | 3900 XPF |
| `purchase_guide` | **Il achète le guide** | **`Purchase`** | `purchase` | 3900 XPF |
| `view_thank_you` | Page de remerciement | *(custom)* | — | — |
| `click_diagnostic` | Il va vers le diagnostic | *(custom)* | `select_content` | — |
| `submit_qualification` | Il remplit la qualification | **`Lead`** (fort) / `SubmitApplication` | `generate_lead` | — |
| `book_diagnostic` | **Il réserve son RDV** | **`Schedule`** | `schedule` | — |

> Les événements en **gras** sont les plus importants : ce sont ceux sur lesquels Facebook peut **optimiser** tes campagnes (Lead, InitiateCheckout, Purchase, Schedule).

---

## 4. Installation — 4 étapes

1. **Créer un compte Google Tag Manager** (tagmanager.google.com) → récupérer l'ID `GTM-XXXXXXX`.
2. **Créer le Pixel Facebook** (Meta Business → Gestionnaire d'événements) → récupérer l'ID du Pixel (16 chiffres).
3. **Créer une propriété Google Analytics 4** (analytics.google.com) → récupérer l'ID `G-XXXXXXX`.
4. **Câbler dans GTM** (aucun code) :
   - Une **variable** + un **déclencheur** « Événement personnalisé » par événement du tableau (le nom du déclencheur = le nom de l'événement, ex. `purchase_guide`).
   - Une **balise Pixel Facebook** (base, sur toutes les pages) + une balise par événement fort (`Lead`, `InitiateCheckout`, `Purchase`, `Schedule`), déclenchée par l'événement correspondant.
   - Une **balise GA4** (config) + les balises d'événements GA4.
   - **Tester** avec l'aperçu GTM + l'extension « Meta Pixel Helper », puis **publier**.

---

## 5. Le seul bout de code à ajouter (après le déploiement)

Le tunnel pousse déjà les événements dans `window.dataLayer`. Il ne manque que **le conteneur GTM** dans l'app (une fois). Dans le projet now.ts :

**Variable d'env :** `NEXT_PUBLIC_GTM_ID=GTM-XXXXXXX`

**Composant** `src/features/analytics/gtm.tsx` :
```tsx
"use client";
import Script from "next/script";
import { env } from "@/lib/env";

export function GoogleTagManager() {
  const id = env.NEXT_PUBLIC_GTM_ID;
  if (!id) return null;
  return (
    <Script id="gtm" strategy="afterInteractive">
      {`(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);})(window,document,'script','dataLayer','${id}');`}
    </Script>
  );
}
```
Puis l'inclure une fois dans le layout du tunnel (`app/(funnel)/layout.tsx`) ou le layout racine, et ajouter `NEXT_PUBLIC_GTM_ID` dans `src/lib/env.ts` (bloc `client`).

> ⚠️ **À appliquer après le déploiement** (ou en coordination avec le chat de déploiement) pour éviter tout conflit sur le dépôt now.ts. Le Pixel Facebook et GA4 ne sont **pas** codés en dur : ils vivent dans GTM. Ainsi, tout se règle ensuite sans retoucher le code.

---

## 6. Les 3 chiffres à regarder (une fois branché)

1. **Coût par test terminé** — combien te coûte un `complete_test` (une pub qui amène des tests pas chers = bon signe).
2. **Taux test → guide** — sur 100 tests terminés, combien achètent le guide (`purchase_guide`).
3. **Coût par acheteur / par RDV** — combien te coûte un `Purchase` et un `book_diagnostic`.

Avec ça, tu compares tes pubs (angle 1 vs angle 2 grâce aux UTM), tu coupes celles qui coûtent cher et tu montes celles qui ramènent des clients.

---

## Récap

- **Suivre tes leads pour les rappeler → Google Sheet** (déjà prêt).
- **Mesurer + rentabiliser les pubs → GTM + Pixel + GA4** (le plan ci-dessus, à brancher après le déploiement).
- Les compteurs sont déjà dans le code ; il ne manque que le conteneur GTM (un petit ajout) et la config côté outils (sans code).
