#!/usr/bin/env bash
set -euo pipefail

# Aller à la racine du repo si possible
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

TS="$(date +%Y%m%d_%H%M%S)"
OUT="export/lunacore_new_session_${TS}"
MD="${OUT}.md"
ZIP="${OUT}.zip"
mkdir -p export

BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)"
COMMIT="$(git rev-parse --short HEAD 2>/dev/null || echo none)"
NOW="$(date --iso-8601=seconds 2>/dev/null || date -u +"%Y-%m-%dT%H:%M:%SZ")"

# Liste des fichiers importants (ajuste si besoin)
FILES=(
  README.md
  docs/STATUS_PHASE1.md
  docs/PHASES_FULL.md
  docs/PHASES.md
  docs/ROADMAP.md
  docs/SETUP.md
  docs/SETUP_DEPENDENCIES.md
  docs/DEPENDENCIES.md
  docs/DEVELOPMENT.md
  docs/WORKFLOWS.md
  docs/EXPORTS.md
  docs/CONTRIBUTING.md
  docs/OPS.md
  docs/HANDOFF.md
  docs/DECISIONS.md
  docs/ARCHITECTURE.md
  docs/MASTER_IDENTITE.md
  docs/MASTER_IDENTITE.txt
  .github/workflows/ci.yml
  pyproject.toml
  Makefile
  docker-compose.yml
)

# Ajouter tous les docs sous docs/phases/** (md/txt)
if [ -d docs/phases ]; then
  while IFS= read -r f; do FILES+=("$f"); done < <(find docs/phases -type f \( -name "*.md" -o -name "*.txt" \) | sort)
fi

# Garder uniquement ceux qui existent
SEL=()
for f in "${FILES[@]}"; do [ -f "$f" ] && SEL+=("$f"); done

# En-tête du compendium
{
  printf "# LunaCore — New Session Pack\n\n"
  printf -- "- Branch : %s\n" "$BRANCH"
  printf -- "- Commit : %s\n" "$COMMIT"
  printf -- "- Généré : %s\n\n" "$NOW"
  printf "## Fichiers inclus (%s)\n" "${#SEL[@]}"
  for f in "${SEL[@]}"; do size=$(wc -c <"$f" | tr -d " "); printf -- "- %s (%s bytes)\n" "$f" "$size"; done
  printf "\n---\n\n"
} > "$MD"

# Contenu des fichiers avec fences
for f in "${SEL[@]}"; do
  base="${f##*/}"; ext="${base##*.}"
  case "$ext" in
    md)   lang="markdown" ;;
    yml|yaml) lang="yaml" ;;
    toml) lang="toml" ;;
    sh)   lang="bash" ;;
    py)   lang="python" ;;
    *)    lang="" ;;
  esac
  printf "## FILE: %s\n\n" "$f" >> "$MD"
  if [ -n "$lang" ]; then printf "\`\`\`%s\n" "$lang" >> "$MD"; else printf "\`\`\`\n" >> "$MD"; fi
  sed -e "s/\r$//" "$f" >> "$MD"
  printf "\n\`\`\`\n\n" >> "$MD"
done

# Archive ZIP (si zip dispo)
if command -v zip >/dev/null 2>&1 && [ "${#SEL[@]}" -gt 0 ]; then
  zip -q "$ZIP" "${SEL[@]}"
fi

# Checksums
sha256sum "$MD" > "${OUT}.sha256"
[ -f "$ZIP" ] && sha256sum "$ZIP" >> "${OUT}.sha256"

echo
echo "✅ Export généré :"
echo " - ${MD}"
[ -f "$ZIP" ] && echo " - ${ZIP}"
echo " - ${OUT}.sha256"
