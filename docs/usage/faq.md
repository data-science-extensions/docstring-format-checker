# Frequently Asked Questions

This page provides answers to common questions about using and configuring the `docstring-format-checker` package.


## 🎯 Which docstring style is this built for?

`docstring-format-checker` is primarily designed to support [**Google-style**][google-style] docstrings. This style is popular because it is highly readable and uses clear indentation to separate different sections like parameters and return values.

However, the tool is not strictly limited to a single style. Because it is configuration-driven, you can **customise** the section names and types in your [`pyproject.toml`](pyproject.toml) to match your team's specific requirements. You can define your own sections using types like `free_text`, `list_name`, `list_type`, and `list_name_and_type`.


## 🧩 Why doesn't it support NumPy or reStructuredText (reST) styles?

We chose to focus on a "section-based" model that works exceptionally well with Google-style formatting. By focusing on AST (Abstract Syntax Tree) parsing rather than complex regular expressions, we can provide much more reliable validation for the most common use cases.

While NumPy and reST are powerful, they often require significantly more complex parsing logic. By keeping the tool focused, we ensure it remains fast, lightweight, and extremely accurate for the styles it does support.


## 🪄 Does it automatically fix my docstrings, like other packages such as [`black`][black] and [`isort`][isort] fixes my code?

No, `docstring-format-checker` is currently a **validator**, not a formatter. It will tell you exactly what is wrong and where, but it won't change the docs in your code.

Think of it like [`pylint`][pylint] or [`pyright`][pyright], it's designed to be used in your CI/CD pipelines or as a pre-commit hook to ensure that everyone on your team follows the same standards.


## 🌳 What is "AST parsing" and why should I care?

AST stands for **Abstract Syntax Tree**. Most simple tools use "Regular Expressions" (regex) to look for patterns in your text. This can often get confused by complex code structures, decorators, or nested classes.

`docstring-format-checker` actually "reads" your Python code just like the Python interpreter does using the [`ast`][ast] module. This means it has a perfect understanding of which docstring belongs to which function or class, making it much more robust and less likely to give you "false positives" (wrongly reported errors).


## 👯 Why are there two commands (`dfc` and `docstring-format-checker`)?

Both commands perform exactly the same actions. We provide `docstring-format-checker` as the primary command, and is descriptive for clarity and discoverability. However, because that can be quite a lot to type, we also provide `dfc` as a convenient short-hand alias for daily use in your terminal.

Similarly, you can use either `[tool.dfc]` or `[tool.docstring-format-checker]` in your [`pyproject.toml`](pyproject.toml) file. The tool will look for `dfc` first, and then fall back to the longer name if the shorter one isn't found. This ensures your configuration remains tidy while still being descriptive.


## 🤐 Can I skip private functions or specific files?

Absolutely! We recognise that you might not want to document every single helper function in your codebase.

- **Private Items**: You can toggle `check_private = false` in your configuration to ignore anything starting with an underscore.
- **Exclusions**: Use the `--exclude` flag or define exclusion patterns in your [`pyproject.toml`](pyproject.toml) to skip specific files or entire directories (like `src/tests/` or `migrations/`).


## 🛠️ How do I handle "Optional" types in my parameters?

The tool includes an `optional_style` configuration. This allows you to decide how strictly you want to enforce the `Optional` label in your docstrings when a parameter has a default value of `None`.

You can choose from three behaviours:

- `silent`: No special checks for `Optional`.
- `validate`: Ensures that if you say a parameter is optional, it actually has a default value.
- `strict`: **Requires** you to mark parameters as optional in the docstring if they have a default value of `None` in the signature.


## 🚀 How do I use this in my CI/CD pipeline?

We recommend running `dfc` (or `docstring-format-checker`) with the `--check` flag in your pipeline. This flag will cause the tool to return a non-zero exit code if any errors are found, which will "break the build" and alert you to the problem.

```bash
# Example for a CI pipeline
dfc --check src/
```


[google-style]: https://google.github.io/styleguide/pyguide.html
[black]: https://black.readthedocs.io/en/
[isort]: https://pycqa.github.io/isort/
[pylint]: https://pylint.readthedocs.io/
[pyright]: https://microsoft.github.io/pyright/#/
[ast]: https://docs.python.org/3/library/ast.html
