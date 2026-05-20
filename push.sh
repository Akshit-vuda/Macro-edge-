#!/bin/bash
# Push MacroEdge to GitHub
# Run this from /workspace/project or any directory with the code

cd "$(dirname "$0")"

echo "Pushing MacroEdge to GitHub..."
git remote add origin https://github.com/Akshit-vuda/Macro-edge-.git 2>/dev/null || true
git push -u origin master

echo "Done! View at: https://github.com/Akshit-vuda/Macro-edge-