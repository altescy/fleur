# Fleur

A Python library for writing web frontends with type safety.

## Overview

Fleur enables you to write JavaScript code in Python while leveraging Python's static type checking system. By combining Python's expressive syntax with strict type checking, Fleur aims to provide a safer and more productive way to develop web frontend applications.

At the core of Fleur is **graine**, a domain-specific language (DSL) for writing JavaScript in Python. The graine DSL provides type-safe primitives and constructs that compile directly to JavaScript, ensuring type correctness throughout the compilation process.

## Goals

- **Type Safety**: Leverage Python's type system to catch errors at compile time rather than runtime
- **Ergonomic API**: Provide a natural, Pythonic way to express JavaScript logic
- **Zero Runtime Overhead**: Generate clean, readable JavaScript that performs well
- **Strict Type Checking**: Maintain strict type checking throughout the entire codebase to prevent type-related bugs

## Current Status

This project is in early development. Currently, Fleur provides:

- Type-safe primitive types (`Number`, `Boolean`, `String`)
- Function definitions with type annotations
- Variable declarations and assignments
- Basic control flow (for loops with `graine.range`)
- JavaScript code generation from Python DSL

## Example

Here's an example that demonstrates calculating sums using type-safe operations:

```python
from fleur.dsl import emit_javascript, graine, require_block


@graine.function
def sum_range(start: graine.Number, end: graine.Number) -> graine.Number:
    """Calculate the sum of all integers in the range [start, end)."""
    total = graine.let(graine.literal(0), name="total")

    for i in graine.range(start, end):
        total += i

    return total


@graine.function
def triangle_number(n: graine.Number) -> graine.Number:
    """Calculate the nth triangle number: 1 + 2 + 3 + ... + n."""
    return sum_range(graine.literal(1), n + graine.literal(1))


@graine.function
def sum_arithmetic_sequence(first: graine.Number, diff: graine.Number, count: graine.Number) -> graine.Number:
    """Calculate the sum of an arithmetic sequence."""
    total = graine.let(graine.literal(0), name="total")
    current = graine.let(first, name="current")

    for _ in graine.range(0, count):
        total += current
        current += diff

    return total


print(emit_javascript(require_block()))
```

This generates the following clean JavaScript:

```javascript
function sum_range(start, end) {
  let total_0 = 0;
  for (let i_1 = start; i_1 < end; i_1++) {
    total_0 = (total_0 + i_1);
  }
  return total_0;
}
function triangle_number(n) {
  let _ret_0 = sum_range(1, (n + 1));
  return _ret_0;
}
function sum_arithmetic_sequence(first, diff, count) {
  let total_0 = 0;
  let current_1 = first;
  for (let i_2 = 0; i_2 < count; i_2++) {
    total_0 = (total_0 + current_1);
    current_1 = (current_1 + diff);
  }
  return total_0;
}
```

The type checker ensures that:
- All function arguments have the correct types (`graine.Number`)
- Variables are properly initialized before use
- Operations are only performed on compatible types
- Return types match the function signatures

## Architecture

Fleur uses a multi-stage compilation approach:

1. **Python DSL** - Write code using Python with type annotations
2. **Intermediate Representation (IR)** - Convert Python expressions to an internal IR
3. **JavaScript Emission** - Generate JavaScript code from the IR

This architecture allows for:
- Type checking at the Python level
- Optimizations at the IR level
- Clean code generation

## Development

```bash
# Run linting and type checking
make lint

# Run tests
make test
```

## License

TBD

## Author

altescy (me@altescy.jp)
