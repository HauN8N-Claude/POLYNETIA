# Brancher le calendrier et la réception du formulaire

Tout se configure dans **3 variables** en haut du `<script>` de `index.html` :

```js
var CALENDAR_URL       = ""; // page publique « Prendre rendez-vous »
var CALENDAR_EMBED_URL = ""; // URL d'intégration iframe (…?gv=true) — recommandé
var SHEET_ENDPOINT     = ""; // URL /exec de l'application web Apps Script
```

Tant qu'une variable est vide, la fonction associée reste **inactive** (aucune donnée n'est envoyée, le bouton renvoie simplement vers le formulaire).

---

## 1. Google Agenda — réservation du diagnostic

1. Ouvre **Google Agenda** sur ordinateur.
2. Bouton **« Créer »** (en haut à gauche) → **« Planning de rendez-vous »**.
3. Crée un service **« Diagnostic gratuit »** de **30 minutes**, définis tes
   disponibilités, puis enregistre.
4. Clique sur **« Partager »** / **« Ouvrir la page de réservation »** :
   - copie le **lien public** → variable `CALENDAR_URL`.
5. Pour l'affichage **directement dans la page** (recommandé) : bouton
   **« Intégrer »** → copie l'URL de l'`iframe` (elle contient `?gv=true`)
   → variable `CALENDAR_EMBED_URL`.

**Comportement :**
- Si `CALENDAR_EMBED_URL` est renseignée → le calendrier s'affiche dans
  l'écran de succès, juste après l'envoi du formulaire.
- Sinon, si seul `CALENDAR_URL` est renseigné → le bouton
  « Choisir mon créneau » ouvre la page de réservation dans un nouvel onglet.

---

## 2. Google Sheets — réception et suivi des demandes

Le fichier **`google-apps-script.gs`** (à la racine) est déjà relié à la
feuille (ID `1OdmUsqg5Lx1chK9YKD0ryp7rT_gABr_xZZVjSYFlQok`). En résumé :

1. Ouvre la feuille → menu **Extensions → Apps Script**.
2. Colle le contenu de `google-apps-script.gs`, enregistre.
3. Choisis la fonction **`initialiser`** en haut, clique **Exécuter**,
   autorise l'accès. → crée l'onglet **Demandes**, l'en-tête et le menu
   déroulant de statut.
4. **Déployer → Nouveau déploiement → Application web**
   - Exécuter en tant que : **Moi**
   - Qui a accès : **Tout le monde**
5. Copie l'URL qui se termine par **`/exec`** → variable `SHEET_ENDPOINT`
   dans `index.html`.

Colonnes de la demande : `date, prenom, entreprise, metier, commune, tel,
email, site, google, probleme, capacite, source`.
Colonnes de suivi (remplies à la main) : `statut, relance, notes`.
Chaque nouvelle demande arrive avec le statut **« Nouveau »**.

> Remarque technique : l'envoi utilise `mode: "no-cors"`. Le navigateur ne
> lit pas la réponse (normal avec Apps Script depuis un site statique), mais
> la ligne est bien ajoutée à la feuille. Pour vérifier, envoie un test et
> regarde l'onglet **« Demandes »**.
