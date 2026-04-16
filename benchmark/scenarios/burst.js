// Step-arrival burst: jump from IDLE_RPS to TARGET_RPS and hold, then down.
// We derive "time to steady state" from the latency trace in post-processing.
import { doRedirect, seedPool } from '../lib/common.js';
import { tagSummary } from '../lib/common.js';

const idleRps = parseInt(__ENV.IDLE_RPS || '5', 10);
const targetRps = parseInt(__ENV.TARGET_RPS || '800', 10);
const idlePre = __ENV.IDLE_PRE || '60s';
const burst = __ENV.BURST_DUR || '300s';
const idlePost = __ENV.IDLE_POST || '60s';

export const options = {
  discardResponseBodies: true,
  scenarios: {
    pre: {
      executor: 'constant-arrival-rate',
      rate: idleRps,
      timeUnit: '1s',
      duration: idlePre,
      preAllocatedVUs: 20,
      maxVUs: 50,
      startTime: '0s',
      exec: 'load',
      tags: { phase: 'pre' },
    },
    burst: {
      executor: 'constant-arrival-rate',
      rate: targetRps,
      timeUnit: '1s',
      duration: burst,
      preAllocatedVUs: Math.ceil(targetRps * 0.5),
      maxVUs: targetRps * 3,
      startTime: idlePre,
      exec: 'load',
      tags: { phase: 'burst' },
    },
    post: {
      executor: 'constant-arrival-rate',
      rate: idleRps,
      timeUnit: '1s',
      duration: idlePost,
      preAllocatedVUs: 20,
      maxVUs: 50,
      startTime: sumSec(idlePre, burst),
      exec: 'load',
      tags: { phase: 'post' },
    },
  },
  summaryTrendStats: ['avg', 'min', 'med', 'max', 'p(50)', 'p(95)', 'p(99)'],
};

function sumSec(a, b) {
  const toSec = (s) => parseInt(s, 10) * (s.endsWith('m') ? 60 : 1);
  return `${toSec(a) + toSec(b)}s`;
}

export function setup() {
  const c = seedPool();
  return { codes: c };
}

export function load(data) {
  doRedirect(data.codes);
}

export function handleSummary(data) {
  return { stdout: JSON.stringify(tagSummary({ scenario: 'burst', idleRps, targetRps, metrics: data.metrics }), null, 2) };
}
