#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"

if ! command -v hermes >/dev/null 2>&1; then
  printf '%s\n' "Hermes CLI is not installed or is not available on PATH." >&2
  printf '%s\n' "Install Hermes Agent using its official guide, then run this script again:" >&2
  printf '%s\n' "https://hermes-agent.nousresearch.com/docs/getting-started/installation" >&2
  exit 127
fi

cd "$repo_root"
printf 'Project directory: %s\n' "$repo_root"
printf '%s\n' "Choose OpenRouter and a model in the Hermes selector. The selection is saved by Hermes."

hermes model
exec hermes
