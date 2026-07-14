#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
dist="$root/dist"

rm -rf "$dist"
mkdir -p "$dist/claude/a-share-corner-case-finder"
mkdir -p "$dist/chatgpt/knowledge"

cp "$root/SKILL.md" "$dist/claude/a-share-corner-case-finder/"
cp -R "$root/references" "$dist/claude/a-share-corner-case-finder/"
cp -R "$root/assets" "$dist/claude/a-share-corner-case-finder/"

cp "$root/adapters/chatgpt/instructions.md" "$dist/chatgpt/INSTRUCTIONS.md"
cp "$root/adapters/chatgpt/config.md" "$dist/chatgpt/CONFIG.md"
cp "$root/references/"*.md "$dist/chatgpt/knowledge/"
cp "$root/assets/"*.md "$dist/chatgpt/knowledge/"

(
  cd "$dist/claude"
  zip -qr ../a-share-corner-case-finder-claude.zip a-share-corner-case-finder
)

(
  cd "$dist/chatgpt"
  zip -qr ../a-share-corner-case-finder-chatgpt.zip INSTRUCTIONS.md CONFIG.md knowledge
)

printf '%s\n' "Built packages in $dist"
