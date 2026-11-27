"""Element-scoped DOM operations for client-side views."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import ClassVar, Final, Generic, Literal, TypeVar

from typing_extensions import TypeAlias

from fleur.js.ast import (
    ESTreeArrayExpression,
    ESTreeAssignmentExpression,
    ESTreeBinaryExpression,
    ESTreeConditionalExpression,
    ESTreeExpression,
    ESTreeExpressionStatement,
    ESTreeGeneratedIdentifier,
    ESTreeNewExpression,
    ESTreeNode,
    ESTreeReturnStatement,
    ESTreeStatement,
)
from fleur.js.builder import call, function_expr, ident, if_stmt, literal, member_expr, object_expr, variable
from fleur.js.traverse import bound_generated_identifiers, generated_identifiers, identifiers
from fleur.types import JsonValue, JsonValueT

from .boolean import Boolean
from .cond import Cond
from .events import FocusEvent, InputEvent, KeyboardEvent, PointerEvent, SubmitEvent
from .expr import Expr, ensure_expr
from .msg import GroupedMsg, MsgGroup
from .runtime import MESSAGE_IDENT, MODEL_IDENT, runtime_ref
from .task import TaskLike
from .types import MsgGroupT, OptionalEventT


def _dom_call(name: str, *args: ESTreeExpression) -> ESTreeExpression:
    return call(member_expr(runtime_ref("Dom"), name), *args)


class DomAction:
    """An operation performed in the browser by a DOM effect or event binding."""

    def __init__(self, _statements: Sequence[ESTreeStatement] = ()) -> None:
        self._statements = _statements

    @staticmethod
    def batch(*actions: DomAction) -> DomAction:
        return DomAction(tuple(statement for action in actions for statement in action._statements))

    @staticmethod
    def microtask(action: DomAction) -> DomAction:
        """Run the action after the current synchronous browser work."""
        return _action(call(ident("queueMicrotask"), function_expr([], *action._statements)))

    @staticmethod
    def with_value(value: Expr[JsonValueT], action: Callable[[Expr[JsonValueT]], DomAction]) -> DomAction:
        ref = ESTreeGeneratedIdentifier()
        return DomAction((variable(ref, ensure_expr(value)), *action(Expr(ref))._statements))

    @staticmethod
    def when(condition: bool | Expr[bool], action: DomAction, *, otherwise: DomAction | None = None) -> DomAction:
        return DomAction(
            (
                if_stmt(
                    ensure_expr(condition),
                    *action._statements,
                    otherwise=() if otherwise is None else otherwise._statements,
                ),
            )
        )

    @staticmethod
    def maybe(
        value: Expr[JsonValueT | None],
        then: Callable[[Expr[JsonValueT]], DomAction],
        *,
        otherwise: DomAction | None = None,
    ) -> DomAction:
        """Run `then` with the value when it is present, and `otherwise` when it is missing.

        The action counterpart of `Cond.maybe`, like Haskell's `maybe` or Rust's `map_or`. The value
        is read once; both `None` and a missing value, such as an absent mapping key, run `otherwise`.
        """

        def branch(snapshot: Expr[JsonValueT | None]) -> DomAction:
            return DomAction.when(
                Cond.not_equal(snapshot, None), then(Expr[JsonValueT](snapshot.__compile__())), otherwise=otherwise
            )

        return DomAction.with_value(value, branch)


def _action(expression: ESTreeExpression) -> DomAction:
    return DomAction((ESTreeExpressionStatement(expression),))


class DomElement:
    """A reference to an HTML element within a browser callback.

    A missing reference has `exists == False`. Traversal returns another missing
    reference and mutations on it are no-ops.
    """

    def __init__(self, _node: ESTreeExpression) -> None:
        self._node = _node

    @property
    def exists(self) -> Expr[bool]:
        return Expr(ESTreeBinaryExpression("!==", self._node, literal(None)))

    @property
    def connected(self) -> Expr[bool]:
        return Expr(_dom_call("connected", self._node))

    def same_as(self, other: DomElement) -> Expr[bool]:
        return Expr(ESTreeBinaryExpression("===", self._node, other._node))

    def or_else(self, other: DomElement) -> DomElement:
        return DomElement.when(self.exists, self, other)

    @staticmethod
    def when(condition: bool | Expr[bool], yes: DomElement, no: DomElement) -> DomElement:
        return DomElement(
            ESTreeConditionalExpression(test=ensure_expr(condition), consequent=yes._node, alternate=no._node)
        )

    def child(self, index: int | Expr[int]) -> DomElement:
        return DomElement(_dom_call("child", self._node, ensure_expr(index)))

    def query(self, selector: str) -> DomElement:
        return DomElement(_dom_call("query", self._node, literal(selector)))

    @property
    def parent(self) -> DomElement:
        return DomElement(_dom_call("parent", self._node))

    @property
    def next_sibling(self) -> DomElement:
        return DomElement(_dom_call("next", self._node))

    @property
    def previous_sibling(self) -> DomElement:
        return DomElement(_dom_call("previous", self._node))

    @property
    def last_child(self) -> DomElement:
        return DomElement(_dom_call("last", self._node))

    @property
    def active_element(self) -> DomElement:
        return DomElement(_dom_call("active", self._node))

    def event_origin(self, event: str) -> DomElement:
        """Find the target of the given event type that triggered this DOM effect."""
        return DomElement(_dom_call("eventOrigin", self._node, literal(event)))

    @property
    def direction(self) -> Expr[str]:
        return Expr(_dom_call("direction", self._node))

    def for_each_child(self, action: Callable[[DomElement, Expr[int]], DomAction]) -> DomAction:
        return self.children.for_each(action)

    def with_reference(self, action: Callable[[DomElement], DomAction]) -> DomAction:
        """Resolve the element once for the given action."""
        ref = ESTreeGeneratedIdentifier()
        return DomAction((variable(ref, self._node), *action(DomElement(ref))._statements))

    def attribute(self, name: str) -> Expr[str | None]:
        return Expr(_dom_call("attribute", self._node, literal(name)))

    @property
    def id(self) -> Expr[str]:
        return Expr(_dom_call("id", self._node))

    def set_attribute(self, name: str, value: str | Expr[str]) -> DomAction:
        return _action(_dom_call("setAttribute", self._node, literal(name), ensure_expr(value)))

    def ensure_id(self, prefix: str = "fleur-") -> DomAction:
        """Assign a document-unique ID if the element does not already have one."""
        return _action(_dom_call("ensureId", self._node, literal(prefix)))

    def focus(self, *, prevent_scroll: bool = False) -> DomAction:
        return _action(_dom_call("focus", self._node, literal(prevent_scroll)))

    def as_dialog(self) -> DomDialog:
        return DomDialog(self._node)

    @staticmethod
    def missing() -> DomElement:
        return DomElement(literal(None))

    @property
    def children(self) -> DomElements:
        return DomElements(_dom_call("children", self._node))

    def query_all(self, selector: str) -> DomElements:
        return DomElements(_dom_call("queryAll", self._node, literal(selector)))

    def document_query_all(self, selector: str) -> DomElements:
        return DomElements(_dom_call("queryAll", _dom_call("document", self._node), literal(selector)))

    def closest(self, selector: str | Expr[str]) -> DomElement:
        return DomElement(_dom_call("closest", self._node, ensure_expr(selector)))

    def matches(self, selector: str) -> Expr[bool]:
        return Expr(_dom_call("matches", self._node, literal(selector)))

    def contains(self, other: DomElement) -> Expr[bool]:
        return Expr(_dom_call("contains", self._node, other._node))

    def has_attribute(self, name: str) -> Expr[bool]:
        return Cond.not_equal(self.attribute(name), None)

    def remove_attribute(self, name: str) -> DomAction:
        return _action(_dom_call("removeAttribute", self._node, literal(name)))

    @property
    def hidden(self) -> Expr[bool]:
        return Expr(_dom_call("hidden", self._node))

    def set_hidden(self, hidden: bool | Expr[bool]) -> DomAction:
        return _action(_dom_call("setHidden", self._node, ensure_expr(hidden)))

    @property
    def text(self) -> Expr[str]:
        return Expr(_dom_call("text", self._node))

    def set_text(self, text: str | Expr[str]) -> DomAction:
        return _action(_dom_call("setText", self._node, ensure_expr(text)))

    def set_style(self, name: str, value: str | Expr[str]) -> DomAction:
        return _action(_dom_call("setStyle", self._node, literal(name), ensure_expr(value)))

    def click(self) -> DomAction:
        return _action(_dom_call("click", self._node))

    def dispatch(self, event: str, *, bubbles: bool = False, detail: str | Expr[str] | None = None) -> DomAction:
        return _action(_dom_call("dispatch", self._node, literal(event), literal(bubbles), ensure_expr(detail)))

    def scroll_into_view(self, *, block: Literal["start", "center", "end", "nearest"] = "nearest") -> DomAction:
        return _action(_dom_call("scrollIntoView", self._node, literal(block)))

    @property
    def bounds(self) -> DomBounds:
        return DomBounds(_dom_call("bounds", self._node))

    @property
    def viewport_width(self) -> Expr[int]:
        return Expr(_dom_call("viewportWidth", self._node))

    @property
    def viewport_height(self) -> Expr[int]:
        return Expr(_dom_call("viewportHeight", self._node))

    @staticmethod
    def supports_style(property: str, value: str) -> Expr[bool]:
        return Expr(_dom_call("cssSupports", literal(property), literal(value)))

    def as_popover(self) -> DomPopover:
        return DomPopover(self._node)

    def as_input(self) -> DomInput:
        return DomInput(_dom_call("input", self._node))

    def as_image(self) -> DomImage:
        return DomImage(self._node)


class DomElements:
    """An ordered collection of HTML element references."""

    def __init__(self, _nodes: ESTreeExpression) -> None:
        self._nodes = _nodes

    @property
    def length(self) -> Expr[int]:
        return Expr(member_expr(self._nodes, "length"))

    def at(self, index: int | Expr[int | float]) -> DomElement:
        """Access a position, with negative indices counting from the end."""
        return DomElement(_dom_call("at", self._nodes, ensure_expr(index)))

    def _select(self, method: str, predicate: Callable[[DomElement], Expr[bool]]) -> ESTreeExpression:
        element = ESTreeGeneratedIdentifier()
        callback = function_expr([element], ESTreeReturnStatement(ensure_expr(predicate(DomElement(element)))))
        return call(member_expr(self._nodes, method), callback)

    def filter(self, predicate: Callable[[DomElement], Expr[bool]]) -> DomElements:
        return DomElements(self._select("filter", predicate))

    def find(self, predicate: Callable[[DomElement], Expr[bool]]) -> DomElement:
        return DomElement(_dom_call("element", self._select("find", predicate)))

    def index_where(self, predicate: Callable[[DomElement], Expr[bool]]) -> Expr[int]:
        return Expr(self._select("findIndex", predicate))

    def index_of(self, element: DomElement) -> Expr[int]:
        return Expr(call(member_expr(self._nodes, "indexOf"), element._node))

    def map(self, select: Callable[[DomElement], DomElement]) -> DomElements:
        element = ESTreeGeneratedIdentifier()
        callback = function_expr([element], ESTreeReturnStatement(select(DomElement(element))._node))
        return DomElements(call(member_expr(self._nodes, "map"), callback))

    def for_each(self, action: Callable[[DomElement, Expr[int]], DomAction]) -> DomAction:
        element, index = ESTreeGeneratedIdentifier(), ESTreeGeneratedIdentifier()
        callback = function_expr([element, index], *action(DomElement(element), Expr(index))._statements)
        return _action(call(member_expr(self._nodes, "forEach"), callback))

    def with_snapshot(self, action: Callable[[DomElements], DomAction]) -> DomAction:
        elements = ESTreeGeneratedIdentifier()
        return DomAction((variable(elements, self._nodes), *action(DomElements(elements))._statements))


class DomBounds:
    """An element's bounding rectangle in viewport coordinates."""

    def __init__(self, _rect: ESTreeExpression) -> None:
        self._rect = _rect

    @property
    def left(self) -> Expr[int | float]:
        return Expr(member_expr(self._rect, "left"))

    @property
    def bottom(self) -> Expr[int | float]:
        return Expr(member_expr(self._rect, "bottom"))

    @property
    def width(self) -> Expr[int | float]:
        return Expr(member_expr(self._rect, "width"))

    @property
    def height(self) -> Expr[int | float]:
        return Expr(member_expr(self._rect, "height"))

    def with_snapshot(self, action: Callable[[DomBounds], DomAction]) -> DomAction:
        rect = ESTreeGeneratedIdentifier()
        return DomAction((variable(rect, self._rect), *action(DomBounds(rect))._statements))


class DomPopover(DomElement):
    """Native popover operations and feature detection."""

    @property
    def supported(self) -> Expr[bool]:
        return Expr(_dom_call("popoverSupported", self._node))

    @property
    def mode(self) -> Expr[str | None]:
        return Expr(_dom_call("popoverMode", self._node))

    @property
    def is_open(self) -> Expr[bool]:
        return self.matches(":popover-open")

    def show(self) -> DomAction:
        return _action(_dom_call("showPopover", self._node))

    def hide(self) -> DomAction:
        return _action(_dom_call("hidePopover", self._node))

    def toggle(self, open: bool | Expr[bool]) -> DomAction:
        return _action(_dom_call("togglePopover", self._node, ensure_expr(open)))


class DomInput(DomElement):
    """Operations on a native input, including the browser's numeric stepping."""

    @property
    def value(self) -> Expr[str]:
        return Expr(_dom_call("inputValue", self._node))

    def set_value(self, value: str | Expr[str]) -> DomAction:
        return _action(_dom_call("setInputValue", self._node, ensure_expr(value)))

    def step(self, direction: Literal[-1, 1]) -> DomAction:
        return _action(_dom_call("step", self._node, literal(direction)))

    def clone(self) -> DomElement:
        """Copy this input into a detached element."""
        return DomElement(_dom_call("cloneInput", self._node))


class DomImage(DomElement):
    """The browser's loading state for an image."""

    @property
    def complete(self) -> Expr[bool]:
        return Expr(_dom_call("imageComplete", self._node))

    @property
    def natural_width(self) -> Expr[int]:
        return Expr(_dom_call("imageWidth", self._node))

    @property
    def source(self) -> Expr[str]:
        return Expr(_dom_call("imageSource", self._node))

    @property
    def current_source(self) -> Expr[str]:
        return Expr(_dom_call("imageCurrentSource", self._node))


class DomDialog(DomElement):
    """Native dialog operations. A reference to any other tag is treated as closed."""

    @property
    def is_open(self) -> Expr[bool]:
        return Expr(_dom_call("dialogOpen", self._node))

    def show_modal(self) -> DomAction:
        return _action(_dom_call("showModal", self._node))

    def close(self) -> DomAction:
        return _action(_dom_call("closeDialog", self._node))


_ElementAction = Callable[[DomElement], DomAction]
_Dependency = JsonValue | Expr[JsonValue]


class DomValue(Generic[JsonValueT]):
    """Mutable browser-local data owned by one mounted view."""

    def __init__(self, _ref: ESTreeGeneratedIdentifier) -> None:
        self._ref = _ref

    @property
    def value(self) -> Expr[JsonValueT]:
        return Expr(self._ref)

    def set(self, value: JsonValueT | Expr[JsonValueT]) -> DomAction:
        return _action(ESTreeAssignmentExpression(self._ref, ensure_expr(value)))


class DomReference:
    """A mutable element reference owned by one mounted view."""

    def __init__(self, _ref: ESTreeGeneratedIdentifier) -> None:
        self._ref = _ref

    @property
    def element(self) -> DomElement:
        return DomElement(self._ref)

    def set(self, element: DomElement) -> DomAction:
        return _action(ESTreeAssignmentExpression(self._ref, element._node))

    def clear(self) -> DomAction:
        return self.set(DomElement.missing())


class DomTimer:
    """A replaceable one-shot timer, cancelled when its effect is disposed."""

    def __init__(self, _id: DomValue[int | None]) -> None:
        self._id = _id

    @property
    def pending(self) -> Expr[bool]:
        return Cond.not_equal(self._id.value, None)

    def cancel(self) -> DomAction:
        return DomAction.when(
            self.pending,
            DomAction.batch(_action(call(ident("clearTimeout"), ensure_expr(self._id.value))), self._id.set(None)),
        )

    def start(self, delay_ms: int | float | Expr[int | float], action: DomAction) -> DomAction:
        callback = function_expr([], *self._id.set(None)._statements, *action._statements)
        timer_id = Expr[int](call(ident("setTimeout"), callback, ensure_expr(delay_ms)))
        return DomAction.batch(self.cancel(), self._id.set(timer_id))


class DomListener:
    """An event listener that may be attached and detached within its effect."""

    def __init__(self, _binding: ESTreeGeneratedIdentifier) -> None:
        self._binding = _binding

    def attach(self) -> DomAction:
        return _action(call(member_expr(self._binding, "attach")))

    def detach(self) -> DomAction:
        return _action(call(member_expr(self._binding, "detach")))


@dataclass(frozen=True)
class DomLifecycle:
    """Actions on effect installation, subsequent updates, and disposal.

    The update also runs immediately after mount.
    """

    mount: DomAction | None = None
    update: DomAction | None = None
    dispose: DomAction | None = None


class DomScope:
    """Allocate state and listeners for a single installation of an effect."""

    def __init__(self) -> None:
        self._inputs: list[tuple[ESTreeGeneratedIdentifier, ESTreeExpression]] = []
        self._declarations: list[ESTreeStatement] = []
        self._cleanup: list[DomAction] = []
        self._controller: ESTreeGeneratedIdentifier | None = None

    def _local(self, initial: ESTreeExpression) -> ESTreeGeneratedIdentifier:
        ref = ESTreeGeneratedIdentifier()
        self._declarations.append(variable(ref, initial))
        return ref

    def input(self, value: JsonValueT | Expr[JsonValueT]) -> Expr[JsonValueT]:
        """Read the latest value of a render-time expression within this effect.

        The value is evaluated outside the effect, so it must not refer to inputs,
        local values, or other bindings created by this effect.
        """
        ref = ESTreeGeneratedIdentifier()
        self._inputs.append((ref, ensure_expr(value)))
        return Expr(ref)

    def value(self, initial: JsonValueT | Expr[JsonValueT]) -> DomValue[JsonValueT]:
        return DomValue(self._local(ensure_expr(initial)))

    def reference(self, initial: DomElement | None = None) -> DomReference:
        return DomReference(self._local(literal(None) if initial is None else initial._node))

    def action(self, action: DomAction) -> DomAction:
        """Define an action once and reuse it in this effect's callbacks."""
        callback = self._local(function_expr([], *action._statements))
        return _action(call(callback))

    def timer(self) -> DomTimer:
        timer = DomTimer(self.value(Expr[int | None](literal(None))))
        self._cleanup.append(timer.cancel())
        return timer

    @staticmethod
    def now() -> Expr[int | float]:
        """Read the browser's monotonic clock in milliseconds."""
        return Expr(_dom_call("now"))

    def unique_id(self, prefix: str = "fleur-") -> Expr[str]:
        """Generate a distinct identifier once per installation."""
        return self.value(Expr[str](_dom_call("uniqueId", literal(prefix)))).value

    def listen(
        self, target: DomElement, event: str, action: Callable[[DomEvent], DomAction], *, capture: bool = False
    ) -> DomAction:
        return self._listener(target._node, event, action, capture).attach()

    def on(
        self,
        target: DomElement,
        event: DomEventType[_DomEventT, _PayloadT],
        action: Callable[[_DomEventT], DomAction],
        *,
        capture: bool = False,
    ) -> DomAction:
        """Listen for a typed event using the same descriptors as EventBinding.on."""
        return self.listen(target, event.name, event._listener(action), capture=capture)

    def on_document(
        self,
        element: DomElement,
        event: DomEventType[_DomEventT, _PayloadT],
        action: Callable[[_DomEventT], DomAction],
        *,
        capture: bool = False,
    ) -> DomListener:
        """Make a scoped document listener for a typed event."""
        return self.document_listener(element, event.name, event._listener(action), capture=capture)

    def document_listener(
        self, element: DomElement, event: str, action: Callable[[DomEvent], DomAction], *, capture: bool = False
    ) -> DomListener:
        return self._listener(_dom_call("document", element._node), event, action, capture)

    def _listener(
        self, target: ESTreeExpression, event: str, action: Callable[[DomEvent], DomAction], capture: bool
    ) -> DomListener:
        if self._controller is None:
            self._controller = self._local(ESTreeNewExpression(ident("AbortController"), []))
            self._cleanup.append(_action(call(member_expr(self._controller, "abort"))))
        raw, payload = ESTreeGeneratedIdentifier(), ESTreeGeneratedIdentifier()
        handler = function_expr([raw, payload], *action(DomEvent(raw, payload))._statements)
        return DomListener(
            self._local(_dom_call("listener", target, literal(event), handler, literal(capture), self._controller))
        )


_Setup = Callable[[DomElement, DomScope], DomLifecycle]


_RENDER_TIME_NAMES: Final = frozenset({MODEL_IDENT, MESSAGE_IDENT})


def _reads_render_time_value(node: ESTreeNode, bound: set[int]) -> bool:
    """Whether the node refers to the model, a message, or a binding from the enclosing view."""
    return any(
        id(ref) not in bound if isinstance(ref, ESTreeGeneratedIdentifier) else ref.name in _RENDER_TIME_NAMES
        for ref in identifiers(node)
    )


def _validate_scoped_effect(key: str, run: ESTreeExpression, inputs: Sequence[ESTreeExpression]) -> None:
    """Keep render-time values and effect-local bindings on their own side of `DomScope.input()`.

    A scoped effect is installed once and keeps its closures, so a render-time value read directly
    inside it would stay at its first value. Inputs are evaluated during rendering, so they cannot
    see bindings that only exist inside the effect.
    """
    bound = {id(ref) for ref in bound_generated_identifiers(run)}
    if _reads_render_time_value(run, bound):
        raise ValueError(
            f"The setup of scoped effect {key!r} reads a render-time value, such as a model field or an item "
            "of a mapped view, directly. The effect is installed once, so that value would never update. "
            "Read it through DomScope.input() instead."
        )
    for position, value in enumerate(inputs):
        if any(id(ref) in bound for ref in generated_identifiers(value)):
            raise ValueError(
                f"DomScope.input() #{position + 1} of effect {key!r} refers to a value created inside the effect, "
                "such as another input or a scope value. Inputs are evaluated during rendering, so pass a "
                "render-time expression and derive effect-local values inside the effect instead."
            )


class DomEffect:
    """Run an element-scoped action when a view mounts and dependencies change.

    Set `watch_subtree` to also run after DOM patches to the element or its
    children. By default actions run after connection in a microtask. Set
    `after_connect=False` to run synchronously once props and children are ready.
    """

    def __init__(
        self,
        key: str,
        update: _ElementAction,
        *,
        dependencies: Sequence[_Dependency] = (),
        watch_subtree: bool = False,
        after_connect: bool = True,
        mount: _ElementAction | None = None,
        dispose: _ElementAction | None = None,
    ) -> None:
        self._key = key
        self._update = update
        self._dependencies = dependencies
        self._watch_subtree = watch_subtree
        self._after_connect = after_connect
        self._mount = mount
        self._dispose = dispose
        self._setup: _Setup | None = None

    @property
    def key(self) -> str:
        """Identify this effect within an element's lifetime."""
        return self._key

    @classmethod
    def scoped(cls, key: str, setup: _Setup, *, watch_subtree: bool = False, after_connect: bool = True) -> DomEffect:
        """Install local state and listeners once per element, with automatic cleanup."""
        effect = cls(key, lambda _: DomAction(), watch_subtree=watch_subtree, after_connect=after_connect)
        effect._setup = setup
        return effect

    def _compile_setup(self, setup: _Setup) -> tuple[ESTreeExpression, ESTreeArrayExpression]:
        root, scope = ESTreeGeneratedIdentifier(), DomScope()
        actions = setup(DomElement(root), scope)
        inputs = [ref for ref, _ in scope._inputs]
        hooks: dict[str, ESTreeExpression] = {}
        if inputs or actions.update is not None:
            latest = [ESTreeGeneratedIdentifier() for _ in inputs]
            # Installed callbacks share the input bindings throughout the effect's lifetime.
            refresh = (
                ESTreeExpressionStatement(ESTreeAssignmentExpression(ref, value))
                for ref, value in zip(inputs, latest, strict=True)
            )
            update = actions.update._statements if actions.update is not None else ()
            hooks["update"] = function_expr(latest, *refresh, *update)
        cleanup = DomAction.batch(*scope._cleanup, actions.dispose or DomAction())
        if cleanup._statements:
            hooks["dispose"] = function_expr([], *cleanup._statements)
        mount = actions.mount._statements if actions.mount is not None else ()
        run = function_expr(
            [root, *inputs], *scope._declarations, *mount, ESTreeReturnStatement(object_expr(hooks.items()))
        )
        values = [value for _, value in scope._inputs]
        _validate_scoped_effect(self._key, run, values)
        return run, ESTreeArrayExpression(values)

    def __compile__(self) -> ESTreeExpression:
        def hook(callback: _ElementAction) -> ESTreeExpression:
            root = ESTreeGeneratedIdentifier()
            return function_expr([root], *callback(DomElement(root))._statements)

        if self._setup is None:
            run = hook(self._update)
            args = ESTreeArrayExpression([ensure_expr(value) for value in self._dependencies])
        else:
            run, args = self._compile_setup(self._setup)

        props = {
            "key": literal(self._key),
            "args": args,
            "refresh": literal(self._watch_subtree),
            "sync": literal(not self._after_connect),
            "run": run,
        }
        if self._mount is not None:
            props["mount"] = hook(self._mount)
        if self._dispose is not None:
            props["dispose"] = hook(self._dispose)
        return object_expr(props.items())


class DomEvent:
    """A browser event available during synchronous view event handling."""

    def __init__(self, _event: ESTreeExpression, _payload: ESTreeExpression) -> None:
        self._event = _event
        self._payload = _payload

    @property
    def target(self) -> DomElement:
        return DomElement(_dom_call("element", member_expr(self._event, "target")))

    @property
    def current_target(self) -> DomElement:
        return DomElement(_dom_call("element", member_expr(self._event, "currentTarget")))

    @property
    def related_target(self) -> DomElement:
        return DomElement(_dom_call("element", member_expr(self._event, "relatedTarget")))

    @property
    def detail_text(self) -> Expr[str | None]:
        return Expr(_dom_call("detailText", self._event))

    def _value(self, name: str, kind: Literal["string", "number"]) -> ESTreeExpression:
        return _dom_call("eventValue", self._event, literal(name), literal(kind))

    def _flag(self, name: str) -> Expr[bool]:
        return Expr(ESTreeBinaryExpression("===", member_expr(self._event, name), literal(True)))

    @property
    def key(self) -> Expr[str | None]:
        return Expr(self._value("key", "string"))

    @property
    def alt(self) -> Expr[bool]:
        return self._flag("altKey")

    @property
    def ctrl(self) -> Expr[bool]:
        return self._flag("ctrlKey")

    @property
    def meta(self) -> Expr[bool]:
        return self._flag("metaKey")

    @property
    def default_prevented(self) -> Expr[bool]:
        return self._flag("defaultPrevented")

    @property
    def shift(self) -> Expr[bool]:
        return self._flag("shiftKey")

    @property
    def button(self) -> Expr[int | None]:
        return Expr(self._value("button", "number"))

    @property
    def client_x(self) -> Expr[int | float | None]:
        return Expr(self._value("clientX", "number"))

    @property
    def client_y(self) -> Expr[int | float | None]:
        return Expr(self._value("clientY", "number"))

    @property
    def new_state(self) -> Expr[str | None]:
        return Expr(_dom_call("toggleState", self._event))

    @property
    def pointer_type(self) -> Expr[str | None]:
        return Expr(self._value("pointerType", "string"))

    @property
    def is_composing(self) -> Expr[bool]:
        return self._flag("isComposing")

    @property
    def key_code(self) -> Expr[int | None]:
        return Expr(self._value("keyCode", "number"))

    def stop_propagation(self) -> DomAction:
        return _action(call(member_expr(self._event, "stopPropagation")))

    def prevent_default(self) -> DomAction:
        return _action(call(member_expr(self._event, "preventDefault")))


class DomKeyboardEvent(DomEvent):
    """Event reference for a validated keyboard event."""

    @property
    def key(self) -> Expr[str]:
        return Expr(member_expr(self._payload, "key"))

    @property
    def code(self) -> Expr[str]:
        return Expr(member_expr(self._payload, "code"))

    @property
    def repeat(self) -> Expr[bool]:
        return Expr(member_expr(self._payload, "repeat"))


class DomPointerEvent(DomEvent):
    """Event reference for a validated mouse or pointer event."""

    @property
    def button(self) -> Expr[int]:
        return Expr(member_expr(self._payload, "button"))

    @property
    def client_x(self) -> Expr[int | float]:
        return Expr(member_expr(self._payload, "client_x"))

    @property
    def client_y(self) -> Expr[int | float]:
        return Expr(member_expr(self._payload, "client_y"))


class DomInputEvent(DomEvent):
    """Event reference exposing normalized input control values."""

    @property
    def value(self) -> Expr[str]:
        return Expr(member_expr(self._payload, "value"))

    @property
    def checked(self) -> Expr[bool]:
        return Expr(member_expr(self._payload, "checked"))


_DomEventT = TypeVar("_DomEventT", bound=DomEvent)
_PayloadT = TypeVar("_PayloadT")
# Method-scoped: class-level variables of `EventBinding` are not solved in its staticmethods.
_OnGroupT = TypeVar("_OnGroupT", bound=MsgGroup)


class DomEventType(Generic[_DomEventT, _PayloadT]):
    """A native event name and its callback and message types."""

    def __init__(
        self,
        name: str,
        _reference: type[_DomEventT],
        _accepts: Callable[[DomEvent], Expr[bool]] | None = None,
    ) -> None:
        self._name = name
        self._reference = _reference
        self._accepts = _accepts

    @property
    def name(self) -> str:
        return self._name

    def _read(self, event: DomEvent) -> _DomEventT:
        return self._reference(event._event, event._payload)

    def _listener(self, action: Callable[[_DomEventT], DomAction]) -> Callable[[DomEvent], DomAction]:
        def handle(event: DomEvent) -> DomAction:
            result = action(self._read(event))
            if self._accepts is not None:
                return DomAction.when(self._accepts(event), result)
            return result

        return handle


def _keyboard_event(name: str) -> DomEventType[DomKeyboardEvent, KeyboardEvent]:
    return DomEventType(name, DomKeyboardEvent, lambda event: Cond.not_equal(event.key, None))


def _pointer_event(name: str) -> DomEventType[DomPointerEvent, PointerEvent]:
    return DomEventType(
        name,
        DomPointerEvent,
        lambda event: Cond.every(
            Cond.not_equal(event.client_x, None),
            Cond.not_equal(event.client_y, None),
            Cond.not_equal(event.button, None),
        ),
    )


class DomEvents:
    """Typed descriptors for common native events."""

    key_down: ClassVar[DomEventType[DomKeyboardEvent, KeyboardEvent]] = _keyboard_event("keydown")
    key_up: ClassVar[DomEventType[DomKeyboardEvent, KeyboardEvent]] = _keyboard_event("keyup")
    click: ClassVar[DomEventType[DomPointerEvent, PointerEvent]] = _pointer_event("click")
    double_click: ClassVar[DomEventType[DomPointerEvent, PointerEvent]] = _pointer_event("dblclick")
    mouse_down: ClassVar[DomEventType[DomPointerEvent, PointerEvent]] = _pointer_event("mousedown")
    context_menu: ClassVar[DomEventType[DomPointerEvent, PointerEvent]] = _pointer_event("contextmenu")
    pointer_enter: ClassVar[DomEventType[DomPointerEvent, PointerEvent]] = _pointer_event("pointerenter")
    pointer_leave: ClassVar[DomEventType[DomPointerEvent, PointerEvent]] = _pointer_event("pointerleave")
    input: ClassVar[DomEventType[DomInputEvent, InputEvent]] = DomEventType("input", DomInputEvent)
    change: ClassVar[DomEventType[DomInputEvent, InputEvent]] = DomEventType("change", DomInputEvent)
    submit: ClassVar[DomEventType[DomEvent, SubmitEvent]] = DomEventType("submit", DomEvent)
    focus: ClassVar[DomEventType[DomEvent, FocusEvent]] = DomEventType("focus", DomEvent)
    blur: ClassVar[DomEventType[DomEvent, FocusEvent]] = DomEventType("blur", DomEvent)


DomFocusError = Literal["not_found", "not_focusable"]


@dataclass(frozen=True, slots=True)
class _FocusTask(TaskLike[None, DomFocusError]):
    element_id: str | Expr[str]
    prevent_scroll: bool

    def __compile__(self) -> ESTreeExpression:
        return _dom_call("focusById", ensure_expr(self.element_id), literal(self.prevent_scroll))


class Dom:
    """DOM tasks that an application can request from its update."""

    @staticmethod
    def focus(element_id: str | Expr[str], *, prevent_scroll: bool = False) -> TaskLike[None, DomFocusError]:
        """Focus a document element after rendering. Missing or unfocusable elements fail the task."""
        return _FocusTask(element_id, prevent_scroll)


# A message that an event handler can dispatch. The handler dispatches it as is, so a message
# that needs a context must be bound first. It may ignore the event (`Msg[None]`) or accept it
# optionally (`Msg[E | None]`), as an Elm `onClick Increment` would.
EventMessage: TypeAlias = (
    GroupedMsg[MsgGroupT, OptionalEventT, None]
    | GroupedMsg[MsgGroupT, OptionalEventT | None, None]
    | GroupedMsg[MsgGroupT, None, None]
)


class EventBinding(Generic[MsgGroupT, OptionalEventT]):
    """Combine synchronous DOM actions and an optional Fleur message.

    The predicate gates the entire binding. Cancellation and actions run before
    message dispatch. Extra payload fields augment the normalized event.
    """

    def __init__(
        self,
        message: EventMessage[MsgGroupT, OptionalEventT] | None = None,
        *,
        when: Callable[[DomEvent], Expr[bool]] | None = None,
        prevent_default: bool | Expr[bool] = False,
        action: Callable[[DomEvent], DomAction] | None = None,
        payload: Callable[[DomEvent], Mapping[str, _Dependency]] | None = None,
    ) -> None:
        self._message = message
        self._when = when
        self._prevent_default = prevent_default
        self._action = action
        self._payload = payload

    @staticmethod
    def on(
        event: DomEventType[_DomEventT, _PayloadT],
        message: EventMessage[_OnGroupT, _PayloadT] | None = None,
        *,
        when: Callable[[_DomEventT], Expr[bool]] | None = None,
        prevent_default: bool | Expr[bool] = False,
        action: Callable[[_DomEventT], DomAction] | None = None,
        capture: bool = False,
    ) -> dict[str, EventBinding[_OnGroupT, _PayloadT]]:
        """Bind a native event with matching types for the action and the message."""

        def accepts(ref: DomEvent) -> Expr[bool]:
            valid = event._accepts(ref) if event._accepts is not None else True
            return Cond.every(valid, when(event._read(ref)) if when is not None else True)

        return EventBinding(
            message,
            when=accepts,
            prevent_default=prevent_default,
            action=(lambda ref: action(event._read(ref))) if action is not None else None,
        ).properties(event.name, capture=capture)

    def properties(self, event: str, *, capture: bool = False) -> dict[str, EventBinding[MsgGroupT, OptionalEventT]]:
        """Make a view prop for the given native event and propagation phase."""
        return {("onCapture:" if capture else "on") + event: self}

    def __compile__(self) -> ESTreeExpression:
        payload, element, event = (ESTreeGeneratedIdentifier() for _ in range(3))
        ref = DomEvent(event, payload)
        statements: list[ESTreeStatement] = []
        if self._when is not None:
            statements.append(
                if_stmt(Boolean.negate(self._when(ref)).__compile__(), ESTreeReturnStatement(literal(None)))
            )
        if self._prevent_default is not False:
            statements.extend(DomAction.when(self._prevent_default, ref.prevent_default())._statements)
        if self._action is not None:
            statements.extend(self._action(ref)._statements)
        if self._message is not None:
            message_payload: ESTreeExpression = payload
            if self._payload is not None:
                extra = object_expr((key, ensure_expr(value)) for key, value in self._payload(ref).items())
                message_payload = call(member_expr(ident("Object"), "assign"), object_expr([]), payload, extra)
            statements.append(ESTreeReturnStatement(call(self._message.__compile__(), message_payload)))
        return function_expr([payload, element, event], *statements)
