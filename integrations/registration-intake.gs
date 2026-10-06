/** Ecotech 12 Connect: append-only registration webhook. No read endpoint. */
const SHEET_ID = PropertiesService.getScriptProperties().getProperty('REGISTRATION_SHEET_ID');
const COLUMNS = {"Candidates":["Received at","Reference","Full name","Mobile","email","Locality","PIN code","Contact preference","Preferred language","Industry","Interested roles","Experience","Education","Skills","Work type","Availability","Expected monthly pay INR","Shift preference","Commute","LinkedIn","Qualification trade","Institute","Last employer","Last role","Certifications","Notes","Attachment name","Form language","Campaign","Consent","Consent version","Submitted at"],"Vendors":["Received at","Reference","Full name","Mobile","email","Locality","PIN code","Contact preference","Preferred language","Business name","Service category","Offering","Business type","Service area","Other service area","Years in business","Team size","Capacity","GST status","Website","Certifications","Notes","Attachment name","Form language","Campaign","Consent","Consent version","Submitted at"]};

function doGet() { return reply_({service: 'Ecotech 12 Connect intake'}); }

function doPost(e) {
  const raw = e && e.postData && e.postData.contents;
  if (!raw || raw.length > 64000) throw new Error('Invalid payload');
  let envelope;
  try { envelope = JSON.parse(raw); } catch (_) { throw new Error('Invalid JSON'); }
  // FormSubmit currently JSON-encodes form_data inside the outer JSON object.
  let data = envelope.form_data;
  if (typeof data === 'string') {
    try { data = JSON.parse(data); } catch (_) { throw new Error('Invalid form JSON'); }
  }
  if (!data || typeof data !== 'object' || Array.isArray(data)) throw new Error('Invalid form');
  // Native multipart submissions normalize spaces to underscores; AJAX keeps spaces.
  data = Object.fromEntries(Object.entries(data).map(([key, value]) => [key.replace(/_/g, ' '), value]));
  const type = data['Registration type'];
  const tab = type === 'Candidate' ? 'Candidates' : type === 'Vendor' ? 'Vendors' : null;
  if (!tab) throw new Error('Invalid registration type');
  const headers = COLUMNS[tab];
  if (!/^E12-[A-Z0-9]{8}$/.test(data.Reference || '')) throw new Error('Invalid reference');
  if (data.Campaign !== 'Ramlila fair 2026') throw new Error('Invalid campaign');
  if (data['Consent version'] !== '2026-10-06-v2' || !String(data.Consent || '').startsWith('Agreed:')) throw new Error('Consent required');
  const required = ['Full name', 'Mobile', 'Locality'];
  required.forEach(key => { if (typeof data[key] !== 'string' || !data[key].trim()) throw new Error('Required field missing'); });
  if (!/^(?:91)?[6-9]\d{9}$/.test(data.Mobile.replace(/[\s()+-]/g, ''))) throw new Error('Invalid mobile');
  const row = headers.map(header => {
    if (header === 'Received at') return new Date();
    const value = data[header];
    if (value == null) return '';
    if (typeof value !== 'string' && typeof value !== 'number') throw new Error('Invalid field type');
    const text = String(value);
    if (text.length > 6000) throw new Error('Field too long');
    // Treat every submitted value as text, including spreadsheet formula prefixes.
    return text ? "'" + text : '';
  });
  const lock = LockService.getScriptLock();
  lock.waitLock(25000);
  try {
    const sheet = SpreadsheetApp.openById(SHEET_ID).getSheetByName(tab);
    if (!sheet || JSON.stringify(sheet.getRange(1, 1, 1, headers.length).getValues()[0]) !== JSON.stringify(headers)) throw new Error('Intake schema mismatch');
    const last = sheet.getLastRow();
    if (last > 1 && sheet.getRange(2, 2, last - 1, 1).createTextFinder(data.Reference).matchEntireCell(true).findNext()) return reply_({ok: true, duplicate: true});
    if (last === sheet.getMaxRows()) sheet.insertRowsAfter(last, 500);
    const target = sheet.getRange(last + 1, 1, 1, headers.length);
    target.setNumberFormat('@');
    target.setValues([row]);
    sheet.getRange(last + 1, 1).setNumberFormat('yyyy-mm-dd hh:mm:ss');
    SpreadsheetApp.flush();
    return reply_({ok: true});
  } finally { lock.releaseLock(); }
}

// HtmlService returns a direct HTTP response. ContentService redirects to a
// googleusercontent URL, which can break FormSubmit's native webhook delivery.
function reply_(value) { return HtmlService.createHtmlOutput(JSON.stringify(value)); }
