#!/usr/bin/env bash
# Installs the Orchard plugin into a project as <project>/.claude/skills/orchard, as a real copy.
# Claude Code refuses a plugin whose folders are links pointing outside it, so the links in plugin/ are resolved
# here. Run it again to update the copy after the skill set changes. Keeps the copy out of git (local exclude).
#
#   install.sh <project root>
set -euo pipefail
PROJECT="$(cd "${1:?usage: install.sh <project root>}" && pwd -P)"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
ORCHARD="$(cd "$HERE/../.." && pwd -P)"
case "$PROJECT" in "$ORCHARD"|"$ORCHARD"/*) echo "refusing to install into the skill set itself" >&2; exit 64 ;; esac
TARGET="$PROJECT/.claude/skills/orchard"
mkdir -p "$PROJECT/.claude/skills"
if [ -L "$TARGET" ]; then rm "$TARGET"; fi
if [ -e "$TARGET" ] && [ ! -f "$TARGET/.orchard-install" ]; then
  echo "$TARGET exists and was not made by this script; leaving it alone" >&2; exit 1
fi
STAGE="$(mktemp -d "${TMPDIR:-/tmp}/orchard-install.XXXXXX")"
cp -RL "$HERE/plugin" "$STAGE/orchard"
find "$STAGE/orchard" -name '__pycache__' -type d -prune -exec rm -rf {} +
{
  echo "source: $ORCHARD"
  echo "commit: $(git -C "$ORCHARD" rev-parse --short HEAD 2>/dev/null || echo none)$(git -C "$ORCHARD" diff --quiet HEAD 2>/dev/null || echo ' (with uncommitted changes)')"
  echo "installed: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
} > "$STAGE/orchard/.orchard-install"
if [ -e "$TARGET" ]; then rm -rf "${TARGET:?}"; fi
mv "$STAGE/orchard" "$TARGET"
rmdir "$STAGE"
if git -C "$PROJECT" rev-parse --git-dir >/dev/null 2>&1 && ! git -C "$PROJECT" check-ignore -q "$TARGET"; then
  EXCLUDE="$(git -C "$PROJECT" rev-parse --git-path info/exclude)"
  case "$EXCLUDE" in /*) ;; *) EXCLUDE="$PROJECT/$EXCLUDE" ;; esac
  mkdir -p "$(dirname "$EXCLUDE")"
  echo ".claude/skills/orchard/" >> "$EXCLUDE"
fi
echo "installed: $TARGET"
cat "$TARGET/.orchard-install"
