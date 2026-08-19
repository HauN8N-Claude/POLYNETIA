#!/usr/bin/env python3
"""
Pipeline de sourcing de prospects paysagistes (NAF 81.30Z) -> fichier Excel.

Source unique de verite pour l'identite legale : API Recherche d'entreprises
(https://recherche-entreprises.api.gouv.fr) - donnees publiques SIRENE + RNE,
sans authentification.

Regle absolue : aucune donnee n'est deduite ni construite. Un champ sans source
reelle reste vide. En particulier, AUCUN email n'est jamais fabrique a partir
du nom de l'entreprise ou d'un nom de domaine.

Usage
-----
    python3 paysagistes_sirene.py --departements 33,40,47,64 --max 500

Fusion optionnelle d'un export de coordonnees (phase 2/3, ex. Google Maps) :

    python3 paysagistes_sirene.py --departements 33 --max 300 \
        --contacts export_maps.csv

Le CSV de contacts doit avoir un en-tete avec au moins les colonnes :
    nom, code_postal
et, quand elles existent :
    adresse, telephone, site_web, email
Les colonnes absentes sont traitees comme vides. Rien n'est invente.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
import time
import unicodedata
from datetime import date
from difflib import SequenceMatcher
from pathlib import Path

import requests
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font
from openpyxl.utils import get_column_letter

API_URL = "https://recherche-entreprises.api.gouv.fr/search"
NAF_PAYSAGISTE = "81.30Z"
PER_PAGE = 25          # maximum autorise par l'API
RATE_LIMIT_SLEEP = 0.2  # l'API plafonne a 7 req/s

COLUMNS = [
    "Entreprise", "Nom commercial", "SIREN", "Dirigeant(s)", "Email",
    "Type email", "Telephone", "WhatsApp probable", "Site web", "Adresse",
    "Code postal", "Ville", "Effectif", "Date creation",
    "Confiance matching", "Source email", "Date extraction",
]

TEXT_COLUMNS = {"SIREN", "Telephone", "Code postal"}

# Tranches d'effectif INSEE (code -> libelle)
TRANCHES_EFFECTIF = {
    "NN": "Non renseigne", "00": "0 salarie", "01": "1 ou 2 salaries",
    "02": "3 a 5 salaries", "03": "6 a 9 salaries", "11": "10 a 19 salaries",
    "12": "20 a 49 salaries", "21": "50 a 99 salaries",
    "22": "100 a 199 salaries", "31": "200 a 249 salaries",
    "32": "250 a 499 salaries", "41": "500 a 999 salaries",
    "42": "1 000 a 1 999 salaries", "51": "2 000 a 4 999 salaries",
    "52": "5 000 a 9 999 salaries", "53": "10 000 salaries et plus",
}

FORMES_JURIDIQUES = [
    "sarl", "sasu", "sas", "eurl", "eirl", "sci", "scic", "scop", "snc",
    "sa", "ei", "gie", "earl", "gaec", "scea", "sarlu", "selarl",
]

LOCAL_PARTS_GENERIQUES = {
    "contact", "contacts", "info", "infos", "accueil", "bonjour", "hello",
    "commercial", "commerce", "devis", "secretariat", "secretaria", "admin",
    "administration", "direction", "mail", "email", "societe", "entreprise",
    "service", "services", "client", "clients", "sav",
}

NON_DIFFUSIBLE_MARKERS = ("non-diffusible", "non diffusible")


# --------------------------------------------------------------------------
# Normalisation & matching
# --------------------------------------------------------------------------

def strip_accents(value: str) -> str:
    decomposed = unicodedata.normalize("NFD", value)
    return "".join(c for c in decomposed if unicodedata.category(c) != "Mn")


def normalize_name(value: str) -> str:
    """minuscules, sans accents, sans forme juridique, sans ponctuation."""
    if not value:
        return ""
    text = strip_accents(value).lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    tokens = [t for t in text.split() if t and t not in FORMES_JURIDIQUES]
    return " ".join(tokens)


def similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    ratio = SequenceMatcher(None, a, b).ratio()
    tokens_a, tokens_b = set(a.split()), set(b.split())
    if tokens_a and tokens_b:
        jaccard = len(tokens_a & tokens_b) / len(tokens_a | tokens_b)
        ratio = max(ratio, jaccard)
    return ratio


def confidence_label(score: float, same_cp: bool, same_city: bool) -> str | None:
    """ELEVE / MOYEN / FAIBLE, ou None si le rapprochement est rejete."""
    if same_cp and score >= 0.90:
        return "ELEVE"
    if same_cp and score >= 0.75:
        return "MOYEN"
    if same_cp and score >= 0.62:
        return "FAIBLE"
    if same_city and score >= 0.85:
        return "FAIBLE"
    return None


# --------------------------------------------------------------------------
# Validation / formatage
# --------------------------------------------------------------------------

def siren_is_valid(siren: str) -> bool:
    """Controle de Luhn : ecarte toute valeur qui n'est pas un SIREN reel."""
    if not (siren and siren.isdigit() and len(siren) == 9):
        return False
    total = 0
    for index, char in enumerate(siren):
        digit = int(char)
        if index % 2 == 1:
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit
    return total % 10 == 0


def to_e164(raw: str) -> str:
    """Numero francais -> +33XXXXXXXXX. Chaine vide si non reconnaissable."""
    if not raw:
        return ""
    digits = re.sub(r"\D", "", raw)
    if digits.startswith("0033"):
        digits = digits[4:]
    elif digits.startswith("33") and len(digits) == 11:
        digits = digits[2:]
    elif digits.startswith("0") and len(digits) == 10:
        digits = digits[1:]
    if len(digits) != 9 or digits[0] not in "123456789":
        return ""
    return "+33" + digits


def is_mobile(e164: str) -> bool:
    """Vrai uniquement pour les prefixes mobiles +336 / +337."""
    return e164.startswith("+336") or e164.startswith("+337")


def email_kind(email: str) -> str:
    if not email:
        return ""
    local = email.split("@", 1)[0].lower()
    if local in LOCAL_PARTS_GENERIQUES:
        return "GENERIQUE"
    if re.fullmatch(r"[a-z]+[._-][a-z]+", strip_accents(local)):
        return "NOMINATIF"
    return "GENERIQUE"


def format_date(iso_date: str) -> str:
    if not iso_date or len(iso_date) < 10:
        return ""
    year, month, day = iso_date[:4], iso_date[5:7], iso_date[8:10]
    return f"{day}/{month}/{year}"


# --------------------------------------------------------------------------
# Phase 1 - sourcing legal
# --------------------------------------------------------------------------

def is_diffusible(company: dict, siege: dict) -> bool:
    """Ecarte toute unite en diffusion partielle (statut 'P')."""
    for holder in (company, siege):
        for key in ("statut_diffusion", "statut_diffusion_etablissement"):
            if str(holder.get(key) or "").upper() == "P":
                return False
    name = (company.get("nom_complet") or "").lower()
    return not any(marker in name for marker in NON_DIFFUSIBLE_MARKERS)


def format_dirigeants(company: dict) -> str:
    """Prenom NOM, separes par ' ; '. Personnes morales incluses telles quelles."""
    parts: list[str] = []
    for dirigeant in company.get("dirigeants") or []:
        if dirigeant.get("type_dirigeant") == "personne morale":
            denomination = (dirigeant.get("denomination") or "").strip()
            if denomination:
                parts.append(denomination)
            continue
        prenoms = (dirigeant.get("prenoms") or "").strip()
        nom = (dirigeant.get("nom") or "").strip()
        full = " ".join(p for p in (prenoms.title(), nom.upper()) if p)
        if full:
            parts.append(full)
    # dedoublonnage en conservant l'ordre
    seen, unique = set(), []
    for part in parts:
        if part not in seen:
            seen.add(part)
            unique.append(part)
    return " ; ".join(unique)


def fetch_departement(departement: str, limit: int, session: requests.Session,
                      verbose: bool = True) -> list[dict]:
    """Toutes les entreprises actives NAF 81.30Z d'un departement."""
    rows: list[dict] = []
    page = 1
    while len(rows) < limit:
        params = {
            "activite_principale": NAF_PAYSAGISTE,
            "departement": departement,
            "etat_administratif": "A",
            "per_page": PER_PAGE,
            "page": page,
        }
        response = session.get(API_URL, params=params, timeout=30)
        response.raise_for_status()
        payload = response.json()
        results = payload.get("results") or []
        if not results:
            break

        for company in results:
            siege = company.get("siege") or {}
            siren = (company.get("siren") or "").strip()

            if not siren_is_valid(siren):
                continue
            if not is_diffusible(company, siege):
                continue
            if (siege.get("etat_administratif") or "A") != "A":
                continue

            rows.append({
                "Entreprise": (company.get("nom_complet")
                               or company.get("nom_raison_sociale") or "").strip(),
                "SIREN": siren,
                "Dirigeant(s)": format_dirigeants(company),
                "Adresse": (siege.get("adresse") or "").strip(),
                "Code postal": (siege.get("code_postal") or "").strip(),
                "Ville": (siege.get("libelle_commune") or "").strip(),
                "Effectif": TRANCHES_EFFECTIF.get(
                    company.get("tranche_effectif_salarie") or "NN",
                    "Non renseigne"),
                "Date creation": format_date(company.get("date_creation") or ""),
            })
            if len(rows) >= limit:
                break

        total_pages = payload.get("total_pages") or 1
        if verbose:
            print(f"  dep {departement} - page {page}/{total_pages} "
                  f"- {len(rows)} ligne(s) retenue(s)", file=sys.stderr)
        if page >= total_pages:
            break
        page += 1
        time.sleep(RATE_LIMIT_SLEEP)

    return rows


def dedupe_on_siren(rows: list[dict]) -> list[dict]:
    """Un SIREN = une ligne. On garde celle qui a le plus de champs remplis."""
    best: dict[str, dict] = {}
    for row in rows:
        siren = row["SIREN"]
        filled = sum(1 for value in row.values() if str(value).strip())
        if siren not in best or filled > best[siren]["_filled"]:
            best[siren] = {**row, "_filled": filled}
    return [{k: v for k, v in row.items() if k != "_filled"}
            for row in best.values()]


# --------------------------------------------------------------------------
# Phase 3 - matching avec un export de coordonnees
# --------------------------------------------------------------------------

def load_contacts(path: Path) -> list[dict]:
    contacts = []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        for raw in csv.DictReader(handle):
            entry = {(k or "").strip().lower(): (v or "").strip()
                     for k, v in raw.items()}
            name = entry.get("nom") or entry.get("name") or entry.get("title") or ""
            if not name:
                continue
            contacts.append({
                "nom": name,
                "code_postal": entry.get("code_postal") or entry.get("postalcode") or "",
                "ville": entry.get("ville") or entry.get("city") or "",
                "adresse": entry.get("adresse") or entry.get("address") or "",
                "telephone": entry.get("telephone") or entry.get("phone") or "",
                "site_web": entry.get("site_web") or entry.get("website") or "",
                "email": entry.get("email") or "",
                "_norm": normalize_name(name),
            })
    return contacts


def match_contacts(rows: list[dict], contacts: list[dict]) -> int:
    """Enrichit les lignes SIRENE sur place. Sans correspondance -> champs vides.

    Retourne le nombre de lignes effectivement rapprochees.
    """
    used: set[int] = set()
    matched = 0
    for row in rows:
        row_norm = normalize_name(row["Entreprise"])
        row_cp = row["Code postal"]
        row_city = normalize_name(row["Ville"])

        best_index, best_label, best_score = None, None, 0.0
        for index, contact in enumerate(contacts):
            if index in used:
                continue
            score = similarity(row_norm, contact["_norm"])
            label = confidence_label(
                score,
                same_cp=bool(row_cp) and row_cp == contact["code_postal"],
                same_city=bool(row_city) and row_city == normalize_name(contact["ville"]),
            )
            if label and score > best_score:
                best_index, best_label, best_score = index, label, score

        if best_index is None:
            continue

        used.add(best_index)
        matched += 1
        contact = contacts[best_index]
        phone = to_e164(contact["telephone"])
        email = contact["email"] if "@" in contact["email"] else ""

        if normalize_name(contact["nom"]) != row_norm:
            row["Nom commercial"] = contact["nom"]
        row["Telephone"] = phone
        row["WhatsApp probable"] = "OUI" if is_mobile(phone) else "NON"
        row["Site web"] = contact["site_web"]
        row["Email"] = email
        row["Type email"] = email_kind(email)
        row["Source email"] = "GOOGLE_MAPS" if email else "AUCUNE"
        row["Confiance matching"] = best_label

    return matched


# --------------------------------------------------------------------------
# Phase 4 - export Excel
# --------------------------------------------------------------------------

def write_xlsx(rows: list[dict], path: Path) -> None:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Prospects"

    sheet.append(COLUMNS)
    for cell in sheet[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(vertical="center")

    for row in rows:
        sheet.append([row.get(column, "") for column in COLUMNS])

    # codes postaux, telephones et SIREN en texte : les zeros de tete restent
    text_indexes = [COLUMNS.index(name) + 1 for name in TEXT_COLUMNS]
    for excel_row in sheet.iter_rows(min_row=2):
        for index in text_indexes:
            excel_row[index - 1].number_format = "@"

    sheet.freeze_panes = "A2"
    sheet.auto_filter.ref = sheet.dimensions

    for index, column in enumerate(COLUMNS, start=1):
        longest = max([len(column)] +
                      [len(str(row.get(column, ""))) for row in rows] or [0])
        sheet.column_dimensions[get_column_letter(index)].width = min(longest + 3, 55)

    workbook.save(path)


# --------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--departements", required=True,
                        help="Codes departements separes par des virgules, ex: 33,40,47,64")
    parser.add_argument("--max", type=int, default=500,
                        help="Nombre maximum d'entreprises au total (defaut: 500)")
    parser.add_argument("--contacts", type=Path,
                        help="CSV de coordonnees a rapprocher (phase 2/3), optionnel")
    parser.add_argument("--out-dir", type=Path, default=Path("."),
                        help="Repertoire de sortie du .xlsx")
    args = parser.parse_args()

    departements = [d.strip() for d in args.departements.split(",") if d.strip()]
    if not departements:
        parser.error("aucun departement valide")

    today = date.today()
    session = requests.Session()
    session.headers["User-Agent"] = "prospection-paysagistes/1.0"

    print(f"PHASE 1 - sourcing SIRENE/RNE, NAF {NAF_PAYSAGISTE}, "
          f"departements {', '.join(departements)}", file=sys.stderr)

    collected: list[dict] = []
    per_dept = max(1, args.max // len(departements))
    try:
        for departement in departements:
            remaining = args.max - len(collected)
            if remaining <= 0:
                break
            collected += fetch_departement(
                departement, min(per_dept, remaining), session)
    except requests.RequestException as exc:
        print(f"\nERREUR reseau : {API_URL} injoignable ({exc.__class__.__name__}).",
              file=sys.stderr)
        print("Aucun fichier n'est genere : mieux vaut zero ligne qu'une ligne "
              "inventee.", file=sys.stderr)
        print("Verifiez la connectivite sortante vers "
              "recherche-entreprises.api.gouv.fr (port 443).", file=sys.stderr)
        return 2

    rows = dedupe_on_siren(collected)[:args.max]
    rows.sort(key=lambda r: (r["Code postal"], r["Entreprise"]))

    extraction_date = today.strftime("%d/%m/%Y")
    for row in rows:
        row.setdefault("Nom commercial", "")
        row.setdefault("Email", "")
        row.setdefault("Type email", "")
        row.setdefault("Telephone", "")
        row.setdefault("WhatsApp probable", "NON")
        row.setdefault("Site web", "")
        row["Confiance matching"] = "FAIBLE"   # aucune correspondance contact
        row["Source email"] = "AUCUNE"
        row["Date extraction"] = extraction_date

    print(f"OK PHASE 1 terminee - {len(rows)} lignes - etablissements actifs, "
          f"diffusion partielle exclue, dedoublonne sur SIREN", file=sys.stderr)

    if args.contacts:
        contacts = load_contacts(args.contacts)
        matched = match_contacts(rows, contacts)
        print(f"OK PHASE 3 terminee - {matched} lignes enrichies sur "
              f"{len(rows)} - matching flou nom + code postal", file=sys.stderr)

    zone = "-".join(departements)
    out_path = args.out_dir / f"paysagistes_france_{zone}_{today:%Y%m%d}.xlsx"
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_xlsx(rows, out_path)
    print(f"OK PHASE 4 terminee - {len(rows)} lignes - {out_path}", file=sys.stderr)

    total = len(rows) or 1
    emails = sum(1 for r in rows if r["Email"])
    dirigeants = sum(1 for r in rows if r["Dirigeant(s)"])
    mobiles = sum(1 for r in rows if is_mobile(r["Telephone"]))
    phones = sum(1 for r in rows if r["Telephone"])
    print("\nRECAPITULATIF", file=sys.stderr)
    print(f"  total lignes            : {len(rows)}", file=sys.stderr)
    print(f"  remplissage email       : {emails}/{len(rows)} ({emails/total:.1%})", file=sys.stderr)
    print(f"  remplissage dirigeant   : {dirigeants}/{len(rows)} ({dirigeants/total:.1%})", file=sys.stderr)
    print(f"  numeros mobiles         : {mobiles}/{phones or 0} numero(s)", file=sys.stderr)
    print("  cout runs Apify         : 0,00 $ (aucune run lancee)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
