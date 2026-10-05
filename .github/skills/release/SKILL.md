---
name: release
description: Generate a comprehensive release description from commits since the previous tag, following this repository's release conventions. Use when preparing release notes for a new version.
argument-hint: "[new tag] [previous tag]"
user-invocable: true
disable-model-invocation: true
---

# Write Release Description

Draft a comprehensive description for a new release based on the commits since the last tag.


## 🧭 Prerequisites

- Identify the new version tag (for example, `v1.12.0`) and the previous tag (for example, `v1.11.4`).
- Analyse all commits more recent than the last tag.
- Review merged PR descriptions in `git_output/prs/` since the last release.
- Check the current `CHANGELOG.md` or git logs for feature details.
- Understand the impact on core components such as `docstring_format_checker/core.py` and `cli.py`.
- Follow the repository's [release instructions](../../instructions/release.instructions.md).


## 🙋 User Input Required

Before proceeding, ask for:

1. The new tag version. Check the current version in `pyproject.toml`, review changes since the previous release, and suggest a major bump for breaking changes, a minor bump for new backwards-compatible features, or a patch bump for bug fixes, minor documentation enhancements, or project configuration changes.
2. The previous tag version. Check `git tag` and suggest the latest tag.
3. Any PRs or contributors to highlight or exclude. Review the git logs and suggest a list for confirmation.
4. Whether to run `uv run src/utils/scripts.py lint-check`. Run it if the user says yes or provides no response; skip it if the user says no.


## ⚙️ Execution

1. Group changes into logical H3 categories, such as Core Logic, CLI Enhancements, and Documentation.
2. Use imperative mood and Australian English spelling.
3. Wrap code symbols in backticks and follow the repository's function, class, and method formatting conventions. Label symbols in prose.
4. Include a changes table with file counts and line metrics. Use `git diff --stat` to gather the available metrics for the release range.
5. Save the final description to `git_output/releases/[NEW_TAG].md`.
