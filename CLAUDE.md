# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Fleur is a Python library for writing JavaScript code with type safety. It provides **graine**, a domain-specific language (DSL) that allows you to write JavaScript logic in Python while leveraging Python's static type checking system. The generated JavaScript is clean and has zero runtime overhead.

## Development Commands

### Testing
```bash
# Run all tests
make test
# or
uv run pytest

# Run tests in a specific file
uv run pytest tests/integration/dsl/test_objects.py

# Run a specific test
uv run pytest tests/integration/dsl/test_objects.py::TestGraineNumberIntegration::test_number_addition
```

### Linting and Type Checking
```bash
# Run all linters and type checking
make lint

# Run ruff linter only
uv run ruff check

# Run pyright type checker only
uv run pyright
```

### Formatting
```bash
# Format code with ruff
make format
```

### Running All Checks
```bash
# Format, lint, and test
make all
```

## Architecture

### Core Components

The codebase is structured around a multi-layer architecture that transforms Python code into JavaScript:

1. **AST Layer** (`src/fleur/dsl/ast.py`): Defines the intermediate representation
   - All AST nodes inherit from `GraineASTNode`
   - Expression nodes: `GraineASTExpr[T]` (typed with `GraineType`)
   - Statement nodes: `GraineASTStmt`
   - Key nodes include: literals (number, string, boolean, array), binary operations, function calls, property/index access, control flow (if, for-of, conditional expressions), functions, and classes

2. **Type System** (`src/fleur/dsl/types.py`): Type-level representations for static checking
   - `GraineType` enum defines all supported types (undefined, boolean, number, string, array, function, class)
   - `GraineObject[T]` protocol represents typed Graine objects with magic methods for operations
   - Type compatibility mappings between Python and Graine types (`PyNumberCompat`, `PyStringCompat`, etc.)
   - Phantom types enable compile-time type checking without runtime overhead

3. **JIT/Builder Layer** (`src/fleur/dsl/jit.py`): Bridges Python execution with AST construction
   - `_GraineBuilder`: Proxy object that intercepts Python operations and builds AST nodes
   - `auto_let` decorator: Automatically creates let-bindings for expressions to ensure proper evaluation order
   - `ensure_graine`: Converts Python values to Graine objects
   - `use_block()` / `require_block()`: Context management for statement emission using `ContextVar`
   - `_function_from_python` / `_class_from_python`: Introspect Python functions/classes and convert to AST

4. **JavaScript Emitter** (`src/fleur/dsl/javascript.py`): Generates JavaScript code from AST
   - Traverses AST and emits corresponding JavaScript syntax
   - Handles indentation and formatting for readable output

5. **DSL Interface** (`src/fleur/dsl/__init__.py`): User-facing API
   - `graine`: Main namespace for DSL operations
     - Type constructors: `number()`, `string()`, `boolean()`, `array()`, `from_python()`
     - Control flow: `when()`, `case()`, `foreach()`
     - Decorators: `func()`, `cls()` for converting Python functions/classes to Graine
     - Built-in modules: `math`, operators: `typeof`, `instanceof`
   - `parterre`: Context manager for code generation
     - Use with `with parterre() as p:` to collect Graine code
     - Call `p.germinate()` to generate JavaScript output

6. **Standard Library** (`src/fleur/dsl/stdlib.py`): Built-in utilities and control flow constructs

### Execution Flow

1. User writes Python code using `graine` API inside a `parterre` context
2. Python operations are intercepted by `_GraineBuilder` proxies
3. AST nodes are constructed and emitted to the current block (managed via `ContextVar`)
4. The `@auto_let` decorator creates intermediate variables to ensure correct evaluation order
5. When `germinate()` is called, the AST is traversed and JavaScript is emitted

### Key Design Patterns

- **Phantom Types**: Generic type parameters track JavaScript types at Python type-check time without runtime cost
- **Context Variables**: Thread-safe block management allows nested contexts
- **Proxy Pattern**: `_GraineBuilder` intercepts attribute access, calls, and operations to build AST
- **Decorator-Based Introspection**: `@graine.func` and `@graine.cls` analyze Python callables and convert them to JavaScript

## Testing

Integration tests use `py-mini-racer` to execute generated JavaScript and verify correctness. The `jsctx` fixture (in `tests/conftest.py`) provides a fresh JavaScript runtime for each test.

Test pattern:
```python
def test_example(jsctx: MiniRacer):
    with parterre() as p:
        @graine.func
        def my_function():
            return graine.number(42)

    js_code = p.germinate()
    jsctx.eval(js_code)
    result = jsctx.call("my_function")
    assert result == 42
```

## Type Safety Guidelines

- Fleur emphasizes strict type checking throughout. All code should pass `pyright` without errors.
- The type system uses `typing_extensions` for advanced features like `TypeAlias`, `ParamSpec`, and covariant type variables.
- When adding new features, ensure proper type annotations for both Python-side and Graine-side types.
- Use overloads extensively to provide precise type information for different use cases.

## Build System

The project uses `uv` for dependency management and build:
- Dependencies are managed in `pyproject.toml`
- Dev dependencies include: `mini-racer` (JavaScript runtime), `pyright` (type checker), `pytest`, `ruff` (linter/formatter)
- Python 3.9+ is required
