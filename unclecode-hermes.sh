#!/usr/bin/env bash
ROOT="$(cd "$(dirname "$0")" && pwd)"
unset PYTHONPATH
export VIRTUAL_ENV="$ROOT/.venv"
if [[ -d "$ROOT/.venv/Scripts" ]]; then
  export PATH="$ROOT/.venv/Scripts:$PATH"
  exec "$ROOT/.venv/Scripts/unclecode-hermes" "$@"
elif [[ -d "$ROOT/.venv/bin" ]]; then
  export PATH="$ROOT/.venv/bin:$PATH"
  exec "$ROOT/.venv/bin/unclecode-hermes" "$@"
else
  echo "No .venv found under $ROOT — create one and pip install -e ." >&2
  exit 1
fi
