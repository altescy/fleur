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

- Type-safe primitive types (`Number`, `Boolean`, `String`, `Array`, `Record`)
- Function definitions with type annotations
- Class definitions with constructors, methods, and getter properties
- Variable declarations and assignments
- Arithmetic operators (`+`, `-`, `*`, `/`) and comparison operators (`==`, `!=`, `<`, `>`, `<=`, `>=`)
- Control flow (for loops with `graine.range`, conditional branches with `graine.cases`)
- Standard library (`graine.math` with JavaScript Math functions)
- JavaScript code generation from Python DSL

## Example

Here's an example demonstrating classes, getters, and Math functions:

```python
from fleur.dsl import graine, parterre


@graine.define
class Point:
    def __init__(self, x: graine.Number, y: graine.Number):
        self.x = x
        self.y = y

    @graine.getter
    def magnitude_squared(self) -> graine.Number:
        """Calculate the squared magnitude (x² + y²)."""
        return self.x * self.x + self.y * self.y

    @graine.getter
    def magnitude(self) -> graine.Number:
        """Calculate the magnitude using Math.sqrt."""
        return graine.math.sqrt(self.magnitude_squared)


@graine.define
def calculate_distance(p1: Point, p2: Point) -> graine.Number:
    """Calculate Euclidean distance between two points."""
    dx = p1.x - p2.x
    dy = p1.y - p2.y
    distance_squared = dx * dx + dy * dy
    return graine.math.sqrt(distance_squared)


@graine.define
def classify_triangle(a: graine.Number, b: graine.Number, c: graine.Number) -> graine.Number:
    """Classify triangle type: 1=equilateral, 2=isosceles, 3=scalene."""
    result = graine.let(0, name="result")

    with graine.cases() as when:
        with when((a == b) & (b == c)):
            result = graine.let(1, name="result")  # Equilateral
        with when((a == b) | (b == c) | (a == c)):
            result = graine.let(2, name="result")  # Isosceles
        with when.default():
            result = graine.let(3, name="result")  # Scalene

    return result


print(parterre().germinate())
```

This generates clean JavaScript:

```javascript
class Point {
  constructor(x, y) {
    this.x = x;
    this.y = y;
  }
  get magnitude_squared() {
    return ((this.x * this.x) + (this.y * this.y));
  }
  get magnitude() {
    return Math.sqrt(this.magnitude_squared);
  }
}
function calculate_distance(p1, p2) {
  let _tmp_0 = (p1.x - p2.x);
  let _tmp_1 = (p1.y - p2.y);
  let _tmp_2 = ((_tmp_0 * _tmp_0) + (_tmp_1 * _tmp_1));
  return Math.sqrt(_tmp_2);
}
function classify_triangle(a, b, c) {
  let result_0 = 0;
  if (((a == b) && (b == c))) {
    let result_0 = 1;
  } else {
    if ((((a == b) || (b == c)) || (a == c))) {
      let result_0 = 2;
    } else {
      let result_0 = 3;
    }
  }
  return result_0;
}
```

The type checker ensures that:
- All function/method arguments have correct types
- Class properties are properly typed
- Getter return types match declarations
- Math functions receive compatible argument types
- Operations are only performed on compatible types

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
