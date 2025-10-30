"""Integration tests for class features with JavaScript runtime execution."""

import pytest
from py_mini_racer import MiniRacer

from fleur.dsl import graine, parterre


class TestClassBasics:
    """Test basic class functionality with JavaScript execution."""

    @pytest.fixture
    def ctx(self):
        """Create a fresh JavaScript context."""
        return MiniRacer()

    def test_simple_class_instantiation(self, ctx):
        """Test creating and using a simple class."""
        with parterre() as p:

            @graine.define
            class Point:
                def __init__(self, x: graine.Number, y: graine.Number):
                    self.x = x
                    self.y = y

            @graine.define
            def create_point(a: graine.Number, b: graine.Number) -> graine.Number:
                p = Point(a, b)
                return p.x + p.y

        js_code = p.germinate()
        ctx.eval(js_code)

        result = ctx.call("create_point", 3, 4)
        assert result == 7

    def test_class_with_instance_method(self, ctx):
        """Test calling instance methods."""
        with parterre() as p:

            @graine.define
            class Counter:
                def __init__(self, initial: graine.Number):
                    self.count = initial

                def increment(self) -> graine.Number:
                    self.count += 1
                    return self.count

            @graine.define
            def test_counter(start: graine.Number) -> graine.Number:
                c = Counter(start)
                graine.let(c.increment(), "r1")
                graine.let(c.increment(), "r2")
                # Access the count property directly
                return c.count

        js_code = p.germinate()
        ctx.eval(js_code)

        # Start with 0, increment twice: final count is 2
        result = ctx.call("test_counter", 0)
        assert result == 2

    def test_class_with_getter(self, ctx):
        """Test getter properties."""
        with parterre() as p:

            @graine.define
            class Circle:
                def __init__(self, radius: graine.Number):
                    self.radius = radius

                @graine.getter
                def diameter(self) -> graine.Number:
                    return self.radius * 2

            @graine.define
            def get_diameter(r: graine.Number) -> graine.Number:
                c = Circle(r)
                return c.diameter

        js_code = p.germinate()
        ctx.eval(js_code)

        result = ctx.call("get_diameter", 5)
        assert result == 10

    def test_class_with_static_method(self, ctx):
        """Test static methods."""
        with parterre() as p:

            @graine.define
            class MathUtils:
                def __init__(self):
                    pass

                @graine.static
                def square(x: graine.Number) -> graine.Number:  # type: ignore[misc]
                    return x * x

        js_code = p.germinate()
        ctx.eval(js_code)

        # Call static method directly
        result = ctx.eval("MathUtils.square(7)")
        assert result == 49


class TestClassWithDifferentTypes:
    """Test classes with various property types."""

    @pytest.fixture
    def ctx(self):
        """Create a fresh JavaScript context."""
        return MiniRacer()

    def test_class_with_string_property(self, ctx):
        """Test class with String property and method."""
        with parterre() as p:

            @graine.define
            class User:
                def __init__(self, name: graine.String):
                    self.name = name

                def get_upper_name(self) -> graine.String:
                    return self.name.toUpperCase()

            @graine.define
            def process_user(username: graine.String) -> graine.Number:
                u = User(username)
                upper_name = graine.let(u.get_upper_name(), "upper")
                return upper_name.length

        js_code = p.germinate()
        ctx.eval(js_code)

        result = ctx.call("process_user", "alice")
        assert result == 5  # "ALICE" has 5 characters

    def test_class_with_mixed_types(self, ctx):
        """Test class with Number, String, and Boolean properties."""
        with parterre() as p:

            @graine.define
            class Product:
                def __init__(self, name: graine.String, price: graine.Number):
                    self.name = name
                    self.price = price

                def calculate_total(self, quantity: graine.Number) -> graine.Number:
                    return self.price * quantity

            @graine.define
            def buy_product(item_name: graine.String, item_price: graine.Number, qty: graine.Number) -> graine.Number:
                prod = Product(item_name, item_price)
                total = graine.let(prod.calculate_total(qty), "total")
                return total

        js_code = p.germinate()
        ctx.eval(js_code)

        result = ctx.call("buy_product", "apple", 2.5, 3)
        assert result == 7.5

    def test_class_with_array_property(self, ctx):
        """Test class with Array property."""
        with parterre() as p:

            @graine.define
            class NumberList:
                def __init__(self, items: graine.Array):
                    self.items = items

                @graine.getter
                def size(self) -> graine.Number:
                    return self.items.length

            @graine.define
            def get_list_size() -> graine.Number:
                arr = graine.array([1, 2, 3, 4, 5])
                nl = NumberList(arr)
                return nl.size

        js_code = p.germinate()
        ctx.eval(js_code)

        result = ctx.call("get_list_size")
        assert result == 5


class TestAugmentedAssignments:
    """Test augmented assignment operators on class properties."""

    @pytest.fixture
    def ctx(self):
        """Create a fresh JavaScript context."""
        return MiniRacer()

    def test_add_assign(self, ctx):
        """Test += operator on class property."""
        with parterre() as p:

            @graine.define
            class Accumulator:
                def __init__(self, value: graine.Number):
                    self.value = value

                def add(self, n: graine.Number):
                    self.value += n

                def get_value(self) -> graine.Number:
                    return self.value

            @graine.define
            def test_add() -> graine.Number:
                acc = Accumulator(graine.literal(10))
                graine.let(acc.add(graine.literal(5)), "tmp")  # type: ignore[arg-type]
                return acc.get_value()

        js_code = p.germinate()
        ctx.eval(js_code)

        result = ctx.call("test_add")
        assert result == 15

    def test_all_augmented_assignments(self, ctx):
        """Test +=, -=, *=, /= operators."""
        with parterre() as p:

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

                def get_value(self) -> graine.Number:
                    return self.value

            @graine.define
            def test_operations() -> graine.Number:
                calc = Calculator(graine.literal(10))
                graine.let(calc.add(graine.literal(5)), "t1")  # type: ignore[arg-type]  # 10 + 5 = 15
                graine.let(calc.subtract(graine.literal(3)), "t2")  # type: ignore[arg-type]  # 15 - 3 = 12
                graine.let(calc.multiply(graine.literal(2)), "t3")  # type: ignore[arg-type]  # 12 * 2 = 24
                graine.let(calc.divide(graine.literal(4)), "t4")  # type: ignore[arg-type]  # 24 / 4 = 6
                return calc.get_value()

        js_code = p.germinate()
        ctx.eval(js_code)

        result = ctx.call("test_operations")
        assert result == 6


class TestComplexScenarios:
    """Test complex scenarios with classes."""

    @pytest.fixture
    def ctx(self):
        """Create a fresh JavaScript context."""
        return MiniRacer()

    def test_multiple_instances(self, ctx):
        """Test creating and using multiple instances."""
        with parterre() as p:

            @graine.define
            class Point:
                def __init__(self, x: graine.Number, y: graine.Number):
                    self.x = x
                    self.y = y

            @graine.define
            def distance_squared(
                x1: graine.Number, y1: graine.Number, x2: graine.Number, y2: graine.Number
            ) -> graine.Number:
                p1 = Point(x1, y1)
                p2 = Point(x2, y2)
                dx = p2.x - p1.x
                dy = p2.y - p1.y
                return dx * dx + dy * dy

        js_code = p.germinate()
        ctx.eval(js_code)

        # Distance squared from (0,0) to (3,4) = 9 + 16 = 25
        result = ctx.call("distance_squared", 0, 0, 3, 4)
        assert result == 25

    def test_class_with_loop(self, ctx):
        """Test using class instance in a loop."""
        with parterre() as p:

            @graine.define
            class Sum:
                def __init__(self):
                    self.total = graine.literal(0)

                def add(self, n: graine.Number):
                    self.total += n  # type: ignore[operator]

                @graine.getter
                def result(self) -> graine.Number:
                    return self.total

            @graine.define
            def sum_range(n: graine.Number) -> graine.Number:
                s = Sum()
                for i in graine.range(0, n):
                    graine.let(s.add(i), "tmp")  # type: ignore[arg-type]
                return s.result

        js_code = p.germinate()
        ctx.eval(js_code)

        # Sum of 0 to 4: 0 + 1 + 2 + 3 + 4 = 10
        result = ctx.call("sum_range", 5)
        assert result == 10

    def test_class_with_getter_calculation(self, ctx):
        """Test getter with complex calculation."""
        with parterre() as p:

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

            @graine.define
            def calculate_metrics(w: graine.Number, h: graine.Number) -> graine.Number:
                rect = Rectangle(w, h)
                return rect.area + rect.perimeter

        js_code = p.germinate()
        ctx.eval(js_code)

        # Rectangle 3x4: area = 12, perimeter = 14, total = 26
        result = ctx.call("calculate_metrics", 3, 4)
        assert result == 26

    def test_method_chaining_with_properties(self, ctx):
        """Test accessing properties and calling methods in sequence."""
        with parterre() as p:

            @graine.define
            class Builder:
                def __init__(self, value: graine.Number):
                    self.value = value

                def double(self):
                    self.value *= 2

                def add_ten(self):
                    self.value += 10

                @graine.getter
                def result(self) -> graine.Number:
                    return self.value

            @graine.define
            def build_value(initial: graine.Number) -> graine.Number:
                b = Builder(initial)
                graine.let(b.double(), "t1")  # type: ignore[arg-type]  # 5 * 2 = 10
                graine.let(b.add_ten(), "t2")  # type: ignore[arg-type]  # 10 + 10 = 20
                graine.let(b.double(), "t3")  # type: ignore[arg-type]  # 20 * 2 = 40
                return b.result

        js_code = p.germinate()
        ctx.eval(js_code)

        result = ctx.call("build_value", 5)
        assert result == 40
