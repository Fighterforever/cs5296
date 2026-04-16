// shared helpers for all k6 scenarios
import http from 'k6/http';
import { check } from 'k6';
import { Trend, Counter, Rate } from 'k6/metrics';
import { randomIntBetween } from 'https://jslib.k6.io/k6-utils/1.2.0/index.js';

export const TARGET   = __ENV.TARGET_URL   || 'http://localhost:8080';
export const PLATFORM = __ENV.PLATFORM     || 'unknown';
export const RUN_ID   = __ENV.RUN_ID       || `${Date.now()}`;

// sentinel URL pool; the redirect path is what we measure under load
const POOL_SIZE = parseInt(__ENV.POOL_SIZE || '200', 10);
const pool = [];
for (let i = 0; i < POOL_SIZE; i++) {
  pool.push(`https://example.com/cs5296/${i}-${RUN_ID}`);
}

export const latencyRedirect = new Trend(`lat_redirect_ms`, true);
export const latencyShorten  = new Trend(`lat_shorten_ms`, true);
export const latencyHealth   = new Trend(`lat_health_ms`, true);
export const latencyCpu      = new Trend(`lat_cpu_ms`, true);
export const errRate         = new Rate(`err_rate`);
export const totalReqs       = new Counter(`reqs_total`);

export function seedPool() {
  const codes = [];
  for (const url of pool) {
    const r = http.post(`${TARGET}/shorten`, JSON.stringify({ url }), {
      headers: { 'Content-Type': 'application/json' },
      timeout: '20s',
      responseType: 'text',
    });
    if (r.status === 200 && r.body) {
      try { codes.push(r.json('code')); } catch (_) { /* ignore */ }
    }
  }
  if (codes.length === 0) {
    throw new Error(`seedPool: no codes returned from ${TARGET}/shorten`);
  }
  return codes;
}

export function doShorten() {
  const url = pool[randomIntBetween(0, pool.length - 1)];
  const r = http.post(`${TARGET}/shorten`, JSON.stringify({ url }), { headers: { 'Content-Type': 'application/json' }, tags: { endpoint: 'shorten', platform: PLATFORM } });
  latencyShorten.add(r.timings.duration);
  totalReqs.add(1);
  errRate.add(r.status !== 200);
  check(r, { 'shorten 200': (x) => x.status === 200 });
  return r.status === 200 ? r.json('code') : null;
}

export function doRedirect(codes) {
  const code = codes[randomIntBetween(0, codes.length - 1)];
  const r = http.get(`${TARGET}/r/${code}`, { redirects: 0, tags: { endpoint: 'redirect', platform: PLATFORM } });
  latencyRedirect.add(r.timings.duration);
  totalReqs.add(1);
  errRate.add(r.status !== 301);
  check(r, { 'redirect 301': (x) => x.status === 301 });
}

export function doHealth() {
  const r = http.get(`${TARGET}/healthz`, { tags: { endpoint: 'health', platform: PLATFORM } });
  latencyHealth.add(r.timings.duration);
  totalReqs.add(1);
  errRate.add(r.status !== 200);
}

export function doCpu(rounds) {
  const r = http.get(`${TARGET}/cpu?rounds=${rounds}`, { tags: { endpoint: 'cpu', platform: PLATFORM } });
  latencyCpu.add(r.timings.duration);
  totalReqs.add(1);
  errRate.add(r.status !== 200);
}

export function tagSummary(data) {
  return {
    platform: PLATFORM,
    run_id: RUN_ID,
    target: TARGET,
    ts_end: new Date().toISOString(),
    ...data,
  };
}
