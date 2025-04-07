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
    def __getattr__(self, name: str) -> Callable[[Mapping, *tuple[Dom | StateProto, ...]], Node]:
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
fleurjs: Final = "\n".join(
    [
        javascript(Hook),
        javascript(StateProto),
        javascript(TagAccessor),
        javascript(get_node),
        javascript(bind),
        javascript(add),
        javascript(state),
        "const tags = TagAccessor();",
        "const fleur = {Hook, StateProto, TagAccessor, bind, add, state, tags};",
    ]
)


def render(component: Callable[[], Node]) -> str:
    script = "\n".join(
        [
            fleurjs,
            f"const app = {javascript(component)}",
            "add(document.body, app());",
        ]
    )
    return f"<!DOCTYPE html><html><body><script>{script}</script></body></html>"
