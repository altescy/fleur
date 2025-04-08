from collections.abc import Callable, Mapping, Sequence
from typing import Final, cast, overload

from fleur.js import JSON, Dom, Node, Object, document, javascript, to_javascript, typeof
from fleur.style import DEFAULT_CSS


@javascript
class Hook[T]:
    def __init__(self, node: Node | None = None) -> None:
        self.node = node

    def update(self, value: T) -> None:
        pass


@javascript
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


@javascript
def get_node(dom: Dom) -> Node:
    if isinstance(dom, Node):
        return dom
    if typeof(dom) == "string":
        return document.createTextNode(dom)
    if typeof(dom) == "function":
        return get_node(dom())
    return document.createTextNode(JSON.stringify(dom))


@javascript
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


@javascript
def state[T](value: T) -> StateProto[T]:
    return StateProto(value)


@javascript
def add(dom: Dom, *children: Dom | StateProto) -> Dom:
    for child in children:
        dom.appendChild(bind(child))
    return dom


@javascript
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
        to_javascript(Hook),
        to_javascript(StateProto),
        to_javascript(TagAccessor),
        to_javascript(get_node),
        to_javascript(bind),
        to_javascript(add),
        to_javascript(state),
        "const tags = TagAccessor();",
        "const fleur = {Hook, StateProto, TagAccessor, bind, add, state, tags};",
    ]
)


# ========================
# Render functions
# ========================


type Component = Callable[..., Node]


def _find_dependencies(component: Component) -> set[Component]:
    import ast
    import inspect

    class CallAnalyzer(ast.NodeVisitor):
        def __init__(self) -> None:
            self.calls: dict[str, ast.AST] = {}

        def visit_Call(self, node: ast.Call) -> None:
            func_expr = node.func
            if isinstance((func_expr), ast.Name):
                self.calls[func_expr.id] = node
            elif isinstance(func_expr, ast.Attribute):
                full_name = ast.unparse(func_expr)
                self.calls[full_name] = node
            self.generic_visit(node)

    source = inspect.getsource(component)
    tree = ast.parse(source)
    analyzer = CallAnalyzer()
    analyzer.visit(tree)

    context = component.__globals__
    dependencies: set[Component] = set(getattr(component, "__fleur_dependencies__", ()))
    for name in analyzer.calls.keys():
        if name in context:
            obj = context[name]
            if callable(obj) and getattr(obj, "__fleur_component__", False):
                dependencies.add(cast(Component, obj))
    return dependencies


def render(
    component: Component,
    style: str | None = DEFAULT_CSS,
) -> str:
    dependencies = _find_dependencies(component)
    script = "\n".join(
        [
            fleurjs,
            *(to_javascript(dep) for dep in dependencies),
            f"const app = {to_javascript(component)}",
            "add(document.body, app());",
        ]
    )
    return f"<!DOCTYPE html><html><head><style>{style}</style></head><body><script>{script}</script></body></html>"


@overload
def component[F: Component](
    fn: None = None,
    *,
    dependencies: Sequence[Component] = (),
) -> Callable[[F], F]: ...


@overload
def component[F: Component](
    fn: F,
    *,
    dependencies: Sequence[Component] = (),
) -> F: ...


def component[F: Component](
    fn: F | None = None,
    *,
    dependencies: Sequence[Component] = (),
) -> F | Callable[[F], F]:
    def decorator(fn: F) -> F:
        setattr(fn, "__fleur_component__", True)
        setattr(fn, "__fleur_dependencies__", dependencies)
        return fn

    if fn is None:
        return decorator

    return decorator(fn)
