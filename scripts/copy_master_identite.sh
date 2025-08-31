#!/bin/bash
set -euo pipefail
set -o pipefail

outdir="docs"
mkdir -p "$outdir"

# motifs
patterns=(
  "master*identite*"
  "identite*master*"
  "master_identite*"
  "MASTER_IDENTITE*"
)

# répertoires à scanner
roots=(
  "."
  "$HOME/projects"
  "$HOME/Documents"
  "$HOME/Downloads"
  "/tmp"
)

candidates=()
for root in "${roots[@]}"; do
  for pat in "${patterns[@]}"; do
    while IFS= read -r -d '' f; do
      case "${f,,}" in
        *.md|*.txt|*.pdf|*.rst) candidates+=("$f");;
      esac
    done < <(find "$root" -type f -iname "$pat" -print0 2>/dev/null || true)
  done
done

if [ "${#candidates[@]}" -eq 0 ]; then
  echo "Aucun 'master identite' trouvé. Chemins scannés:"
  printf ' - %s\n' "${roots[@]}"
  exit 1
fi

# choisir le plus récent
latest="$(ls -t "${candidates[@]}" | head -n1)"
ext="${latest##*.}"
dest="$outdir/MASTER_IDENTITE.$ext"
cp -f "$latest" "$dest"
sha="$(sha256sum "$dest" | awk "{print \$1}")"
echo "Copié: $latest → $dest"
echo "SHA256: $sha"
