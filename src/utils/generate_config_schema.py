# ============================================================================ #
#                                                                              #
#     Title: Generate Configuration Schema                                     #
#     Purpose: Generate JSON Schema for tool.dfc in pyproject.toml             #
#                                                                              #
# ============================================================================ #


# ---------------------------------------------------------------------------- #
#                                                                              #
#     Setup                                                                 ####
#                                                                              #
# ---------------------------------------------------------------------------- #


## --------------------------------------------------------------------------- #
##  Imports                                                                 ####
## --------------------------------------------------------------------------- #


# ## Python StdLib Imports ----
import json
import os
import sys
from dataclasses import MISSING, fields
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal, Self, Union, get_args, get_origin

# ## Python Third Party Imports ----
import black

# ## Local First Party Imports ----
from docstring_format_checker.config import GlobalConfig, SectionConfig


if sys.version_info >= (3, 11):
    # ## Python StdLib Imports ----
    import tomllib
else:
    # ## Python Third Party Imports ----
    import tomli as tomllib


## --------------------------------------------------------------------------- #
##  Constants                                                               ####
## --------------------------------------------------------------------------- #


PYPROJECT_TOML_LOCATION: Path = Path(__file__).parent.parent.parent.joinpath("pyproject.toml")
SCHEMA_OUTPUT_LOCATION: Path = Path(__file__).parent.parent.joinpath("schemas").joinpath("json")
VERBOSE: bool = bool(os.environ.get("VERBOSE") or False)
TYPE_MAP: dict[str, str] = {
    "str": "string",
    "int": "integer",
    "bool": "boolean",
    "float": "number",
}


# ---------------------------------------------------------------------------- #
#                                                                              #
#     Classes                                                               ####
#                                                                              #
# ---------------------------------------------------------------------------- #


## --------------------------------------------------------------------------- #
##  Mixin                                                                   ####
## --------------------------------------------------------------------------- #


class SchemaGeneratorMixin:

    schema: dict[str, Any] = {}

    @property
    @lru_cache
    def package_info(self) -> dict[str, Any]:
        with open(file=PYPROJECT_TOML_LOCATION, mode="rb") as f:
            pyproject_data: dict[str, Any] = tomllib.load(f)
        return pyproject_data["project"]

    def write_schema_to_file(self, output_name: str, output_path: Path = SCHEMA_OUTPUT_LOCATION) -> None:
        output_path.mkdir(parents=True, exist_ok=True)
        with open(output_path.joinpath(output_name), "w", encoding="utf-8") as f:
            json.dump(self.schema, f, indent=4)
            f.write("\n")
        print(f"✅ Successfully generated docstring-format-checker schema at: {output_path.joinpath(output_name)}")


## --------------------------------------------------------------------------- #
##  DFC Schema                                                              ####
## --------------------------------------------------------------------------- #


class DFCSchemaGenerator(SchemaGeneratorMixin):

    def generate_schema_headers(self) -> Self:
        self.schema: dict[str, Any] = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "$id": "https://json.schemastore.org/partial-dfc.json",
            "$comment": "This is a partial schema for the `docstring-format-checker` package pyproject.toml, under the header [tool.dfc] or [tool.docstring-format-checker].",
            "type": "object",
            "additionalProperties": False,
        }

        # Return self for chaining
        return self

    def generate_schema_global_properties(self) -> Self:

        # Extract GlobalConfig fields
        global_fields = fields(GlobalConfig)

        # Initialize properties dictionary
        self.schema["properties"] = {}

        # Loop through each field
        for field in global_fields:

            # Initialize property.NAME dictionary
            self.schema["properties"][field.name] = {}

            # Add title if available
            if field.metadata.get("title") is not None:
                self.schema["properties"][field.name]["title"] = field.metadata["title"]

            # Add description if available
            if field.metadata.get("description") is not None:
                self.schema["properties"][field.name]["description"] = field.metadata["description"]

            # Add type, handling Literal types separately
            if get_origin(field.type) is Literal:
                self.schema["properties"][field.name]["type"] = "string"
                self.schema["properties"][field.name]["enum"] = list(get_args(field.type))
            else:
                typ: str = getattr(field.type, "__name__", str(field.type))
                self.schema["properties"][field.name]["type"] = TYPE_MAP.get(typ, typ)

            # Add default if available
            if field.default is not None:
                self.schema["properties"][field.name]["default"] = field.default

        # Return self for chaining
        return self

    def generate_schema_section_properties(self) -> Self:

        # Extract SectionConfig fields
        section_fields = fields(SectionConfig)

        # Initialize sections property
        self.schema["properties"]["sections"] = {
            "type": "array",
            "title": "Docstring Sections",
            "description": "List of docstring section configurations.",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [],
                "properties": {},
            },
        }

        # Loop through each field
        for field in section_fields:

            # Add to required if field has no default
            if field.default is MISSING:
                self.schema["properties"]["sections"]["items"]["required"].append(field.name)

            # Initialize property.NAME dictionary
            self.schema["properties"]["sections"]["items"]["properties"][field.name] = {}

            # Add title if available
            if field.metadata.get("title") is not None:
                self.schema["properties"]["sections"]["items"]["properties"][field.name]["title"] = field.metadata[
                    "title"
                ]

            # Add description if available
            if field.metadata.get("description") is not None:
                self.schema["properties"]["sections"]["items"]["properties"][field.name]["description"] = (
                    field.metadata["description"]
                )

            # Add type, handling different types separately
            if get_origin(field.type) is Literal:

                # Literal types are treated as strings, with enum values
                self.schema["properties"]["sections"]["items"]["properties"][field.name]["type"] = "string"
                self.schema["properties"]["sections"]["items"]["properties"][field.name]["enum"] = list(
                    get_args(field.type)
                )

            elif (
                get_origin(field.type) is Union
                and len(get_args(field.type)) == 2
                and get_args(field.type)[1] is type(None)
            ):

                # Optional types are stored as a Union, with the second argument as NoneType
                self.schema["properties"]["sections"]["items"]["properties"][field.name]["type"] = [
                    TYPE_MAP.get(get_args(field.type)[0].__name__, get_args(field.type)[0].__name__),
                    "null",
                ]

            elif get_origin(field.type) is Union:

                # Union types with multiple arguments are treated as an array of possible types
                self.schema["properties"]["sections"]["items"]["properties"][field.name]["type"] = []
                for arg in get_args(field.type):
                    self.schema["properties"]["sections"]["items"]["properties"][field.name]["type"].append(
                        TYPE_MAP.get(arg.__name__, arg.__name__)
                    )

            else:

                # Everything else is treated normally
                self.schema["properties"]["sections"]["items"]["properties"][field.name]["type"] = TYPE_MAP.get(
                    field.type.__name__, field.type.__name__
                )

            # Add default if available
            if field.default is not MISSING:
                self.schema["properties"]["sections"]["items"]["properties"][field.name]["default"] = field.default

        # Return self for chaining
        return self

    def generate_schema(self) -> Self:
        self.generate_schema_headers().generate_schema_global_properties().generate_schema_section_properties()

        # Return self for chaining
        return self


## --------------------------------------------------------------------------- #
##  Pyproject Schema                                                        ####
## --------------------------------------------------------------------------- #


class PyprojectSchemaGenerator(SchemaGeneratorMixin):

    def generate_schema(self) -> Self:
        self.schema = {
            "properties": {
                "tool": {
                    "properties": {
                        "dfc": {
                            "$ref": "https://json.schemastore.org/partial-dfc.json",
                            "title": self.package_info["name"],
                            "description": self.package_info["description"],
                        },
                        "docstring-format-checker": {
                            "$ref": "https://json.schemastore.org/partial-dfc.json",
                            "title": self.package_info["name"],
                            "description": self.package_info["description"],
                        },
                    },
                }
            }
        }

        # Return self for chaining
        return self


# ---------------------------------------------------------------------------- #
#                                                                              #
#     Executor                                                              ####
#                                                                              #
# ---------------------------------------------------------------------------- #


if __name__ == "__main__":

    if VERBOSE:
        print(black.format_str(repr(DFCSchemaGenerator().generate_schema().schema), mode=black.FileMode()))
        print(black.format_str(repr(PyprojectSchemaGenerator().generate_schema().schema), mode=black.FileMode()))

    DFCSchemaGenerator().generate_schema().write_schema_to_file("partial-dfc.json")
    PyprojectSchemaGenerator().generate_schema().write_schema_to_file("pyproject.json")
