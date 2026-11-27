from fleur import Cmd, Msg, MsgGroup, builtins, emit
from fleur.types import JsonValue


class HttpMsg(MsgGroup):
    OK: Msg[builtins.HttpResponse[str] | builtins.HttpResponse[JsonValue]] = Msg()
    ERR = Msg[builtins.HttpError]()


class TestHttp:
    def test_http_get_expect_json_compiles_to_runtime_http_request(self) -> None:
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

    def test_http_request_with_options_compiles_all_fields(self) -> None:
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

    def test_http_post_compiles_to_runtime_http_request_with_body(self) -> None:
        cmd = Cmd.task(
            builtins.Http.post(
                "https://example.com/todo",
                expect=builtins.Http.expectText(),
                body={"title": "Buy milk"},
            ),
            HttpMsg.OK,
            HttpMsg.ERR,
        )

        source = emit(cmd.__compile__())

        assert "__fleur.Http.request" in source
        assert 'method: "POST"' in source
        assert 'body: {title: "Buy milk"}' in source

    def test_http_other_method_helpers_compile_to_runtime_http_request(self) -> None:
        cases = [
            (
                "PUT",
                builtins.Http.put("https://example.com/todo", expect=builtins.Http.expectJson(), body={"done": True}),
            ),
            (
                "PATCH",
                builtins.Http.patch("https://example.com/todo", expect=builtins.Http.expectJson(), body={"done": True}),
            ),
            ("DELETE", builtins.Http.delete("https://example.com/todo", expect=builtins.Http.expectJson())),
            ("HEAD", builtins.Http.head("https://example.com/todo", expect=builtins.Http.expectText())),
            ("OPTIONS", builtins.Http.options("https://example.com/todo", expect=builtins.Http.expectText())),
        ]

        for method, task in cases:
            cmd = Cmd.task(task, HttpMsg.OK, HttpMsg.ERR)
            source = emit(cmd.__compile__())
            assert "__fleur.Http.request" in source
            assert f'method: "{method}"' in source
