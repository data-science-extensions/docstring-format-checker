---
name: pull-request
description: Generate a comprehensive description for the current feature branch's pull request, following this repository's conventions. Use when preparing a pull request description.
argument-hint: "[issue number] [PR number]"
user-invocable: true
disable-model-invocation: true
---

# Write Pull Request Description

Draft a comprehensive pull request description for the current feature branch against `main`.


## 🧭 Prerequisites

- Identify the current branch and verify changes against `main`.
- Review the commit history and `git diff` to understand the full scope of implementation. Read commit messages in detail and synthesise their information.
- Review existing PR descriptions in `git_output/prs/` for style.
- Check related issues in `git_output/issues/` if an issue number is provided.
- Verify whether changes pass the project's QA pipeline with `uv run ./src/utils/scripts.py lint-check`.
- Follow the repository's [pull request instructions](../../instructions/pull_request.instructions.md).


## 🙋 User Input Required

Before proceeding, ask for:

1. The issue number this PR closes. Check `git_output/issues/` for a related `#X.md` file and suggest its number for confirmation. If there is no related issue, ask for an issue number or `None`. Do not include a `Closes #X` section when the user says `None`.
2. The PR number for the new description file. Check `git_output/prs/` for the highest existing `#X.md` and suggest the next sequential number for confirmation.
3. Any Copilot summary or specific feedback to incorporate. Include a Copilot Summary section only when the user provides one; omit it if the user says `No` or provides no response.
4. Whether to run `uv run src/utils/scripts.py lint-check`. Run it if the user says yes or provides no response; skip it if the user says no.


## ⚙️ Execution

1. Synthesise code changes into a detailed report, highlighting architectural improvements and API changes.
2. Follow the repository's PR formatting rules, including Australian English spelling and icon-prefixed H2 headings.
3. Wrap code symbols in backticks and follow the repository's function, class, and method formatting conventions. Label symbols in prose.
4. Verify that any new or modified functions have DFC-compliant docstrings.
5. Save the final description to `git_output/prs/#[PR_NUMBER].md`.
