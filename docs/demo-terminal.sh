#!/usr/bin/env bash
#
# CS5296 Group 24 — terminal demo runner
#
# How to use:
#   1. Open Terminal, set font to 16pt+ monospace, set window size ~120x32.
#      Tip: Terminal.app -> Preferences -> Profile -> Text -> Font.
#   2. Start a screen recording with Cmd+Shift+5 (Record Selected Portion),
#      pick the terminal window only.
#   3. Run:    bash docs/demo-terminal.sh
#   4. When the script prints "done.", stop the recording.
#
# Total wall-clock time: ~80 seconds.
# In your editor, you can speed this up to 2x or 2.5x for the final video.

set -euo pipefail
cd "$(dirname "$0")/.."

ALB="${ALB:-http://cs5296-alb-550516460.us-east-1.elb.amazonaws.com}"

# colour palette
PROMPT=$'\033[1;36m'    # cyan
HEAD=$'\033[1;33m'      # yellow for section headers
DIM=$'\033[2m'          # dim for transcript
RESET=$'\033[0m'

type_speed=0.025
pause_short=0.4
pause_med=0.9
pause_long=1.5

# self-typing helper (single-line)
type_cmd() {
  local cmd="$1"
  printf "%s\$ %s" "$PROMPT" "$RESET"
  for ((i=0; i<${#cmd}; i++)); do
    printf "%s" "${cmd:$i:1}"
    sleep $type_speed
  done
  printf "\n"
  sleep $pause_short
}

# self-typing helper for multi-line (preserves backslash newlines visually)
type_multi() {
  local cmd="$1"
  printf "%s\$ %s" "$PROMPT" "$RESET"
  local IFS=$'\n'
  local first=1
  for line in $cmd; do
    if [ $first -eq 1 ]; then first=0; else printf "  "; fi
    for ((i=0; i<${#line}; i++)); do
      printf "%s" "${line:$i:1}"
      sleep $type_speed
    done
    printf "\n"
    sleep 0.1
  done
  sleep $pause_short
}

section() {
  printf "\n%s# %s%s\n" "$HEAD" "$1" "$RESET"
  sleep 0.7
}

clear

# =============================================================================
section "1 of 3  —  three deployments, one ALB, all alive"
# =============================================================================

type_cmd "curl -s ${ALB}/ec2/healthz | jq ."
curl -s "${ALB}/ec2/healthz" | jq .
sleep $pause_med

type_cmd "curl -s ${ALB}/fargate/healthz | jq ."
curl -s "${ALB}/fargate/healthz" | jq .
sleep $pause_med

type_cmd "curl -s ${ALB}/lambda/healthz | jq ."
curl -s "${ALB}/lambda/healthz" | jq .
sleep $pause_long

# =============================================================================
section "2 of 3  —  shorten then redirect, end-to-end on Lambda"
# =============================================================================

type_multi "curl -s -X POST -H 'Content-Type: application/json' \\
       -d '{\"url\":\"https://example.com\"}' \\
       ${ALB}/lambda/shorten | jq ."

RESULT=$(curl -s -X POST -H 'Content-Type: application/json' \
              -d '{"url":"https://example.com"}' \
              "${ALB}/lambda/shorten")
echo "$RESULT" | jq .
CODE=$(echo "$RESULT" | jq -r .code)
sleep $pause_med

type_cmd "curl -s -i ${ALB}/lambda/r/${CODE} | head -3"
curl -s -i "${ALB}/lambda/r/${CODE}" | head -3
sleep $pause_long

# =============================================================================
section "3 of 3  —  artifact: regenerate every figure from raw measurements"
# =============================================================================

type_cmd "ls data/results/run-personal-20260418T154912Z/*.json"
ls data/results/run-personal-20260418T154912Z/*.json
sleep $pause_med

type_cmd "python -m analysis.build_figures run-personal-20260418T154912Z"
# activate venv quietly if present
if [ -f .venv-analysis/bin/activate ]; then
  source .venv-analysis/bin/activate 2>/dev/null || true
fi
python -m analysis.build_figures run-personal-20260418T154912Z 2>&1 | tail -3
sleep $pause_med

type_cmd "ls report/figures/*.pdf"
ls report/figures/*.pdf
sleep $pause_med

type_cmd "open report/main.pdf"
open report/main.pdf
sleep $pause_long

printf "\n%sdone.%s\n" "$HEAD" "$RESET"
