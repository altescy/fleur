"""Unit tests for error types and error formatting."""

from fleur.dsl import errors


class TestCustomErrors:
    """Tests for custom error types."""

    def test_graine_error_is_exception(self):
        """Test that GraineError is an Exception."""
        err = errors.GraineError("test error")
        assert isinstance(err, Exception)

    def test_graine_type_error_is_type_error(self):
        """Test that GraineTypeError is both GraineError and TypeError."""
        err = errors.GraineTypeError("type error")
        assert isinstance(err, errors.GraineError)
        assert isinstance(err, TypeError)

    def test_graine_value_error_is_value_error(self):
        """Test that GraineValueError is both GraineError and ValueError."""
        err = errors.GraineValueError("value error")
        assert isinstance(err, errors.GraineError)
        assert isinstance(err, ValueError)

    def test_graine_block_error_is_lookup_error(self):
        """Test that GraineBlockError is both GraineError and LookupError."""
        err = errors.GraineBlockError("block error")
        assert isinstance(err, errors.GraineError)
        assert isinstance(err, LookupError)

    def test_graine_ast_error(self):
        """Test GraineASTError."""
        err = errors.GraineASTError("AST error")
        assert isinstance(err, errors.GraineError)


class TestErrorFormatting:
    """Tests for error message formatting functions."""

    def test_format_type_error_with_int(self):
        """Test formatting a type error message for an int."""
        msg = errors.format_type_error(42, "str, list, dict")
        assert "int" in msg
        assert "str, list, dict" in msg
        assert "42" in msg

    def test_format_type_error_with_custom_object(self):
        """Test formatting a type error message for a custom object."""

        class CustomClass:
            pass

        obj = CustomClass()
        msg = errors.format_type_error(obj, "supported types")
        assert "CustomClass" in msg
        assert "supported types" in msg

    def test_format_unsupported_ast_error(self):
        """Test formatting an unsupported AST node error."""

        class FakeNode:
            pass

        msg = errors.format_unsupported_ast_error(FakeNode)
        assert "FakeNode" in msg
        assert "unsupported" in msg.lower() or "Unsupported" in msg
