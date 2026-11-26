# pyright: reportUnnecessaryTypeIgnoreComment=error
"""Check the public expression types and rejected inputs."""

from typing import assert_type

from fleur import Array, Expr, Model, Number, State, String, Url


class Values(Model):
    integers: State[list[int]]
    decimals: State[list[float]]
    strings: State[list[str]]
    text: State[str]


def valid_examples() -> None:
    assert_type(Array.length(Values.strings), Expr[int])
    assert_type(Array.sum(Values.integers), Expr[int])
    assert_type(Array.sum(Values.decimals), Expr[int | float])
    assert_type(Array.join(Values.strings, Values.text), Expr[str])
    assert_type(Number.from_string(Values.text), Expr[int | float])
    assert_type(Number.format(1234, locale=Values.text), Expr[str])
    assert_type(String.from_number(Number.from_string(Values.text)), Expr[str])
    assert_type(String.replace_all(Values.text, '"', '""'), Expr[str])
    assert_type(Url.encode_component(Values.text), Expr[str])


def invalid_examples() -> None:
    Array.sum(Values.strings)  # pyright: ignore[reportArgumentType, reportCallIssue]
    Array.join(Values.integers)  # pyright: ignore[reportArgumentType]
    Number.from_string(42)  # pyright: ignore[reportArgumentType]
    Number.format(Values.text)  # pyright: ignore[reportArgumentType]
    String.replace_all(Values.text, '"', 0)  # pyright: ignore[reportArgumentType]
    Url.encode_component(42)  # pyright: ignore[reportArgumentType]
