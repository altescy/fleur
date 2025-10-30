"""Pytest configuration and shared fixtures for fleur tests."""

import pytest

from fleur.dsl.ir import (
    IRBinaryOperator,
    IRBinaryOpExpr,
    IRBlock,
    IRIdentifierExpr,
    IRLiteralBooleanExpr,
    IRLiteralNumberExpr,
    IRLiteralStringExpr,
)
from fleur.dsl.runtime import use_block


@pytest.fixture
def clean_block():
    """Provide a clean IR block for testing."""
    with use_block() as block:
        yield block


@pytest.fixture
def sample_number_expr():
    """Provide a sample number expression."""
    return IRLiteralNumberExpr(42)


@pytest.fixture
def sample_boolean_expr():
    """Provide a sample boolean expression."""
    return IRLiteralBooleanExpr(True)


@pytest.fixture
def sample_string_expr():
    """Provide a sample string expression."""
    return IRLiteralStringExpr("hello")


@pytest.fixture
def sample_identifier_expr():
    """Provide a sample identifier expression."""
    return IRIdentifierExpr("x")


@pytest.fixture
def sample_binary_op_expr():
    """Provide a sample binary operation expression."""
    left = IRLiteralNumberExpr(10)
    right = IRLiteralNumberExpr(20)
    return IRBinaryOpExpr(operator=IRBinaryOperator.ADD, left=left, right=right)


@pytest.fixture
def empty_block():
    """Provide an empty IR block."""
    return IRBlock(body=[])
