from fleur.js import builder
from fleur.js.emitter import ES2022Emitter


def main():
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
        print(code)


main()
