# Pipeline prospects paysagistes (NAF 81.30Z)

Génère un `.xlsx` de prospects paysagistes à partir de données publiques
françaises (API Recherche d'entreprises — SIRENE + RNE, sans authentification).

## Installation

```bash
pip install openpyxl requests
```

## Utilisation

Phase 1 + 4 (identité légale seule, aucune coordonnée de contact) :

```bash
python3 scripts/paysagistes_sirene.py --departements 33,40,47,64 --max 500
```

Phase 2 + 3 (enrichissement contact) — le script ne scrape rien lui-même.
Fournissez un export CSV de coordonnées (Apify Google Maps, export manuel,
autre source) et il sera rapproché en matching flou :

```bash
python3 scripts/paysagistes_sirene.py --departements 33 --max 300 \
    --contacts export_maps.csv
```

En-têtes CSV reconnus (les colonnes absentes restent vides) :
`nom` (obligatoire), `code_postal`, `ville`, `adresse`, `telephone`,
`site_web`, `email`.

Sortie : `paysagistes_france_<ZONE>_<AAAAMMJJ>.xlsx`

## Règles appliquées

- Établissements **ACTIFS** uniquement, NAF 81.30Z.
- Toute unité en **diffusion partielle** (statut `P`, ou nom
  « INFORMATION NON-DIFFUSIBLE ») est exclue.
- SIREN validé par **clé de Luhn** : une valeur non conforme est écartée,
  jamais corrigée.
- Dédoublonnage sur le SIREN, la ligne la plus remplie l'emporte.
- **Aucun email n'est jamais déduit ou construit.** Sans source réelle, la
  cellule reste vide et `Source email` vaut `AUCUNE`.
- `WhatsApp probable = OUI` uniquement pour les préfixes mobiles `+336` /
  `+337`. Jamais sur un fixe.
- Erreur réseau → aucun fichier généré, code de sortie 2. Zéro ligne vaut
  mieux qu'une ligne inventée.

## Matching flou (phase 3)

Normalisation : minuscules, suppression des accents, suppression des formes
juridiques (SARL, SAS, SASU, EURL, EI, SCI…), suppression de la ponctuation.
Score = max(ratio de séquence, indice de Jaccard sur les tokens).

| Condition | Confiance |
|---|---|
| même code postal + score ≥ 0,90 | ÉLEVÉ |
| même code postal + score ≥ 0,75 | MOYEN |
| même code postal + score ≥ 0,62 | FAIBLE |
| même commune + score ≥ 0,85 | FAIBLE |
| sinon | rejeté — la ligne SIRENE est conservée, champs contact vides |

## Limite connue

L'API Recherche d'entreprises **n'expose ni téléphone, ni email, ni site web**.
Sans source de contact en entrée (`--contacts`), les colonnes Email, Téléphone,
Site web et Nom commercial sont vides sur 100 % des lignes.
