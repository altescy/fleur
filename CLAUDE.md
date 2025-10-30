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
make test                    # Run all tests (328 tests)
uv run pytest tests/dsl/     # Run all DSL module tests
uv run pytest tests/integration/  # Run integration tests only
uv run pytest tests/dsl/test_stdlib.py  # Run stdlib unit tests
uv run pytest tests/integration/test_stdlib_runtime.py  # Run stdlib integration tests
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
│   ├── test_api.py          # graine API tests (literal, let, range, define)
│   ├── test_ir.py           # IR structure tests
│   ├── test_javascript.py   # JavaScript emission tests
│   ├── test_runtime.py      # Context management tests
│   ├── test_stdlib.py       # Standard library unit tests (Math functions)
│   ├── test_types.py        # Type system tests (Number, Boolean, String, Array, Record)
│   └── test_utils.py        # Utility function tests
└── integration/             # End-to-end integration tests
    ├── test_e2e.py          # Complete DSL → JavaScript compilation tests
    └── test_stdlib_runtime.py  # Standard library runtime tests (with py_mini_racer)
```

## Architecture

Fleur uses a multi-stage compilation pipeline: **Python DSL → IR → JavaScript**

### 1. Type System (`types.py`)

Defines type-safe wrappers around IR expressions:
- **GraineType**: Base class for all types
- **Number, Boolean, String**: Primitive types with operator overloading
  - Arithmetic operators: `+`, `-`, `*`, `/` (Number)
  - Comparison operators: `==`, `!=`, `<`, `>`, `<=`, `>=`
  - Logical operators: `&` (AND), `|` (OR) (Boolean)
- **Array[ElementT, ExprT]**: Generic array type with element type tracking
- **Record[ValueT, ExprT]**: Generic record/object type with value type tracking

**Key compatibility types**:
- `PyBooleanCompat = bool`
- `PyNumberCompat = Union[int, float]`
- `PyStringCompat = str`

**Important**: `bool` is a subclass of `int` in Python, causing type overlap. The overloads in `_utils.py` and `__init__.py` use `# pyright: ignore[reportOverlappingOverload]` to suppress warnings while maintaining correct runtime behavior through `isinstance(value, bool)` checks.

### 2. Intermediate Representation (`ir.py`)

Immutable dataclasses representing the AST:

**Expressions (`IRExpr`)**:
- Literals: `IRLiteralNumberExpr`, `IRLiteralBooleanExpr`, `IRLiteralStringExpr`, `IRLiteralArrayExpr`, `IRLiteralRecordExpr`
- Operations: `IRBinaryOpExpr` (ADD, SUBTRACT, MULTIPLY, DIVIDE, EQ, NE, LT, GT, LE, GE, AND, OR)
- References: `IRIdentifierExpr`, `IRCallExpr` (function can be `str` or `IRExpr` for property access)
- Access: `IRPropertyAccessExpr` (for object property access like `Math.sqrt`)

**Statements (`IRStmt`)**:
- Variables: `IRLetStmt` (declaration), `IRAssignStmt` (mutation)
- Control flow: `IRRangeStmt` (for loops), `IRCasesStmt` (if-else chains), `IRReturnStmt`
- Structure: `IRBlock`, `IRFunctionStmt`, `IRClassStmt` (with constructor, methods, getters)

### 3. Runtime Context (`runtime.py`)

Manages compilation context using Python's `contextvars`:
- `require_block()`: Get current IR block being built
- `use_block()`: Context manager to create new scope

**Pattern**: When executing a function/class decorated with `@graine.define`, the decorator body is executed to build the IR, not the actual computation.

### 4. Standard Library (`stdlib.py`)

Provides wrappers for JavaScript standard library functions:
- **Math class**: Static methods mapping to JavaScript `Math` object
  - Constants: `Math.PI`, `Math.E`
  - Basic: `abs`, `ceil`, `floor`, `round`, `max`, `min`, `pow`, `sqrt`
  - Trigonometric: `sin`, `cos`, `tan`, `asin`, `acos`, `atan`, `atan2`
  - Logarithmic: `exp`, `log`, `log10`, `log2`
  - Utility: `random`, `sign`, `trunc`
- **Helper function**: `_to_ir_expr()` handles conversion of `Number`, `_GraineMethod` (property access), and Python primitives to IR expressions

### 5. JIT Compilation (`jit.py`)

Handles function and class definition at runtime:
- `define_function()`: Captures function body execution to build IR
- `define_class()`: Processes class definitions including `__init__`, methods, and getters
- **Range**: Iterator class for `graine.range()` that generates `IRRangeStmt`
- **Cases**: Context manager for conditional branching (`graine.cases()`)

### 6. JavaScript Emission (`javascript.py`)

Converts IR to JavaScript strings:
- `emit_javascript(*args)`: Takes IR nodes and produces JavaScript code
- Recursive traversal with proper indentation
- Direct mapping: IR constructs → JavaScript syntax

### 7. DSL Interface (`__init__.py`)

The public API through the `graine` class:
- `graine.literal(value)`: Create typed literals (scalars, arrays, records)
- `graine.let(init, name)`: Declare mutable variables
- `graine.range(start, end)`: Create for-loop ranges
- `graine.cases()`: Create conditional branches
- `graine.array(elements)` / `graine.record(fields)`: Create collections
- `@graine.define`: Decorator for function and class definitions
- `@graine.getter`: Decorator for getter properties
- `graine.math`: Access to Math standard library

**Execution model**: Decorated functions/classes are executed during definition to capture their IR, not at runtime.

**Context manager**: `parterre()` provides explicit block management and code generation via `germinate()`.

## Type Safety Approach

1. **Python-level type checking**: Use type annotations and pyright to validate the DSL usage
2. **Runtime type conversion**: The `as_literal()` function uses `isinstance()` checks to distinguish `bool` from `int` despite type overlap
3. **IR validation**: Immutable IR nodes ensure correctness
4. **Clean JavaScript output**: No runtime type checking in generated code

## Current Limitations

- Limited standard library (only Math currently implemented)
- No string manipulation functions
- No array methods (map, filter, reduce, etc.)
- No DOM manipulation APIs
- No async/await support
- No module system (import/export)
- Variable scoping in conditional branches needs improvement (shadowing issues)

## Important Implementation Details

### Math stdlib and _GraineMethod handling

When getter properties or property access results are passed to Math functions, they return `_GraineMethod` objects that wrap `IRPropertyAccessExpr`. The `_to_ir_expr()` helper in `stdlib.py` handles this by checking `hasattr(value, "_expr")` to extract the IR expression uniformly for:
- `Number` objects
- `_GraineMethod` objects (from getters/properties)
- Python primitives (converted to `IRLiteralNumberExpr`)

This allows code like:
```python
@graine.getter
def magnitude(self) -> graine.Number:
    return graine.math.sqrt(self.magnitude_squared)  # self.magnitude_squared is a _GraineMethod
```

### Class definitions with @graine.define

The `define_class()` function in `jit.py`:
1. Executes the class body to capture methods
2. Identifies getters by checking `isinstance(value, _GraineProperty)`
3. Wraps the class to intercept `__init__` calls
4. Returns a wrapper that creates `ClassWrapper` instances with `_graine_class` metadata

### IRCallExpr function field

`IRCallExpr.function` is `Union[str, IRExpr]` to support both:
- Direct function calls: `function="myFunc"`
- Property access calls: `function=IRPropertyAccessExpr(target=..., property=...)`

This enables `Math.sqrt(x)` to compile to JavaScript `Math.sqrt(x)`.

## Code Style Notes

- Prefer `@overload` with type-specific signatures over Union return types
- Use `# pyright: ignore[reportOverlappingOverload]` only for bool/int overlap cases
- Always use frozen dataclasses for IR nodes
- Python version: 3.9+ (specified in pyproject.toml)
- Use `_to_ir_expr()` helper when implementing new stdlib functions
