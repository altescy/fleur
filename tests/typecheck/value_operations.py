# pyright: reportUnnecessaryTypeIgnoreComment=error
"""Check the public expression types and rejected inputs."""

from typing import Literal, assert_type

from fleur import Array, Cond, Expr, Model, ModelUpdate, Number, State, String, Url

Variant = Literal["success", "error"]


class Values(Model):
    integers: State[list[int]]
    decimals: State[list[float]]
    strings: State[list[str]]
    text: State[str]
    ok: State[bool]
    variant: State[Variant]


def valid_examples(values: Values) -> None:
    assert_type(Array.length(values.strings), Expr[int])
    assert_type(Array.sum(values.integers), Expr[int])
    assert_type(Array.sum(values.decimals), Expr[int | float])
    assert_type(Array.join(values.strings, values.text), Expr[str])
    assert_type(Number.from_string(values.text), Expr[int | float])
    assert_type(Number.format(1234, locale=values.text), Expr[str])
    assert_type(String.from_number(Number.from_string(values.text)), Expr[str])
    assert_type(String.replace_all(values.text, '"', '""'), Expr[str])
    assert_type(Url.encode_component(values.text), Expr[str])
    # Literal branches keep their type where a literal is expected, as for a `Literal` field.
    assert_type(State.set(Values.variant, Cond.when(values.ok, "success", "error")), ModelUpdate[Values])
    assert_type(Cond.when(values.ok, 1, "one"), Expr[int | str])


def invalid_examples(values: Values) -> None:
    Array.sum(values.strings)  # pyright: ignore[reportArgumentType, reportCallIssue]
    Array.join(values.integers)  # pyright: ignore[reportArgumentType]
    Number.from_string(42)  # pyright: ignore[reportArgumentType]
    Number.format(values.text)  # pyright: ignore[reportArgumentType]
    String.replace_all(values.text, '"', 0)  # pyright: ignore[reportArgumentType]
    Url.encode_component(42)  # pyright: ignore[reportArgumentType]
    State.set(Values.variant, Cond.when(values.ok, "success", "failure"))  # pyright: ignore[reportArgumentType]
    # A field is a write target, so a `str` does not fit a field of literals.
    State.set(Values.variant, values.text)  # pyright: ignore[reportArgumentType]
