#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${ENV_FILE:-$SCRIPT_DIR/.env}"

if [[ -f "$ENV_FILE" ]]; then
  # shellcheck disable=SC1090
  source "$ENV_FILE"
fi

: "${OCI_GENAI_API_KEY:?Set OCI_GENAI_API_KEY in .env or environment.}"
: "${REGION:?Set REGION in .env or environment.}"
: "${MODEL_ID:?Set MODEL_ID in .env or environment.}"

OPENAI_BASE_URL="${OPENAI_BASE_URL:-https://inference.generativeai.${REGION}.oci.oraclecloud.com/openai}"
MODEL_TOKENIZER="${MODEL_TOKENIZER:-Qwen/Qwen2.5-7B-Instruct}"
GENAI_BENCH_BIN="${GENAI_BENCH_BIN:-genai-bench}"
PROJECT_ID="${PROJECT_ID:-}"
MAX_TIME_PER_RUN="${MAX_TIME_PER_RUN:-20}"
MAX_REQUESTS_PER_RUN="${MAX_REQUESTS_PER_RUN:-200}"
TRAFFIC_SCENARIO="${TRAFFIC_SCENARIO:-N(1000,200)/(120,40)}"
CONCURRENCY_LEVELS="${CONCURRENCY_LEVELS:-8 16 32 64 96}"
RUN_TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
EXPERIMENT_FOLDER_NAME="${EXPERIMENT_FOLDER_NAME:-benchmark_run_${RUN_TIMESTAMP}}"

if [[ -n "$PROJECT_ID" ]]; then
  export OPENAI_PROJECT="$PROJECT_ID"
else
  unset OPENAI_PROJECT 2>/dev/null || true
fi

if ! command -v "$GENAI_BENCH_BIN" >/dev/null 2>&1; then
  echo "genai-bench not found: $GENAI_BENCH_BIN" >&2
  echo "Set GENAI_BENCH_BIN to the full path of the binary or install genai-bench in your environment." >&2
  exit 1
fi

args=(
  benchmark
  --api-backend openai
  --api-base "$OPENAI_BASE_URL"
  --api-key "$OCI_GENAI_API_KEY"
  --api-model-name "$MODEL_ID"
  --model-tokenizer "$MODEL_TOKENIZER"
  --task text-to-text
  --max-time-per-run "$MAX_TIME_PER_RUN"
  --max-requests-per-run "$MAX_REQUESTS_PER_RUN"
  --traffic-scenario "$TRAFFIC_SCENARIO"
  --experiment-folder-name "$EXPERIMENT_FOLDER_NAME"
)

for concurrency in $CONCURRENCY_LEVELS; do
  args+=(--num-concurrency "$concurrency")
done

"$GENAI_BENCH_BIN" "${args[@]}"
