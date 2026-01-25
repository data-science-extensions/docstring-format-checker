# Standardise Your Documentation with Configuration

Define your own standards and ensure consistency across your project with a `pyproject.toml` file. `docstring-format-checker` (or `dfc`) offers a wide range of configuration options to suit any project's needs.


<style>
    .scroll-chunks {
        max-height: 400px;
        overflow: auto;
    }
</style>


## 🌍 Global Configuration Options

Configuring these options at the top-level of the `[tool.dfc]` section affect how `dfc` behave across all checked files.

There are five main global options you can set.


### 1. Require Docstring

Enforce documentation across your entire project by setting `require_docstrings` to `true`.

|        Config        |   Type    | Required | Default |
| :------------------: | :-------: | :------: | :-----: |
| `require_docstrings` | `boolean` |    no    | `true`  |

When enabled, `dfc` flags any public function, method, or class that lacks a docstring.

| Option  | Description                                         |
| ------- | --------------------------------------------------- |
| `true`  | `dfc` will report missing docstrings as errors.     |
| `false` | `dfc` will not report missing docstrings as errors. |

<div class="scroll-chunks" markdown>
```toml {.toml linenums="1" title="pyproject.toml" hl_lines="2"}
--8<-- "docs/usage/examples/config_full.toml"
```
</div>


### 2. Check Private Members

By default, `dfc` only check public members (those that do not start with an underscore `_`).

|     Config      |   Type    | Required | Default |
| :-------------: | :-------: | :------: | :-----: |
| `check_private` | `boolean` |    no    | `false` |

Set `check_private` to `true` to include private functions and methods in the checks.

| Option  | Description                                       |
| ------- | ------------------------------------------------- |
| `true`  | `dfc` will check both public and private members. |
| `false` | `dfc` will only check public members.             |

<div class="scroll-chunks" markdown>
```toml {.toml linenums="1" title="pyproject.toml" hl_lines="3"}
--8<-- "docs/usage/examples/config_full.toml"
```
</div>


### 3. Allow Undefined Sections

Control how `dfc` handle sections that be not explicitly defined in your configuration.

|           Config           |   Type    | Required | Default |
| :------------------------: | :-------: | :------: | :-----: |
| `allow_undefined_sections` | `boolean` |    no    | `false` |

If set to `false`, any section header found in a docstring that do not match a defined section name raise an error.

| Option  | Description                                     |
| ------- | ----------------------------------------------- |
| `true`  | `dfc` will ignore any undefined sections.       |
| `false` | `dfc` will report undefined sections as errors. |

<div class="scroll-chunks" markdown>
```toml {.toml linenums="1" title="pyproject.toml" hl_lines="4"}
--8<-- "docs/usage/examples/config_full.toml"
```
</div>


### 4. Validate Parameter Types

Ensure that all parameters in your `Params` (or similar) section include type annotations.

|         Config         |   Type    | Required | Default |
| :--------------------: | :-------: | :------: | :-----: |
| `validate_param_types` | `boolean` |    no    | `true`  |

When `true`, `dfc` expect the format `name (type): description`.

| Option  | Description                                                   |
| ------- | ------------------------------------------------------------- |
| `true`  | `dfc` will validate that each parameter has a type specified. |
| `false` | `dfc` will not check for parameter types.                     |

<div class="scroll-chunks" markdown>
```toml {.toml linenums="1" title="pyproject.toml" hl_lines="5"}
--8<-- "docs/usage/examples/config_full.toml"
```
</div>


### 5. Optional Style

Standardise how optional parameters be described.

|      Config      |   Type   | Required |   Default    |
| :--------------: | :------: | :------: | :----------: |
| `optional_style` | `string` |    no    | `"validate"` |

This setting control how `dfc` report issues when a parameter have a default value in the function signature.

| Option       | Description                                                                                    |
| ------------ | ---------------------------------------------------------------------------------------------- |
| `"silent"`   | Do not report any missing optional indicator.                                                  |
| `"validate"` | Warn if `, optional` be present but the parameter do not have a default value.                 |
| `"strict"`   | Require all parameters with default value to include the `, optional` suffix in the docstring. |

<div class="scroll-chunks" markdown>
```toml {.toml linenums="1" title="pyproject.toml" hl_lines="6"}
--8<-- "docs/usage/examples/config_full.toml"
```
</div>


## 📂 Section Configuration

Define specific sections within your docstrings using the `[[tool.dfc.sections]]` array. This allow you to validate for summaries, parameters, return values, and more.

There are seven section options you can set.


### 1. Section Name

Specify the name of the section as it appears in your docstrings.

| Config |   Type   | Required |  Default   |
| :----: | :------: | :------: | :--------: |
| `name` | `string` |   yes    | _required_ |

`dfc` look for this exact string (case-insensitive) followed by a colon.

<div class="scroll-chunks" markdown>
```toml {.toml linenums="1" title="pyproject.toml" hl_lines="9 18 26 32 38"}
--8<-- "docs/usage/examples/config_full.toml"
```
</div>


### 2. Section Type

Define the expected format of the section content.

| Config |   Type   | Required |  Default   |
| :----: | :------: | :------: | :--------: |
| `type` | `string` |   yes    | _required_ |

Each type have specific validation rules.

| Option                 | Description                                | Example         |
| ---------------------- | ------------------------------------------ | --------------- |
| `"free_text"`          | Any text content.                          | Summary, Notes  |
| `"list_name"`          | A list of named items.                     | See Also        |
| `"list_type"`          | A list of types.                           | Raises          |
| `"list_name_and_type"` | A list of names with types in parentheses. | Params, Returns |

<div class="scroll-chunks" markdown>
```toml {.toml linenums="1" title="pyproject.toml" hl_lines="10 19 27 33 39"}
--8<-- "docs/usage/examples/config_full.toml"
```
</div>



### 3. Order

Enforce a specific sequence of sections within your docstrings.

| Config  |   Type    | Required | Default |
| :-----: | :-------: | :------: | :-----: |
| `order` | `integer` |    no    | `null`  |

If two sections have an `order` defined, `dfc` ensure they appear in that relative order.
If `order` is not set, the section can appear anywhere in the docstring.
If `order` is set, all sections with an `order` must appear before any sections without an `order`, maintaining the defined sequence, and cannot have any duplicate `order` values.

<div class="scroll-chunks" markdown>
```toml {.toml linenums="1" title="pyproject.toml" hl_lines="11 20 28 34"}
--8<-- "docs/usage/examples/config_full.toml"
```
</div>


### 4. Admonitions

Standardise modern documentation styles like MkDocs-Material admonitions.

|    Config    |         Type          | Required | Default |
| :----------: | :-------------------: | :------: | :-----: |
| `admonition` | `string` or `boolean` |    no    | `false` |

If you provide an `admonition` type (like `"note"` or `"info"`), you must also provide a `prefix` (like `"!!!"` or `"???"`). `dfc` will then expect the section to be formatted as an admonition: `!!! note "Section Name"`.

For more details on supported admonition types, see the [MkDocs-Material documentation](https://squidfunk.github.io/mkdocs-material/reference/admonitions/).

<div class="scroll-chunks" markdown>
```toml {.toml linenums="1" title="pyproject.toml" hl_lines="12 22 40"}
--8<-- "docs/usage/examples/config_full.toml"
```
</div>


### 5. Prefix

Specify the prefix used for admonitions.

|  Config  |   Type   |                 Required                 | Default |
| :------: | :------: | :--------------------------------------: | :-----: |
| `prefix` | `string` | yes if `admonition` is set, otherwise no |  `""`   |

If you set an `admonition` type, you must also provide a `prefix` to indicate how the admonition is formatted.

| Option | Description                                         |
| ------ | --------------------------------------------------- |
| `!!!`  | Standard admonition section.                        |
| `???`  | Expandable admonition section, not expanded.        |
| `???+` | Expandable admonition section, expanded by default. |

For more details on supported prefixes, see the [MkDocs-Material documentation](https://squidfunk.github.io/mkdocs-material/reference/admonitions/).

<div class="scroll-chunks" markdown>
```toml {.toml linenums="1" title="pyproject.toml" hl_lines="14 23 41"}
--8<-- "docs/usage/examples/config_full.toml"
```
</div>


### 6. Required

Mark a section as mandatory for every docstring.

|   Config   |   Type    | Required | Default |
| :--------: | :-------: | :------: | :-----: |
| `required` | `boolean` |    no    | `false` |

<div class="scroll-chunks" markdown>
```toml {.toml linenums="1" title="pyproject.toml" hl_lines="13 21 29 35"}
--8<-- "docs/usage/examples/config_full.toml"
```
</div>


### 7. Custom Error Message

Provide a more helpful error message when a section validator fail or a required section be missing.

|  Config   |   Type   | Required | Default |
| :-------: | :------: | :------: | :-----: |
| `message` | `string` |    no    |  `""`   |

<div class="scroll-chunks" markdown>
```toml {.toml linenums="1" title="pyproject.toml" hl_lines="15"}
--8<-- "docs/usage/examples/config_full.toml"
```
</div>


## 🛠️ How To: Customise Your Config

Walk through a practical example to see how these options work together.


### Create a sample module

Create `sample_config.py` to test different configurations:

```python {.py .python linenums="1" title="sample_config.py"}
--8<-- "docs/usage/examples/sample_config.py"
```


### Use Global Flags

Apply global settings to control the tool's overall behaviour. Create `pyproject.toml`:

```toml {.toml linenums="1" title="pyproject.toml"}
--8<-- "docs/usage/examples/config_global.toml"
```

Run `dfc` with this configuration:

```sh {.sh .bash linenums="1" title="Terminal"}
dfc --config=pyproject.toml sample_config.py
```

<div class="result" markdown>

```text
docs/usage/sample_config.py
  Line 1 - function 'my_function':
    - Parameter 'param2' has default value but missing ', optional' suffix in docstring
  Line 15 - function '_private_function':
    - Missing required section: 'summary'
  Line 21 - function 'undocumented_function':
    - Missing docstring for function

Found 3 error(s) in 3 functions over 1 file
```

Notice how `dfc` now check private functions and enforce strict optional parameter naming.

</div>


### Design Custom Sections

Define your own documentation structure. Create `pyproject.toml`:

```toml {.toml linenums="1" title="pyproject.toml"}
--8<-- "docs/usage/examples/config_sections.toml"
```

Run the check again:

```sh {.sh .bash linenums="1" title="Terminal"}
dfc --config=pyproject.toml sample_config.py
```

<div class="result" markdown>

```text
docs/usage/sample_config.py
  Line 21 - function 'undocumented_function':
    - Missing docstring for function

Found 1 error(s) in 1 function over 1 file
```

In this case, `my_function()` and `_private_function()` pass because they meet the basic requirements of the new section config, while `undocumented_function()` still fail because docstrings be required globally.

</div>


## 💡 Watch-outs and Pro-tips

### **Watch-out**: Duplicate Orders

Never assign the same `order` value to two different sections. If you do, `dfc` will raise an `InvalidConfigError_DuplicateOrderValues` and stop execution.


### **Pro-tip**: Floating Sections

Omit the `order` attribute for sections that might appear anywhere, such as "Notes" or "Examples". These be referred to as "floating" sections. They provide flexibility while still ensuring the content follow your mandated `type`.


### **Pro-tip**: Disable Built-ins

If you provide a `sections` list in your `pyproject.toml`, `dfc` completely replace the default configuration. This allow you to fully customise what sections be checked without any unexpected behavior from built-in defaults.


## 🔍 Configuration Discovery

`dfc` automatically look for configuration in the following order:

1.  A path provided via the `--config` or `-f` command-line argument.
2.  A `pyproject.toml` file in the current working directory containing a `[tool.dfc]` or `[tool.docstring-format-checker]` section.
3.  The default built-in configuration if no file be found.
