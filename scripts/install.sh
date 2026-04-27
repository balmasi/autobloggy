#!/usr/bin/env bash
# Install Autobloggy: Python deps, Playwright browser, and agent skill copies.
set -euo pipefail

cd "$(dirname "$0")/.."

echo "==> uv sync"
uv sync

echo "==> playwright install chromium"
uv run playwright install chromium

echo "==> install skills into .agents/ and .claude/"
npx skills experimental_install -y

echo "Done."
