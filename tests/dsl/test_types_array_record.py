"""Tests for Array and Record types."""

import pytest

from fleur.dsl.ir import (
    IRIdentifierExpr,
    IRIndexAccessExpr,
    IRLiteralArrayExpr,
    IRLiteralNumberExpr,
    IRLiteralRecordExpr,
    IRLiteralStringExpr,
    IRPropertyAccessExpr,
)
from fleur.dsl.types import Array, GraineType, Number, Record


class TestArray:
    """Test Array type operations."""

    def test_array_creation(self):
        """Test creating an Array instance."""
        elements = [IRLiteralNumberExpr(1), IRLiteralNumberExpr(2)]
        expr = IRLiteralArrayExpr(elements)
        arr = Array(expr)
        assert arr._expr == expr

    def test_array_index_access_with_int(self):
        """Test accessing array element by integer index."""
        arr = Array(IRLiteralArrayExpr([IRLiteralNumberExpr(10), IRLiteralNumberExpr(20)]))
        result = arr[0]

        assert isinstance(result, GraineType)
        assert isinstance(result._expr, IRIndexAccessExpr)
        assert result._expr.target == arr._expr
        assert isinstance(result._expr.index, IRLiteralNumberExpr)
        assert result._expr.index.value == 0

    def test_array_index_access_with_number(self):
        """Test accessing array element by Number index."""
        arr = Array(IRLiteralArrayExpr([IRLiteralNumberExpr(10), IRLiteralNumberExpr(20)]))
        idx = Number(IRIdentifierExpr("i"))
        result = arr[idx]

        assert isinstance(result, GraineType)
        assert isinstance(result._expr, IRIndexAccessExpr)
        assert result._expr.target == arr._expr
        assert result._expr.index == idx._expr


class TestRecord:
    """Test Record type operations."""

    def test_record_creation(self):
        """Test creating a Record instance."""
        fields = {"x": IRLiteralNumberExpr(10), "y": IRLiteralNumberExpr(20)}
        expr = IRLiteralRecordExpr(fields)
        rec = Record(expr)
        assert rec._expr == expr

    def test_record_property_access(self):
        """Test accessing record property."""
        rec = Record(IRLiteralRecordExpr({"name": IRLiteralStringExpr("Alice"), "age": IRLiteralNumberExpr(30)}))
        result = rec.name

        assert isinstance(result, GraineType)
        assert isinstance(result._expr, IRPropertyAccessExpr)
        assert result._expr.target == rec._expr
        assert result._expr.property == "name"

    def test_record_property_access_raises_for_private(self):
        """Test that accessing private attributes raises AttributeError."""
        rec = Record(IRLiteralRecordExpr({"x": IRLiteralNumberExpr(10)}))

        with pytest.raises(AttributeError):
            _ = rec._nonexistent  # Should raise for any private attribute that doesn't exist
