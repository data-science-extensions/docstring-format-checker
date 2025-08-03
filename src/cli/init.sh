cd docstring-format-checker
curl -LsSf https://astral.sh/uv/install.sh | sh
uv self update
uv --version
uv sync --all-groups
.venv/bin/activate
uv run pre-commit install
uv run pre-commit autoupdate
