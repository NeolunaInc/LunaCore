# MASTER_IDENTITE (référence)

> **IMPORTANT** : Collez ici **la copie EXACTE** du document “master_identite”.  
> Ce dépôt conserve ce fichier comme **source de vérité** pour les règles d’exécution et de collaboration.

## Plan du document (si besoin de structurer)
1. **Mission & périmètre**
2. **Principes directeurs**
3. **Règles d’exécution pour assistants (Copilot/Grok)**
   - Ce que l’agent **PEUT** faire
   - Ce que l’agent **NE DOIT PAS** faire
   - Branching, PR, labels, milestones
4. **Qualité & CI**
5. **Sécurité & données**
6. **Process d’export / handoff**
7. **Glossaire**

## Résumé opérationnel (actuel)
- Branches : `feat/*`, `chore/*`, `fix/*`. Pas de merge direct vers `main`.
- Assistants : autorisés à créer branch/commit/push/PR; **interdits** de merger vers `main`.
- Pré-commit obligatoire (black/ruff).
- CI doit être **verte** avant merge.
- Exports : script fourni (`docs/EXPORTS.md`).

> 🔧 Quand le texte “maître” sera collé ici, supprimez ce résumé si redondant.
