// Cold start probe: for Lambda, a long gap between calls trips a fresh init.
// We issue N lightweight requests with SLEEP_SEC gap and record first-byte latency.
import http from 'k6/http';
import { sleep } from 'k6';
import { Trend } from 'k6/metrics';
import { TARGET, PLATFORM, RUN_ID, tagSummary } from '../lib/common.js';

const iter = parseInt(__ENV.ITER || '30', 10);
const sleepSec = parseInt(__ENV.SLEEP_SEC || '30', 10);

export const options = {
  discardResponseBodies: true,
  scenarios: {
    cold: {
      executor: 'per-vu-iterations',
      vus: 1,
      iterations: iter,
      exec: 'probe',
      maxDuration: `${(sleepSec + 5) * (iter + 1)}s`,
    },
  },
  summaryTrendStats: ['avg', 'min', 'med', 'max', 'p(50)', 'p(95)', 'p(99)'],
};

export const firstByte = new Trend('first_byte_ms', true);
export const connect   = new Trend('connect_ms', true);
export const total     = new Trend('total_ms', true);

export function probe() {
  const r = http.get(`${TARGET}/healthz`, { tags: { endpoint: 'health', platform: PLATFORM } });
  firstByte.add(r.timings.waiting);
  connect.add(r.timings.connecting + r.timings.tls_handshaking);
  total.add(r.timings.duration);
  sleep(sleepSec);
}

export function handleSummary(data) {
  return { stdout: JSON.stringify(tagSummary({ scenario: 'coldstart', iter, sleepSec, metrics: data.metrics }), null, 2) };
}
