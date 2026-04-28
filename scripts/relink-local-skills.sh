#!/usr/bin/env bash
# Replace each local skill's .agents/skills/<name> copy with a symlink to
# ../../skills/<name>. Idempotent. Skips entries that are already correct
# symlinks and skips entries with no matching source dir (GitHub-installed
# skills). The .claude/skills/<name> symlink to .agents/skills/<name> is
# managed by `npx skills add` and is left alone.
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$repo_root"

[ -d skills ] || exit 0
[ -d .agents/skills ] || exit 0

for src in skills/*/; do
  name="$(basename "$src")"
  target=".agents/skills/$name"
  link_dest="../../skills/$name"

  if [ -L "$target" ]; then
    current="$(readlink "$target")"
    [ "$current" = "$link_dest" ] && continue
    rm "$target"
  elif [ -e "$target" ]; then
    rm -rf "$target"
  else
    continue
  fi

  ln -s "$link_dest" "$target"
done
