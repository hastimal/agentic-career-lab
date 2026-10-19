#!/usr/bin/env bash
# Preflight for the Docker Compose path (#9).
#
# Checks the host tools, the local Ollama runtime and the model it serves, the
# app port, and the container -> host route *before* anything is launched, and
# prints the one command that fixes whatever failed. It installs nothing, reads
# no secrets, and sends no telemetry.

set -euo pipefail

APP_PORT="${ACL_APP_PORT:-8501}"
MODEL="${GEMMA_MODEL:-gemma4:12b}"
OLLAMA_URL="${ACL_OLLAMA_URL:-http://host.docker.internal:11434}"
DRY_RUN=0
NO_PROMPT=0
ASSUME_YES=0
FAILED=0

usage() {
    cat <<'EOF'
Usage: scripts/setup.sh [--dry-run] [--no-prompt] [--yes] [--port N] [--model NAME]

  --dry-run    print the commands that have side effects instead of running them
  --no-prompt  never ask; print the missing command and exit non-zero
  --yes, -y    pull the model without asking
  --port N     app port to check (default 8501, or ACL_APP_PORT)
  --model M    model to require (default gemma4:12b, or GEMMA_MODEL)
  --help, -h   this text

Exits 0 when ready, 1 when a check failed, 2 when the model pull was declined.
EOF
}

pass() { printf '[PASS] %s\n' "$*"; }
warn() { printf '[WARN] %s\n' "$*"; }
fail() { printf '[FAIL] %s\n' "$*"; FAILED=1; }
hint() { printf '       %s\n' "$*"; }
step() { printf '\n%s\n' "$*"; }

# Run a command, or print it when --dry-run is set, so the script can be
# exercised without Docker or a model pull.
run() {
    if [ "$DRY_RUN" -eq 1 ]; then
        printf '       (dry run) %s\n' "$*"
        return 0
    fi
    "$@"
}

need() {
    command -v "$1" >/dev/null 2>&1
}

has_model() {
    ollama list 2>/dev/null | awk 'NR>1 {print $1}' | grep -qx "$MODEL"
}

while [ "$#" -gt 0 ]; do
    case "$1" in
        --dry-run) DRY_RUN=1 ;;
        --no-prompt) NO_PROMPT=1 ;;
        --yes|-y) ASSUME_YES=1 ;;
        --port)
            [ "$#" -ge 2 ] || { echo "--port needs a value" >&2; exit 1; }
            APP_PORT="$2"; shift ;;
        --model)
            [ "$#" -ge 2 ] || { echo "--model needs a value" >&2; exit 1; }
            MODEL="$2"; shift ;;
        -h|--help) usage; exit 0 ;;
        *) echo "unknown argument: $1 (try --help)" >&2; exit 1 ;;
    esac
    shift
done

printf 'Agentic Career Lab — Docker Compose preflight\n'
printf 'port %s · model %s · ollama %s' "$APP_PORT" "$MODEL" "$OLLAMA_URL"
if [ "$DRY_RUN" -eq 1 ]; then
    printf ' · dry run'
fi
printf '\n'

step '1/5 Host tools'
if need docker; then
    pass "Docker CLI $(docker --version 2>/dev/null | sed 's/^Docker version //;s/,.*//')"
else
    fail 'Docker CLI not found'
    hint 'Install Docker Desktop (macOS/Windows) or docker-ce + the compose plugin (Linux):'
    hint '  https://docs.docker.com/engine/install/'
fi

if need docker && docker info >/dev/null 2>&1; then
    pass 'Docker daemon is reachable'
else
    fail 'Docker daemon is not reachable'
    hint 'Start Docker Desktop, or `sudo systemctl start docker` on Linux.'
fi

if need docker && docker compose version >/dev/null 2>&1; then
    pass "Compose plugin $(docker compose version --short 2>/dev/null)"
else
    fail 'Docker Compose plugin not found (the `docker compose` subcommand)'
    hint 'Install the plugin: https://docs.docker.com/compose/install/'
fi

if need uv; then
    pass "uv $(uv --version 2>/dev/null | awk '{print $2}')"
else
    fail 'uv not found (needed for the local Python path and the test suite)'
    hint 'Install it: curl -LsSf https://astral.sh/uv/install.sh | sh'
fi

step '2/5 Local Ollama runtime'
if need ollama; then
    pass 'ollama CLI found'
else
    fail 'ollama not found'
    hint 'Install it: https://ollama.com/download — the container reaches it on the host.'
fi

if need ollama; then
    if has_model; then
        pass "model $MODEL is pulled"
    elif [ "$ASSUME_YES" -eq 1 ]; then
        printf '       pulling %s (this downloads several GB)\n' "$MODEL"
        if run ollama pull "$MODEL"; then
            if has_model; then
                pass "model $MODEL is pulled"
            else
                fail "model $MODEL is still missing after the pull"
            fi
        else
            fail "ollama pull $MODEL failed"
        fi
    else
        fail "model $MODEL is not pulled"
        hint "Pull it: ollama pull $MODEL"
        if [ "$NO_PROMPT" -eq 0 ] && [ "$DRY_RUN" -eq 0 ] && [ -t 0 ]; then
            printf '       pull it now? [y/N] '
            read -r answer
            case "$answer" in
                y|Y|yes|YES)
                    if run ollama pull "$MODEL"; then
                        pass "model $MODEL is pulled"
                    else
                        fail "ollama pull $MODEL failed"
                    fi
                    ;;
                *)
                    hint 'Declined; nothing was pulled.'
                    exit 2
                    ;;
            esac
        fi
    fi
fi

step "3/5 Port $APP_PORT"
if need nc; then
    if nc -z 127.0.0.1 "$APP_PORT" >/dev/null 2>&1; then
        fail "port $APP_PORT is already in use"
        hint 'Stop the process holding it, or pick another port:'
        hint '  ACL_APP_PORT=8502 scripts/setup.sh'
    else
        pass "port $APP_PORT is free"
    fi
else
    warn 'nc not found, skipping the port check'
    hint 'Install netcat (macOS: preinstalled, Debian: apt install netcat-openbsd).'
fi

step '4/5 Container -> host Ollama route'
if [ "$FAILED" -ne 0 ]; then
    warn 'skipped: fix the failures above first'
elif [ "$DRY_RUN" -eq 1 ]; then
    printf '       %s/api/tags\n' "$OLLAMA_URL"
    run docker compose run --rm --no-deps --entrypoint curl app -fsS -m 5 "$OLLAMA_URL/api/tags"
else
    printf '       %s/api/tags\n' "$OLLAMA_URL"
    if docker compose run --rm --no-deps --entrypoint curl app -fsS -m 5 "$OLLAMA_URL/api/tags" >/dev/null 2>&1; then
        pass 'the app container reaches Ollama on the host'
    else
        fail 'the app container cannot reach Ollama on the host'
        hint 'On Linux the compose file adds host.docker.internal via extra_hosts;'
        hint 'if Ollama listens on 127.0.0.1 only, start it with OLLAMA_HOST=0.0.0.0:11434.'
    fi
fi

step '5/5 Next step'
if [ "$FAILED" -ne 0 ]; then
    printf '\n'
    fail 'not ready: fix the items above and run this script again'
    exit 1
fi

printf '\n'
pass 'ready'
printf '       docker compose up -d --build\n'
printf '       Streamlit: http://localhost:%s\n' "$APP_PORT"
printf '       Logs:      docker compose logs -f app\n'
printf '       Stop:      docker compose down\n'
