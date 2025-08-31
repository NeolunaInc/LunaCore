# Exports (Markdown + ZIP + SHA256)

## Qu’est-ce que ça produit ?
- `lunacore_phase1_export_YYYYMMDD_HHMMSS.md` → contenu texte des fichiers suivis par Git.
- `... .zip` → archive des fichiers suivis par Git.
- `... .sha256` → sommes de contrôle.

## Script robuste (safe bash)
> Corrige les erreurs `awk` (mot-clé `in`) et `printf` (toujours citer).

```bash
#!/usr/bin/env bash
set -euo pipefail

TS="$(date +%Y%m%d_%H%M%S)"
OUT="lunacore_phase1_export_${TS}"
MD="/tmp/${OUT}.md"
ZIP="/tmp/${OUT}.zip"

BRANCH="$(git rev-parse --abbrev-ref HEAD)"
COMMIT="$(git rev-parse --short HEAD)"
NOW="$(date --iso-8601=seconds || date -u +"%Y-%m-%dT%H:%M:%SZ")"

# En-tête
{
  printf "# LunaCore — Phase 1 Export\n\n"
  printf "- Branche : %s\n" "$BRANCH"
  printf "- Commit  : %s\n" "$COMMIT"
  printf "- Généré  : %s\n\n" "$NOW"
  printf "## Fichiers inclus\n"
} > "$MD"

# Liste des fichiers suivis
git ls-files | while IFS= read -r f; do
  size="$(wc -c <"$f" | tr -d ' ')"
  printf "- %s (%s bytes)\n" "$f" "$size" >> "$MD"
done

# Séparateur
printf "\n" >> "$MD"

# Contenu détaillé
git ls-files | while IFS= read -r f; do
  printf "-----8<----- FILE: ./%s -----\n" "$f" >> "$MD"
  sed -e 's/\r$//' "$f" >> "$MD"
  printf "\n-----8<----- END FILE: ./%s -----\n\n" "$f" >> "$MD"
done

# Archive & checksum
zip -q -@ "$ZIP" < <(git ls-files)
sha256sum "$MD" "$ZIP" > "/tmp/${OUT}.sha256"

printf "Chemins export:\n- %s\n- %s\n- %s\n" "$MD" "$ZIP" "/tmp/${OUT}.sha256"

Astuces

Sur Windows/WSL, privilégier le script côté WSL (fin de ligne LF).

Toujours committer l’export seulement s’il est utile (sinon ignorer via .gitignore).
