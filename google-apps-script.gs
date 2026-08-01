/**
 * PolynetIA — Réception du formulaire « diagnostic » + suivi des demandes
 * ----------------------------------------------------------------------
 * Ce script enregistre chaque envoi du formulaire de la landing page dans
 * ta feuille Google Sheets, et prépare une structure de suivi commercial
 * (colonnes de statut, relance et notes).
 *
 * MISE EN PLACE (une seule fois) :
 *
 * 1. Ouvre ta feuille :
 *    https://docs.google.com/spreadsheets/d/1OdmUsqg5Lx1chK9YKD0ryp7rT_gABr_xZZVjSYFlQok/edit
 * 2. Menu « Extensions » > « Apps Script ».
 * 3. Supprime le code par défaut, colle CE fichier en entier, enregistre
 *    (icône disquette).
 * 4. En haut de l'éditeur, choisis la fonction « initialiser » puis clique
 *    sur « Exécuter ». Autorise l'accès quand Google le demande.
 *    → Cela crée l'onglet « Demandes », l'en-tête et le menu déroulant
 *      de statut.
 * 5. Clique « Déployer » > « Nouveau déploiement ».
 *      - Type : « Application web »
 *      - Description : PolynetIA formulaire
 *      - Exécuter en tant que : Moi
 *      - Qui a accès : « Tout le monde »
 * 6. Clique « Déployer », puis COPIE l'URL qui se termine par « /exec ».
 * 7. Colle cette URL dans la variable SHEET_ENDPOINT du fichier index.html.
 *
 * Astuce : après une modification du script, refais « Déployer » >
 * « Gérer les déploiements » > modifie le déploiement existant pour
 * conserver la même URL /exec.
 */

// ID de la feuille Google Sheets qui reçoit les demandes.
var SPREADSHEET_ID = '1OdmUsqg5Lx1chK9YKD0ryp7rT_gABr_xZZVjSYFlQok';

// Nom de l'onglet où écrire les demandes (créé automatiquement s'il manque).
var SHEET_NAME = 'Demandes';

// Colonnes envoyées par le formulaire (ne pas réordonner sans mettre à jour index.html).
var CHAMPS = [
  'date', 'prenom', 'entreprise', 'metier', 'commune',
  'tel', 'email', 'site', 'google', 'probleme', 'capacite', 'source'
];

// Colonnes de suivi ajoutées à droite (remplies à la main dans la feuille).
var SUIVI = ['statut', 'relance', 'notes'];

// En-tête complet.
var HEADERS = CHAMPS.concat(SUIVI);

// Choix possibles du menu déroulant « statut ».
var STATUTS = [
  'Nouveau', 'Contacté', 'RDV pris', 'Diagnostic fait',
  'Proposition envoyée', 'Client', 'Perdu'
];

/**
 * À exécuter UNE FOIS depuis l'éditeur : prépare l'onglet, l'en-tête,
 * le figeage de la première ligne et le menu déroulant de statut.
 */
function initialiser() {
  var ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  var sheet = ss.getSheetByName(SHEET_NAME) || ss.insertSheet(SHEET_NAME);

  // En-tête
  sheet.getRange(1, 1, 1, HEADERS.length)
    .setValues([HEADERS])
    .setFontWeight('bold')
    .setBackground('#1a73e8')
    .setFontColor('#ffffff');
  sheet.setFrozenRows(1);

  // Menu déroulant sur la colonne « statut »
  var col = HEADERS.indexOf('statut') + 1;
  if (col > 0) {
    var regle = SpreadsheetApp.newDataValidation()
      .requireValueInList(STATUTS, true)
      .setAllowInvalid(false)
      .build();
    sheet.getRange(2, col, 2000, 1).setDataValidation(regle);
  }

  sheet.autoResizeColumns(1, HEADERS.length);
}

/**
 * Reçoit les envois du formulaire (POST) et ajoute une ligne.
 * La colonne « statut » des nouvelles demandes est pré-remplie « Nouveau ».
 */
function doPost(e) {
  var lock = LockService.getScriptLock();
  lock.tryLock(30000);
  try {
    var ss = SpreadsheetApp.openById(SPREADSHEET_ID);
    var sheet = ss.getSheetByName(SHEET_NAME) || ss.insertSheet(SHEET_NAME);

    // Crée l'en-tête si la feuille est vide.
    if (sheet.getLastRow() === 0) {
      sheet.appendRow(HEADERS);
    }

    var data = {};
    if (e && e.postData && e.postData.contents) {
      data = JSON.parse(e.postData.contents);
    } else if (e && e.parameter) {
      data = e.parameter; // repli si envoi en query string
    }

    var row = HEADERS.map(function (key) {
      if (key === 'statut') { return 'Nouveau'; }
      return data[key] != null ? data[key] : '';
    });
    sheet.appendRow(row);

    return json({ ok: true });
  } catch (err) {
    return json({ ok: false, error: String(err) });
  } finally {
    lock.releaseLock();
  }
}

// Permet un test rapide dans le navigateur (ouvre l'URL /exec).
function doGet() {
  return json({ ok: true, message: 'PolynetIA endpoint actif.' });
}

function json(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
