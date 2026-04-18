#!/usr/bin/env bash
# Drive the k6 benchmark matrix against the three deployment targets.
# Expects the following env vars (or tf outputs) to point to live endpoints:
#   EC2_URL FARGATE_URL LAMBDA_ALB_URL
#
# Lambda is driven at strictly lower RPS than EC2/Fargate to stay within
# its reserved-concurrency envelope and to avoid triggering platform-side
# anti-abuse heuristics for sudden fan-out.
#
# Raw JSON summaries land in data/results/<run_id>/<platform>-<scenario>.json .

set -euo pipefail
cd "$(dirname "$0")/.."

RUN_ID="${RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)}"
OUT_ROOT="data/results/${RUN_ID}"
mkdir -p "${OUT_ROOT}"
echo "run_id=${RUN_ID}  out=${OUT_ROOT}"

EC2_URL="${EC2_URL:-}"
FARGATE_URL="${FARGATE_URL:-}"
LAMBDA_ALB_URL="${LAMBDA_ALB_URL:-}"

# Default sweep profile (EC2 / Fargate)
RPS_LIST="${RPS_LIST:-50,100,200,400}"
STAGE_DURATION="${STAGE_DURATION:-120s}"

# Lambda-specific profile (capped to stay within reserved_concurrency=50)
LAMBDA_RPS_LIST="${LAMBDA_RPS_LIST:-50,100,200}"
LAMBDA_STAGE_DURATION="${LAMBDA_STAGE_DURATION:-90s}"

# Burst
BURST_TARGET="${BURST_TARGET:-400}"
LAMBDA_BURST_TARGET="${LAMBDA_BURST_TARGET:-200}"
BURST_DUR="${BURST_DUR:-180s}"

# Cold-start probe (Lambda only, gentle parameters)
COLD_ITER="${COLD_ITER:-12}"
COLD_SLEEP="${COLD_SLEEP:-60}"
RUN_COLDSTART="${RUN_COLDSTART:-lambda}"   # set to empty to skip entirely

# Mixed
MIX_RPS="${MIX_RPS:-200}"
LAMBDA_MIX_RPS="${LAMBDA_MIX_RPS:-150}"
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

# 1) Steady-state RPS sweep
for tgt in "ec2 ${EC2_URL} ${RPS_LIST} ${STAGE_DURATION}" \
           "fargate ${FARGATE_URL} ${RPS_LIST} ${STAGE_DURATION}" \
           "lambda ${LAMBDA_ALB_URL} ${LAMBDA_RPS_LIST} ${LAMBDA_STAGE_DURATION}"; do
  set -- $tgt
  run_one "$1" "$2" "steady" benchmark/scenarios/steady.js \
    -e RPS_LIST="$3" -e STAGE_DURATION="$4" -e WARMUP=20s
done

# 2) Burst / elasticity
for tgt in "ec2 ${EC2_URL} ${BURST_TARGET}" \
           "fargate ${FARGATE_URL} ${BURST_TARGET}" \
           "lambda ${LAMBDA_ALB_URL} ${LAMBDA_BURST_TARGET}"; do
  set -- $tgt
  run_one "$1" "$2" "burst" benchmark/scenarios/burst.js \
    -e TARGET_RPS="$3" -e BURST_DUR="${BURST_DUR}" -e IDLE_PRE=60s -e IDLE_POST=60s
done

# 3) Cold start — Lambda only by default (anti-abuse pattern on shared platforms)
if [ "${RUN_COLDSTART}" = "lambda" ] && [ -n "${LAMBDA_ALB_URL}" ]; then
  run_one "lambda" "${LAMBDA_ALB_URL}" "coldstart" benchmark/scenarios/coldstart.js \
    -e ITER="${COLD_ITER}" -e SLEEP_SEC="${COLD_SLEEP}"
fi

# 4) Realistic mixed workload
for tgt in "ec2 ${EC2_URL} ${MIX_RPS}" \
           "fargate ${FARGATE_URL} ${MIX_RPS}" \
           "lambda ${LAMBDA_ALB_URL} ${LAMBDA_MIX_RPS}"; do
  set -- $tgt
  run_one "$1" "$2" "mixed" benchmark/scenarios/mixed.js \
    -e RPS="$3" -e DURATION="${MIX_DURATION}"
done

echo "all done — results in ${OUT_ROOT}"
