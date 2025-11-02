"""Integration tests for Graine standard library."""

import pytest
from py_mini_racer import MiniRacer

from fleur.dsl import graine, parterre, types


class TestWhenIntegration:
    """Integration tests for when() conditional expression."""

    @staticmethod
    def test_when_with_then_and_otherwise(jsctx: MiniRacer):
        """Test when() with both then and otherwise branches."""
        with parterre() as p:

            @graine.func
            def check_value(x: types.GraineNumber):
                return graine.when(
                    x == 10,
                    then=graine.string("equal"),
                    otherwise=graine.string("not equal"),
                )

        js_code = p.germinate()
        jsctx.eval(js_code)
        assert jsctx.call("check_value", 10) == "equal"
        assert jsctx.call("check_value", 5) == "not equal"

    @staticmethod
    def test_when_without_otherwise(jsctx: MiniRacer):
        """Test when() without otherwise branch (returns undefined)."""
        with parterre() as p:

            @graine.func
            def check_positive(x: types.GraineNumber):
                result = graine.when(x == 10, then=graine.string("ten"))
                return graine.when(
                    graine.typeof(result) == "undefined",
                    then=graine.string("undefined"),
                    otherwise=result,
                )

        js_code = p.germinate()
        jsctx.eval(js_code)
        assert jsctx.call("check_positive", 10) == "ten"
        assert jsctx.call("check_positive", 5) == "undefined"


class TestCaseIntegration:
    """Integration tests for case() conditional decorator."""

    @staticmethod
    def test_case_single_condition(jsctx: MiniRacer):
        """Test case() with a single condition."""
        with parterre() as p:

            @graine.func
            def classify_number(x: types.GraineNumber):
                @graine.case(x == 0)
                def zero():
                    return graine.string("zero")

                @graine.case(x == 10)
                def positive():
                    return graine.string("ten")

                return graine.string("other")

        js_code = p.germinate()
        jsctx.eval(js_code)
        assert jsctx.call("classify_number", 0) == "zero"
        assert jsctx.call("classify_number", 10) == "ten"
        assert jsctx.call("classify_number", 5) == "other"


class TestCasesIntegration:
    """Integration tests for cases() context manager."""

    @staticmethod
    def test_cases_multiple_conditions(jsctx: MiniRacer):
        """Test cases() with multiple when conditions."""
        with parterre() as p:

            @graine.func
            def classify_number(x: types.GraineNumber):
                with graine.cases() as c:
                    @c.when(x == 0)
                    def zero():
                        return graine.string("zero")

                    @c.when(x == -5)
                    def negative():
                        return graine.string("negative")

                    @c.when(x == 10)
                    def positive():
                        return graine.string("positive")

                return graine.string("unreachable")

        js_code = p.germinate()
        jsctx.eval(js_code)
        assert jsctx.call("classify_number", 0) == "zero"
        assert jsctx.call("classify_number", -5) == "negative"
        assert jsctx.call("classify_number", 10) == "positive"

    @staticmethod
    def test_cases_with_otherwise(jsctx: MiniRacer):
        """Test cases() with otherwise clause."""
        with parterre() as p:

            @graine.func
            def grade_score(score: types.GraineNumber):
                with graine.cases() as c:
                    @c.when(score == 95)
                    def excellent():
                        return graine.string("A")

                    @c.when(score == 85)
                    def good():
                        return graine.string("B")

                    @c.when(score == 75)
                    def fair():
                        return graine.string("C")

                    @c.otherwise
                    def failing():
                        return graine.string("F")

                return graine.string("unreachable")

        js_code = p.germinate()
        jsctx.eval(js_code)
        assert jsctx.call("grade_score", 95) == "A"
        assert jsctx.call("grade_score", 85) == "B"
        assert jsctx.call("grade_score", 75) == "C"
        assert jsctx.call("grade_score", 60) == "F"

    @staticmethod
    def test_cases_without_return(jsctx: MiniRacer):
        """Test cases() for side effects without return values."""
        with parterre() as p:

            @graine.func
            def classify_and_store(x: types.GraineNumber):
                state = graine.record(result=graine.string("none"))

                with graine.cases() as c:
                    @c.when(x == 0)
                    def zero():
                        state.result = graine.string("zero")  # pyright: ignore[reportAttributeAccessIssue]

                    @c.when(x == -1)
                    def negative():
                        state.result = graine.string("negative")  # pyright: ignore[reportAttributeAccessIssue]

                    @c.otherwise
                    def positive():
                        state.result = graine.string("positive")  # pyright: ignore[reportAttributeAccessIssue]

                return state.result  # pyright: ignore[reportAttributeAccessIssue]

        js_code = p.germinate()
        jsctx.eval(js_code)
        assert jsctx.call("classify_and_store", 0) == "zero"
        assert jsctx.call("classify_and_store", -1) == "negative"
        assert jsctx.call("classify_and_store", 5) == "positive"

    @staticmethod
    def test_cases_with_python_boolean(jsctx: MiniRacer):
        """Test cases() with Python boolean conditions."""
        with parterre() as p:

            @graine.func
            def check_constant():
                with graine.cases() as c:
                    @c.when(False)
                    def first():
                        return graine.string("first")

                    @c.when(True)
                    def second():
                        return graine.string("second")

                return graine.string("unreachable")

        js_code = p.germinate()
        jsctx.eval(js_code)
        assert jsctx.call("check_constant") == "second"

    @staticmethod
    def test_cases_only_otherwise(jsctx: MiniRacer):
        """Test cases() with only otherwise clause."""
        with parterre() as p:

            @graine.func
            def always_return():
                with graine.cases() as c:
                    @c.otherwise
                    def default():
                        return graine.string("default")

                return graine.string("unreachable")

        js_code = p.germinate()
        jsctx.eval(js_code)
        assert jsctx.call("always_return") == "default"

    @staticmethod
    def test_cases_fallthrough_behavior(jsctx: MiniRacer):
        """Test that cases() evaluates conditions in order and stops at first match."""
        with parterre() as p:

            @graine.func
            def test_order(x: types.GraineNumber):
                state = graine.record(matched=graine.string("none"))

                with graine.cases() as c:
                    @c.when(x == 10)
                    def first():
                        state.matched = graine.string("first")  # pyright: ignore[reportAttributeAccessIssue]
                        return graine.string("first")

                    @c.when(x == 3)
                    def second():
                        state.matched = graine.string("second")  # pyright: ignore[reportAttributeAccessIssue]
                        return graine.string("second")

                return state.matched  # pyright: ignore[reportAttributeAccessIssue]

        js_code = p.germinate()
        jsctx.eval(js_code)
        # When x=10, it matches first condition and should return "first"
        assert jsctx.call("test_order", 10) == "first"
        # When x=3, it doesn't match first but matches second
        assert jsctx.call("test_order", 3) == "second"
        # When x=-1, it matches neither
        assert jsctx.call("test_order", -1) == "none"


class TestForeachIntegration:
    """Integration tests for foreach() loop."""

    @staticmethod
    def test_foreach_iterate_array(jsctx: MiniRacer):
        """Test foreach() to iterate over an array."""
        with parterre() as p:

            @graine.func
            def sum_array():
                arr = graine.array(1, 2, 3, 4, 5)
                state = graine.record(total=graine.number(0))

                @graine.foreach(arr)
                def process(item):
                    state.total = state.total + item  # pyright: ignore[reportAttributeAccessIssue]

                return state.total  # pyright: ignore[reportAttributeAccessIssue]

        js_code = p.germinate()
        jsctx.eval(js_code)
        result = jsctx.call("sum_array")
        assert result == 15

    @staticmethod
    def test_foreach_with_strings(jsctx: MiniRacer):
        """Test foreach() to iterate over string array."""
        with parterre() as p:

            @graine.func
            def concatenate_strings():
                words = graine.array("Hello", " ", "World", "!")
                state = graine.record(result=graine.string(""))

                @graine.foreach(words)
                def process(word):
                    state.result = state.result + word  # pyright: ignore[reportAttributeAccessIssue]

                return state.result  # pyright: ignore[reportAttributeAccessIssue]

        js_code = p.germinate()
        jsctx.eval(js_code)
        result = jsctx.call("concatenate_strings")
        assert result == "Hello World!"


class TestTypeofIntegration:
    """Integration tests for typeof operator."""

    @staticmethod
    def test_typeof_number(jsctx: MiniRacer):
        """Test typeof with number."""
        with parterre() as p:

            @graine.func
            def get_type():
                x = graine.number(42)
                return graine.typeof(x)

        js_code = p.germinate()
        jsctx.eval(js_code)
        assert jsctx.call("get_type") == "number"

    @staticmethod
    def test_typeof_string(jsctx: MiniRacer):
        """Test typeof with string."""
        with parterre() as p:

            @graine.func
            def get_type():
                x = graine.string("hello")
                return graine.typeof(x)

        js_code = p.germinate()
        jsctx.eval(js_code)
        assert jsctx.call("get_type") == "string"


class TestInstanceofIntegration:
    """Integration tests for instanceof operator."""

    @staticmethod
    def test_instanceof_with_class(jsctx: MiniRacer):
        """Test instanceof with a custom class."""
        with parterre() as p:

            @graine.cls
            class Point:
                def __init__(self, x: types.GraineNumber, y: types.GraineNumber):
                    self.x = x
                    self.y = y

            @graine.func
            def check_instance():
                p = Point(graine.number(1), graine.number(2))
                return graine.instanceof(p, Point)  # pyright: ignore[reportArgumentType]

        js_code = p.germinate()
        jsctx.eval(js_code)
        assert jsctx.call("check_instance") is True


class TestMathIntegration:
    """Integration tests for Math module."""

    @staticmethod
    def test_math_sqrt(jsctx: MiniRacer):
        """Test Math.sqrt()."""
        with parterre() as p:

            @graine.func
            def calculate_sqrt():
                return graine.math.sqrt(graine.number(16))

        js_code = p.germinate()
        jsctx.eval(js_code)
        assert jsctx.call("calculate_sqrt") == 4

    @staticmethod
    def test_math_sqrt_with_python_number(jsctx: MiniRacer):
        """Test Math.sqrt() with Python number."""
        with parterre() as p:

            @graine.func
            def calculate_sqrt():
                return graine.math.sqrt(25)

        js_code = p.germinate()
        jsctx.eval(js_code)
        assert jsctx.call("calculate_sqrt") == 5


class TestJSONIntegration:
    """Integration tests for JSON module."""

    @staticmethod
    def test_json_stringify(jsctx: MiniRacer):
        """Test JSON.stringify()."""
        with parterre() as p:

            @graine.func
            def stringify_object():
                obj = graine.record(name=graine.string("Alice"), age=graine.number(30))
                return graine.json.stringify(obj)

        js_code = p.germinate()
        jsctx.eval(js_code)
        result = jsctx.call("stringify_object")
        assert result == '{"name":"Alice","age":30}'

    @staticmethod
    def test_json_stringify_array(jsctx: MiniRacer):
        """Test JSON.stringify() with array."""
        with parterre() as p:

            @graine.func
            def stringify_array():
                arr = graine.array(1, 2, 3)
                return graine.json.stringify(arr)

        js_code = p.germinate()
        jsctx.eval(js_code)
        result = jsctx.call("stringify_array")
        assert result == "[1,2,3]"

    @staticmethod
    def test_json_parse(jsctx: MiniRacer):
        """Test JSON.parse()."""
        with parterre() as p:

            @graine.func
            def parse_string():
                json_str = graine.string('{"x":100,"y":200}')
                obj = graine.json.parse(json_str)
                return obj.x  # pyright: ignore[reportAttributeAccessIssue]

        js_code = p.germinate()
        jsctx.eval(js_code)
        result = jsctx.call("parse_string")
        assert result == 100

    @staticmethod
    def test_json_parse_with_python_string(jsctx: MiniRacer):
        """Test JSON.parse() with Python string."""
        with parterre() as p:

            @graine.func
            def parse_string():
                obj = graine.json.parse('{"value":42}')
                return obj.value  # pyright: ignore[reportAttributeAccessIssue]

        js_code = p.germinate()
        jsctx.eval(js_code)
        result = jsctx.call("parse_string")
        assert result == 42


@pytest.mark.skip(reason="Document API requires browser/Node.js environment, not available in MiniRacer")
class TestDocumentIntegration:
    """Integration tests for Document API."""

    @staticmethod
    def test_document_create_element(jsctx: MiniRacer):
        """Test document.createElement()."""
        with parterre() as p:

            @graine.func
            def create_div():
                elem = graine.document.createElement(graine.string("div"))
                return graine.typeof(elem)

        js_code = p.germinate()
        jsctx.eval(js_code)
        result = jsctx.call("create_div")
        assert result == "object"

    @staticmethod
    def test_document_create_text_node(jsctx: MiniRacer):
        """Test document.createTextNode()."""
        with parterre() as p:

            @graine.func
            def create_text():
                text = graine.document.createTextNode(graine.string("Hello"))
                return text.data  # pyright: ignore[reportAttributeAccessIssue]

        js_code = p.germinate()
        jsctx.eval(js_code)
        result = jsctx.call("create_text")
        assert result == "Hello"

    @staticmethod
    def test_element_set_and_get_attribute(jsctx: MiniRacer):
        """Test Element setAttribute and getAttribute."""
        with parterre() as p:

            @graine.func
            def test_attributes():
                elem = graine.document.createElement(graine.string("div"))
                elem.setAttribute(graine.string("id"), graine.string("myDiv"))
                return elem.getAttribute(graine.string("id"))

        js_code = p.germinate()
        jsctx.eval(js_code)
        result = jsctx.call("test_attributes")
        assert result == "myDiv"

    @staticmethod
    def test_element_append_child(jsctx: MiniRacer):
        """Test Element appendChild."""
        with parterre() as p:

            @graine.func
            def test_append():
                parent = graine.document.createElement(graine.string("div"))
                child = graine.document.createElement(graine.string("span"))
                parent.appendChild(child)
                return parent.childNodes.length

        js_code = p.germinate()
        jsctx.eval(js_code)
        result = jsctx.call("test_append")
        assert result == 1
