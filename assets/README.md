# assets/ — visuels de la LP Local Partner

Fichiers attendus (visuels générés, design « Nocturne ») :

| Fichier | Section de la LP | Format |
| --- | --- | --- |
| `seau-publicite-x2.png` | 04 — Le faux remède | portrait 1024×1536 |
| `systeme-local-partner.png` | 08 — Le système complet | carré 1248×1248 |
| `parcours-client.png` | 10 — Parcours du client | paysage 1536×1024 |
| `logo-polynetia.png` | Header (navigation) | fond TRANSPARENT recommandé, hauteur affichée 44 px |

Tant qu'un fichier manque, sa figure se masque automatiquement dans la page
(gestionnaire `onerror` sur la balise `<img>`), donc aucune image cassée
n'apparaît.

Avant mise en ligne :

- Compresser chaque image (Squoosh, TinyPNG…) — objectif < 300 Ko par fichier.
- Conserver exactement ces noms de fichiers : ils sont référencés dans
  `local-partner.html` et `preview-high-ticket.html`.
