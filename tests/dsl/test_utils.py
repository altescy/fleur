"""Tests for utility functions."""

import pytest

from fleur.dsl._utils import as_literal, extract_first_grainetype
from fleur.dsl.types import Boolean, Number, String


class TestAsLiteral:
    """Test as_literal function."""

    def test_as_literal_true(self):
        """Test converting True to Boolean."""
        result = as_literal(True)
        assert isinstance(result, Boolean)

    def test_as_literal_false(self):
        """Test converting False to Boolean."""
        result = as_literal(False)
        assert isinstance(result, Boolean)

    def test_as_literal_int(self):
        """Test converting int to Number."""
        result = as_literal(42)
        assert isinstance(result, Number)

    def test_as_literal_zero(self):
        """Test converting 0 to Number (not Boolean)."""
        result = as_literal(0)
        # 0 is an int, not a bool, so should return Number
        assert isinstance(result, Number)

    def test_as_literal_negative_int(self):
        """Test converting negative int to Number."""
        result = as_literal(-5)
        assert isinstance(result, Number)

    def test_as_literal_float(self):
        """Test converting float to Number."""
        result = as_literal(3.14)
        assert isinstance(result, Number)

    def test_as_literal_string(self):
        """Test converting string to String."""
        result = as_literal("hello")
        assert isinstance(result, String)

    def test_as_literal_empty_string(self):
        """Test converting empty string to String."""
        result = as_literal("")
        assert isinstance(result, String)

    def test_as_literal_graine_type_passthrough(self):
        """Test that GraineType instances are returned as-is."""
        from fleur.dsl.ir import IRLiteralNumberExpr

        num = Number(IRLiteralNumberExpr(42))
        result = as_literal(num)  # type: ignore[arg-type]
        assert result is num

    def test_as_literal_list(self):
        """Test converting list to Array."""
        from fleur.dsl.ir import IRLiteralArrayExpr
        from fleur.dsl.types import Array

        result = as_literal([1, 2, 3])  # type: ignore
        assert isinstance(result, Array)
        assert isinstance(result._expr, IRLiteralArrayExpr)
        assert len(result._expr.elements) == 3

    def test_as_literal_dict(self):
        """Test converting dict to Record."""
        from fleur.dsl.ir import IRLiteralRecordExpr
        from fleur.dsl.types import Record

        result = as_literal({"key": "value"})  # type: ignore
        assert isinstance(result, Record)
        assert isinstance(result._expr, IRLiteralRecordExpr)
        assert "key" in result._expr.fields

    def test_as_literal_none_raises(self):
        """Test that None raises TypeError."""
        with pytest.raises(TypeError):
            as_literal(None)  # type: ignore


class TestExtractFirstGraineType:
    """Test extract_first_grainetype function."""

    def test_extract_number_type(self):
        """Test extracting Number type."""
        result = extract_first_grainetype(Number)
        assert result is Number

    def test_extract_boolean_type(self):
        """Test extracting Boolean type."""
        result = extract_first_grainetype(Boolean)
        assert result is Boolean

    def test_extract_string_type(self):
        """Test extracting String type."""
        result = extract_first_grainetype(String)
        assert result is String

    def test_extract_from_union(self):
        """Test extracting from Union type."""
        from typing import Union

        from fleur.dsl.types import GraineType

        result = extract_first_grainetype(Union[Number, Boolean])
        # Should extract the first GraineType found
        assert result in (Number, Boolean)
        assert issubclass(result, GraineType)

    def test_extract_from_optional(self):
        """Test extracting from Optional type."""
        from typing import Optional

        result = extract_first_grainetype(Optional[Number])
        assert result is Number

    def test_extract_from_nested_union(self):
        """Test extracting from nested Union."""
        from typing import Union

        result = extract_first_grainetype(Union[int, Union[Number, str]])
        assert result is Number

    def test_extract_no_graine_type_raises(self):
        """Test that missing GraineType raises TypeError."""
        with pytest.raises(TypeError, match="No IRExpr type found"):
            extract_first_grainetype(int)

    def test_extract_from_complex_annotation(self):
        """Test extracting from complex type annotation."""
        from typing import Union

        # Union with non-GraineType and GraineType
        result = extract_first_grainetype(Union[int, float, Number])
        assert result is Number
