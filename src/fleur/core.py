from typing_extensions import TypeAlias

from fleur import js

Dispatch: TypeAlias = js.Function[..., js.Undefined]


class Cmd(js.Record):
    @staticmethod
    @js.function
    def none() -> js.Function[[], js.Undefined]:
        @js.function
        def run() -> None:
            pass

        return run

    @staticmethod
    @js.function
    def batch(cmds: js.Array[js.Function[[Dispatch], js.Undefined]]) -> js.Function[[Dispatch], js.Undefined]:
        @js.function
        def run(dispatch: Dispatch) -> None:
            @cmds.forEach
            @js.function
            def _(cmd: js.Function[[Dispatch], js.Undefined]) -> None:
                cmd(dispatch)

        return run


if __name__ == "__main__":
    with js.use_context():
        js.const(Cmd)
        emitter = js.ES2022Emitter()
        code = emitter(*(js.collect_statements()))
        print(code)
