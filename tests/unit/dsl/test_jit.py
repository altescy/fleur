"""Unit tests for JIT/Builder layer."""

import pytest

from fleur.dsl import ast, errors, jit


class TestBlockManagement:
    """Tests for block context management."""

    def test_use_block_creates_new_block(self):
        """Test that use_block creates a new block."""
        with jit.use_block() as block:
            assert isinstance(block, ast.GraineBlockNode)
            assert block.statements == []

    def test_use_block_restores_previous_block(self):
        """Test that use_block restores the previous block."""
        # This tests the context management behavior
        with jit.use_block() as block1:
            block1.emit(
                ast.GraineLetNode(identifier=ast.GraineIdentifierNode(name="x"), value=ast.GraineNumberNode(value=1.0))
            )
            with jit.use_block() as block2:
                block2.emit(
                    ast.GraineLetNode(
                        identifier=ast.GraineIdentifierNode(name="y"), value=ast.GraineNumberNode(value=2.0)
                    )
                )
                assert len(block2.statements) == 1
            # Back to outer block
            assert len(block1.statements) == 1

    def test_require_block_has_default(self):
        """Test that require_block has a default block."""
        # The module-level _BLOCK has a default value
        block = jit.require_block()
        assert isinstance(block, ast.GraineBlockNode)

    def test_require_block_with_context(self):
        """Test that require_block returns current block."""
        with jit.use_block() as block:
            current = jit.require_block()
            assert current is block


class TestTypeConversion:
    """Tests for Python to Graine type conversion."""

    def test_from_python_bool(self):
        """Test converting Python bool to Graine."""
        result = jit.from_python(True)
        assert isinstance(result, jit._GraineBuilder)
        assert isinstance(result.__graine_ast__, ast.GraineBooleanNode)
        assert result.__graine_ast__.value is True

    def test_from_python_int(self):
        """Test converting Python int to Graine."""
        result = jit.from_python(42)
        assert isinstance(result, jit._GraineBuilder)
        assert isinstance(result.__graine_ast__, ast.GraineNumberNode)
        assert result.__graine_ast__.value == 42.0

    def test_from_python_float(self):
        """Test converting Python float to Graine."""
        result = jit.from_python(3.14)
        assert isinstance(result, jit._GraineBuilder)
        assert isinstance(result.__graine_ast__, ast.GraineNumberNode)
        assert result.__graine_ast__.value == 3.14

    def test_from_python_string(self):
        """Test converting Python string to Graine."""
        result = jit.from_python("hello")
        assert isinstance(result, jit._GraineBuilder)
        assert isinstance(result.__graine_ast__, ast.GraineStringNode)
        assert result.__graine_ast__.value == "hello"

    def test_from_python_list(self):
        """Test converting Python list to Graine."""
        result = jit.from_python([1, 2, 3])
        assert isinstance(result, jit._GraineBuilder)
        assert isinstance(result.__graine_ast__, ast.GraineArrayNode)

    def test_from_python_dict(self):
        """Test converting Python dict to Graine."""
        result = jit.from_python({"x": 10, "y": 20})
        assert isinstance(result, jit._GraineBuilder)
        assert isinstance(result.__graine_ast__, ast.GraineRecordNode)

    def test_from_python_unsupported_type(self):
        """Test that unsupported types raise GraineTypeError."""

        class CustomClass:
            pass

        with pytest.raises(errors.GraineTypeError) as exc_info:
            jit.from_python(CustomClass())  # type: ignore[arg-type]
        assert "CustomClass" in str(exc_info.value)
        assert "bool, int, float, str, list, dict" in str(exc_info.value)


class TestPrimitiveConstructors:
    """Tests for primitive value constructors."""

    def test_boolean_true(self):
        """Test creating a Graine boolean true."""
        result = jit.boolean(True)
        assert isinstance(result.__graine_ast__, ast.GraineBooleanNode)
        assert result.__graine_ast__.value is True

    def test_boolean_false(self):
        """Test creating a Graine boolean false."""
        result = jit.boolean(False)
        assert isinstance(result.__graine_ast__, ast.GraineBooleanNode)
        assert result.__graine_ast__.value is False

    def test_number_int(self):
        """Test creating a Graine number from int."""
        result = jit.number(42)
        assert isinstance(result.__graine_ast__, ast.GraineNumberNode)
        assert result.__graine_ast__.value == 42.0

    def test_number_float(self):
        """Test creating a Graine number from float."""
        result = jit.number(3.14)
        assert isinstance(result.__graine_ast__, ast.GraineNumberNode)
        assert result.__graine_ast__.value == 3.14

    def test_string(self):
        """Test creating a Graine string."""
        result = jit.string("hello")
        assert isinstance(result.__graine_ast__, ast.GraineStringNode)
        assert result.__graine_ast__.value == "hello"

    def test_array_empty(self):
        """Test creating an empty Graine array."""
        result = jit.array()
        assert isinstance(result.__graine_ast__, ast.GraineArrayNode)
        assert result.__graine_ast__.elements == []

    def test_array_with_elements(self):
        """Test creating a Graine array with elements."""
        result = jit.array(1, 2, 3)
        assert isinstance(result.__graine_ast__, ast.GraineArrayNode)
        assert len(result.__graine_ast__.elements) == 3

    def test_record_empty(self):
        """Test creating an empty Graine record."""
        result = jit.record()
        assert isinstance(result.__graine_ast__, ast.GraineRecordNode)
        assert result.__graine_ast__.fields == {}

    def test_record_with_fields(self):
        """Test creating a Graine record with fields."""
        result = jit.record(x=10, y=20)
        assert isinstance(result.__graine_ast__, ast.GraineRecordNode)
        assert "x" in result.__graine_ast__.fields
        assert "y" in result.__graine_ast__.fields


class TestEnsureGraine:
    """Tests for ensure_graine function."""

    def test_ensure_graine_with_graine_object(self):
        """Test that Graine objects are returned as-is."""
        original = jit.number(42)
        result = jit.ensure_graine(original)
        assert result is original

    def test_ensure_graine_with_python_int(self):
        """Test converting Python int."""
        result = jit.ensure_graine(42)
        assert isinstance(result.__graine_ast__, ast.GraineNumberNode)

    def test_ensure_graine_with_python_string(self):
        """Test converting Python string."""
        result = jit.ensure_graine("hello")
        assert isinstance(result.__graine_ast__, ast.GraineStringNode)


class TestGraineBuilder:
    """Tests for _GraineBuilder proxy class."""

    def test_builder_wraps_ast(self):
        """Test that builder wraps an AST node."""
        node = ast.GraineNumberNode(value=42.0)
        builder = jit._GraineBuilder(node)
        assert builder.__graine_ast__ is node

    def test_builder_getattr_creates_property_access(self):
        """Test that attribute access creates property access node."""
        obj = jit._GraineBuilder(ast.GraineIdentifierNode(name="obj"))
        result = obj.prop
        assert isinstance(result.__graine_ast__, ast.GrainePropertyAccessNode)
        assert result.__graine_ast__.property_name == "prop"

    def test_builder_call_creates_call_node(self):
        """Test that calling creates a call node."""
        with jit.use_block():
            func = jit._GraineBuilder(ast.GraineIdentifierNode(name="func"))
            result = func()
            # auto_let wraps the result, so we get an identifier
            assert isinstance(result.__graine_ast__, ast.GraineIdentifierNode)

    def test_builder_getitem_creates_index_access(self):
        """Test that indexing creates index access node."""
        with jit.use_block():
            arr = jit._GraineBuilder(ast.GraineIdentifierNode(name="arr"))
            result = arr[0]
            # auto_let wraps the result
            assert isinstance(result.__graine_ast__, ast.GraineIdentifierNode)

    def test_builder_setattr_emits_assignment(self):
        """Test that attribute assignment emits an assign node."""
        with jit.use_block() as block:
            obj = jit._GraineBuilder(ast.GraineIdentifierNode(name="obj"))
            value = jit.number(42)
            obj.prop = value
            # Should have emitted an assignment
            assert len(block.statements) > 0
            # The last statement should be an assignment
            last_stmt = block.statements[-1]
            assert isinstance(last_stmt, ast.GraineAssignNode)

    def test_builder_setitem_emits_assignment(self):
        """Test that index assignment emits an assign node."""
        with jit.use_block() as block:
            arr = jit._GraineBuilder(ast.GraineIdentifierNode(name="arr"))
            value = jit.number(42)
            arr[0] = value
            # Should have emitted an assignment
            assert len(block.statements) > 0
            last_stmt = block.statements[-1]
            assert isinstance(last_stmt, ast.GraineAssignNode)

    def test_builder_eq_creates_comparison(self):
        """Test that == creates a binary operation."""
        with jit.use_block():
            a = jit.number(1)
            b = jit.number(2)
            result = a == b  # type: ignore
            # auto_let wraps the result
            assert isinstance(result.__graine_ast__, ast.GraineIdentifierNode)

    def test_builder_add_creates_binary_op(self):
        """Test that + creates a binary operation."""
        with jit.use_block():
            a = jit.number(1)
            b = jit.number(2)
            result = a + b
            # auto_let wraps the result
            assert isinstance(result.__graine_ast__, ast.GraineIdentifierNode)


class TestAutoLet:
    """Tests for auto_let decorator."""

    def test_auto_let_creates_let_binding(self):
        """Test that auto_let creates a let statement."""

        @jit.auto_let
        def make_number():
            return jit._GraineBuilder(ast.GraineNumberNode(value=42.0))

        with jit.use_block() as block:
            result = make_number()
            # Should have emitted a let statement
            assert len(block.statements) == 1
            assert isinstance(block.statements[0], ast.GraineLetNode)
            # Result should be an identifier
            assert isinstance(result.__graine_ast__, ast.GraineIdentifierNode)

    def test_auto_let_preserves_function_name(self):
        """Test that auto_let preserves the original function name."""

        @jit.auto_let
        def my_function():
            return jit.number(42)

        assert my_function.__name__ == "my_function"


class TestFunctionConversion:
    """Tests for converting Python functions to Graine."""

    def test_function_from_python_simple(self):
        """Test converting a simple Python function."""

        def add(a, b):
            return a + b

        node = jit._function_from_python(add)
        assert isinstance(node, ast.GraineFunctionNode)
        assert node.name == "add"
        assert len(node.parameters) == 2
        assert node.parameters[0].name == "a"
        assert node.parameters[1].name == "b"

    def test_function_from_python_no_params(self):
        """Test converting a function with no parameters."""

        def get_answer():
            return jit.number(42)

        node = jit._function_from_python(get_answer)
        assert node.name == "get_answer"
        assert len(node.parameters) == 0

    def test_function_from_python_with_return(self):
        """Test that return values are converted."""

        def get_value():
            return jit.number(42)

        node = jit._function_from_python(get_value)
        # Should have a return statement in the body
        assert len(node.body.statements) > 0
        last_stmt = node.body.statements[-1]
        assert isinstance(last_stmt, ast.GraineReturnNode)


class TestClassConversion:
    """Tests for converting Python classes to Graine."""

    def test_class_ast_from_python_simple(self):
        """Test converting a simple Python class."""

        class Point:
            pass

        node = jit._class_ast_from_python(Point)
        assert isinstance(node, ast.GraineClassNode)
        assert node.name == "Point"

    def test_class_ast_from_python_with_init(self):
        """Test converting a class with __init__."""

        class Point:
            def __init__(self, x, y):
                self.x = x
                self.y = y

        node = jit._class_ast_from_python(Point)
        assert node.constructor is not None
        assert node.constructor.name == "constructor"

    def test_class_ast_from_python_with_method(self):
        """Test converting a class with methods."""

        class Counter:
            def increment(self):
                pass

        node = jit._class_ast_from_python(Counter)
        # Should have at least the increment method
        method_names = [m.name for m in node.methods]
        assert "increment" in method_names

    def test_class_ast_from_python_with_property(self):
        """Test converting a class with property."""

        class Container:
            @property
            def value(self):
                return jit.number(42)

        node = jit._class_ast_from_python(Container)
        # Should have a getter method
        getters = [m for m in node.methods if m.accessor == "get"]
        assert len(getters) > 0
        assert any(m.name == "value" for m in getters)
