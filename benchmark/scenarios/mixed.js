// Realistic 70/30 GET-redirect / POST-shorten mix at a single RPS.
import { doRedirect, doShorten, seedPool } from '../lib/common.js';
import { tagSummary } from '../lib/common.js';
import { randomIntBetween } from 'https://jslib.k6.io/k6-utils/1.2.0/index.js';

const rps = parseInt(__ENV.RPS || '500', 10);
const duration = __ENV.DURATION || '180s';

export const options = {
  discardResponseBodies: true,
  scenarios: {
    mix: {
      executor: 'constant-arrival-rate',
      rate: rps,
      timeUnit: '1s',
      duration,
      preAllocatedVUs: Math.max(50, Math.ceil(rps * 0.5)),
      maxVUs: Math.max(100, rps * 2),
      exec: 'mix',
    },
  },
  summaryTrendStats: ['avg', 'min', 'med', 'max', 'p(50)', 'p(95)', 'p(99)'],
};

export function setup() {
  return { codes: seedPool() };
}

export function mix(data) {
  if (randomIntBetween(0, 99) < 70) doRedirect(data.codes);
  else doShorten();
}

export function handleSummary(data) {
  return { stdout: JSON.stringify(tagSummary({ scenario: 'mixed', rps, metrics: data.metrics }), null, 2) };
}
