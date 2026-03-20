import { defineWorkersConfig } from '@cloudflare/vitest-pool-workers/config';

export default defineWorkersConfig({
  test: {
    poolOptions: {
      workers: {
        wrangler: { configPath: './wrangler.toml' },
        miniflare: {
          kvNamespaces: ['READINGS', 'RATE_LIMITS'],
          bindings: {
            ANTHROPIC_API_KEY: 'test-api-key',
            ADMIN_API_KEY: 'test-admin-key',
          },
        },
      },
    },
  },
});
