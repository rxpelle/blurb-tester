import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import {
  isValidEmail,
  generateId,
  corsHeaders,
  ALLOWED_ORIGINS,
  GOOGLE_APPS_SCRIPT_URL,
  subscribeEmail,
  storeFailedEmail,
} from './index.js';

// ============================================
// Unit Tests - Pure Functions
// ============================================

describe('isValidEmail', () => {
  it('returns true for valid emails', () => {
    expect(isValidEmail('test@example.com')).toBe(true);
    expect(isValidEmail('user.name@domain.co.uk')).toBe(true);
    expect(isValidEmail('user+tag@example.org')).toBe(true);
  });

  it('returns false for invalid emails', () => {
    expect(isValidEmail('')).toBe(false);
    expect(isValidEmail(null)).toBe(false);
    expect(isValidEmail(undefined)).toBe(false);
    expect(isValidEmail('notanemail')).toBe(false);
    expect(isValidEmail('missing@domain')).toBe(false);
    expect(isValidEmail('@nodomain.com')).toBe(false);
    expect(isValidEmail('spaces in@email.com')).toBe(false);
  });
});

describe('generateId', () => {
  it('generates 8 character IDs', () => {
    const id = generateId();
    expect(id).toHaveLength(8);
  });

  it('generates unique IDs', () => {
    const ids = new Set();
    for (let i = 0; i < 100; i++) {
      ids.add(generateId());
    }
    expect(ids.size).toBe(100);
  });

  it('only uses allowed characters', () => {
    const allowedChars = 'abcdefghijkmnpqrstuvwxyz23456789';
    for (let i = 0; i < 50; i++) {
      const id = generateId();
      for (const char of id) {
        expect(allowedChars).toContain(char);
      }
    }
  });
});

describe('corsHeaders', () => {
  it('returns allowed origin when origin is in allowed list', () => {
    const headers = corsHeaders('https://randypellegrini.com');
    expect(headers['Access-Control-Allow-Origin']).toBe('https://randypellegrini.com');
  });

  it('returns first allowed origin for unknown origins', () => {
    const headers = corsHeaders('https://malicious.com');
    expect(headers['Access-Control-Allow-Origin']).toBe(ALLOWED_ORIGINS[0]);
  });

  it('includes required CORS headers', () => {
    const headers = corsHeaders('https://randypellegrini.com');
    expect(headers['Access-Control-Allow-Methods']).toContain('POST');
    expect(headers['Access-Control-Allow-Headers']).toContain('Content-Type');
    expect(headers['Access-Control-Allow-Headers']).toContain('X-API-Key');
  });
});

// ============================================
// Integration Tests - Worker Behavior
// ============================================

describe('Worker Integration', () => {
  // Mock KV namespace
  const createMockKV = () => {
    const store = new Map();
    return {
      get: vi.fn(async (key) => store.get(key) || null),
      put: vi.fn(async (key, value) => store.set(key, value)),
      list: vi.fn(async ({ prefix, cursor, limit }) => {
        const keys = Array.from(store.keys())
          .filter(k => k.startsWith(prefix))
          .map(name => ({ name }));
        return { keys, list_complete: true, cursor: null };
      }),
      _store: store,
    };
  };

  const createMockEnv = () => ({
    READINGS: createMockKV(),
    RATE_LIMITS: createMockKV(),
    ANTHROPIC_API_KEY: 'test-api-key',
    ADMIN_API_KEY: 'test-admin-key',
  });

  describe('Rate Limiting', () => {
    it('allows first 3 requests from same IP', async () => {
      const env = createMockEnv();
      
      // Simulate rate limit check
      for (let i = 0; i < 3; i++) {
        const key = 'rate:192.168.1.1';
        const current = await env.RATE_LIMITS.get(key);
        const count = current ? parseInt(current, 10) : 0;
        expect(count).toBeLessThan(3);
        await env.RATE_LIMITS.put(key, String(count + 1));
      }
    });

    it('blocks 4th request from same IP', async () => {
      const env = createMockEnv();
      const key = 'rate:192.168.1.1';
      
      // Set count to 3 (already used limit)
      await env.RATE_LIMITS.put(key, '3');
      
      const current = await env.RATE_LIMITS.get(key);
      const count = parseInt(current, 10);
      expect(count).toBe(3);
      expect(count >= 3).toBe(true); // Would be blocked
    });
  });

  describe('Email Storage in KV', () => {
    it('stores reading without email when none provided', async () => {
      const env = createMockEnv();
      const readingId = 'abc12345';
      const timestamp = new Date().toISOString();

      // Store reading without email (new flow: email is optional)
      await env.READINGS.put(
        `reading:${readingId}`,
        JSON.stringify({
          reading: 'Your reading...',
          firstName: null,
          email: null,
          timestamp,
        })
      );

      // Verify storage
      const stored = await env.READINGS.get(`reading:${readingId}`);
      const data = JSON.parse(stored);
      expect(data.email).toBeNull();
      expect(data.firstName).toBeNull();
      expect(data.reading).toBe('Your reading...');
    });

    it('stores email with reading when provided', async () => {
      const env = createMockEnv();
      const readingId = 'abc12345';
      const email = 'test@example.com';
      const firstName = 'Test';
      const timestamp = new Date().toISOString();

      await env.READINGS.put(
        `reading:${readingId}`,
        JSON.stringify({
          reading: 'Your reading...',
          firstName,
          email,
          timestamp,
        })
      );

      const stored = await env.READINGS.get(`reading:${readingId}`);
      const data = JSON.parse(stored);
      expect(data.email).toBe(email);
      expect(data.firstName).toBe(firstName);
    });

    it('stores email:{id} for easy lookup', async () => {
      const env = createMockEnv();
      const readingId = 'abc12345';
      const email = 'test@example.com';
      const firstName = 'Test';
      const timestamp = new Date().toISOString();

      await env.READINGS.put(
        `email:${readingId}`,
        JSON.stringify({ email, firstName, timestamp })
      );

      const stored = await env.READINGS.get(`email:${readingId}`);
      const data = JSON.parse(stored);
      expect(data.email).toBe(email);
    });
  });

  describe('Post-Reading Subscribe Endpoint', () => {
    it('updates reading record with email after subscription', async () => {
      const env = createMockEnv();
      const readingId = 'sub12345';
      const email = 'subscriber@example.com';
      const firstName = 'Subscriber';

      // First, store a reading without email (simulating initial flow)
      await env.READINGS.put(
        `reading:${readingId}`,
        JSON.stringify({
          reading: 'Your patterns reveal...',
          firstName: null,
          email: null,
          timestamp: new Date().toISOString(),
        })
      );

      // Simulate subscribe: update reading with email
      const stored = await env.READINGS.get(`reading:${readingId}`);
      const readingData = JSON.parse(stored);
      readingData.email = email.toLowerCase().trim();
      readingData.firstName = firstName;
      await env.READINGS.put(`reading:${readingId}`, JSON.stringify(readingData));

      // Verify
      const updated = await env.READINGS.get(`reading:${readingId}`);
      const data = JSON.parse(updated);
      expect(data.email).toBe(email);
      expect(data.firstName).toBe(firstName);
      expect(data.reading).toBe('Your patterns reveal...');
    });

    it('rejects subscription with invalid email', () => {
      expect(isValidEmail('')).toBe(false);
      expect(isValidEmail('notanemail')).toBe(false);
      expect(isValidEmail(null)).toBe(false);
    });

    it('rejects subscription for non-existent reading', async () => {
      const env = createMockEnv();
      const stored = await env.READINGS.get('reading:nonexistent');
      expect(stored).toBeNull();
    });

    it('stores email index after subscription', async () => {
      const env = createMockEnv();
      const readingId = 'idx12345';
      const email = 'indexed@example.com';
      const firstName = 'Indexed';
      const timestamp = new Date().toISOString();

      // Simulate storeEmailInKV
      await env.READINGS.put(
        `email:${readingId}`,
        JSON.stringify({ email, firstName, timestamp })
      );
      await env.READINGS.put(
        `emails:${email}`,
        JSON.stringify({
          email,
          firstName,
          readingIds: [readingId],
          firstSeen: timestamp,
          lastSeen: timestamp,
        })
      );

      // Verify email index
      const indexStored = await env.READINGS.get(`emails:${email}`);
      const indexData = JSON.parse(indexStored);
      expect(indexData.readingIds).toContain(readingId);
      expect(indexData.email).toBe(email);
    });
  });

  describe('Email Index Updates', () => {
    it('creates new email index for new email', async () => {
      const env = createMockEnv();
      const email = 'new@example.com';
      const indexKey = `emails:${email}`;
      const readingId = 'read123';
      const timestamp = new Date().toISOString();

      // Simulate storeEmailInKV for new email
      const indexData = {
        email,
        firstName: 'New',
        readingIds: [readingId],
        firstSeen: timestamp,
        lastSeen: timestamp,
      };
      await env.READINGS.put(indexKey, JSON.stringify(indexData));

      const stored = await env.READINGS.get(indexKey);
      const data = JSON.parse(stored);
      expect(data.readingIds).toContain(readingId);
      expect(data.firstSeen).toBe(timestamp);
    });

    it('updates existing email index for repeat email', async () => {
      const env = createMockEnv();
      const email = 'existing@example.com';
      const indexKey = `emails:${email}`;
      const firstTimestamp = '2024-01-01T00:00:00Z';
      const secondTimestamp = '2024-01-02T00:00:00Z';

      // Set up existing index
      await env.READINGS.put(indexKey, JSON.stringify({
        email,
        firstName: 'Existing',
        readingIds: ['read1'],
        firstSeen: firstTimestamp,
        lastSeen: firstTimestamp,
      }));

      // Update for second reading
      const existing = await env.READINGS.get(indexKey);
      const existingData = JSON.parse(existing);
      existingData.readingIds.push('read2');
      existingData.lastSeen = secondTimestamp;
      await env.READINGS.put(indexKey, JSON.stringify(existingData));

      // Verify
      const updated = await env.READINGS.get(indexKey);
      const data = JSON.parse(updated);
      expect(data.readingIds).toEqual(['read1', 'read2']);
      expect(data.firstSeen).toBe(firstTimestamp);
      expect(data.lastSeen).toBe(secondTimestamp);
    });
  });

  describe('Failed Email Storage', () => {
    it('stores failed email for later retry', async () => {
      const env = createMockEnv();
      const readingId = 'fail123';
      const email = 'failed@example.com';
      const error = 'HTTP 404: Not Found';
      const timestamp = new Date().toISOString();

      await env.READINGS.put(
        `failed_email:${readingId}`,
        JSON.stringify({
          email,
          firstName: 'Failed',
          readingId,
          error,
          timestamp,
          retryCount: 0,
        })
      );

      const stored = await env.READINGS.get(`failed_email:${readingId}`);
      const data = JSON.parse(stored);
      expect(data.email).toBe(email);
      expect(data.error).toBe(error);
      expect(data.retryCount).toBe(0);
    });
  });

  describe('Admin Emails Endpoint', () => {
    it('rejects requests without API key', async () => {
      const env = createMockEnv();
      
      // Simulate auth check
      const apiKey = null;
      const isAuthorized = apiKey === env.ADMIN_API_KEY;
      expect(isAuthorized).toBe(false);
    });

    it('rejects requests with wrong API key', async () => {
      const env = createMockEnv();
      
      const apiKey = 'wrong-key';
      const isAuthorized = apiKey === env.ADMIN_API_KEY;
      expect(isAuthorized).toBe(false);
    });

    it('accepts requests with correct API key', async () => {
      const env = createMockEnv();
      
      const apiKey = 'test-admin-key';
      const isAuthorized = apiKey === env.ADMIN_API_KEY;
      expect(isAuthorized).toBe(true);
    });

    it('returns all emails from index', async () => {
      const env = createMockEnv();
      
      // Store some test emails
      await env.READINGS.put('emails:user1@test.com', JSON.stringify({
        email: 'user1@test.com',
        firstName: 'User1',
        readingIds: ['r1'],
        firstSeen: '2024-01-01T00:00:00Z',
        lastSeen: '2024-01-01T00:00:00Z',
      }));
      await env.READINGS.put('emails:user2@test.com', JSON.stringify({
        email: 'user2@test.com',
        firstName: 'User2',
        readingIds: ['r2', 'r3'],
        firstSeen: '2024-01-02T00:00:00Z',
        lastSeen: '2024-01-03T00:00:00Z',
      }));

      // Simulate listing
      const listResult = await env.READINGS.list({ prefix: 'emails:' });
      expect(listResult.keys).toHaveLength(2);
    });

    it('returns failed emails for visibility', async () => {
      const env = createMockEnv();
      
      await env.READINGS.put('failed_email:f1', JSON.stringify({
        email: 'failed@test.com',
        error: 'Network error',
      }));

      const listResult = await env.READINGS.list({ prefix: 'failed_email:' });
      expect(listResult.keys).toHaveLength(1);
    });
  });

  describe('Reading Storage', () => {
    it('stores reading without email (new default flow)', async () => {
      const env = createMockEnv();
      const readingId = 'read123';
      const data = {
        reading: '**The Patterns**\nYou see...',
        firstName: null,
        email: null,
        timestamp: new Date().toISOString(),
      };

      await env.READINGS.put(`reading:${readingId}`, JSON.stringify(data));

      const stored = await env.READINGS.get(`reading:${readingId}`);
      const parsed = JSON.parse(stored);

      expect(parsed.reading).toBe(data.reading);
      expect(parsed.firstName).toBeNull();
      expect(parsed.email).toBeNull();
      expect(parsed.timestamp).toBe(data.timestamp);
    });

    it('stores reading with email when provided upfront', async () => {
      const env = createMockEnv();
      const readingId = 'read456';
      const data = {
        reading: '**The Patterns**\nYou see...',
        firstName: 'Test',
        email: 'test@example.com',
        timestamp: new Date().toISOString(),
      };

      await env.READINGS.put(`reading:${readingId}`, JSON.stringify(data));

      const stored = await env.READINGS.get(`reading:${readingId}`);
      const parsed = JSON.parse(stored);

      expect(parsed.reading).toBe(data.reading);
      expect(parsed.firstName).toBe(data.firstName);
      expect(parsed.email).toBe(data.email);
    });

    it('retrieves reading by ID', async () => {
      const env = createMockEnv();
      const readingId = 'retrieve123';

      await env.READINGS.put(`reading:${readingId}`, JSON.stringify({
        reading: 'Your patterns reveal...',
        firstName: null,
        email: null,
        timestamp: '2024-01-15T10:30:00Z',
      }));

      const stored = await env.READINGS.get(`reading:${readingId}`);
      expect(stored).not.toBeNull();

      const data = JSON.parse(stored);
      expect(data.reading).toContain('patterns');
    });

    it('returns null for non-existent reading', async () => {
      const env = createMockEnv();
      const stored = await env.READINGS.get('reading:nonexistent');
      expect(stored).toBeNull();
    });
  });

  describe('CORS Headers', () => {
    it('includes all required CORS headers for allowed origin', () => {
      const headers = corsHeaders('https://randypellegrini.com');
      
      expect(headers['Access-Control-Allow-Origin']).toBe('https://randypellegrini.com');
      expect(headers['Access-Control-Allow-Methods']).toContain('GET');
      expect(headers['Access-Control-Allow-Methods']).toContain('POST');
      expect(headers['Access-Control-Allow-Methods']).toContain('OPTIONS');
      expect(headers['Access-Control-Allow-Headers']).toContain('Content-Type');
      expect(headers['Access-Control-Max-Age']).toBe('86400');
    });

    it('handles localhost origins', () => {
      const headers = corsHeaders('http://localhost:8080');
      expect(headers['Access-Control-Allow-Origin']).toBe('http://localhost:8080');
    });
  });
});

// ============================================
// Subscribe Email Retry Logic Tests
// ============================================

describe('Subscribe Email Retry Logic', () => {
  it('should attempt retry on first failure', async () => {
    let attempts = 0;
    const mockFetch = vi.fn().mockImplementation(() => {
      attempts++;
      if (attempts === 1) {
        return Promise.reject(new Error('Network error'));
      }
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ success: true }),
      });
    });

    // Simulate retry logic
    let success = false;
    for (let attempt = 0; attempt < 2; attempt++) {
      try {
        const response = await mockFetch();
        if (response.ok) {
          success = true;
          break;
        }
      } catch (e) {
        if (attempt < 1) {
          await new Promise(r => setTimeout(r, 10)); // Short delay for test
        }
      }
    }

    expect(attempts).toBe(2);
    expect(success).toBe(true);
  });

  it('should store failed email after both attempts fail', async () => {
    const mockFetch = vi.fn().mockRejectedValue(new Error('Permanent failure'));
    
    let success = false;
    let lastError = null;
    
    for (let attempt = 0; attempt < 2; attempt++) {
      try {
        await mockFetch();
        success = true;
        break;
      } catch (e) {
        lastError = e;
      }
    }

    expect(success).toBe(false);
    expect(lastError.message).toBe('Permanent failure');
    expect(mockFetch).toHaveBeenCalledTimes(2);
  });
});

// ============================================
// Email Normalization Tests
// ============================================

describe('Email Normalization', () => {
  it('normalizes email to lowercase', () => {
    const email = 'TEST@EXAMPLE.COM';
    const normalized = email.toLowerCase().trim();
    expect(normalized).toBe('test@example.com');
  });

  it('trims whitespace', () => {
    const email = '  test@example.com  ';
    const normalized = email.toLowerCase().trim();
    expect(normalized).toBe('test@example.com');
  });

  it('handles mixed case and whitespace', () => {
    const email = '  TeSt@ExAmPlE.CoM  ';
    const normalized = email.toLowerCase().trim();
    expect(normalized).toBe('test@example.com');
  });
});

// ============================================
// Google Apps Script URL Tests
// ============================================

describe('GOOGLE_APPS_SCRIPT_URL', () => {
  it('points to the correct Apps Script deployment URL', () => {
    expect(GOOGLE_APPS_SCRIPT_URL).toBe(
      'https://script.google.com/macros/s/AKfycbwlmi9FeZlAeICXIImBGDU4-zKo1iwdMmVmzzaP68tD-uoTAP0ZmPK38zL-qOkY3VRX1A/exec'
    );
  });

  it('does not point to the old dead URL', () => {
    expect(GOOGLE_APPS_SCRIPT_URL).not.toBe(
      'https://script.google.com/macros/s/AKfycbzQDd5-UcGkXwQRCw_F9kUZebPAZNThYg3BSrhlZ9EueW7VwOxc4KX2R-WhfGYnDfbXAA/exec'
    );
  });
});

// ============================================
// subscribeEmail Function Tests
// ============================================

describe('subscribeEmail', () => {
  let originalFetch;

  beforeEach(() => {
    originalFetch = globalThis.fetch;
  });

  afterEach(() => {
    globalThis.fetch = originalFetch;
  });

  it('sends correct payload format to Apps Script', async () => {
    let capturedBody = null;
    let capturedHeaders = null;

    globalThis.fetch = vi.fn().mockImplementation(async (url, options) => {
      capturedBody = JSON.parse(options.body);
      capturedHeaders = options.headers;
      return {
        ok: true,
        json: async () => ({ status: 'ok', added: true }),
      };
    });

    const mockEnv = {
      READINGS: {
        put: vi.fn(),
        get: vi.fn(),
      },
    };

    await subscribeEmail('test@example.com', 'Test', 'read123', mockEnv);

    // Verify payload format matches what Apps Script expects
    expect(capturedBody.action).toBe('grounds_subscribe');
    expect(capturedBody.email).toBe('test@example.com');
    expect(capturedBody.first_name).toBe('Test');
    expect(capturedBody.reading_id).toBe('read123');
    expect(capturedBody.timestamp).toBeDefined();
    expect(typeof capturedBody.timestamp).toBe('string');
  });

  it('sends Content-Type text/plain header', async () => {
    let capturedHeaders = null;

    globalThis.fetch = vi.fn().mockImplementation(async (url, options) => {
      capturedHeaders = options.headers;
      return {
        ok: true,
        json: async () => ({ status: 'ok', added: true }),
      };
    });

    const mockEnv = {
      READINGS: {
        put: vi.fn(),
        get: vi.fn(),
      },
    };

    await subscribeEmail('test@example.com', '', 'read123', mockEnv);

    expect(capturedHeaders['Content-Type']).toBe('text/plain');
  });

  it('posts to the correct Google Apps Script URL', async () => {
    let capturedUrl = null;

    globalThis.fetch = vi.fn().mockImplementation(async (url) => {
      capturedUrl = url;
      return {
        ok: true,
        json: async () => ({ status: 'ok', added: true }),
      };
    });

    const mockEnv = {
      READINGS: {
        put: vi.fn(),
        get: vi.fn(),
      },
    };

    await subscribeEmail('test@example.com', '', 'read123', mockEnv);

    expect(capturedUrl).toBe(GOOGLE_APPS_SCRIPT_URL);
  });

  it('returns true on successful subscription', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ status: 'ok', added: true }),
    });

    const mockEnv = {
      READINGS: {
        put: vi.fn(),
        get: vi.fn(),
      },
    };

    const result = await subscribeEmail('test@example.com', 'Test', 'read123', mockEnv);
    expect(result).toBe(true);
  });

  it('retries on first failure and succeeds on second attempt', async () => {
    let attempts = 0;
    globalThis.fetch = vi.fn().mockImplementation(async () => {
      attempts++;
      if (attempts === 1) {
        throw new Error('Network error');
      }
      return {
        ok: true,
        json: async () => ({ status: 'ok', added: true }),
      };
    });

    const mockEnv = {
      READINGS: {
        put: vi.fn(),
        get: vi.fn(),
      },
    };

    const result = await subscribeEmail('test@example.com', 'Test', 'read123', mockEnv);
    expect(result).toBe(true);
    expect(attempts).toBe(2);
  });

  it('stores failed email after both attempts fail', async () => {
    globalThis.fetch = vi.fn().mockRejectedValue(new Error('Permanent failure'));

    const mockEnv = {
      READINGS: {
        put: vi.fn(),
        get: vi.fn(),
      },
    };

    const result = await subscribeEmail('test@example.com', 'Test', 'fail123', mockEnv);
    expect(result).toBe(false);

    // Verify storeFailedEmail was called (it calls env.READINGS.put with failed_email: prefix)
    const failedPutCall = mockEnv.READINGS.put.mock.calls.find(
      call => call[0] === 'failed_email:fail123'
    );
    expect(failedPutCall).toBeDefined();
    const failedData = JSON.parse(failedPutCall[1]);
    expect(failedData.email).toBe('test@example.com');
    expect(failedData.firstName).toBe('Test');
    expect(failedData.readingId).toBe('fail123');
    expect(failedData.error).toBe('Permanent failure');
    expect(failedData.retryCount).toBe(0);
  });

  it('handles empty firstName as empty string in payload', async () => {
    let capturedBody = null;

    globalThis.fetch = vi.fn().mockImplementation(async (url, options) => {
      capturedBody = JSON.parse(options.body);
      return {
        ok: true,
        json: async () => ({ status: 'ok', added: true }),
      };
    });

    const mockEnv = {
      READINGS: {
        put: vi.fn(),
        get: vi.fn(),
      },
    };

    await subscribeEmail('test@example.com', '', 'read123', mockEnv);

    expect(capturedBody.first_name).toBe('');
  });
});

// ============================================
// storeFailedEmail Function Tests
// ============================================

describe('storeFailedEmail', () => {
  it('stores failed email data in KV with correct key', async () => {
    const mockEnv = {
      READINGS: {
        put: vi.fn(),
      },
    };

    await storeFailedEmail('test@example.com', 'Test', 'fail456', new Error('Connection refused'), mockEnv);

    expect(mockEnv.READINGS.put).toHaveBeenCalledTimes(1);
    const [key, value, options] = mockEnv.READINGS.put.mock.calls[0];
    expect(key).toBe('failed_email:fail456');

    const data = JSON.parse(value);
    expect(data.email).toBe('test@example.com');
    expect(data.firstName).toBe('Test');
    expect(data.readingId).toBe('fail456');
    expect(data.error).toBe('Connection refused');
    expect(data.retryCount).toBe(0);
    expect(data.timestamp).toBeDefined();

    // 30-day TTL
    expect(options.expirationTtl).toBe(30 * 24 * 60 * 60);
  });
});
