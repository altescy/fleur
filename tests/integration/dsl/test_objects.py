"""Integration tests for Graine objects."""

from py_mini_racer import MiniRacer

from fleur.dsl import graine, parterre, types


class TestGraineNumberIntegration:
    """Integration tests for Array type."""

    @staticmethod
    def test_number_addition(jsctx: MiniRacer):
        """Test addition of two Graine numbers."""
        with parterre() as p:

            @graine.func
            def get_result():
                a = graine.number(42)
                b = graine.number(58)
                return a + b

        js_code = p.germinate()
        jsctx.eval(js_code)
        result = jsctx.call("get_result")
        assert result == 100


class TestGraineStringIntegration:
    """Integration tests for String type."""

    @staticmethod
    def test_string_concatenation(jsctx: MiniRacer):
        """Test concatenation of two Graine strings."""
        with parterre() as p:

            @graine.func
            def get_result():
                str1 = graine.string("Hello, ")
                str2 = graine.string("World!")
                return str1 + str2

        js_code = p.germinate()
        jsctx.eval(js_code)
        result = jsctx.call("get_result")
        assert result == "Hello, World!"

    @staticmethod
    def test_string_length(jsctx: MiniRacer):
        """Test length property of a Graine string."""
        with parterre() as p:

            @graine.func
            def get_length():
                s = graine.string("Graine")
                return s.length

        js_code = p.germinate()
        jsctx.eval(js_code)
        result = jsctx.call("get_length")
        assert result == 6

    @staticmethod
    def test_string_indexing(jsctx: MiniRacer):
        """Test indexing of a Graine string."""
        with parterre() as p:

            @graine.func
            def get_char():
                s = graine.string("Graine")
                return s[2]

        js_code = p.germinate()
        jsctx.eval(js_code)
        result = jsctx.call("get_char")
        assert result == "a"


class TestGraineArrayIntegration:
    """Integration tests for Array type."""

    @staticmethod
    def test_array_length(jsctx: MiniRacer):
        """Test length property of a Graine array."""
        with parterre() as p:

            @graine.func
            def get_length():
                arr = graine.array(1.0, 2.0, 3.0)
                return arr.length

        js_code = p.germinate()
        jsctx.eval(js_code)
        result = jsctx.call("get_length")
        assert result == 3


class TestGraineRecordIntegration:
    """Integration tests for Record type."""

    @staticmethod
    def test_record_creation(jsctx: MiniRacer):
        """Test creation of a Graine record."""
        with parterre() as p:

            @graine.func
            def get_record():
                return graine.record(name=graine.string("Alice"), age=graine.number(30))

        js_code = p.germinate()
        jsctx.eval(js_code)
        result = jsctx.call("get_record")
        assert result == {"name": "Alice", "age": 30}

    @staticmethod
    def test_record_property_access(jsctx: MiniRacer):
        """Test property access on a Graine record."""
        with parterre() as p:

            @graine.func
            def get_name():
                rec = graine.record(name=graine.string("Bob"), age=graine.number(25))
                return rec.name

        js_code = p.germinate()
        jsctx.eval(js_code)
        result = jsctx.call("get_name")
        assert result == "Bob"

    @staticmethod
    def test_record_property_access_by_indexing(jsctx: MiniRacer):
        """Test property access on a Graine record."""
        with parterre() as p:

            @graine.func
            def get_name():
                rec = graine.record(name=graine.string("Bob"), age=graine.number(25))
                return rec["name"]

        js_code = p.germinate()
        jsctx.eval(js_code)
        result = jsctx.call("get_name")
        assert result == "Bob"

    @staticmethod
    def test_record_from_python(jsctx: MiniRacer):
        """Test creation of a Graine record from Python dict."""
        with parterre() as p:

            @graine.func
            def get_record():
                return graine.from_python({"x": 100, "y": 200})

        js_code = p.germinate()
        jsctx.eval(js_code)
        result = jsctx.call("get_record")
        assert result == {"x": 100, "y": 200}


class TestGraineClassIntegration:
    """Integration tests for Graine classes."""

    @staticmethod
    def test_class_basic_instantiation(jsctx: MiniRacer):
        """Test instantiation of a Graine class."""

        with parterre() as p:

            @graine.cls
            class Point:
                def __init__(self, x: types.GraineNumber, y: types.GraineNumber):
                    self.x = x
                    self.y = y

                def get_coordinates(self):
                    return graine.array(self.x, self.y)

            @graine.func
            def create_point_and_get_coordinates():
                return Point(graine.number(10), graine.number(20)).get_coordinates()

        js_code = p.germinate()
        jsctx.eval(js_code)
        result = jsctx.call("create_point_and_get_coordinates")
        assert result == [10, 20]

    def test_class_with_getter_and_setter(self, jsctx: MiniRacer):
        """Test Graine class with getter and setter."""

        with parterre() as p:

            @graine.cls
            class Counter:
                def __init__(self):
                    self._count = graine.number(0)

                @property
                def count(self) -> types.GraineNumber:
                    return self._count

                @count.setter
                def count(self, value: types.GraineNumber):
                    self._count = value

                def increment(self):
                    self.count = self.count + graine.number(1)

            @graine.func
            def use_counter():
                counter = Counter()
                counter.count = graine.number(10)
                counter.increment()
                counter.increment()
                return counter.count

        js_code = p.germinate()
        jsctx.eval(js_code)
        result = jsctx.call("use_counter")
        assert result == 12
