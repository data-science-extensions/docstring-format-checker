---
name: docs
description: Audit and improve Python docstrings and Markdown documentation in this repository to meet DFC and project documentation standards. Use when asked to harden or validate documentation.
user-invocable: true
disable-model-invocation: true
---

# Documentation Hardening

Audit and update docstrings and Markdown documentation in the `docstring-format-checker` library and `docs/` folder. Ensure compliance with the repository's [Copilot instructions](../../copilot-instructions.md), [chat instructions](../../instructions/chat.instructions.md), and `pyproject.toml` configuration.


## 📖 Docstring Standards

Follow the section order and formatting configured in `pyproject.toml` under `[tool.dfc]`.


### Required Sections

1. **Summary** (`!!! note "Summary"`): Required for all functions. Write a concise, one-sentence description of the function's purpose.
2. **Details** (`???+ abstract "Details"`): Recommended for public APIs. Explain what the function does and why.
3. **Parameters**: Use a standard Markdown list. Include every parameter's name, type (matching its Python type hint), and a brief description. Mention default values on a separate line as `Default: \`<default_value>\``.
4. **Raises and Returns**: Use standard Markdown lists. Match types to Python type hints. Do not include both `Returns` and `Yields` for one function.
5. **Examples** (`???+ example "Examples"`): Recommended for public APIs. Provide verified Python examples, preferably multiple `pycon` blocks for setup and distinct use cases. Include accurate output where relevant. Leave blank lines around each code block and before its closing fence.
6. **Calculation** (`??? equation "Calculation"`): Optional; use LaTeX for relevant mathematical definitions.
7. **Notes** (`??? note "Notes"`): Recommended for complex logic; explain useful context, edge cases, or implementation details.
8. **Credit** (`??? success "Credit"`): Recommended when adapting from another source; acknowledge the original authors or libraries.
9. **References** (`??? question "References"`): Optional; link to relevant standards and tools.
10. **See Also** (`??? tip "See Also"`): Recommended for related package functions.


## 📝 Documentation Page Standards

Apply these standards to pages in `docs/code/`.


### Header and Introduction

- Use a main heading such as `# Configuration Management`, `# CLI Management`, or `# Core Management`.
- Add an `## Introduction` section.


### Core Summary Block

Include one `!!! abstract "Summary"` admonition containing:

1. A relevant quote in a `!!! quote "As stated by [Source Name](URL):"` admonition.
2. An `!!! info "Info"` admonition explaining the component's importance and containing a table with the columns `tool`, `category`, `purpose`, `short`, `import script`, and `url`.
3. An `!!! example "Source Module"` admonition containing bulleted links to the relevant GitHub source files.


### API Reference

- Add a `## {Module} Reference` heading.
- Use `mkdocstrings` syntax, such as `::: docstring_format_checker.core`, with appropriate filters.


## 🔍 Workflow and Validation

1. Audit files in `src/docstring_format_checker/` and `docs/code/`.
2. Update docstrings to follow the DFC section order and admonition tags.
3. Update Markdown pages to follow the documentation page structure.
4. Run `uv run src/utils/scripts.py lint-check`. Fix reported DFC violations and MkDocs link or structure warnings.
5. Verify documentation examples. Use `uv run src/utils/scripts.py check-doctest-cli $MODULE` for a specific module, or `uv run src/utils/scripts.py check-doctest` for all modules when available. Correct output discrepancies.
6. Re-run relevant validation after making fixes.


## ✅ Completion Criteria

- `dfc` reports `✅ All docstrings are valid!`.
- `mkdocs build` completes without missing-link or formatting warnings.
- `pylint` remains at 10/10.
