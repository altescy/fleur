"""Integration tests for standard library functions with JavaScript runtime execution."""

import pytest
from py_mini_racer import MiniRacer

from fleur.dsl import graine, parterre


class TestMathRuntime:
    """Test Math functions with actual JavaScript execution."""

    @pytest.fixture
    def ctx(self):
        """Create a fresh JavaScript context."""
        return MiniRacer()

    def test_math_abs(self, ctx):
        """Test Math.abs function execution."""
        with parterre() as p:

            @graine.define
            def test_abs(x: graine.Number) -> graine.Number:
                return graine.math.abs(x)

        js_code = p.germinate()
        ctx.eval(js_code)

        assert ctx.call("test_abs", -5) == 5
        assert ctx.call("test_abs", 3) == 3
        assert ctx.call("test_abs", 0) == 0

    def test_math_sqrt(self, ctx):
        """Test Math.sqrt function execution."""
        with parterre() as p:

            @graine.define
            def test_sqrt(x: graine.Number) -> graine.Number:
                return graine.math.sqrt(x)

        js_code = p.germinate()
        ctx.eval(js_code)

        assert ctx.call("test_sqrt", 16) == 4
        assert ctx.call("test_sqrt", 9) == 3
        assert ctx.call("test_sqrt", 4) == 2

    def test_math_pow(self, ctx):
        """Test Math.pow function execution."""
        with parterre() as p:

            @graine.define
            def test_pow(base: graine.Number, exp: graine.Number) -> graine.Number:
                return graine.math.pow(base, exp)

        js_code = p.germinate()
        ctx.eval(js_code)

        assert ctx.call("test_pow", 2, 3) == 8
        assert ctx.call("test_pow", 3, 2) == 9
        assert ctx.call("test_pow", 5, 0) == 1

    def test_math_max(self, ctx):
        """Test Math.max function execution."""
        with parterre() as p:

            @graine.define
            def test_max(a: graine.Number, b: graine.Number, c: graine.Number) -> graine.Number:
                return graine.math.max(a, b, c)

        js_code = p.germinate()
        ctx.eval(js_code)

        assert ctx.call("test_max", 1, 5, 3) == 5
        assert ctx.call("test_max", 10, 2, 7) == 10
        assert ctx.call("test_max", -1, -5, -3) == -1

    def test_math_min(self, ctx):
        """Test Math.min function execution."""
        with parterre() as p:

            @graine.define
            def test_min(a: graine.Number, b: graine.Number) -> graine.Number:
                return graine.math.min(a, b)

        js_code = p.germinate()
        ctx.eval(js_code)

        assert ctx.call("test_min", 5, 3) == 3
        assert ctx.call("test_min", 10, 2) == 2
        assert ctx.call("test_min", -1, -5) == -5

    def test_math_floor(self, ctx):
        """Test Math.floor function execution."""
        with parterre() as p:

            @graine.define
            def test_floor(x: graine.Number) -> graine.Number:
                return graine.math.floor(x)

        js_code = p.germinate()
        ctx.eval(js_code)

        assert ctx.call("test_floor", 4.9) == 4
        assert ctx.call("test_floor", 4.1) == 4
        assert ctx.call("test_floor", -4.1) == -5

    def test_math_ceil(self, ctx):
        """Test Math.ceil function execution."""
        with parterre() as p:

            @graine.define
            def test_ceil(x: graine.Number) -> graine.Number:
                return graine.math.ceil(x)

        js_code = p.germinate()
        ctx.eval(js_code)

        assert ctx.call("test_ceil", 4.1) == 5
        assert ctx.call("test_ceil", 4.9) == 5
        assert ctx.call("test_ceil", -4.9) == -4

    def test_math_round(self, ctx):
        """Test Math.round function execution."""
        with parterre() as p:

            @graine.define
            def test_round(x: graine.Number) -> graine.Number:
                return graine.math.round(x)

        js_code = p.germinate()
        ctx.eval(js_code)

        assert ctx.call("test_round", 4.5) == 5
        assert ctx.call("test_round", 4.4) == 4
        assert ctx.call("test_round", 4.6) == 5

    def test_math_pi(self, ctx):
        """Test Math.PI constant."""
        with parterre() as p:

            @graine.define
            def circle_area(radius: graine.Number) -> graine.Number:
                pi = graine.math.PI
                return pi * radius * radius

        js_code = p.germinate()
        ctx.eval(js_code)

        # Area of circle with radius 1 should be approximately PI
        result = ctx.call("circle_area", 1)
        assert abs(result - 3.141592653589793) < 0.0001

        # Area of circle with radius 2 should be approximately 4*PI
        result = ctx.call("circle_area", 2)
        assert abs(result - 12.566370614359172) < 0.0001

    def test_pythagorean_theorem(self, ctx):
        """Test Pythagorean theorem using Math.sqrt and Math.pow."""
        with parterre() as p:

            @graine.define
            def pythagorean(a: graine.Number, b: graine.Number) -> graine.Number:
                a_squared = graine.math.pow(a, graine.literal(2))
                b_squared = graine.math.pow(b, graine.literal(2))
                c_squared = a_squared + b_squared
                return graine.math.sqrt(c_squared)

        js_code = p.germinate()
        ctx.eval(js_code)

        # 3-4-5 triangle
        assert ctx.call("pythagorean", 3, 4) == 5
        # 5-12-13 triangle
        assert ctx.call("pythagorean", 5, 12) == 13
        # 8-15-17 triangle
        assert ctx.call("pythagorean", 8, 15) == 17

    def test_math_trigonometric(self, ctx):
        """Test trigonometric functions."""
        with parterre() as p:

            @graine.define
            def test_sin(x: graine.Number) -> graine.Number:
                return graine.math.sin(x)

            @graine.define
            def test_cos(x: graine.Number) -> graine.Number:
                return graine.math.cos(x)

        js_code = p.germinate()
        ctx.eval(js_code)

        # sin(0) should be 0
        assert abs(ctx.call("test_sin", 0)) < 0.0001
        # cos(0) should be 1
        assert abs(ctx.call("test_cos", 0) - 1) < 0.0001

    def test_math_exp_log(self, ctx):
        """Test Math.exp and Math.log functions."""
        with parterre() as p:

            @graine.define
            def exp_log_identity(x: graine.Number) -> graine.Number:
                # log(exp(x)) should equal x
                exp_x = graine.math.exp(x)
                return graine.math.log(exp_x)

        js_code = p.germinate()
        ctx.eval(js_code)

        # Test with various values
        assert abs(ctx.call("exp_log_identity", 1) - 1) < 0.0001
        assert abs(ctx.call("exp_log_identity", 2) - 2) < 0.0001
        assert abs(ctx.call("exp_log_identity", 0.5) - 0.5) < 0.0001

    def test_math_sign(self, ctx):
        """Test Math.sign function."""
        with parterre() as p:

            @graine.define
            def test_sign(x: graine.Number) -> graine.Number:
                return graine.math.sign(x)

        js_code = p.germinate()
        ctx.eval(js_code)

        assert ctx.call("test_sign", 5) == 1
        assert ctx.call("test_sign", -5) == -1
        assert ctx.call("test_sign", 0) == 0

    def test_math_trunc(self, ctx):
        """Test Math.trunc function."""
        with parterre() as p:

            @graine.define
            def test_trunc(x: graine.Number) -> graine.Number:
                return graine.math.trunc(x)

        js_code = p.germinate()
        ctx.eval(js_code)

        assert ctx.call("test_trunc", 4.9) == 4
        assert ctx.call("test_trunc", 4.1) == 4
        assert ctx.call("test_trunc", -4.9) == -4
        assert ctx.call("test_trunc", -4.1) == -4

    def test_math_random_range(self, ctx):
        """Test that Math.random returns values in [0, 1) range."""
        with parterre() as p:

            @graine.define
            def get_random() -> graine.Number:
                return graine.math.random()

        js_code = p.germinate()
        ctx.eval(js_code)

        # Test multiple times to ensure randomness
        for _ in range(10):
            result = ctx.call("get_random")
            assert 0 <= result < 1

    def test_complex_calculation(self, ctx):
        """Test a complex calculation using multiple Math functions."""
        with parterre() as p:

            @graine.define
            def distance_from_origin(x: graine.Number, y: graine.Number) -> graine.Number:
                # Calculate distance using sqrt(x^2 + y^2), then round it
                x_squared = graine.math.pow(x, graine.literal(2))
                y_squared = graine.math.pow(y, graine.literal(2))
                distance = graine.math.sqrt(x_squared + y_squared)
                return graine.math.round(distance)

        js_code = p.germinate()
        ctx.eval(js_code)

        assert ctx.call("distance_from_origin", 3, 4) == 5
        assert ctx.call("distance_from_origin", 5, 12) == 13

    def test_math_with_getter(self, ctx):
        """Test Math functions with getter properties."""
        with parterre() as p:

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
                    return graine.math.sqrt(self.magnitude_squared)

            @graine.define
            def get_magnitude(x: graine.Number, y: graine.Number) -> graine.Number:
                p = Point(x, y)
                return p.magnitude

        js_code = p.germinate()
        ctx.eval(js_code)

        # Test 3-4-5 triangle
        result = ctx.call("get_magnitude", 3, 4)
        assert result == 5

        # Test 5-12-13 triangle
        result = ctx.call("get_magnitude", 5, 12)
        assert result == 13

    def test_math_chained_getters(self, ctx):
        """Test chaining Math functions through getters."""
        with parterre() as p:

            @graine.define
            class Circle:
                def __init__(self, radius: graine.Number):
                    self.radius = radius

                @graine.getter
                def diameter(self) -> graine.Number:
                    return self.radius * graine.literal(2)

                @graine.getter
                def circumference(self) -> graine.Number:
                    return graine.math.PI * self.diameter

                @graine.getter
                def area(self) -> graine.Number:
                    return graine.math.PI * graine.math.pow(self.radius, graine.literal(2))

            @graine.define
            def calculate_circle_properties(r: graine.Number) -> graine.Number:
                c = Circle(r)
                # Return rounded area
                return graine.math.round(c.area)

        js_code = p.germinate()
        ctx.eval(js_code)

        # Circle with radius 5: area = π * 25 ≈ 78.54
        result = ctx.call("calculate_circle_properties", 5)
        assert result == 79

        # Circle with radius 10: area = π * 100 ≈ 314.16
        result = ctx.call("calculate_circle_properties", 10)
        assert result == 314

    def test_math_with_property_access(self, ctx):
        """Test Math functions with property access in getters."""
        with parterre() as p:

            @graine.define
            class Rectangle:
                def __init__(self, width: graine.Number, height: graine.Number):
                    self.width = width
                    self.height = height

                @graine.getter
                def diagonal(self) -> graine.Number:
                    # Use property access (self.width, self.height) in Math functions
                    w_sq = graine.math.pow(self.width, graine.literal(2))
                    h_sq = graine.math.pow(self.height, graine.literal(2))
                    return graine.math.sqrt(w_sq + h_sq)

            @graine.define
            def get_diagonal(w: graine.Number, h: graine.Number) -> graine.Number:
                rect = Rectangle(w, h)
                return rect.diagonal

        js_code = p.germinate()
        ctx.eval(js_code)

        # Rectangle 3x4: diagonal = 5
        assert ctx.call("get_diagonal", 3, 4) == 5

        # Rectangle 5x12: diagonal = 13
        assert ctx.call("get_diagonal", 5, 12) == 13

    def test_math_nested_getters(self, ctx):
        """Test deeply nested getter calls with Math functions."""
        with parterre() as p:

            @graine.define
            class Vector3D:
                def __init__(self, x: graine.Number, y: graine.Number, z: graine.Number):
                    self.x = x
                    self.y = y
                    self.z = z

                @graine.getter
                def xy_magnitude(self) -> graine.Number:
                    return graine.math.sqrt(self.x * self.x + self.y * self.y)

                @graine.getter
                def magnitude(self) -> graine.Number:
                    # Use xy_magnitude (getter) in Math.pow
                    xy_sq = graine.math.pow(self.xy_magnitude, graine.literal(2))
                    z_sq = graine.math.pow(self.z, graine.literal(2))
                    return graine.math.sqrt(xy_sq + z_sq)

                @graine.getter
                def normalized_magnitude(self) -> graine.Number:
                    # Use magnitude (getter) in Math.round
                    return graine.math.round(self.magnitude)

            @graine.define
            def get_normalized_magnitude(x: graine.Number, y: graine.Number, z: graine.Number) -> graine.Number:
                v = Vector3D(x, y, z)
                return v.normalized_magnitude

        js_code = p.germinate()
        ctx.eval(js_code)

        # Vector (2, 3, 6): magnitude = sqrt(4 + 9 + 36) = sqrt(49) = 7
        assert ctx.call("get_normalized_magnitude", 2, 3, 6) == 7

        # Vector (1, 2, 2): magnitude = sqrt(1 + 4 + 4) = sqrt(9) = 3
        assert ctx.call("get_normalized_magnitude", 1, 2, 2) == 3
