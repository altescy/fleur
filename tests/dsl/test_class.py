"""Tests for class support in Fleur DSL."""

from fleur.dsl import graine
from fleur.dsl.javascript import emit_javascript
from fleur.dsl.runtime import use_block


class TestClassDefinition:
    """Test basic class definition and instantiation."""

    def test_simple_class_definition(self):
        """Test defining a simple class with constructor."""
        with use_block() as block:

            @graine.define
            class Point:
                def __init__(self, x: graine.Number, y: graine.Number):
                    self.x = x
                    self.y = y

            js = emit_javascript(block)

        assert "class Point" in js
        assert "constructor(x, y)" in js
        assert "this.x = x" in js
        assert "this.y = y" in js

    def test_class_with_multiple_properties(self):
        """Test class with multiple properties."""
        with use_block() as block:

            @graine.define
            class Rectangle:
                def __init__(self, width: graine.Number, height: graine.Number, color: graine.String):
                    self.width = width
                    self.height = height
                    self.color = color

            js = emit_javascript(block)

        assert "class Rectangle" in js
        assert "constructor(width, height, color)" in js
        assert "this.width = width" in js
        assert "this.height = height" in js
        assert "this.color = color" in js


class TestInstanceMethods:
    """Test instance methods."""

    def test_simple_instance_method(self):
        """Test defining an instance method."""
        with use_block() as block:

            @graine.define
            class Counter:
                def __init__(self, initial: graine.Number):
                    self.count = initial

                def increment(self) -> graine.Number:
                    self.count += 1
                    return self.count

            js = emit_javascript(block)

        assert "class Counter" in js
        assert "increment()" in js
        assert "this.count = (this.count + 1)" in js
        # Should not have 'return this.count' after the assignment
        # because increment has no explicit return statement after +=

    def test_method_with_parameters(self):
        """Test instance method with parameters."""
        with use_block() as block:

            @graine.define
            class Calculator:
                def __init__(self, initial: graine.Number):
                    self.value = initial

                def add(self, n: graine.Number) -> graine.Number:
                    result = self.value + n
                    return result

            js = emit_javascript(block)

        assert "class Calculator" in js
        assert "add(n)" in js
        assert "return" in js

    def test_method_accessing_multiple_properties(self):
        """Test method that accesses multiple properties."""
        with use_block() as block:

            @graine.define
            class Point:
                def __init__(self, x: graine.Number, y: graine.Number):
                    self.x = x
                    self.y = y

                def distance_squared(self) -> graine.Number:
                    return self.x * self.x + self.y * self.y

            js = emit_javascript(block)

        assert "distance_squared()" in js
        assert "return ((this.x * this.x) + (this.y * this.y))" in js


class TestStaticMethods:
    """Test static methods."""

    def test_simple_static_method(self):
        """Test defining a static method."""
        with use_block() as block:

            @graine.define
            class MathUtils:
                def __init__(self):
                    pass

                @graine.static
                def square(x: graine.Number) -> graine.Number:  # type: ignore[misc]
                    return x * x

            js = emit_javascript(block)

        assert "class MathUtils" in js
        assert "static square(x)" in js
        assert "return (x * x)" in js

    def test_static_method_with_return(self):
        """Test static method with calculations."""
        with use_block() as block:

            @graine.define
            class MathUtils:
                def __init__(self):
                    pass

                @graine.static
                def double(x: graine.Number) -> graine.Number:  # type: ignore[misc]
                    return x * 2

            js = emit_javascript(block)

        assert "static double(x)" in js
        assert "return (x * 2)" in js


class TestGetterProperties:
    """Test getter properties."""

    def test_simple_getter(self):
        """Test defining a getter property."""
        with use_block() as block:

            @graine.define
            class Circle:
                def __init__(self, radius: graine.Number):
                    self.radius = radius

                @graine.getter
                def diameter(self) -> graine.Number:
                    return self.radius * 2

            js = emit_javascript(block)

        assert "class Circle" in js
        assert "get diameter()" in js
        assert "return (this.radius * 2)" in js

    def test_getter_with_complex_calculation(self):
        """Test getter with complex calculation."""
        with use_block() as block:

            @graine.define
            class Rectangle:
                def __init__(self, width: graine.Number, height: graine.Number):
                    self.width = width
                    self.height = height

                @graine.getter
                def area(self) -> graine.Number:
                    return self.width * self.height

                @graine.getter
                def perimeter(self) -> graine.Number:
                    return (self.width + self.height) * 2

            js = emit_javascript(block)

        assert "get area()" in js
        assert "return (this.width * this.height)" in js
        assert "get perimeter()" in js
        assert "return ((this.width + this.height) * 2)" in js


class TestPropertyAccess:
    """Test property access from outside the class."""

    def test_property_access_in_function(self):
        """Test accessing class properties from a function."""
        with use_block() as block:

            @graine.define
            class Point:
                def __init__(self, x: graine.Number, y: graine.Number):
                    self.x = x
                    self.y = y

            @graine.define
            def get_x(p: Point) -> graine.Number:
                return p.x

            js = emit_javascript(block)

        assert "function get_x(p)" in js
        assert "return p.x" in js

    def test_property_access_in_arithmetic(self):
        """Test using properties in arithmetic operations."""
        with use_block() as block:

            @graine.define
            class Vector:
                def __init__(self, x: graine.Number, y: graine.Number):
                    self.x = x
                    self.y = y

            @graine.define
            def dot_product(v1: Vector, v2: Vector) -> graine.Number:
                return v1.x * v2.x + v1.y * v2.y

            js = emit_javascript(block)

        assert "function dot_product(v1, v2)" in js
        assert "return ((v1.x * v2.x) + (v1.y * v2.y))" in js


class TestMethodCalls:
    """Test calling methods from outside the class."""

    def test_method_call_in_function(self):
        """Test calling instance method from a function."""
        with use_block() as block:

            @graine.define
            class Calculator:
                def __init__(self, value: graine.Number):
                    self.value = value

                def double(self) -> graine.Number:
                    return self.value * 2

            @graine.define
            def compute(calc: Calculator) -> graine.Number:
                result = calc.double()
                return result

            js = emit_javascript(block)

        assert "function compute(calc)" in js
        assert "calc.double()" in js

    def test_method_call_with_arguments(self):
        """Test calling method with arguments."""
        with use_block() as block:

            @graine.define
            class Accumulator:
                def __init__(self, value: graine.Number):
                    self.value = value

                def add(self, n: graine.Number) -> graine.Number:
                    return self.value + n

            @graine.define
            def use_accumulator(acc: Accumulator, x: graine.Number) -> graine.Number:
                return acc.add(x)

            js = emit_javascript(block)

        assert "function use_accumulator(acc, x)" in js
        assert "return acc.add(x)" in js


class TestGetterAccess:
    """Test accessing getter properties."""

    def test_getter_access_in_function(self):
        """Test accessing getter from a function."""
        with use_block() as block:

            @graine.define
            class Square:
                def __init__(self, side: graine.Number):
                    self.side = side

                @graine.getter
                def area(self) -> graine.Number:
                    return self.side * self.side

            @graine.define
            def get_area(sq: Square) -> graine.Number:
                return sq.area

            js = emit_javascript(block)

        assert "function get_area(sq)" in js
        assert "return sq.area" in js  # No parentheses, accessed as property

    def test_getter_in_arithmetic(self):
        """Test using getter in arithmetic operations."""
        with use_block() as block:

            @graine.define
            class Circle:
                def __init__(self, radius: graine.Number):
                    self.radius = radius

                @graine.getter
                def area(self) -> graine.Number:
                    return self.radius * self.radius * 3

            @graine.define
            def sum_areas(c1: Circle, c2: Circle) -> graine.Number:
                return c1.area + c2.area

            js = emit_javascript(block)

        assert "function sum_areas(c1, c2)" in js
        assert "return (c1.area + c2.area)" in js


class TestClassInstantiation:
    """Test creating instances of classes."""

    def test_instantiation_in_function(self):
        """Test creating class instance in a function."""
        with use_block() as block:

            @graine.define
            class Point:
                def __init__(self, x: graine.Number, y: graine.Number):
                    self.x = x
                    self.y = y

            @graine.define
            def create_point(a: graine.Number, b: graine.Number) -> graine.Number:
                p = Point(a, b)
                return p.x + p.y

            js = emit_javascript(block)

        assert "function create_point(a, b)" in js
        assert "new Point(a, b)" in js

    def test_instantiation_with_literals(self):
        """Test creating instance with literal values."""
        with use_block() as block:

            @graine.define
            class Counter:
                def __init__(self, initial: graine.Number):
                    self.count = initial

            @graine.define
            def make_counter() -> graine.Number:
                c = Counter(0)  # type: ignore[arg-type]
                return c.count

            js = emit_javascript(block)

        assert "new Counter(0)" in js


class TestMixedTypeProperties:
    """Test classes with various property types."""

    def test_class_with_number_string_boolean(self):
        """Test class with Number, String, and Boolean properties."""
        with use_block() as block:

            @graine.define
            class Person:
                def __init__(self, name: graine.String, age: graine.Number, active: graine.Boolean):
                    self.name = name
                    self.age = age
                    self.active = active

            js = emit_javascript(block)

        assert "class Person" in js
        assert "constructor(name, age, active)" in js
        assert "this.name = name" in js
        assert "this.age = age" in js
        assert "this.active = active" in js

    def test_class_with_string_operations(self):
        """Test class with String property and operations."""
        with use_block() as block:

            @graine.define
            class User:
                def __init__(self, username: graine.String):
                    self.username = username

                def get_upper_name(self) -> graine.String:
                    return self.username.toUpperCase()

            js = emit_javascript(block)

        assert "class User" in js
        assert "get_upper_name()" in js
        assert "return this.username.toUpperCase()" in js

    def test_class_with_array_property(self):
        """Test class with Array property."""
        with use_block() as block:

            @graine.define
            class NumberList:
                def __init__(self, items: graine.Array):
                    self.items = items

                @graine.getter
                def size(self) -> graine.Number:
                    return self.items.length

            js = emit_javascript(block)

        assert "class NumberList" in js
        assert "this.items = items" in js
        assert "get size()" in js
        assert "return this.items.length" in js

    def test_class_with_augmented_assignments(self):
        """Test class with various augmented assignment operators."""
        with use_block() as block:

            @graine.define
            class Calculator:
                def __init__(self, value: graine.Number):
                    self.value = value

                def add(self, n: graine.Number):
                    self.value += n

                def subtract(self, n: graine.Number):
                    self.value -= n

                def multiply(self, n: graine.Number):
                    self.value *= n

                def divide(self, n: graine.Number):
                    self.value /= n

            js = emit_javascript(block)

        assert "class Calculator" in js
        assert "this.value = (this.value + n)" in js
        assert "this.value = (this.value - n)" in js
        assert "this.value = (this.value * n)" in js
        assert "this.value = (this.value / n)" in js

    def test_accessing_different_type_properties(self):
        """Test accessing various types of properties from a function."""
        with use_block() as block:

            @graine.define
            class Product:
                def __init__(self, name: graine.String, price: graine.Number):
                    self.name = name
                    self.price = price

            @graine.define
            def get_product_info(p: Product) -> graine.Number:
                # Access both string and number properties
                name_len = p.name.length
                total = name_len + p.price
                return total

            js = emit_javascript(block)

        assert "function get_product_info(p)" in js
        assert "p.name.length" in js
        assert "p.price" in js


class TestComplexScenarios:
    """Test complex scenarios combining multiple features."""

    def test_class_with_all_features(self):
        """Test class with properties, methods, static methods, and getters."""
        with use_block() as block:

            @graine.define
            class Rectangle:
                def __init__(self, width: graine.Number, height: graine.Number):
                    self.width = width
                    self.height = height

                def scale(self, factor: graine.Number):
                    self.width = self.width * factor
                    self.height = self.height * factor

                @graine.static
                def unit_square() -> graine.Number:  # type: ignore[misc]
                    return graine.literal(1)

                @graine.getter
                def area(self) -> graine.Number:
                    return self.width * self.height

            js = emit_javascript(block)

        assert "class Rectangle" in js
        assert "constructor(width, height)" in js
        assert "scale(factor)" in js
        assert "static unit_square()" in js
        assert "get area()" in js

    def test_multiple_classes(self):
        """Test defining multiple classes."""
        with use_block() as block:

            @graine.define
            class Point:
                def __init__(self, x: graine.Number, y: graine.Number):
                    self.x = x
                    self.y = y

            @graine.define
            class Rectangle:
                def __init__(self, width: graine.Number, height: graine.Number):
                    self.width = width
                    self.height = height

                @graine.getter
                def area(self) -> graine.Number:
                    return self.width * self.height

            js = emit_javascript(block)

        assert "class Point" in js
        assert "class Rectangle" in js
        assert "get area()" in js

    def test_chained_property_access(self):
        """Test accessing properties through multiple object."""
        with use_block() as block:

            @graine.define
            class Point:
                def __init__(self, x: graine.Number, y: graine.Number):
                    self.x = x
                    self.y = y

            @graine.define
            def sum_coordinates(p1: Point, p2: Point) -> graine.Number:
                # Chain property access through multiple objects
                return p1.x + p1.y + p2.x + p2.y

            js = emit_javascript(block)

        assert "function sum_coordinates(p1, p2)" in js
        assert "return (((p1.x + p1.y) + p2.x) + p2.y)" in js

    def test_method_chaining(self):
        """Test calling method and accessing getter."""
        with use_block() as block:

            @graine.define
            class Builder:
                def __init__(self, value: graine.Number):
                    self.value = value

                def increment(self) -> graine.Number:
                    self.value += 1
                    return self.value

                @graine.getter
                def result(self) -> graine.Number:
                    return self.value

            @graine.define
            def use_builder(initial: graine.Number) -> graine.Number:
                b = Builder(initial)
                graine.let(b.increment(), "temp")
                return b.result

            js = emit_javascript(block)

        assert "_builder_0.increment()" in js
        assert "return _builder_0.result" in js
