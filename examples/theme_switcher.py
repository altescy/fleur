"""Switch the theme and mode around a controlled input."""

from typing import Literal

from fleur import Component, Cond, Model, Msg, MsgGroup, State
from fleur.core import InputEvent
from fleur.ui import BASIC_THEME, ZEN_THEME, Input, RadioGroup, Text, Theme, ThemeMode, ThemeScope, VStack

Preset = Literal["basic", "zen"]
PRESETS: dict[Preset, Theme] = {"basic": BASIC_THEME, "zen": ZEN_THEME}


class PreviewModel(Model):
    preset: State[Preset]
    mode: State[ThemeMode]
    name: State[str]


class PreviewMsg(MsgGroup):
    SELECT_PRESET: Msg[InputEvent, Preset] = Msg()
    SELECT_MODE: Msg[InputEvent, ThemeMode] = Msg()
    ENTER_NAME: Msg[InputEvent] = Msg()


def app() -> Component[PreviewModel, PreviewMsg]:
    presets: dict[Preset, str] = {preset: preset.title() for preset in PRESETS}
    modes: dict[ThemeMode, str] = {"light": "Light", "dark": "Dark"}
    return Component(
        PreviewModel(preset="basic", mode="light", name=""),
        update=lambda _: PreviewMsg.cases(
            PreviewMsg.SELECT_PRESET.then(lambda _, preset: State.set(PreviewModel.preset, preset)),
            PreviewMsg.SELECT_MODE.then(lambda _, mode: State.set(PreviewModel.mode, mode)),
            PreviewMsg.ENTER_NAME.then(lambda event: State.set(PreviewModel.name, event.value)),
        ),
        view=lambda model: VStack(
            ThemeScope(
                VStack(
                    Text("Theme preview", font_size="xl", font_weight=700),
                    RadioGroup(
                        presets,
                        name="preview-theme",
                        label="Theme",
                        value=model.preset,
                        onselect=PreviewMsg.SELECT_PRESET,
                    ),
                    RadioGroup(
                        modes,
                        name="preview-mode",
                        label="Color mode",
                        value=model.mode,
                        onselect=PreviewMsg.SELECT_MODE,
                    ),
                    Input(
                        value=model.name,
                        placeholder="Your name",
                        oninput=PreviewMsg.ENTER_NAME,
                        props={"aria-label": "Your name"},
                    ),
                    Text(
                        Cond.when(
                            Cond.equal(model.name, ""),
                            "Type a name, then switch themes.",
                            "Hello, " + model.name,
                        ),
                        fg="muted-foreground",
                    ),
                    gap="sm",
                ),
                theme=Theme.select(model.preset, PRESETS),
                mode=model.mode,
                p="lg",
                radius="md",
                border="1px solid var(--fleur-color-border)",
            ),
            mx="md",
            my="lg",
            max_w=420,
        ),
    )
