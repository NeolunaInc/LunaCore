#!/bin/bash
set -euo pipefail
REPO="${1:-NeoLunaInc/LunaCore}"
echo "Seeding extra labels on $REPO"
gh label create "ci" --repo "$REPO" --color "0366d6" --description "CI-related changes" || \
gh label edit   "ci" --repo "$REPO" --color "0366d6" --description "CI-related changes"
gh label create "tooling" --repo "$REPO" --color "0e8a16" --description "Dev tooling / build" || \
gh label edit   "tooling" --repo "$REPO" --color "0e8a16" --description "Dev tooling / build"
echo "OK."
