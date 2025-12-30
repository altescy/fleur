from fleur.js import builder
from fleur.js.emitter import ES2022Emitter


class TestStatementBuilder:
    @staticmethod
    def test_variable_declaration_statement():
        with builder.use_context():
            builder.let("x", builder.Number(42))
            builder.const("y", builder.String("Hello"))
            builder.var("z", builder.Boolean(True))

            code = ES2022Emitter("minify")(*builder.collect_statements())
            assert code == 'let x=42;const y="Hello";var z=true;'

    @staticmethod
    def test_function_declaration_statement():
        with builder.use_context():

            @builder.function
            def add(a: builder.Number, b: builder.Number) -> builder.Number:
                return builder.ret(a + b)

            code = ES2022Emitter("minify")(*builder.collect_statements())
            assert code == "function add(a,b){return (a+b);}"

    @staticmethod
    def test_recursive_function_declaration_statement():
        with builder.use_context():

            @builder.function
            def factorial(n: builder.Number) -> builder.Number:
                return builder.ret(
                    builder.conditional(
                        n <= builder.Number(1),
                        builder.Number(1),
                        n * factorial(n - builder.Number(1)),
                    )
                )

            code = ES2022Emitter("minify")(*builder.collect_statements())
            assert code == "function factorial(n){return ((n<=1)?1:(n*factorial((n-1))));}"
