/**
 * PolynetIA — Réception du formulaire « diagnostic » dans Google Sheets
 * ---------------------------------------------------------------------
 * Ce script reçoit les envois du formulaire de la landing page et ajoute
 * une ligne dans une feuille Google Sheets.
 *
 * MISE EN PLACE (5 minutes) :
 *
 * 1. Crée (ou ouvre) une feuille Google Sheets qui recevra les demandes.
 * 2. Menu « Extensions » > « Apps Script ».
 * 3. Supprime le code par défaut, colle CE fichier en entier, puis
 *    enregistre (icône disquette).
 * 4. Clique sur « Déployer » > « Nouveau déploiement ».
 *      - Type : « Application web »
 *      - Description : PolynetIA formulaire
 *      - Exécuter en tant que : Moi
 *      - Qui a accès : « Tout le monde »
 * 5. Clique « Déployer », autorise l'accès, puis COPIE l'URL de
 *    l'application web (elle se termine par « /exec »).
 * 6. Colle cette URL dans la variable SHEET_ENDPOINT du fichier index.html.
 *
 * Astuce : après une modification du script, refais « Déployer » >
 * « Gérer les déploiements » > modifie le déploiement existant pour
 * conserver la même URL /exec.
 */

// Nom de l'onglet où écrire les demandes (créé automatiquement s'il manque).
var SHEET_NAME = 'Demandes';

// Ordre des colonnes dans la feuille.
var HEADERS = [
  'date', 'prenom', 'entreprise', 'metier', 'commune',
  'tel', 'email', 'site', 'google', 'probleme', 'capacite', 'source'
];

function doPost(e) {
  var lock = LockService.getScriptLock();
  lock.tryLock(30000);
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName(SHEET_NAME) || ss.insertSheet(SHEET_NAME);

    // Écrit l'en-tête si la feuille est vide.
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
