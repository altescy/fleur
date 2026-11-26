"""Switch the theme and mode around a controlled input."""

from typing import Literal

from fleur import Component, Cond, Expr, Model, Msg, MsgGroup, State
from fleur.core import InputEvent, PointerEvent
from fleur.core.view import ViewProps
from fleur.ui import BASIC_THEME, ZEN_THEME, Button, HStack, Input, Text, Theme, ThemeMode, ThemeScope, VStack

Preset = Literal["basic", "zen"]
PRESETS: dict[Preset, Theme] = {"basic": BASIC_THEME, "zen": ZEN_THEME}


class PreviewModel(Model):
    preset: State[Preset]
    mode: State[ThemeMode]
    name: State[str]


class PreviewMsg(MsgGroup):
    SELECT_PRESET: Msg[PointerEvent, Preset] = Msg()
    SELECT_MODE: Msg[PointerEvent, ThemeMode] = Msg()
    ENTER_NAME: Msg[InputEvent] = Msg()


def _selection_props(selected: Expr[bool]) -> ViewProps:
    return {
        "aria-pressed": Cond.when(selected, "true", "false"),
        "style": {
            "border-color": Cond.when(selected, "var(--fleur-color-primary)", "var(--fleur-color-border)"),
        },
    }


def app() -> Component[PreviewModel, PreviewMsg]:
    return Component(
        PreviewModel(preset="basic", mode="light", name=""),
        PreviewMsg.cases(
            PreviewMsg.SELECT_PRESET.then(State.set(PreviewModel.preset, PreviewMsg.SELECT_PRESET.context)),
            PreviewMsg.SELECT_MODE.then(State.set(PreviewModel.mode, PreviewMsg.SELECT_MODE.context)),
            PreviewMsg.ENTER_NAME.then(State.set(PreviewModel.name, PreviewMsg.ENTER_NAME.event.value)),
        ),
        VStack(
            ThemeScope(
                VStack(
                    Text("Theme preview", font_size="xl", font_weight=700),
                    HStack(
                        *(
                            Button(
                                preset.title(),
                                variant="secondary",
                                props=_selection_props(Cond.equal(PreviewModel.preset, preset)),
                                onclick=PreviewMsg.SELECT_PRESET.bind(preset),
                            )
                            for preset in PRESETS
                        ),
                        props={"role": "group", "aria-label": "Theme"},
                        gap="xs",
                    ),
                    HStack(
                        *(
                            Button(
                                mode.title(),
                                variant="secondary",
                                props=_selection_props(Cond.equal(PreviewModel.mode, mode)),
                                onclick=PreviewMsg.SELECT_MODE.bind(mode),
                            )
                            for mode in ("light", "dark")
                        ),
                        props={"role": "group", "aria-label": "Color mode"},
                        gap="xs",
                    ),
                    Input(
                        value=PreviewModel.name,
                        placeholder="Your name",
                        oninput=PreviewMsg.ENTER_NAME,
                        props={"aria-label": "Your name"},
                    ),
                    Text(
                        Cond.when(
                            Cond.equal(PreviewModel.name, ""),
                            "Type a name, then switch themes.",
                            "Hello, " + PreviewModel.name,
                        ),
                        fg="muted-foreground",
                    ),
                    gap="sm",
                ),
                theme=Theme.select(PreviewModel.preset, PRESETS),
                mode=PreviewModel.mode,
                p="lg",
                radius="md",
                border="1px solid var(--fleur-color-border)",
            ),
            mx="md",
            my="lg",
            max_w=420,
        ),
    )
