# JSON Schema for pyproject.toml


## 🌐 Overview

The validation of `pyproject.toml` files in modern IDEs relies on a sophisticated ecosystem of standards and community-driven repositories. Utilise JSON Schema to ensure that configuration errors are caught during authoring rather than at runtime.

When you open a `pyproject.toml` file in VS Code with the `Even Better TOML` extension, several processes occur:

1. **Schema Association**: Check if there is a mapping between the filename and a known schema. For common files like `pyproject.toml`, this mapping is often retrieved from a central registry.
2. **SchemaStore.org**: Fetch schemas from this source automatically via extensions. This is the primary open-source repository where most schemas for configuration files live.
3. **JSON Schema Standard**: Convert the TOML data into a JSON-compatible structure and validate it against the rules defined in the schema.


## 🛠️ Schema Generation

To support `[tool.dfc]` in the `pyproject.toml` file, a JSON Schema fragment is required that describes the configuration structure. This project uses a tailored script to automate this process.


### ⚙️ Automated Generation

Utilise the [src/utils/generate_config_schema.py](src/utils/generate_config_schema.py) script to generate and update the schema files. This script uses introspection on the `GlobalConfig()` and `SectionConfig()` classes to ensure the schema always reflects the actual code structure.

Run the following command to regenerate the schemas:

```bash
source .venv/bin/activate
uv run ./src/utils/generate_config_schema.py
```


### 🚀 Continuous Integration

This generation process is integrated into the project's CI workflow, as defined in [.github/workflows/ci.yml](.github/workflows/ci.yml). During a pull request, the CI environment executes the generator and validates that no drift has occurred between the code and the schema files:

- Execute `uv run ./src/utils/generate_config_schema.py` to generate the latest schemas.
- Run `git diff --exit-code src/schemas/json/` to ensure that any changes to the configuration classes have been correctly captured and committed in the schema.


## 📜 Generated Schema Files

Two primary schema files are generated in this directory:

- [src/schemas/json/partial-dfc.json](src/schemas/json/partial-dfc.json): Contains the core schema definitions for the `dfc` tool configuration. This is the file intended for submission to SchemaStore.org.
- [src/schemas/json/pyproject.json](src/schemas/json/pyproject.json): A wrapper schema used for local testing and validation of the entire `pyproject.toml` structure.


### 💻 Local Validation in VS Code

Before a schema is merged into the global SchemaStore registry, you can test validation locally in your workspace. Add the following to your `settings.json` to associate the local schema with your `pyproject.toml`:

```json
{
  "toml.shared.schema": {
    "pyproject.toml": "./src/schemas/json/partial-dfc.json"
  }
}
```
