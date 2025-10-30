"""Tests for standard library functions."""

from fleur.dsl import graine
from fleur.dsl.javascript import emit_javascript
from fleur.dsl.runtime import use_block
from fleur.dsl.stdlib import Math


class TestMathInFunction:
    """Test using Math functions in graine functions."""

    def test_math_abs_in_function(self):
        """Test using Math.abs in a function."""
        with use_block() as block:

            @graine.define
            def absolute_value(x: graine.Number) -> graine.Number:
                return Math.abs(x)

            js = emit_javascript(block)

        assert "function absolute_value(x)" in js
        assert "return Math.abs(x)" in js

    def test_math_sqrt_in_function(self):
        """Test using Math.sqrt in a function."""
        with use_block() as block:

            @graine.define
            def square_root(x: graine.Number) -> graine.Number:
                return Math.sqrt(x)

            js = emit_javascript(block)

        assert "function square_root(x)" in js
        assert "return Math.sqrt(x)" in js

    def test_math_pow_in_function(self):
        """Test using Math.pow in a function."""
        with use_block() as block:

            @graine.define
            def power(base: graine.Number, exp: graine.Number) -> graine.Number:
                return Math.pow(base, exp)

            js = emit_javascript(block)

        assert "function power(base, exp)" in js
        assert "return Math.pow(base, exp)" in js

    def test_math_max_in_function(self):
        """Test using Math.max in a function."""
        with use_block() as block:

            @graine.define
            def maximum(a: graine.Number, b: graine.Number, c: graine.Number) -> graine.Number:
                return Math.max(a, b, c)

            js = emit_javascript(block)

        assert "function maximum(a, b, c)" in js
        assert "return Math.max(a, b, c)" in js

    def test_math_min_in_function(self):
        """Test using Math.min in a function."""
        with use_block() as block:

            @graine.define
            def minimum(a: graine.Number, b: graine.Number) -> graine.Number:
                return Math.min(a, b)

            js = emit_javascript(block)

        assert "function minimum(a, b)" in js
        assert "return Math.min(a, b)" in js

    def test_math_floor_ceil_round(self):
        """Test using Math.floor, ceil, and round functions."""
        with use_block() as block:

            @graine.define
            def rounding_operations(x: graine.Number) -> graine.Number:
                floored = Math.floor(x)
                ceiled = Math.ceil(x)
                rounded = Math.round(x)
                return floored + ceiled + rounded

            js = emit_javascript(block)

        assert "function rounding_operations(x)" in js
        assert "Math.floor(x)" in js
        assert "Math.ceil(x)" in js
        assert "Math.round(x)" in js

    def test_math_trigonometric(self):
        """Test using trigonometric functions."""
        with use_block() as block:

            @graine.define
            def calculate_sine(angle: graine.Number) -> graine.Number:
                return Math.sin(angle)

            js = emit_javascript(block)

        assert "function calculate_sine(angle)" in js
        assert "return Math.sin(angle)" in js

    def test_math_pi_constant(self):
        """Test using Math.PI constant."""
        with use_block() as block:

            @graine.define
            def circle_circumference(radius: graine.Number) -> graine.Number:
                pi = Math.PI
                return graine.literal(2) * pi * radius

            js = emit_javascript(block)

        assert "function circle_circumference(radius)" in js
        assert "Math.PI" in js
        assert "return ((2 * Math.PI) * radius)" in js

    def test_math_circle_area(self):
        """Test calculating circle area using Math.PI."""
        with use_block() as block:

            @graine.define
            def circle_area(radius: graine.Number) -> graine.Number:
                pi = Math.PI
                return pi * radius * radius

            js = emit_javascript(block)

        assert "function circle_area(radius)" in js
        assert "Math.PI" in js
        assert "return ((Math.PI * radius) * radius)" in js

    def test_math_pythagorean_theorem(self):
        """Test Pythagorean theorem using Math.sqrt and Math.pow."""
        with use_block() as block:

            @graine.define
            def pythagorean(a: graine.Number, b: graine.Number) -> graine.Number:
                a_squared = Math.pow(a, graine.literal(2))
                b_squared = Math.pow(b, graine.literal(2))
                c_squared = a_squared + b_squared
                return Math.sqrt(c_squared)

            js = emit_javascript(block)

        assert "function pythagorean(a, b)" in js
        assert "Math.pow(a, 2)" in js
        assert "Math.pow(b, 2)" in js
        assert "Math.sqrt" in js

    def test_math_random_in_function(self):
        """Test using Math.random in a function."""
        with use_block() as block:

            @graine.define
            def random_number() -> graine.Number:
                return Math.random()

            js = emit_javascript(block)

        assert "function random_number()" in js
        assert "return Math.random()" in js

    def test_math_exp_log(self):
        """Test using Math.exp and Math.log functions."""
        with use_block() as block:

            @graine.define
            def exp_and_log(x: graine.Number) -> graine.Number:
                exp_x = Math.exp(x)
                log_x = Math.log(x)
                return exp_x + log_x

            js = emit_javascript(block)

        assert "function exp_and_log(x)" in js
        assert "Math.exp(x)" in js
        assert "Math.log(x)" in js

    def test_math_sign_trunc(self):
        """Test using Math.sign and Math.trunc functions."""
        with use_block() as block:

            @graine.define
            def sign_and_trunc(x: graine.Number) -> graine.Number:
                sign = Math.sign(x)
                truncated = Math.trunc(x)
                return sign + truncated

            js = emit_javascript(block)

        assert "function sign_and_trunc(x)" in js
        assert "Math.sign(x)" in js
        assert "Math.trunc(x)" in js

    def test_math_with_getter_property(self):
        """Test using Math functions with getter properties."""
        with use_block() as block:

            @graine.define
            class Point:
                def __init__(self, x: graine.Number, y: graine.Number):
                    self.x = x
                    self.y = y

                @graine.getter
                def magnitude_squared(self) -> graine.Number:
                    return self.x * self.x + self.y * self.y

                @graine.getter
                def magnitude(self) -> graine.Number:
                    return Math.sqrt(self.magnitude_squared)

            js = emit_javascript(block)

        assert "class Point" in js
        assert "get magnitude_squared()" in js
        assert "get magnitude()" in js
        assert "return Math.sqrt(this.magnitude_squared)" in js

    def test_math_with_property_access(self):
        """Test using Math functions with property access (_GraineMethod)."""
        with use_block() as block:

            @graine.define
            class Rectangle:
                def __init__(self, width: graine.Number, height: graine.Number):
                    self.width = width
                    self.height = height

                @graine.getter
                def diagonal(self) -> graine.Number:
                    width_sq = self.width * self.width
                    height_sq = self.height * self.height
                    return Math.sqrt(width_sq + height_sq)

            js = emit_javascript(block)

        assert "class Rectangle" in js
        assert "get diagonal()" in js
        assert "Math.sqrt" in js

    def test_math_chained_with_getters(self):
        """Test chaining Math functions with getter results."""
        with use_block() as block:

            @graine.define
            class Vector:
                def __init__(self, x: graine.Number, y: graine.Number):
                    self.x = x
                    self.y = y

                @graine.getter
                def length_squared(self) -> graine.Number:
                    return self.x * self.x + self.y * self.y

                @graine.getter
                def length(self) -> graine.Number:
                    return Math.sqrt(self.length_squared)

                @graine.getter
                def rounded_length(self) -> graine.Number:
                    return Math.round(self.length)

            js = emit_javascript(block)

        assert "class Vector" in js
        assert "get length()" in js
        assert "Math.sqrt(this.length_squared)" in js
        assert "get rounded_length()" in js
        assert "Math.round(this.length)" in js
