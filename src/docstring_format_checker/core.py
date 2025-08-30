# ============================================================================ #
#                                                                              #
#     Title: Title                                                             #
#     Purpose: Purpose                                                         #
#     Notes: Notes                                                             #
#     Author: chrimaho                                                         #
#     Created: Created                                                         #
#     References: References                                                   #
#     Sources: Sources                                                         #
#     Edited: Edited                                                           #
#                                                                              #
# ============================================================================ #


# ---------------------------------------------------------------------------- #
#                                                                              #
#     Overview                                                              ####
#                                                                              #
# ---------------------------------------------------------------------------- #


# ---------------------------------------------------------------------------- #
#  Description                                                              ####
# ---------------------------------------------------------------------------- #


"""
!!! note "Summary"
    Core docstring checking functionality.
"""


# ---------------------------------------------------------------------------- #
#                                                                              #
#     Setup                                                                 ####
#                                                                              #
# ---------------------------------------------------------------------------- #


## --------------------------------------------------------------------------- #
##  Imports                                                                 ####
## --------------------------------------------------------------------------- #


# ## Python StdLib Imports ----
import ast
import fnmatch
import re
from pathlib import Path
from typing import Literal, NamedTuple, Optional, Union

# ## Local First Party Imports ----
from docstring_format_checker.config import SectionConfig
from docstring_format_checker.utils.exceptions import (
    DirectoryNotFoundError,
    DocstringError,
    InvalidFileError,
)


## --------------------------------------------------------------------------- #
##  Exports                                                                 ####
## --------------------------------------------------------------------------- #


__all__: list[str] = [
    "DocstringChecker",
    "FunctionAndClassDetails",
    "SectionConfig",
    "DocstringError",
]


# ---------------------------------------------------------------------------- #
#                                                                              #
#     Main Section                                                          ####
#                                                                              #
# ---------------------------------------------------------------------------- #


class FunctionAndClassDetails(NamedTuple):
    """
    Details about a function or class found in the AST.
    """

    item_type: Literal["function", "class", "method"]
    name: str
    node: Union[ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef]
    lineno: int
    parent_class: Optional[str] = None


class DocstringChecker:
    """
    Main class for checking docstring format and completeness.
    """

    def __init__(self, sections_config: list[SectionConfig]) -> None:
        """
        Initialize the docstring checker.

        Args:
            sections_config:
                List of section configurations to check against.
        """
        self.sections_config: list[SectionConfig] = sections_config
        self.required_sections: list[SectionConfig] = [s for s in sections_config if s.required]
        self.optional_sections: list[SectionConfig] = [s for s in sections_config if not s.required]

    def check_file(self, file_path: Union[str, Path]) -> list[DocstringError]:
        """
        Check docstrings in a Python file.

        Args:
            file_path:
                Path to the Python file to check.

        Returns:
            List of DocstringError objects for any validation failures.

        Raises:
            (FileNotFoundError):
                If the file doesn't exist.
            (InvalidFileError):
                If the file is not a Python file.
            (UnicodeError):
                If the file can't be decoded.
            (SyntaxError):
                If the file contains invalid Python syntax.
        """

        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if file_path.suffix != ".py":
            raise InvalidFileError(f"File must be a Python file (.py): {file_path}")

        # Read and parse the file
        try:
            with open(file_path, encoding="utf-8") as f:
                content: str = f.read()
        except UnicodeDecodeError as e:
            raise UnicodeError(f"Cannot decode file {file_path}: {e}") from e

        try:
            tree: ast.Module = ast.parse(content)
        except SyntaxError as e:
            raise SyntaxError(f"Invalid Python syntax in {file_path}: {e}") from e

        # Extract all functions and classes
        items: list[FunctionAndClassDetails] = self._extract_items(tree)

        # Check each item
        errors: list[DocstringError] = []
        for item in items:
            try:
                self._check_single_docstring(item, str(file_path))
            except DocstringError as e:
                errors.append(e)

        return errors

    def check_directory(
        self,
        directory_path: Union[str, Path],
        recursive: bool = True,
        exclude_patterns: Optional[list[str]] = None,
    ) -> dict[str, list[DocstringError]]:
        """
        Check docstrings in all Python files in a directory.

        Args:
            directory_path:
                Path to the directory to check.
            recursive:
                Whether to check subdirectories recursively.
            exclude_patterns:
                List of glob patterns to exclude.

        Raises:
            (FileNotFoundError):
                If the directory doesn't exist.
            (DirectoryNotFoundError):
                If the path is not a directory.

        Returns:
            Dictionary mapping file paths to lists of DocstringError objects.
        """

        directory_path = Path(directory_path)
        if not directory_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")

        if not directory_path.is_dir():
            raise DirectoryNotFoundError(f"Path is not a directory: {directory_path}")

        # Find all Python files
        if recursive:
            pattern = "**/*.py"
        else:
            pattern = "*.py"

        python_files: list[Path] = list(directory_path.glob(pattern))

        # Filter out excluded patterns
        if exclude_patterns:
            filtered_files: list[Path] = []
            for file_path in python_files:
                relative_path: Path = file_path.relative_to(directory_path)
                should_exclude = False
                for pattern in exclude_patterns:
                    if fnmatch.fnmatch(str(relative_path), pattern):
                        should_exclude = True
                        break
                if not should_exclude:
                    filtered_files.append(file_path)
            python_files = filtered_files

        # Check each file
        results: dict[str, list[DocstringError]] = {}
        for file_path in python_files:
            try:
                errors: list[DocstringError] = self.check_file(file_path)
                if errors:  # Only include files with errors
                    results[str(file_path)] = errors
            except (FileNotFoundError, ValueError, SyntaxError) as e:
                # Create a special error for file-level issues
                error = DocstringError(
                    message=str(e),
                    file_path=str(file_path),
                    line_number=0,
                    item_name="",
                    item_type="file",
                )
                results[str(file_path)] = [error]

        return results

    def _extract_items(self, tree: ast.AST) -> list[FunctionAndClassDetails]:
        """
        Extract all functions and classes from the AST.
        """

        items: list[FunctionAndClassDetails] = []

        class ItemVisitor(ast.NodeVisitor):

            def __init__(self) -> None:
                self.class_stack: list[str] = []

            def visit_ClassDef(self, node: ast.ClassDef) -> None:
                if not node.name.startswith("_"):  # Skip private classes
                    items.append(
                        FunctionAndClassDetails(
                            item_type="class",
                            name=node.name,
                            node=node,
                            lineno=node.lineno,
                            parent_class=None,
                        )
                    )

                # Visit methods in this class
                self.class_stack.append(node.name)
                self.generic_visit(node)
                self.class_stack.pop()

            def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
                self._visit_function(node)

            def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
                self._visit_function(node)

            def _visit_function(self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef]) -> None:
                """Visit function definition node (sync or async)."""
                if not node.name.startswith("_"):  # Skip private functions
                    item_type: Literal["function", "method"] = "method" if self.class_stack else "function"
                    parent_class: str | None = self.class_stack[-1] if self.class_stack else None

                    items.append(
                        FunctionAndClassDetails(
                            item_type=item_type,
                            name=node.name,
                            node=node,
                            lineno=node.lineno,
                            parent_class=parent_class,
                        )
                    )

                self.generic_visit(node)

        visitor = ItemVisitor()
        visitor.visit(tree)

        return items

    def _check_single_docstring(self, item: FunctionAndClassDetails, file_path: str) -> None:
        """
        Check a single function or class docstring.
        """

        docstring: str | None = ast.get_docstring(item.node)

        # Check if any required sections apply to this item type
        requires_docstring = False
        applicable_sections: list[SectionConfig] = []

        for section in self.sections_config:
            if section.required:
                # Check if this section applies to this item type
                if section.type == "free_text":
                    # Free text sections apply only to functions and methods, not classes
                    if isinstance(item.node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        requires_docstring = True
                        applicable_sections.append(section)
                elif section.type == "list_name_and_type":
                    if section.name.lower() == "params" and isinstance(
                        item.node, (ast.FunctionDef, ast.AsyncFunctionDef)
                    ):
                        # Params only apply to functions/methods
                        requires_docstring = True
                        applicable_sections.append(section)
                    elif section.name.lower() in ["returns", "return"] and isinstance(
                        item.node, (ast.FunctionDef, ast.AsyncFunctionDef)
                    ):
                        # Returns only apply to functions/methods
                        requires_docstring = True
                        applicable_sections.append(section)
                elif section.type in ["list_type", "list_name"]:
                    # These sections apply to functions/methods that might have them
                    if isinstance(item.node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        requires_docstring = True
                        applicable_sections.append(section)

        if not docstring:
            if requires_docstring:
                message: str = f"Missing docstring for {item.item_type}"
                raise DocstringError(
                    message=message,
                    file_path=file_path,
                    line_number=item.lineno,
                    item_name=item.name,
                    item_type=item.item_type,
                )
            return  # No docstring required

        # Validate docstring sections if docstring exists
        self._validate_docstring_sections(docstring, item, file_path)

    def _validate_docstring_sections(self, docstring: str, item: FunctionAndClassDetails, file_path: str) -> None:
        """
        Validate the sections within a docstring.
        """
        errors: list[str] = []

        # Check each required section
        for section in self.required_sections:
            if section.type == "free_text":
                if not self._check_free_text_section(docstring, section):
                    errors.append(f"Missing required section: {section.name}")

            elif section.type == "list_name_and_type":
                if section.name.lower() == "params" and isinstance(item.node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if not self._check_params_section(docstring, item.node):
                        errors.append("Missing or invalid Params section")
                elif section.name.lower() in ["returns", "return"]:
                    if not self._check_returns_section(docstring):
                        errors.append("Missing or invalid Returns section")

            elif section.type == "list_type":
                if section.name.lower() in ["raises", "raise"]:
                    if not self._check_raises_section(docstring):
                        errors.append("Missing or invalid Raises section")
                elif section.name.lower() in ["yields", "yield"]:
                    if not self._check_yields_section(docstring):
                        errors.append("Missing or invalid Yields section")

            elif section.type == "list_name":
                # Simple name sections - check if they exist
                if not self._check_simple_section(docstring, section.name):
                    errors.append(f"Missing required section: {section.name}")

        # Check section order
        order_errors: list[str] = self._check_section_order(docstring)
        errors.extend(order_errors)

        # Check for mutual exclusivity (returns vs yields)
        if self._has_both_returns_and_yields(docstring):
            errors.append("Docstring cannot have both Returns and Yields sections")

        if errors:
            combined_message: str = "; ".join(errors)
            raise DocstringError(
                message=combined_message,
                file_path=file_path,
                line_number=item.lineno,
                item_name=item.name,
                item_type=item.item_type,
            )

    def _check_free_text_section(self, docstring: str, section: SectionConfig) -> bool:
        """
        Check if a free text section exists in the docstring.
        """
        if section.admonition and section.prefix:
            # Format like: !!! note "Summary"
            pattern = rf'{re.escape(section.prefix)}\s+{re.escape(section.admonition)}\s+".*{re.escape(section.name)}"'
            return bool(re.search(pattern, docstring, re.IGNORECASE))
        elif section.name.lower() in ["summary"]:
            # For summary, accept either formal format or simple docstring
            formal_pattern = r'!!! note "Summary"'
            if re.search(formal_pattern, docstring, re.IGNORECASE):
                return True
            # Accept any non-empty docstring as summary
            return len(docstring.strip()) > 0
        elif section.name.lower() in ["examples", "example"]:
            # Look for examples section
            return bool(re.search(r'\?\?\?\+ example "Examples"', docstring, re.IGNORECASE))

        return True  # Default to true for unknown free text sections

    def _check_params_section(self, docstring: str, node: Union[ast.FunctionDef, ast.AsyncFunctionDef]) -> bool:
        """
        Check if the Params section exists and documents all parameters.
        """
        # Get function parameters (excluding 'self' for methods)
        params: list[str] = [arg.arg for arg in node.args.args if arg.arg != "self"]

        if not params:
            return True  # No parameters to document

        # Check if Params section exists
        if not re.search(r"Params:", docstring):
            return False

        # Check each parameter is documented
        for param in params:
            param_pattern: str = rf"{re.escape(param)}\s*\([^)]+\):"
            if not re.search(param_pattern, docstring):
                return False

        return True

    def _check_returns_section(self, docstring: str) -> bool:
        """
        Check if the Returns section exists.
        """
        return bool(re.search(r"Returns:", docstring))

    def _check_raises_section(self, docstring: str) -> bool:
        """
        Check if the Raises section exists.
        """
        return bool(re.search(r"Raises:", docstring))

    def _has_both_returns_and_yields(self, docstring: str) -> bool:
        """
        Check if docstring has both Returns and Yields sections.
        """
        has_returns = bool(re.search(r"Returns:", docstring))
        has_yields = bool(re.search(r"Yields:", docstring))
        return has_returns and has_yields

    def _check_section_order(self, docstring: str) -> list[str]:
        """
        Check that sections appear in the correct order.
        """
        # Build expected order from configuration
        section_patterns: list[tuple[str, str]] = []
        for section in sorted(self.sections_config, key=lambda x: x.order):
            if section.type == "free_text" and section.admonition and section.prefix:
                pattern: str = (
                    rf'{re.escape(section.prefix)}\s+{re.escape(section.admonition)}\s+".*{re.escape(section.name)}"'
                )
                section_patterns.append((pattern, section.name))
            elif section.name.lower() == "params":
                section_patterns.append((r"Params:", "Params"))
            elif section.name.lower() in ["returns", "return"]:
                section_patterns.append((r"Returns:", "Returns"))
            elif section.name.lower() in ["yields", "yield"]:
                section_patterns.append((r"Yields:", "Yields"))
            elif section.name.lower() in ["raises", "raise"]:
                section_patterns.append((r"Raises:", "Raises"))

        # Add some default patterns for common sections
        default_patterns: list[tuple[str, str]] = [
            (r'!!! note "Summary"', "Summary"),
            (r'!!! details "Details"', "Details"),
            (r'\?\?\?\+ example "Examples"', "Examples"),
            (r'\?\?\?\+ success "Credit"', "Credit"),
            (r'\?\?\?\+ calculation "Equation"', "Equation"),
            (r'\?\?\?\+ info "Notes"', "Notes"),
            (r'\?\?\? question "References"', "References"),
            (r'\?\?\? tip "See Also"', "See Also"),
        ]

        all_patterns: list[tuple[str, str]] = section_patterns + default_patterns

        found_sections: list[tuple[int, str]] = []
        for pattern, section_name in all_patterns:
            match: re.Match[str] | None = re.search(pattern, docstring, re.IGNORECASE)
            if match:
                found_sections.append((match.start(), section_name))

        # Sort by position in docstring
        found_sections.sort(key=lambda x: x[0])

        # Build expected order
        expected_order: list[str] = [s.name.title() for s in sorted(self.sections_config, key=lambda x: x.order)]
        expected_order.extend(
            [
                "Summary",
                "Details",
                "Examples",
                "Credit",
                "Equation",
                "Notes",
                "References",
                "See Also",
            ]
        )

        # Check order matches expected order
        errors: list[str] = []
        last_expected_index = -1
        for _, section_name in found_sections:
            try:
                current_index: int = expected_order.index(section_name)
                if current_index < last_expected_index:
                    errors.append(f"Section '{section_name}' appears out of order")
                last_expected_index: int = current_index
            except ValueError:
                # Section not in expected order list - might be OK
                pass

        return errors

    def _check_yields_section(self, docstring: str) -> bool:
        """
        Check if the Yields section exists.
        """
        return bool(re.search(r"Yields:", docstring))

    def _check_simple_section(self, docstring: str, section_name: str) -> bool:
        """
        Check if a simple named section exists.
        """
        pattern = rf"{re.escape(section_name)}:"
        return bool(re.search(pattern, docstring, re.IGNORECASE))
