#!/bin/bash
# install_extension.sh
# Installs the MadCore Engine Launcher extension into Antigravity.
# Run this once after cloning the repo, or after updating the extension source.

set -e

SRC="$(cd "$(dirname "$0")/madcore-extension" && pwd)"
DEST="$HOME/.antigravity/extensions/madcore-dev-server-1.0.0"

echo "⚡ Installing MadCore Dev Server extension..."
echo "   Source : $SRC"
echo "   Target : $DEST"

rm -rf "$DEST"
cp -r "$SRC" "$DEST"

echo ""
echo "✅ Done! Reload the Antigravity window to activate:"
echo "   Cmd+Shift+P → Developer: Reload Window"
echo "   Then open the 'MadCore Dev Server' tab in the sidebar."
