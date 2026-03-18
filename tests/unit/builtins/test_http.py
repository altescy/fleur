from fleur import Cmd, Msg, MsgGroup, builtins, emit


class HttpMsg(MsgGroup):
    OK = Msg()
    ERR = Msg[builtins.HttpError]()


def test_http_get_expect_json_compiles_to_runtime_http_request() -> None:
    cmd = Cmd.task(
        builtins.Http.get("https://example.com/todo", expect=builtins.Http.expectJson()),
        HttpMsg.OK,
        HttpMsg.ERR,
    )

    source = emit(cmd.__compile__())

    assert "__fleur.Cmd.task" in source
    assert "__fleur.Http.request" in source
    assert 'method: "GET"' in source
    assert 'url: "https://example.com/todo"' in source
    assert 'expect: "json"' in source


def test_http_request_with_options_compiles_all_fields() -> None:
    cmd = Cmd.task(
        builtins.Http.request(
            "POST",
            "https://example.com/todo",
            expect=builtins.Http.expectText(),
            headers={"X-Trace": "trace-1"},
            body={"title": "Buy milk"},
            timeout_ms=3000,
            credentials="include",
        ),
        HttpMsg.OK,
        HttpMsg.ERR,
    )

    source = emit(cmd.__compile__())

    assert "__fleur.Http.request" in source
    assert 'method: "POST"' in source
    assert 'expect: "text"' in source
    assert 'headers: {"X-Trace": "trace-1"}' in source
    assert 'body: {title: "Buy milk"}' in source
    assert "timeoutMs: 3000" in source
    assert 'credentials: "include"' in source
