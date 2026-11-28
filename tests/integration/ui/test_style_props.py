import json
import shutil
import subprocess
from collections.abc import Mapping
from pathlib import Path

import pytest

from fleur import Cond, Model, Msg, MsgGroup, State, View, emit
from fleur.core import FocusEvent, InputEvent, record
from fleur.core.model import model_ref
from fleur.core.view import ViewProp, ViewProps
from fleur.js.builder import ident
from fleur.ui import Checkbox, GridItem
from fleur.ui.views._utils import extend_props


class FormModel(Model):
    compact: State[bool]


class FormMsg(MsgGroup):
    FOCUS: Msg[FocusEvent] = Msg()
    CHANGE: Msg[InputEvent] = Msg()


def _model() -> FormModel:
    """The model as a component's view receives it, so that `_model().compact` compiles to `model.compact`."""
    return model_ref(FormModel, ident("model"))


def _controls(compact: bool) -> list[str]:
    regular = {"padding-left": "1px", "padding": "2px", "width": "4rem", "opacity": "0"}
    small = {"padding": "5px", "padding-left": "6px", "width": "3rem"}
    selected = small if compact else regular
    dynamic = Cond.when(_model().compact, record(small), record(regular))
    attrs = {"id": "accept", "className": "user", "data-field": "terms", "onfocus": FormMsg.FOCUS}
    cases: tuple[ViewProps, ...] = (
        {**attrs, "style": selected},
        {**attrs, "style": dynamic},
        record({**attrs, "style": dynamic}),
    )
    return [
        emit(
            Checkbox(
                props=props,
                name="terms",
                onchange=FormMsg.CHANGE,
                bg="primary",
                p=16,
                px=8,
                pl=4,
                style={"padding": "3px", "padding-left": Cond.when(_model().compact, "12px", "9px")},
            ).__compile__()
        )
        for props in cases
    ]


def test_generated_props_match_after_state_changes() -> None:
    runner = shutil.which("node") or shutil.which("bun")
    if runner is None:
        pytest.skip("JavaScript execution requires Node or Bun")
    bundle = Path(__file__).parents[3] / "src/fleur/assets/fleur.js"
    steps = [(compact, _controls(compact)) for compact in (False, True, False)]
    script = """
    require(process.argv[1])
    const steps = JSON.parse(require("node:fs").readFileSync(0, "utf8"))
    const results = steps.map(([compact, sources]) => sources.map(source => {
      const { props } = new Function("model", "return " + source)({ compact })
      const { style, onfocus, onchange, ...attrs } = props
      return [Object.entries(style), attrs, onfocus({type:"focus"}), onchange({type:"change", checked:true})]
    }))
    console.log(JSON.stringify(results))
    """
    result = subprocess.run(
        [runner, "-e", script, str(bundle)], input=json.dumps(steps), text=True, capture_output=True, check=True
    )
    for (compact, _), (static, nested, whole) in zip(steps, json.loads(result.stdout), strict=True):
        assert static == nested == whole
        entries, attrs, focus, change = static
        assert entries[-3:] == [
            ["padding-right", "8px"],
            ["padding", "3px"],
            ["padding-left", "12px" if compact else "9px"],
        ]
        style = dict(entries)
        assert style["--fleur-local-bg"] == "var(--fleur-color-primary)"
        assert style["width"] == ("3rem" if compact else "4rem")
        assert style["height"] == "1rem"
        assert style.get("opacity") == (None if compact else "0")
        assert attrs == {
            "id": "accept",
            "className": "user",
            "data-field": "terms",
            "data-fleur-bg": "",
            "type": "checkbox",
            "name": "terms",
        }
        assert focus == {"type": "FOCUS", "event": {"type": "focus"}, "context": None}
        assert change == {"type": "CHANGE", "event": {"type": "change", "checked": True}, "context": None}


def test_extend_dynamic_attributes_compiles_nested_props_and_events() -> None:
    attrs: Mapping[str, ViewProp] = {"values": [_model().compact], "onfocus": FormMsg.FOCUS}
    props = extend_props({"metadata": attrs}, record({"title": Cond.when(_model().compact, "small", "large")}))
    source = emit(View(tag="div", props=props).__compile__())
    assert "values: [model.compact]" in source
    assert 'type: "FOCUS"' in source
    assert 'title: (model.compact?"small":"large")' in source


def test_grid_layout_precedes_explicit_style_in_declaration_order() -> None:
    item = GridItem(
        props={"style": {"grid-column": "2", "grid-area": "main"}}, col_span=2, style={"grid-column": "1 / -1"}
    )
    source = emit(item.__compile__())
    assert '"grid-area": "main","grid-column": "1 / -1"' in source
