"""Integration tests for Array and Record types."""

import pytest
from py_mini_racer import MiniRacer

from fleur.dsl import graine, parterre


class TestArrayIntegration:
    """Integration tests for Array type."""

    @pytest.fixture
    def ctx(self):
        """Create a fresh JavaScript context."""
        return MiniRacer()

    def test_array_literal(self, ctx):
        """Test creating and accessing array literal."""
        with parterre() as p:

            @graine.define
            def get_first(arr: graine.Array) -> graine.Number:
                return arr[0]  # type: ignore[return-value]

        js_code = p.germinate()
        ctx.eval(js_code)

        result = ctx.call("get_first", [10, 20, 30])
        assert result == 10

    def test_array_index_with_number(self, ctx):
        """Test accessing array with Number index."""
        with parterre() as p:

            @graine.define
            def get_element(arr: graine.Array, idx: graine.Number) -> graine.Number:
                return arr[idx]  # type: ignore[return-value]

        js_code = p.germinate()
        ctx.eval(js_code)

        result = ctx.call("get_element", [10, 20, 30], 1)
        assert result == 20

    def test_array_literal_creation(self, ctx):
        """Test creating array with graine.literal."""
        with parterre() as p:

            @graine.define
            def create_array() -> graine.Array:
                return graine.literal([1, 2, 3])  # pyright: ignore[reportReturnType]

        js_code = p.germinate()
        ctx.eval(js_code)

        result = ctx.call("create_array")
        assert result == [1, 2, 3]


class TestRecordIntegration:
    """Integration tests for Record type."""

    @pytest.fixture
    def ctx(self):
        """Create a fresh JavaScript context."""
        return MiniRacer()

    def test_record_property_access(self, ctx):
        """Test accessing record properties."""
        with parterre() as p:

            @graine.define
            def get_name(person: graine.Record) -> graine.String:
                return person.name  # type: ignore[return-value]

        js_code = p.germinate()
        ctx.eval(js_code)

        result = ctx.call("get_name", {"name": "Alice", "age": 30})
        assert result == "Alice"

    def test_record_literal_creation(self, ctx):
        """Test creating record with graine.literal."""
        with parterre() as p:

            @graine.define
            def create_person() -> graine.Record:
                return graine.literal({"name": "Bob", "age": 25})  # pyright: ignore[reportReturnType]

        js_code = p.germinate()
        ctx.eval(js_code)

        result = ctx.call("create_person")
        assert result == {"name": "Bob", "age": 25}

    def test_nested_access(self, ctx):
        """Test nested record and array access."""
        with parterre() as p:

            @graine.define
            def get_first_friend_name(person: graine.Record) -> graine.String:
                friends = person.friends
                first_friend = friends[0]
                return first_friend.name  # type: ignore[return-value]

        js_code = p.germinate()
        ctx.eval(js_code)

        person_data = {"name": "Alice", "friends": [{"name": "Bob"}, {"name": "Charlie"}]}
        result = ctx.call("get_first_friend_name", person_data)
        assert result == "Bob"
