
ADR-0001 — Ollama host (11434) vs container
Décision
Nous conservons Ollama installé sur l’hôte (port 11434) et non le service Docker pour éviter les conflits et simplifier l’admin.

Raisons
Déjà présent et opérationnel avec llama3:8b.

Moins de friction réseau, pas de port clash avec compose.

Simplicité pour les tests locaux.

Comment basculer vers le conteneur (si besoin)
Ajouter service ollama dans docker-compose.yml (profiles: ["ollama"]).

Exporter OLLAMA_BASE_URL=http://localhost:11434 vers le conteneur.

S’assurer que le port 11434 n’est pas déjà occupé par l’hôte.
