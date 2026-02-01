const crypto = require('crypto');
const https = require('https');

// Load .env
require('dotenv').config({ path: '/Users/randypellegrini/Documents/antigravity/.env' });

// Gemini API call
function checkGemini() {
  return new Promise((resolve, reject) => {
    const apiKey = process.env.GEMINI_API_KEY;
    const apiSecret = process.env.GEMINI_API_SECRET;
    const sandbox = process.env.GEMINI_SANDBOX === 'true';

    const baseUrl = sandbox ? 'api.sandbox.gemini.com' : 'api.gemini.com';

    const payload = {
      request: '/v1/balances',
      nonce: Date.now()
    };

    const b64 = Buffer.from(JSON.stringify(payload)).toString('base64');
    const signature = crypto.createHmac('sha384', apiSecret).update(b64).digest('hex');

    const options = {
      hostname: baseUrl,
      path: '/v1/balances',
      method: 'POST',
      headers: {
        'Content-Type': 'text/plain',
        'X-GEMINI-APIKEY': apiKey,
        'X-GEMINI-PAYLOAD': b64,
        'X-GEMINI-SIGNATURE': signature
      }
    };

    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        try {
          const balances = JSON.parse(data);
          resolve({
            environment: sandbox ? 'SANDBOX' : 'LIVE PRODUCTION',
            baseUrl,
            balances
          });
        } catch (e) {
          reject(new Error('Parse error: ' + data));
        }
      });
    });

    req.on('error', reject);
    req.end();
  });
}

// Alpaca API call
function checkAlpaca() {
  return new Promise((resolve, reject) => {
    const apiKey = process.env.ALPACA_API_KEY;
    const apiSecret = process.env.ALPACA_API_SECRET;
    const baseUrl = process.env.ALPACA_BASE_URL || 'https://api.alpaca.markets';

    const isPaper = baseUrl.includes('paper');
    const hostname = new URL(baseUrl).hostname;

    const options = {
      hostname: hostname,
      path: '/v2/account',
      method: 'GET',
      headers: {
        'APCA-API-KEY-ID': apiKey,
        'APCA-API-SECRET-KEY': apiSecret
      }
    };

    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        try {
          const account = JSON.parse(data);
          resolve({
            environment: isPaper ? 'PAPER TRADING' : 'LIVE PRODUCTION',
            baseUrl,
            account
          });
        } catch (e) {
          reject(new Error('Parse error: ' + data));
        }
      });
    });

    req.on('error', reject);
    req.end();
  });
}

// Get Alpaca positions
function getAlpacaPositions() {
  return new Promise((resolve, reject) => {
    const apiKey = process.env.ALPACA_API_KEY;
    const apiSecret = process.env.ALPACA_API_SECRET;
    const baseUrl = process.env.ALPACA_BASE_URL || 'https://api.alpaca.markets';
    const hostname = new URL(baseUrl).hostname;

    const options = {
      hostname: hostname,
      path: '/v2/positions',
      method: 'GET',
      headers: {
        'APCA-API-KEY-ID': apiKey,
        'APCA-API-SECRET-KEY': apiSecret
      }
    };

    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        try {
          const positions = JSON.parse(data);
          resolve(positions);
        } catch (e) {
          reject(new Error('Parse error: ' + data));
        }
      });
    });

    req.on('error', reject);
    req.end();
  });
}

// Main
async function main() {
  console.log('🔍 VALIDATING EXCHANGE ACCOUNTS');
  console.log('='.repeat(70));
  console.log();

  // Check Gemini
  try {
    const gemini = await checkGemini();
    console.log('💎 GEMINI ACCOUNT');
    console.log('-'.repeat(70));
    console.log('Environment:', gemini.environment);
    console.log('API Endpoint:', gemini.baseUrl);
    console.log();
    console.log('BALANCES:');

    let totalUSD = 0;
    let hasCrypto = false;

    gemini.balances.forEach(bal => {
      const available = parseFloat(bal.available);
      const amount = parseFloat(bal.amount);

      if (amount > 0.00000001) {
        console.log('  ' + bal.currency + ':');
        console.log('    Available: ' + available.toFixed(8));
        console.log('    Total: ' + amount.toFixed(8));

        if (bal.currency === 'USD') {
          totalUSD += available;
        } else {
          hasCrypto = true;
        }
      }
    });

    console.log();
    console.log('💵 USD Cash: $' + totalUSD.toFixed(2));
    console.log('📊 Has Crypto Positions: ' + (hasCrypto ? 'YES' : 'NO'));
    console.log();

  } catch (err) {
    console.log('❌ GEMINI ERROR:', err.message);
    console.log();
  }

  // Check Alpaca
  try {
    const alpaca = await checkAlpaca();
    const positions = await getAlpacaPositions();

    console.log('📈 ALPACA ACCOUNT');
    console.log('-'.repeat(70));
    console.log('Environment:', alpaca.environment);
    console.log('API Endpoint:', alpaca.baseUrl);
    console.log();
    console.log('ACCOUNT STATUS:');
    console.log('  Cash: $' + parseFloat(alpaca.account.cash).toFixed(2));
    console.log('  Portfolio Value: $' + parseFloat(alpaca.account.portfolio_value).toFixed(2));
    console.log('  Equity: $' + parseFloat(alpaca.account.equity).toFixed(2));
    console.log('  Buying Power: $' + parseFloat(alpaca.account.buying_power).toFixed(2));
    console.log('  Account Status: ' + alpaca.account.status);
    console.log('  Pattern Day Trader: ' + alpaca.account.pattern_day_trader);
    console.log();

    if (positions.length > 0) {
      console.log('CURRENT POSITIONS:');
      positions.forEach(pos => {
        const qty = parseFloat(pos.qty);
        const value = parseFloat(pos.market_value);
        const pl = parseFloat(pos.unrealized_pl);
        const plPct = parseFloat(pos.unrealized_plpc) * 100;

        console.log('  ' + pos.symbol + ':');
        console.log('    Quantity: ' + qty);
        console.log('    Market Value: $' + value.toFixed(2));
        console.log('    Unrealized P/L: $' + pl.toFixed(2) + ' (' + plPct.toFixed(2) + '%)');
      });
      console.log();
    } else {
      console.log('📊 No open positions');
      console.log();
    }

  } catch (err) {
    console.log('❌ ALPACA ERROR:', err.message);
    console.log();
  }
}

main().catch(console.error);
