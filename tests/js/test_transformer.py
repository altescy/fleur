"""
Tests for AST transformer that converts Python code to builder API calls.
"""

import ast
import inspect
import textwrap

from fleur.js.transformer import PyASTTransformer


class TestPyASTTransformer:
    """Test cases for PyASTTransformer"""

    @staticmethod
    def test_return_with_value():
        """Test that 'return expr' is transformed to '__fleur_get_current_builder__().ret(expr)' (expression statement)"""

        def sample_func(n):
            return n + 1

        source = textwrap.dedent(inspect.getsource(sample_func))
        tree = ast.parse(source)
        func_def = next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))

        transformer = PyASTTransformer({"n"})
        func_def.body = [transformer.visit(stmt) for stmt in func_def.body]
        ast.fix_missing_locations(func_def)

        result = ast.unparse(func_def)
        assert "__fleur_get_current_builder__().ret" in result
        assert "__fleur_get_current_builder__().ret(n + 1)" in result
        # Should NOT be a return statement
        assert "return __fleur_get_current_builder__().ret" not in result

    @staticmethod
    def test_return_without_value():
        """Test that 'return' is transformed to '__fleur_get_current_builder__().ret()' (expression statement)"""

        def sample_func():
            return

        source = textwrap.dedent(inspect.getsource(sample_func))
        tree = ast.parse(source)
        func_def = next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))

        transformer = PyASTTransformer(set())
        func_def.body = [transformer.visit(stmt) for stmt in func_def.body]
        ast.fix_missing_locations(func_def)

        result = ast.unparse(func_def)
        assert "__fleur_get_current_builder__().ret()" in result
        assert "return __fleur_get_current_builder__().ret" not in result

    @staticmethod
    def test_first_assignment():
        """Test that first assignment is transformed to __fleur_get_current_builder__().let()"""

        def sample_func(n):
            x = n + 1
            return x

        source = textwrap.dedent(inspect.getsource(sample_func))
        tree = ast.parse(source)
        func_def = next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))

        transformer = PyASTTransformer({"n"})
        func_def.body = [transformer.visit(stmt) for stmt in func_def.body]
        ast.fix_missing_locations(func_def)

        result = ast.unparse(func_def)
        assert (
            'x = __fleur_get_current_builder__().let("x", n + 1)' in result
            or "x = __fleur_get_current_builder__().let('x', n + 1)" in result
        )

    @staticmethod
    def test_reassignment():
        """Test that reassignment is transformed to __fleur_get_current_builder__().assign()"""

        def sample_func(n):
            x = n + 1
            x = x * 2
            return x

        source = textwrap.dedent(inspect.getsource(sample_func))
        tree = ast.parse(source)
        func_def = next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))

        transformer = PyASTTransformer({"n"})
        func_def.body = [transformer.visit(stmt) for stmt in func_def.body]
        ast.fix_missing_locations(func_def)

        result = ast.unparse(func_def)
        # First assignment should use let
        assert "__fleur_get_current_builder__().let" in result
        # Second assignment should use assign
        assert "__fleur_get_current_builder__().assign(x, x * 2)" in result

    @staticmethod
    def test_parameter_assignment():
        """Test that assigning to a parameter uses __fleur_get_current_builder__().assign()"""

        def sample_func(n):
            n = n + 1
            return n

        source = textwrap.dedent(inspect.getsource(sample_func))
        tree = ast.parse(source)
        func_def = next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))

        transformer = PyASTTransformer({"n"})
        func_def.body = [transformer.visit(stmt) for stmt in func_def.body]
        ast.fix_missing_locations(func_def)

        result = ast.unparse(func_def)
        # Parameter is already declared, so should use assign
        assert "__fleur_get_current_builder__().assign(n, n + 1)" in result
        assert "__fleur_get_current_builder__().let" not in result

    @staticmethod
    def test_if_statement():
        """Test that if statements are transformed to __fleur_get_current_builder__().if_then_else()"""

        def sample_func(n):
            if n > 0:
                return n
            else:
                return -n

        source = textwrap.dedent(inspect.getsource(sample_func))
        tree = ast.parse(source)
        func_def = next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))

        transformer = PyASTTransformer({"n"})
        func_def.body = [transformer.visit(stmt) for stmt in func_def.body]
        ast.fix_missing_locations(func_def)

        result = ast.unparse(func_def)
        assert "__fleur_get_current_builder__().if_then_else" in result
        assert "__fleur_temp_consequent_" in result
        assert "__fleur_temp_alternate_" in result

    @staticmethod
    def test_if_without_else():
        """Test that if without else is transformed correctly"""

        def sample_func(n):
            if n > 0:
                return n

        source = textwrap.dedent(inspect.getsource(sample_func))
        tree = ast.parse(source)
        func_def = next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))

        transformer = PyASTTransformer({"n"})
        func_def.body = [transformer.visit(stmt) for stmt in func_def.body]
        ast.fix_missing_locations(func_def)

        result = ast.unparse(func_def)
        assert "__fleur_get_current_builder__().if_then_else" in result
        # Should have only consequent function (no alternate)
        assert "__fleur_temp_consequent_" in result
        assert "__fleur_temp_alternate_" not in result

    @staticmethod
    def test_multiple_variables():
        """Test multiple variable declarations"""

        def sample_func(n):
            x = n + 1
            y = n * 2
            z = x + y
            return z

        source = textwrap.dedent(inspect.getsource(sample_func))
        tree = ast.parse(source)
        func_def = next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))

        transformer = PyASTTransformer({"n"})
        func_def.body = [transformer.visit(stmt) for stmt in func_def.body]
        ast.fix_missing_locations(func_def)

        result = ast.unparse(func_def)
        # All three should be let (first assignments)
        assert result.count("__fleur_get_current_builder__().let") == 3
        assert (
            '__fleur_get_current_builder__().let("x"' in result or "__fleur_get_current_builder__().let('x'" in result
        )
        assert (
            '__fleur_get_current_builder__().let("y"' in result or "__fleur_get_current_builder__().let('y'" in result
        )
        assert (
            '__fleur_get_current_builder__().let("z"' in result or "__fleur_get_current_builder__().let('z'" in result
        )
