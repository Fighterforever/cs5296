#!/usr/bin/env bash
# Drive the k6 benchmark matrix against the three deployment targets.
# Expects the following env vars (or tf outputs) to point to live endpoints:
#   EC2_URL FARGATE_URL LAMBDA_URL LAMBDA_ALB_URL
#
# Raw JSON summaries land in data/results/<run_id>/<platform>-<scenario>.json .
# A machine-readable streaming log (for latency-vs-time plots) lands beside
# each summary as <platform>-<scenario>.out.csv .

set -euo pipefail
cd "$(dirname "$0")/.."

RUN_ID="${RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)}"
OUT_ROOT="data/results/${RUN_ID}"
mkdir -p "${OUT_ROOT}"
echo "run_id=${RUN_ID}  out=${OUT_ROOT}"

EC2_URL="${EC2_URL:-}"
FARGATE_URL="${FARGATE_URL:-}"
LAMBDA_URL="${LAMBDA_URL:-}"
LAMBDA_ALB_URL="${LAMBDA_ALB_URL:-}"
RPS_LIST="${RPS_LIST:-50,100,250,500,1000}"
STAGE_DURATION="${STAGE_DURATION:-120s}"
BURST_TARGET="${BURST_TARGET:-800}"
BURST_DUR="${BURST_DUR:-240s}"
COLD_ITER="${COLD_ITER:-25}"
COLD_SLEEP="${COLD_SLEEP:-45}"
MIX_RPS="${MIX_RPS:-500}"
MIX_DURATION="${MIX_DURATION:-180s}"

run_one() {
  local platform="$1" target="$2" scenario="$3" script="$4"
  shift 4
  if [ -z "${target}" ]; then
    echo ">> skip ${platform}/${scenario} — no endpoint"
    return
  fi
  local base="${OUT_ROOT}/${platform}-${scenario}"
  echo ">> run ${platform}/${scenario}"
  TARGET_URL="${target}" \
  PLATFORM="${platform}" \
  RUN_ID="${RUN_ID}" \
  k6 run \
    --summary-trend-stats="avg,med,p(50),p(90),p(95),p(99),p(99.9),max" \
    --out csv="${base}.out.csv" \
    --quiet \
    "${script}" \
    > "${base}.json" "$@"
}

# 1) Steady-state RPS sweep on all three paradigms
for tgt in "ec2 ${EC2_URL}" "fargate ${FARGATE_URL}" "lambda ${LAMBDA_ALB_URL:-$LAMBDA_URL}"; do
  set -- $tgt
  run_one "$1" "$2" "steady" benchmark/scenarios/steady.js \
    -e RPS_LIST="${RPS_LIST}" -e STAGE_DURATION="${STAGE_DURATION}" -e WARMUP=20s
done

# 2) Burst / elasticity
for tgt in "ec2 ${EC2_URL}" "fargate ${FARGATE_URL}" "lambda ${LAMBDA_ALB_URL:-$LAMBDA_URL}"; do
  set -- $tgt
  run_one "$1" "$2" "burst" benchmark/scenarios/burst.js \
    -e TARGET_RPS="${BURST_TARGET}" -e BURST_DUR="${BURST_DUR}" -e IDLE_PRE=60s -e IDLE_POST=60s
done

# 3) Cold start (mainly meaningful for lambda; we also sample the others as baselines)
for tgt in "lambda ${LAMBDA_URL:-$LAMBDA_ALB_URL}" "fargate ${FARGATE_URL}" "ec2 ${EC2_URL}"; do
  set -- $tgt
  run_one "$1" "$2" "coldstart" benchmark/scenarios/coldstart.js \
    -e ITER="${COLD_ITER}" -e SLEEP_SEC="${COLD_SLEEP}"
done

# 4) Realistic mixed workload
for tgt in "ec2 ${EC2_URL}" "fargate ${FARGATE_URL}" "lambda ${LAMBDA_ALB_URL:-$LAMBDA_URL}"; do
  set -- $tgt
  run_one "$1" "$2" "mixed" benchmark/scenarios/mixed.js \
    -e RPS="${MIX_RPS}" -e DURATION="${MIX_DURATION}"
done

echo "all done — results in ${OUT_ROOT}"
