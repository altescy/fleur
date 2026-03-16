from fleur import Cmd, Msg, MsgGroup, builtins, emit


class HttpMsg(MsgGroup):
    OK = Msg[object]()
    ERR = Msg[builtins.HttpError]()


def test_http_get_expect_json_compiles_to_fetch_then_json() -> None:
    cmd = Cmd.task(
        builtins.Http.get("https://example.com/todo", expect=builtins.Http.expectJson()),
        HttpMsg.OK,
        HttpMsg.ERR,
    )

    source = emit(cmd.__compile__())

    assert "__fleur.Cmd.task" in source
    assert 'fetch("https://example.com/todo")' in source
    assert ".then(" in source
    assert ".json()" in source
