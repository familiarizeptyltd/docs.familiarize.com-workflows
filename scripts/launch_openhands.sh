#!/usr/bin/env bash
set -euo pipefail

IMAGE=""
REPO_PATH=""
PROMPT_PATH=""
LLM_KIND=""
LLM_KEY="${LLM_KEY:-}"
LLM_BASE="${LLM_BASE:-}"
LLM_MODEL=""
ENABLE_BROWSING="true"
ENABLE_SEARCH="true"
LOG_DIR="openhands_run"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --image) IMAGE="$2"; shift 2 ;;
    --repo-path) REPO_PATH="$2"; shift 2 ;;
    --prompt-path) PROMPT_PATH="$2"; shift 2 ;;
    --llm-kind) LLM_KIND="$2"; shift 2 ;;
    --llm-key) LLM_KEY="$2"; shift 2 ;;
    --llm-base) LLM_BASE="$2"; shift 2 ;;
    --llm-model) LLM_MODEL="$2"; shift 2 ;;
    --enable-browsing) ENABLE_BROWSING="$2"; shift 2 ;;
    --enable-search) ENABLE_SEARCH="$2"; shift 2 ;;
    --logs) LOG_DIR="$2"; shift 2 ;;
    *) echo "Unknown arg: $1"; exit 2 ;;
  esac
done

if [[ -z "${IMAGE}" || -z "${REPO_PATH}" || -z "${PROMPT_PATH}" || -z "${LLM_KIND}" || -z "${LLM_MODEL}" ]]; then
  cat <<EOF
Missing required args.

IMAGE=${IMAGE}
REPO_PATH=${REPO_PATH}
PROMPT_PATH=${PROMPT_PATH}
LLM_KIND=${LLM_KIND}
LLM_MODEL=${LLM_MODEL}
EOF
  exit 2
fi

mkdir -p "${LOG_DIR}"

ENV_FLAGS=()
case "${LLM_KIND}" in
  openai)
    ENV_FLAGS+=("-e" "OPENAI_API_KEY=${LLM_KEY}")
    ENV_FLAGS+=("-e" "OPENAI_MODEL=${LLM_MODEL}")
    ;;
  openai_compat)
    ENV_FLAGS+=("-e" "OPENAI_API_KEY=${LLM_KEY}")
    ENV_FLAGS+=("-e" "OPENAI_BASE_URL=${LLM_BASE}")
    ENV_FLAGS+=("-e" "OPENAI_MODEL=${LLM_MODEL}")
    ;;
  grok)
    ENV_FLAGS+=("-e" "GROK_API_KEY=${LLM_KEY}")
    ENV_FLAGS+=("-e" "GROK_MODEL=${LLM_MODEL}")
    ;;
  *)
    echo "Unsupported LLM kind: ${LLM_KIND}"
    exit 2
    ;;
esac

# Feature toggles — update names if your image expects different envs
ENV_FLAGS+=("-e" "OH_ENABLE_BROWSING=${ENABLE_BROWSING}")
ENV_FLAGS+=("-e" "OH_ENABLE_SEARCH=${ENABLE_SEARCH}")

# NOTE: Replace the command below with the exact CLI your OpenHands image exposes if it differs.
docker run --rm \
  -v "$(pwd)/${REPO_PATH}:/workspace" \
  -v "$(pwd)/${PROMPT_PATH}:/prompt.md:ro" \
  -v "$(pwd)/${LOG_DIR}:/logs" \
  -e "OH_GOAL_FILE=/prompt.md" \
  "${ENV_FLAGS[@]}" \
  "${IMAGE}" \
  bash -lc 'openhands run --repo /workspace --goal-file "$OH_GOAL_FILE" --logs /logs || true'
