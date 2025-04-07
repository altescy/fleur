from collections.abc import Callable, Mapping
from typing import Final

from fleur.js import JSON, Dom, Node, Object, document, javascript, typeof


class Hook[T]:
    def __init__(self, node: Node | None = None) -> None:
        self.node = node

    def update(self, value: T) -> None:
        pass


class StateProto[T]:
    _value: T
    _hooks: list[Hook[T]]

    def __init__(self, value: T) -> None:
        self._value = value
        self._hooks = []

    @property
    def value(self) -> T:
        return self._value

    @value.setter
    def value(self, v: T) -> None:
        self._value = v
        for hook in self._hooks:
            hook.update(self._value)


def get_node(dom: Dom) -> Node:
    if isinstance(dom, Node):
        return dom
    if typeof(dom) == "string":
        return document.createTextNode(dom)
    if typeof(dom) == "function":
        return get_node(dom())
    return document.createTextNode(JSON.stringify(dom))


def bind(dom: Dom | StateProto) -> Node:
    if isinstance(dom, StateProto):
        node = get_node(dom.value)

        class _Hook[T](Hook[T]):
            def update(self, value: T) -> None:
                new_node = get_node(value)
                self.node.replaceWith(new_node)
                self.node = new_node

        dom._hooks.append(_Hook(node))
        return node
    return get_node(dom)


def state[T](value: T) -> StateProto[T]:
    return StateProto(value)


def add(dom: Dom, *children: Dom | StateProto) -> Dom:
    for child in children:
        dom.appendChild(bind(child))
    return dom


class TagAccessor:
    def __getattr__(
        self, name: str
    ) -> Callable[[Mapping, *tuple[Dom | StateProto, ...]], Node]:
        def _tag(props: Mapping, *children: Dom | StateProto) -> Node:
            dom = document.createElement(name)
            for key, value in Object.entries(props):
                if isinstance(value, StateProto):

                    class _Hook[T](Hook[T]):
                        def update(self, value: T) -> None:
                            dom.setAttribute(key, value)

                    value._hooks.append(_Hook())
                    value = value.value
                if key.startswith("on"):
                    dom.addEventListener(key[2:].lower(), value)
                elif key == "ref":
                    value.current = dom
                else:
                    dom.setAttribute(key, value)
            return add(dom, *children)

        return _tag


tags: Final = TagAccessor()
fleurjs: Final = "\n".join([
    javascript(Hook),
    javascript(StateProto),
    javascript(TagAccessor),
    javascript(get_node),
    javascript(bind),
    javascript(add),
    javascript(state),
    "const tags = TagAccessor();",
    "const fleur = {Hook, StateProto, TagAccessor, bind, add, state, tags};",
])
_DEFAULT_STYLE: Final = """
* { box-sizing: border-box; }
.block { display: block; }
.flex { display: flex; }
.grid { display: grid; }
.inline { display: inline; }
.inline-block { display: inline-block; }
.hidden { display: none; }
.absolute { position: absolute; }
.relative { position: relative; }
.fixed { position: fixed; }
.w-full { width: 100%; }
.w-auto { width: auto; }
.w-fit { width: fit-content; }
.w-screen { width: 100vw; }
.w-min { width: min-content; }
.w-max { width: max-content; }
.w-1/2 { width: 50%; }
.w-1/3 { width: 33.333333%; }
.w-1/4 { width: 25%; }
.h-full { height: 100%; }
.h-auto { height: auto; }
.h-fit { height: fit-content; }
.h-screen { height: 100vh; }
.h-min { height: min-content; }
.h-max { height: max-content; }
.h-1/2 { height: 50%; }
.h-1/3 { height: 33.333333%; }
.h-1/4 { height: 25%; }
.m-0 { margin: 0; }
.m-1 { margin: 0.25rem; }
.m-2 { margin: 0.5rem; }
.m-3 { margin: 0.75rem; }
.m-4 { margin: 1rem; }
.p-0 { padding: 0; }
.p-1 { padding: 0.25em; }
.p-2 { padding: 0.5em; }
.p-3 { padding: 0.75em; }
.p-4 { padding: 1em; }
.text-center { text-align: center; }
.text-left { text-align: left; }
.text-right { text-align: right; }
.text-sm { font-size: 0.875rem; }
.text-base { font-size: 1rem; }
.text-lg { font-size: 1.125rem; }
.font-bold { font-weight: bold; }
.font-normal { font-weight: normal; }
.font-light { font-weight: 300; }
.text-xl { font-size: 1.25rem; }
.jsutify-center { justify-content: center; }
.jsutify-start { justify-content: flex-start; }
.jsutify-end { justify-content: flex-end; }
.items-center { align-items: center; }
.items-start { align-items: flex-start; }
.items-end { align-items: flex-end; }
.flex-col { flex-direction: column; }
.flex-row { flex-direction: row; }
.gap-0 { gap: 0; }
.gap-1 { gap: 0.25rem; }
.gap-2 { gap: 0.5rem; }
.gap-3 { gap: 0.75rem; }
.gap-4 { gap: 1rem; }
.rounded { border-radius: 0.25rem; }
.rounded-sm { border-radius: 0.125rem; }
.rounded-md { border-radius: 0.375rem; }
.rounded-lg { border-radius: 0.5rem; }
.rounded-full { border-radius: 9999px; }
.border { border: 1px solid #000; }
.shadow { box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); }
.shadow-md { box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); }
.shadow-lg { box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1); }
.overflow-hidden { overflow: hidden; }
.overflow-auto { overflow: auto; }
.overflow-scroll { overflow: scroll; }
.overflow-x-auto { overflow-x: auto; }
.overflow-y-auto { overflow-y: auto; }
"""


def render(
    component: Callable[[], Node],
    style: str | None = _DEFAULT_STYLE,
) -> str:
    script = "\n".join([
        fleurjs,
        f"const app = {javascript(component)}",
        "add(document.body, app());",
    ])
    return f"<!DOCTYPE html><html><head><style>{style}</style></head><body><script>{script}</script></body></html>"
