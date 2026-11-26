from collections.abc import Callable
from pathlib import Path

from fleur import Component, Model, Msg, MsgGroup, State, bloom
from fleur.core import PointerEvent
from fleur.ui import Avatar, Button, HStack, Text, VStack


class Screen(Model):
    source: State[str | None]


class Actions(MsgGroup):
    REPLACE: Msg[PointerEvent] = Msg()
    CLEAR: Msg[PointerEvent] = Msg()


def test_avatar_preserves_name_and_layout_during_image_updates(playwright_page: Callable[[str, Path], str]) -> None:
    app = Component(
        Screen(source="https://avatars.example.test/portrait.gif"),
        Actions.cases(
            Actions.REPLACE.then(State.set(Screen.source, "https://avatars.example.test/missing.gif")),
            Actions.CLEAR.then(State.set(Screen.source, None)),
        ),
        VStack(
            HStack(Avatar(name="Lead reviewer", fallback="LR", src=Screen.source), Text("The Secret Garden"), gap="sm"),
            HStack(Avatar(name=None, fallback="SR"), Text("Second reviewer"), gap="sm"),
            Button("Replace photo", onclick=Actions.REPLACE),
            Button("Remove photo", onclick=Actions.CLEAR),
        ),
    )
    playwright_page(bloom(app), Path(__file__).with_name("avatar.cjs"))
