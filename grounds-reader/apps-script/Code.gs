/**
 * Google Apps Script for Read Your Grounds email capture
 *
 * Writes to the "grinds" tab in PA Welcome Sequence spreadsheet.
 * Columns: email | first_name | signup_date | emails_sent | status
 */

const SPREADSHEET_ID = '1UyY3cTYmLAWDgNQehS5sDC7lxUXFdCo5_DQUii0-ok0';
const SHEET_NAME = 'grinds';

function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);

    if (data.action === 'grounds_subscribe') {
      return handleGroundsSubscribe(data);
    }

    return jsonResponse({ error: 'Unknown action' });
  } catch (error) {
    console.error('doPost error:', error);
    return jsonResponse({ error: error.message });
  }
}

function doGet(e) {
  return jsonResponse({
    status: 'ok',
    message: 'Grounds Reader email endpoint is running',
    timestamp: new Date().toISOString()
  });
}

function handleGroundsSubscribe(data) {
  const { email, first_name, reading_id, timestamp } = data;

  if (!email) {
    return jsonResponse({ error: 'Email is required' });
  }

  const normalizedEmail = email.toLowerCase().trim();
  const sheet = getSheet();

  // Check for existing email (deduplication)
  const existingRow = findEmailRow(sheet, normalizedEmail);

  if (existingRow) {
    return jsonResponse({
      success: true,
      action: 'updated',
      message: 'Email already exists'
    });
  }

  // Add new record matching grinds tab columns:
  // email | first_name | signup_date | emails_sent | status
  const signupDate = timestamp || new Date().toISOString();
  sheet.appendRow([
    normalizedEmail,        // A: email
    first_name || '',       // B: first_name
    signupDate,             // C: signup_date
    0,                      // D: emails_sent
    'new',                  // E: status
  ]);

  console.log('Added grounds reader email: ' + normalizedEmail);
  return jsonResponse({
    success: true,
    action: 'created',
    message: 'Email added to grinds list'
  });
}

function getSheet() {
  const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  const sheet = ss.getSheetByName(SHEET_NAME);
  if (!sheet) {
    throw new Error('Sheet "' + SHEET_NAME + '" not found');
  }
  return sheet;
}

function findEmailRow(sheet, email) {
  const data = sheet.getDataRange().getValues();
  for (let i = 1; i < data.length; i++) {
    if (data[i][0] && data[i][0].toString().toLowerCase().trim() === email) {
      return i + 1;
    }
  }
  return null;
}

function jsonResponse(data) {
  const output = ContentService.createTextOutput(JSON.stringify(data));
  output.setMimeType(ContentService.MimeType.JSON);
  return output;
}

function testSetup() {
  const sheet = getSheet();
  console.log('Sheet name: ' + sheet.getName());
  console.log('Headers: ' + sheet.getRange(1, 1, 1, 5).getValues()[0].join(' | '));
}
