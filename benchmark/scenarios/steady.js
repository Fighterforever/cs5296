// constant-arrival-rate sweep: a new stage at each RPS level.
// Run with RPS_LIST=100,250,500,1000 STAGE_DURATION=180s k6 run steady.js
import { doRedirect, seedPool } from '../lib/common.js';
import { tagSummary } from '../lib/common.js';

const rpsList = (__ENV.RPS_LIST || '50,100,250,500,1000').split(',').map((x) => parseInt(x, 10));
const stageDuration = __ENV.STAGE_DURATION || '120s';
const warmup = __ENV.WARMUP || '30s';

export const options = {
  discardResponseBodies: true,
  scenarios: Object.fromEntries(
    rpsList.map((r, i) => [
      `rps_${r}`,
      {
        executor: 'constant-arrival-rate',
        rate: r,
        timeUnit: '1s',
        duration: stageDuration,
        preAllocatedVUs: Math.max(50, Math.ceil(r * 0.4)),
        maxVUs: Math.max(200, r * 2),
        startTime: durationSum(rpsList.slice(0, i), stageDuration, warmup, i === 0),
        tags: { stage: `rps_${r}` },
        exec: 'load',
      },
    ])
  ),
  summaryTrendStats: ['avg', 'min', 'med', 'max', 'p(50)', 'p(90)', 'p(95)', 'p(99)', 'p(99.9)'],
};

function durationSum(list, stage, wu, first) {
  const sec = (s) => parseInt(s, 10) * (s.endsWith('m') ? 60 : 1);
  const wuSec = wu ? sec(wu) : 0;
  const stSec = sec(stage);
  const elapsed = list.length * (stSec + wuSec);
  return `${elapsed + (first ? 0 : wuSec)}s`;
}

let codes = [];

export function setup() {
  const c = seedPool();
  return { codes: c };
}

export function load(data) {
  doRedirect(data.codes);
}

export function handleSummary(data) {
  return { stdout: JSON.stringify(tagSummary({ scenario: 'steady', metrics: data.metrics }), null, 2) };
}
