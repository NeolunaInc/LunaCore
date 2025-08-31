#!/bin/bash
# Enable pre-commit hooks for LunaCore
# Run with: bash scripts/enable_hooks.sh

set -euo pipefail

echo "=== Enabling Pre-commit Hooks ==="

# Install hooks if not already
poetry run pre-commit install

echo "Hooks installed."

# Dry run to show what would be checked
echo "Dry run of all hooks:"
poetry run pre-commit run --all-files --dry-run

echo "To run hooks: poetry run pre-commit run --all-files"
echo "Hooks enabled! See docs/OPS.md for more."
