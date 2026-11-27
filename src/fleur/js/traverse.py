"""Generic traversal over ESTree nodes."""

import dataclasses
from collections.abc import Iterator

from .ast import (
    ESTreeCatchClause,
    ESTreeFunction,
    ESTreeGeneratedIdentifier,
    ESTreeIdentifier,
    ESTreeMemberExpression,
    ESTreeNode,
    ESTreeObjectProperty,
    ESTreeVariableDeclarator,
)


def _children(value: object) -> Iterator[ESTreeNode]:
    if isinstance(value, ESTreeNode):
        yield value
    elif isinstance(value, list | tuple):
        for item in value:  # pyright: ignore[reportUnknownVariableType]
            yield from _children(item)  # pyright: ignore[reportUnknownArgumentType]


def iter_nodes(node: ESTreeNode) -> Iterator[ESTreeNode]:
    """Yield the node and all of its descendants in depth-first order."""
    yield node
    for field in dataclasses.fields(node):
        for child in _children(getattr(node, field.name)):
            yield from iter_nodes(child)


def identifiers(node: ESTreeNode) -> Iterator[ESTreeIdentifier]:
    """Yield every identifier referenced or bound within the node, excluding static property names."""
    if isinstance(node, ESTreeIdentifier):
        yield node
        return
    for field in dataclasses.fields(node):
        if _is_static_name(node, field.name):
            continue
        for child in _children(getattr(node, field.name)):
            yield from identifiers(child)


def _is_static_name(node: ESTreeNode, field: str) -> bool:
    """Whether the field holds a property name rather than a variable reference."""
    if isinstance(node, ESTreeMemberExpression):
        return field == "property" and not node.computed
    if isinstance(node, ESTreeObjectProperty):
        return field == "key"
    return False


def generated_identifiers(node: ESTreeNode) -> Iterator[ESTreeGeneratedIdentifier]:
    """Yield every generated identifier referenced or bound within the node."""
    for child in iter_nodes(node):
        if isinstance(child, ESTreeGeneratedIdentifier):
            yield child


def bound_generated_identifiers(node: ESTreeNode) -> Iterator[ESTreeGeneratedIdentifier]:
    """Yield generated identifiers declared as parameters or variables within the node."""
    for child in iter_nodes(node):
        if isinstance(child, ESTreeFunction):
            patterns = list(child.params)
        elif isinstance(child, ESTreeVariableDeclarator):
            patterns = [child.id]
        elif isinstance(child, ESTreeCatchClause) and child.param is not None:
            patterns = [child.param]
        else:
            continue
        for pattern in patterns:
            yield from generated_identifiers(pattern)
