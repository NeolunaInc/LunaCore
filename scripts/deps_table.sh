#!/bin/bash
set -euo pipefail
LOCK="poetry.lock"
[ -f "$LOCK" ] || { echo "poetry.lock introuvable"; exit 1; }
awk '
  /^\[\[package\]\]/ { p=1; name=""; version=""; groups=""; next }
  p && /^name = /     { gsub(/["]/,""); name=$3 }
  p && /^version = /  { gsub(/["]/,""); version=$3 }
  p && /^groups = /   { gsub(/[\[\]",]/,""); groups=$3" "$4 }
  p && /^description = / { desc=$0; sub(/^description = /,"",desc); gsub(/"/,"",desc) }
  p && /^\s*$/        { if(name!="") print name"\t"version"\t"groups"\t"desc; p=0 }
' "$LOCK" | column -t -s $'\t'
