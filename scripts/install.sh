#!/usr/bin/env bash
# Install Autobloggy: Python deps, Playwright browser, and agent skill copies.
set -euo pipefail

cd "$(dirname "$0")/.."

# Preflight checks
if ! command -v uv &>/dev/null; then
  echo "ERROR: uv not found. Install it with:"
  echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
  exit 1
fi

if ! command -v npx &>/dev/null; then
  echo "ERROR: npx not found. Install Node.js (v18+) from https://nodejs.org"
  exit 1
fi

echo "==> uv sync"
uv sync

echo "==> playwright install chromium"
uv run playwright install chromium

echo "==> install skills into .agents/ and .claude/"
npx skills add ./skills --agent claude-code codex -y

echo "Done."
