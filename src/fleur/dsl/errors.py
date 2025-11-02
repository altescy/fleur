"""
Custom error types for Graine DSL.

This module defines specific exception types for different error scenarios
in Graine code generation, providing clearer error messages and better
debugging experience.
"""

from typing import Any


class GraineError(Exception):
    """Base exception for all Graine-related errors."""

    pass


class GraineTypeError(GraineError, TypeError):
    """
    Raised when a type conversion or type operation fails.

    This typically occurs when trying to convert an unsupported Python type
    to a Graine type, or when performing invalid type operations.
    """

    pass


class GraineValueError(GraineError, ValueError):
    """
    Raised when a value is invalid or out of range.

    This occurs when values don't meet the expected constraints for
    Graine operations.
    """

    pass


class GraineBlockError(GraineError, LookupError):
    """
    Raised when block context operations fail.

    This typically occurs when trying to emit statements outside of a
    proper block context.
    """

    pass


class GraineASTError(GraineError):
    """
    Raised when AST construction or manipulation fails.

    This occurs when the AST is malformed or contains invalid structures.
    """

    pass


def format_type_error(value: Any, supported_types: str) -> str:
    """
    Format a helpful error message for type conversion failures.

    Args:
        value: The value that failed conversion
        supported_types: String describing supported types

    Returns:
        A formatted error message
    """
    return (
        f"Cannot convert Python type '{type(value).__name__}' to Graine type. "
        f"Supported types: {supported_types}\n"
        f"Got value: {repr(value)}"
    )


def format_unsupported_ast_error(node_type: type) -> str:
    """
    Format an error message for unsupported AST nodes.

    Args:
        node_type: The type of the unsupported node

    Returns:
        A formatted error message
    """
    return (
        f"Unsupported AST node type: {node_type.__name__}\n"
        f"This may indicate an internal error or an unimplemented feature."
    )
