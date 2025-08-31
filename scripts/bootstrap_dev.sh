#!/bin/bash
# Bootstrap script for LunaCore dev environment
# Run with: bash scripts/bootstrap_dev.sh
# This script is in echo-only mode for documentation

set -euo pipefail

echo "=== LunaCore Dev Bootstrap ==="
echo "This script documents the setup steps."
echo "Run each command manually or uncomment as needed."
echo ""

echo "1. System dependencies (requires sudo):"
echo "# sudo apt update"
echo "# sudo apt install -y build-essential git curl make jq unzip"
echo "# sudo apt install -y docker.io docker-compose-v2"
echo "# sudo apt install -y gh libpq-dev pkg-config"
echo ""

echo "2. Python via pyenv:"
echo "# curl https://pyenv.run | bash"
echo "# echo 'export PATH=\"\$HOME/.pyenv/bin:\$PATH\"' >> ~/.bashrc"
echo "# echo 'eval \"\$(pyenv init -)\"' >> ~/.bashrc"
echo "# source ~/.bashrc"
echo "# pyenv install 3.12.7"
echo "# pyenv global 3.12.7"
echo ""

echo "3. Poetry:"
echo "# pipx install poetry"
echo "# poetry --version"
echo ""

echo "4. Verifications:"
echo "# docker --version"
echo "# gh --version"
echo "# python --version"
echo "# poetry --version"
echo ""

echo "5. Project setup:"
echo "# poetry install"
echo "# poetry run pre-commit install"
echo ""

echo "6. Test run:"
echo "# make run-api"
echo "# curl http://localhost:8000/healthz"
echo ""

echo "Bootstrap complete! See docs/SETUP.md for details."
