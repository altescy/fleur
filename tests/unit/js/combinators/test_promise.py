from fleur.js.builder import ident
from fleur.js.combinators import Promise, TaskValueRef
from fleur.js.emitter import emit


def test_promise_then_compiles_mapper_function() -> None:
    promise = Promise[object, object, TaskValueRef[object]](
        ident("promise"),
        value_ref_factory=lambda expr: TaskValueRef(expr),
    )

    mapped = promise.then(lambda value: value)
    source = emit(mapped.__compile__())

    assert "promise.then" in source
    assert "function(value) {return value;}" in source
