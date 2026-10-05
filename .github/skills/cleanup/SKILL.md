---
name: cleanup
description: Audit and fix linting, typing, testing, and documentation issues to bring this repository into a green state. Use when asked to perform project-wide QA or cleanup.
user-invocable: true
disable-model-invocation: true
---

# QA and Cleanup

Perform a comprehensive quality audit and cleanup of the codebase to bring the project into full compliance with its standards.


## 🧭 Prerequisites

- Run the full QA suite using `uv run src/utils/scripts.py lint-check`.
- Follow the repository's [Copilot instructions](../../copilot-instructions.md), particularly the typing and docstring requirements.


## ⚙️ Execution

1. Fix linting and typing errors, particularly those reported by `pylint` and `pyright`.
2. Avoid `Any` and replace pipe (`|`) type unions with `Union[]`.
3. Avoid `# pylint: disable` comments unless absolutely necessary.
4. Add explicit type hints to variables and function signatures.
5. Resolve failing tests using `pytest` assert style. Maintain 100% code coverage and use the standard `pytest` structure. Prefer one assert check per method where feasible.
6. Run `dfc` to validate docstring order and formatting. Fix DFC violations and use Google-style admonitions.
7. Re-run `lint-check` until the workspace is clean.


## 🛠️ Troubleshooting

- If an error cannot be resolved without violating architectural principles, document the reasoning before applying a `# pylint: disable` comment.
- Ignore `ty` warnings that say "Remove the unused suppression comment".
