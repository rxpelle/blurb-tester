const ALLOWED_ORIGINS = [
  'https://randypellegrini.com',
  'http://localhost:8080',
  'http://localhost:8081',
];

const SYSTEM_PROMPT = `You are a reader of coffee grounds and tea leaves — a practitioner of tasseography, the ancient art of finding patterns where others see chaos. This is exactly what Sarah Chen does in The Genesis Protocol: she reads the hidden architecture beneath the surface.

The patterns in a cup are like genetic sequences — seemingly random, but encoding information about what's coming. The same defensive network that's been reading patterns since the Bronze Age taught that every residue tells a story.

When analyzing the cup image:
1. IDENTIFY 2-3 specific shapes or formations you see in the residue
2. INTERPRET each using the language of hidden patterns, genetic memory, and generational knowledge
3. DELIVER a weekly prediction (3-4 sentences) — specific, actionable, tied to themes of discovery, resilience, and the patterns hiding in plain sight
4. End with a one-line "protocol fragment" in italics — a mysterious sentence that sounds like it could be from a classified GenVault document

Format your response as:

**The Patterns**
[Your shape identifications and interpretations]

**Your Week Ahead**
[Your 3-4 sentence prediction]

*[Your protocol fragment]*

Keep under 250 words total. Write in second person ("You..."). Be specific about what you see in the image. If the image isn't a cup or doesn't contain readable residue, gracefully acknowledge this and still deliver an entertaining reading based on whatever you can see. Do NOT mention being an AI.`;

const GOOGLE_APPS_SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbwlmi9FeZlAeICXIImBGDU4-zKo1iwdMmVmzzaP68tD-uoTAP0ZmPK38zL-qOkY3VRX1A/exec';

function corsHeaders(origin) {
  const allowed = ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0];
  return {
    'Access-Control-Allow-Origin': allowed,
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, X-API-Key',
    'Access-Control-Max-Age': '86400',
  };
}

function jsonResponse(data, status, origin) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json', ...corsHeaders(origin) },
  });
}

async function checkRateLimit(ip, env) {
  const key = `rate:${ip}`;
  const current = await env.RATE_LIMITS.get(key);
  const count = current ? parseInt(current, 10) : 0;
  if (count >= 3) return false;
  // TTL of 86400 seconds (24 hours)
  await env.RATE_LIMITS.put(key, String(count + 1), { expirationTtl: 86400 });
  return true;
}

function generateId() {
  const chars = 'abcdefghijkmnpqrstuvwxyz23456789';
  let id = '';
  for (let i = 0; i < 8; i++) {
    id += chars[Math.floor(Math.random() * chars.length)];
  }
  return id;
}

function isValidEmail(email) {
  return Boolean(email && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email));
}

async function callClaude(imageBase64, mediaType, firstName, apiKey) {
  const seekerName = firstName || 'a curious soul';

  const response = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': apiKey,
      'anthropic-version': '2023-06-01',
    },
    body: JSON.stringify({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 512,
      system: SYSTEM_PROMPT,
      messages: [
        {
          role: 'user',
          content: [
            {
              type: 'image',
              source: {
                type: 'base64',
                media_type: mediaType,
                data: imageBase64,
              },
            },
            {
              type: 'text',
              text: `Read the patterns in this cup. The seeker's name is ${seekerName}.`,
            },
          ],
        },
      ],
    }),
  });

  if (!response.ok) {
    const err = await response.text();
    throw new Error(`Claude API error ${response.status}: ${err}`);
  }

  const data = await response.json();
  return data.content[0].text;
}

/**
 * Store email in KV for resilience. Creates/updates email index.
 */
async function storeEmailInKV(email, firstName, readingId, env) {
  const timestamp = new Date().toISOString();
  const normalizedEmail = email.toLowerCase().trim();
  
  // Store email:{id} for easy lookup
  await env.READINGS.put(
    `email:${readingId}`,
    JSON.stringify({ email: normalizedEmail, firstName, timestamp }),
    { expirationTtl: 365 * 24 * 60 * 60 } // 1 year
  );
  
  // Update or create emails:{email} index
  const indexKey = `emails:${normalizedEmail}`;
  const existingIndex = await env.READINGS.get(indexKey);
  
  let indexData;
  if (existingIndex) {
    indexData = JSON.parse(existingIndex);
    indexData.readingIds.push(readingId);
    indexData.lastSeen = timestamp;
    // Update firstName if provided and wasn't before
    if (firstName && !indexData.firstName) {
      indexData.firstName = firstName;
    }
  } else {
    indexData = {
      email: normalizedEmail,
      firstName: firstName || null,
      readingIds: [readingId],
      firstSeen: timestamp,
      lastSeen: timestamp,
    };
  }
  
  await env.READINGS.put(indexKey, JSON.stringify(indexData), {
    expirationTtl: 365 * 24 * 60 * 60, // 1 year
  });
  
  return indexData;
}

/**
 * Store a failed email push for later retry
 */
async function storeFailedEmail(email, firstName, readingId, error, env) {
  const timestamp = new Date().toISOString();
  const failedKey = `failed_email:${readingId}`;
  
  await env.READINGS.put(
    failedKey,
    JSON.stringify({
      email,
      firstName,
      readingId,
      error: error.message || String(error),
      timestamp,
      retryCount: 0,
    }),
    { expirationTtl: 30 * 24 * 60 * 60 } // 30 days
  );
  
  console.error(`Stored failed email for later retry: ${failedKey}`);
}

/**
 * Subscribe email to Google Sheets with retry logic
 */
async function subscribeEmail(email, firstName, readingId, env) {
  const payload = {
    action: 'grounds_subscribe',
    email,
    first_name: firstName || '',
    reading_id: readingId,
    timestamp: new Date().toISOString(),
  };
  
  let lastError = null;
  
  // Try up to 2 times (initial + 1 retry)
  for (let attempt = 0; attempt < 2; attempt++) {
    try {
      const response = await fetch(GOOGLE_APPS_SCRIPT_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'text/plain' },
        body: JSON.stringify(payload),
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }
      
      const result = await response.json();
      if (result.error) {
        throw new Error(result.error);
      }
      
      console.log(`Email subscribed successfully: ${email} (attempt ${attempt + 1})`);
      return true;
    } catch (e) {
      lastError = e;
      console.error(`Email subscribe attempt ${attempt + 1} failed:`, e.message);
      
      // Wait 500ms before retry
      if (attempt < 1) {
        await new Promise(resolve => setTimeout(resolve, 500));
      }
    }
  }
  
  // Both attempts failed - store for later retry
  console.error(`Email subscribe failed after 2 attempts: ${email}`, lastError);
  await storeFailedEmail(email, firstName, readingId, lastError, env);
  return false;
}

async function handleReadGrounds(request, env, ctx) {
  const origin = request.headers.get('Origin') || '';

  // Parse multipart form data
  const formData = await request.formData();
  const imageFile = formData.get('image');
  const email = formData.get('email');
  const firstName = formData.get('firstName');

  // Validate image
  if (!imageFile || !(imageFile instanceof File)) {
    return jsonResponse({ error: 'No image provided' }, 400, origin);
  }

  const allowedTypes = ['image/jpeg', 'image/png', 'image/webp'];
  if (!allowedTypes.includes(imageFile.type)) {
    return jsonResponse({ error: 'Image must be JPEG, PNG, or WebP' }, 400, origin);
  }

  if (imageFile.size > 5 * 1024 * 1024) {
    return jsonResponse({ error: 'Image must be under 5MB' }, 400, origin);
  }

  // Email is optional — users can subscribe after seeing their reading
  // If provided, validate format
  if (email && !isValidEmail(email)) {
    return jsonResponse({ error: 'Invalid email format' }, 400, origin);
  }

  // Rate limit
  const ip = request.headers.get('CF-Connecting-IP') || 'unknown';
  const allowed = await checkRateLimit(ip, env);
  if (!allowed) {
    return jsonResponse(
      { error: 'Limit reached — 3 readings per day. Come back tomorrow for a fresh cup.' },
      429,
      origin
    );
  }

  // Convert image to base64 (chunked to avoid stack overflow on large images)
  const arrayBuffer = await imageFile.arrayBuffer();
  const bytes = new Uint8Array(arrayBuffer);
  let binary = '';
  for (let i = 0; i < bytes.length; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  const base64 = btoa(binary);

  // Call Claude vision
  const reading = await callClaude(base64, imageFile.type, firstName, env.ANTHROPIC_API_KEY);

  // Generate shareable ID
  const id = generateId();
  const timestamp = new Date().toISOString();
  const normalizedEmail = email ? email.toLowerCase().trim() : null;

  // Store reading (email may or may not be present)
  await env.READINGS.put(
    `reading:${id}`,
    JSON.stringify({
      reading,
      firstName: firstName || null,
      email: normalizedEmail,
      timestamp,
    }),
    { expirationTtl: 30 * 24 * 60 * 60 } // 30 days
  );

  // If email was provided upfront, store and subscribe
  if (normalizedEmail) {
    await storeEmailInKV(normalizedEmail, firstName, id, env);

    // Subscribe email to Google Sheets (non-blocking, with retry)
    if (ctx) {
      ctx.waitUntil(subscribeEmail(normalizedEmail, firstName, id, env));
    } else {
      subscribeEmail(normalizedEmail, firstName, id, env);
    }
  }

  return jsonResponse({ id, reading }, 200, origin);
}

/**
 * POST /api/reading/:id/subscribe
 * Accepts email + firstName after the reading has been shown.
 * Links the email to the existing reading and pushes to Sheets.
 */
async function handleSubscribe(id, request, env, ctx) {
  const origin = request.headers.get('Origin') || '';

  // Parse JSON body
  let body;
  try {
    body = await request.json();
  } catch {
    return jsonResponse({ error: 'Invalid JSON body' }, 400, origin);
  }

  const { email, firstName } = body;

  if (!isValidEmail(email)) {
    return jsonResponse({ error: 'Valid email is required' }, 400, origin);
  }

  // Verify reading exists
  const stored = await env.READINGS.get(`reading:${id}`);
  if (!stored) {
    return jsonResponse({ error: 'Reading not found' }, 404, origin);
  }

  const normalizedEmail = email.toLowerCase().trim();

  // Update reading record with email
  const readingData = JSON.parse(stored);
  readingData.email = normalizedEmail;
  if (firstName) readingData.firstName = firstName;
  await env.READINGS.put(`reading:${id}`, JSON.stringify(readingData), {
    expirationTtl: 30 * 24 * 60 * 60,
  });

  // Store email in KV index
  await storeEmailInKV(normalizedEmail, firstName || null, id, env);

  // Subscribe to Google Sheets (non-blocking)
  if (ctx) {
    ctx.waitUntil(subscribeEmail(normalizedEmail, firstName || '', id, env));
  } else {
    subscribeEmail(normalizedEmail, firstName || '', id, env);
  }

  return jsonResponse({ success: true }, 200, origin);
}

async function handleGetReading(id, env, origin) {
  const stored = await env.READINGS.get(`reading:${id}`);
  if (!stored) {
    return jsonResponse({ error: 'Reading not found or expired' }, 404, origin);
  }
  const data = JSON.parse(stored);
  return jsonResponse({ id, reading: data.reading, firstName: data.firstName }, 200, origin);
}

/**
 * Admin endpoint to export all captured emails
 * GET /api/admin/emails
 * Requires X-API-Key header matching env.ADMIN_API_KEY
 */
async function handleAdminEmails(request, env, origin) {
  // Check API key
  const apiKey = request.headers.get('X-API-Key');
  if (!apiKey || apiKey !== env.ADMIN_API_KEY) {
    return jsonResponse({ error: 'Unauthorized' }, 401, origin);
  }

  // List all emails from the emails: prefix
  const emails = [];
  let cursor = null;
  
  do {
    const listResult = await env.READINGS.list({
      prefix: 'emails:',
      cursor,
      limit: 1000,
    });
    
    for (const key of listResult.keys) {
      const data = await env.READINGS.get(key.name);
      if (data) {
        emails.push(JSON.parse(data));
      }
    }
    
    cursor = listResult.list_complete ? null : listResult.cursor;
  } while (cursor);

  // Also get failed emails for visibility
  const failedEmails = [];
  cursor = null;
  
  do {
    const listResult = await env.READINGS.list({
      prefix: 'failed_email:',
      cursor,
      limit: 1000,
    });
    
    for (const key of listResult.keys) {
      const data = await env.READINGS.get(key.name);
      if (data) {
        failedEmails.push(JSON.parse(data));
      }
    }
    
    cursor = listResult.list_complete ? null : listResult.cursor;
  } while (cursor);

  return jsonResponse({
    emails,
    failedEmails,
    counts: {
      totalEmails: emails.length,
      failedPushes: failedEmails.length,
    },
  }, 200, origin);
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const origin = request.headers.get('Origin') || '';

    // Handle CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: corsHeaders(origin) });
    }

    try {
      // POST /api/read-grounds
      if (request.method === 'POST' && url.pathname === '/api/read-grounds') {
        return await handleReadGrounds(request, env, ctx);
      }

      // POST /api/reading/:id/subscribe
      if (request.method === 'POST' && url.pathname.match(/^\/api\/reading\/[^/]+\/subscribe$/)) {
        const id = url.pathname.split('/api/reading/')[1].split('/subscribe')[0];
        if (!id) return jsonResponse({ error: 'Reading ID required' }, 400, origin);
        return await handleSubscribe(id, request, env, ctx);
      }

      // GET /api/reading/:id
      if (request.method === 'GET' && url.pathname.startsWith('/api/reading/')) {
        const id = url.pathname.split('/api/reading/')[1];
        if (!id) return jsonResponse({ error: 'Reading ID required' }, 400, origin);
        return await handleGetReading(id, env, origin);
      }

      // GET /api/admin/emails
      if (request.method === 'GET' && url.pathname === '/api/admin/emails') {
        return await handleAdminEmails(request, env, origin);
      }

      return jsonResponse({ error: 'Not found' }, 404, origin);
    } catch (err) {
      console.error('Worker error:', err);
      return jsonResponse({ error: 'Something went wrong. Try again.' }, 500, origin);
    }
  },
};

// Export for testing
export {
  isValidEmail,
  generateId,
  corsHeaders,
  storeEmailInKV,
  storeFailedEmail,
  subscribeEmail,
  checkRateLimit,
  ALLOWED_ORIGINS,
  GOOGLE_APPS_SCRIPT_URL,
};
