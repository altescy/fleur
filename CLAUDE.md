# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Fleur is a Python library for writing web frontends with type safety. At its core is **graine**, a domain-specific language (DSL) for writing JavaScript in Python. The graine DSL provides type-safe primitives that compile to JavaScript, leveraging Python's static type checking to catch errors at compile time.

**Key Concept**: graine (French for "seed") is the DSL/core, while fleur (French for "flower") is the overall framework.

## Development Commands

All Python commands must use `uv run python` (not plain `python` or `python3`).

```bash
# Run all checks (format, lint, test)
make all

# Linting and type checking
make lint                    # Run ruff and pyright
PYTHONPATH=$(PWD) uv run pyright  # Type check only

# Formatting
make format                  # Auto-format code with ruff

# Testing
make test                    # Run all tests (183 tests)
uv run pytest tests/dsl/     # Run all DSL module tests
uv run pytest tests/integration/  # Run integration tests only
uv run pytest tests/dsl/test_ir.py  # Run single test file
uv run pytest tests/dsl/test_api.py::TestGraineLiteral -v  # Run specific test class

# Running examples
uv run python main.py        # Run the main example
uv run python example.py     # Run the example file
```

## Test Structure

Tests are organized to mirror the `src/fleur` structure:

```
tests/
├── conftest.py              # Root pytest configuration
├── test_version.py          # Version tests
├── dsl/                     # Tests for fleur.dsl module
│   ├── conftest.py          # DSL-specific fixtures
│   ├── test_api.py          # graine API tests (literal, let, range, function)
│   ├── test_ir.py           # IR structure tests
│   ├── test_javascript.py   # JavaScript emission tests
│   ├── test_runtime.py      # Context management tests
│   ├── test_stdlib.py       # Standard library tests (Range)
│   ├── test_types.py        # Type system tests (Number, Boolean, String, Var)
│   └── test_utils.py        # Utility function tests
└── integration/             # End-to-end integration tests
    └── test_e2e.py          # Complete DSL → JavaScript compilation tests
```

## Architecture

Fleur uses a multi-stage compilation pipeline: **Python DSL → IR → JavaScript**

### 1. Type System (`types.py`)

Defines type-safe wrappers around IR expressions:
- **GraineType**: Base class for all types
- **Number, Boolean, String**: Primitive types with operator overloading
- **Var[T]**: Mutable variables with generic typing
- **Function[T]**: Type-safe function definitions

**Key compatibility types**:
- `PyBooleanCompat = bool`
- `PyNumberCompat = Union[int, float]`
- `PyStringCompat = str`

**Important**: `bool` is a subclass of `int` in Python, causing type overlap. The overloads in `_utils.py:22,26` and `__init__.py:46,50` use `# pyright: ignore[reportOverlappingOverload]` to suppress warnings while maintaining correct runtime behavior through `isinstance(value, bool)` checks.

### 2. Intermediate Representation (`ir.py`)

Immutable dataclasses representing the AST:

**Expressions (`IRExpr`)**:
- Literals: `IRLiteralNumberExpr`, `IRLiteralBooleanExpr`, `IRLiteralStringExpr`
- Operations: `IRBinaryOpExpr` (ADD, SUBTRACT, MULTIPLY, DIVIDE)
- References: `IRIdentifierExpr`, `IRCallExpr`

**Statements (`IRStmt`)**:
- Variables: `IRLetStmt` (declaration), `IRAssignStmt` (mutation)
- Control flow: `IRRangeStmt` (for loops), `IRReturnStmt`
- Structure: `IRBlock`, `IRFunctionStmt`

### 3. Runtime Context (`runtime.py`)

Manages compilation context using Python's `contextvars`:
- `require_block()`: Get current IR block being built
- `use_block()`: Context manager to create new scope

**Pattern**: When executing a function decorated with `@graine.function`, the decorator body is executed to build the IR, not the actual computation.

### 4. JavaScript Emission (`javascript.py`)

Converts IR to JavaScript strings:
- `emit_javascript(*args)`: Takes IR nodes and produces JavaScript code
- Recursive traversal with proper indentation
- Direct mapping: IR constructs → JavaScript syntax

### 5. DSL Interface (`__init__.py`)

The public API through the `graine` class:
- `graine.literal(value)`: Create typed literals
- `graine.let(init, name)`: Declare mutable variables
- `graine.range(start, end)`: Create for-loop ranges
- `@graine.function`: Decorator for function definitions

**Execution model**: Decorated functions are executed during definition to capture their IR, not at runtime.

## Type Safety Approach

1. **Python-level type checking**: Use type annotations and pyright to validate the DSL usage
2. **Runtime type conversion**: The `as_literal()` function uses `isinstance()` checks to distinguish `bool` from `int` despite type overlap
3. **IR validation**: Immutable IR nodes ensure correctness
4. **Clean JavaScript output**: No runtime type checking in generated code

## Current Limitations

- Only basic operators: `+`, `-` (multiplication and division defined in IR but not in Number type)
- No conditional statements (if/else)
- No variable reassignment (only `+=` through `__iadd__`)
- No arrays or objects
- No DOM manipulation APIs

## Code Style Notes

- Prefer `@overload` with type-specific signatures over Union return types
- Use `# pyright: ignore[reportOverlappingOverload]` only for bool/int overlap cases
- Always use frozen dataclasses for IR nodes
- Python version: 3.9+ (specified in pyproject.toml)
