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

            @builder.define
            def add(a: builder.Number, b: builder.Number) -> builder.Number:
                return a + b

            code = ES2022Emitter("minify")(*builder.collect_statements())
            assert code == "function add(a,b){return (a+b);}"

    @staticmethod
    def test_recursive_function_declaration_statement():
        with builder.use_context():

            @builder.define
            def factorial(n: builder.Number) -> builder.Number:
                return builder.conditional(
                    n <= builder.Number(1),
                    builder.Number(1),
                    n * factorial(n - builder.Number(1)),
                )

            code = ES2022Emitter("minify")(*builder.collect_statements())
            assert code == "function factorial(n){return ((n<=1)?1:(n*factorial((n-1))));}"

    @staticmethod
    def test_function_with_variables():
        """Test function with transform=True and variable declarations"""
        with builder.use_context():

            @builder.define
            def calculate(n: builder.Number) -> builder.Number:
                x = n + builder.Number(1)
                y = x * builder.Number(2)
                return y

            code = ES2022Emitter("minify")(*builder.collect_statements())
            assert code == "function calculate(n){let x=(n+1);let y=(x*2);return y;}"

    @staticmethod
    def test_function_with_if_statement():
        """Test function with if statement"""
        with builder.use_context():

            @builder.define
            def check_positive(n: builder.Number) -> builder.String:
                if n > builder.Number(0):
                    return builder.String("Positive")
                else:
                    return builder.String("Non-positive")

            code = ES2022Emitter("minify")(*builder.collect_statements())
            assert code == 'function check_positive(n){if((0<n)){return "Positive";}else{return "Non-positive";}}'

    @staticmethod
    def test_function_with_multiple_scopes():
        """Test function with multiple variable declarations in different scopes"""
        with builder.use_context():

            @builder.define
            def complex_function(n: builder.Number) -> builder.Number:
                a = n + builder.Number(1)

                if a > builder.Number(10):
                    b = a * builder.Number(2)
                else:
                    b = a - builder.Number(2)

                return b

            code = ES2022Emitter("minify")(*builder.collect_statements())
            assert (
                code == "function complex_function(n){let a=(n+1);if((10<a)){let b=(a*2);}else{let b=(a-2);}return b;}"
            )

    @staticmethod
    def test_function_and_record():
        with builder.use_context():

            class Message(builder.Record):
                text: builder.String

            @builder.const
            class Foo(builder.Record):
                @staticmethod
                @builder.function
                def send(msg: builder.String) -> Message:
                    return Message(text=builder.String("Sent: ") + msg)

            @builder.define
            def run() -> Message:
                return Foo.send(builder.String("Hello"))

            code = ES2022Emitter("minify")(*builder.collect_statements())
            assert (
                code
                == 'const Foo={"send":(function(msg){return {"text":("Sent: "+msg)};})};function run(){return Foo.send("Hello");}'
            )
