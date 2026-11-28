import json
from collections.abc import Callable
from typing import Literal

from fleur import Boolean, Component, Cond, Expr, Model, Msg, MsgGroup, Page, State, View, bloom, emit
from fleur.core import PointerEvent
from fleur.ui import Box, Button, Grid, GridItem, ThemeScope, css
from fleur.ui.views.types import Length, StyleMap, ViewStyleArgs


class Layout(Model):
    compact: State[bool]


class Actions(MsgGroup):
    RESIZE: Msg[PointerEvent] = Msg()


class Dimensions(Model):
    width: State[Literal["full", "fit", "lg", "2/3"] | int]


class DimensionActions(MsgGroup):
    SET_WIDTH: Msg[PointerEvent, Literal["full", "fit", "lg", "2/3"] | int] = Msg()


def test_dimension_margin_and_overflow_shorthands(chromium_title: Callable[[str], str]) -> None:
    app = Component(
        init=Dimensions(width="full"),
        update=lambda _: DimensionActions.cases(
            DimensionActions.SET_WIDTH.then(lambda _, context: State.set(Dimensions.width, context)),
        ),
        view=lambda model: ThemeScope(
            Button("Token", onclick=DimensionActions.SET_WIDTH.bind("lg"), props={"id": "token"}),
            Button("Pixels", onclick=DimensionActions.SET_WIDTH.bind(80), props={"id": "pixels"}),
            Button("Fit", onclick=DimensionActions.SET_WIDTH.bind("fit"), props={"id": "fit"}),
            Button("Fraction", onclick=DimensionActions.SET_WIDTH.bind("2/3"), props={"id": "fraction"}),
            Button("Full", onclick=DimensionActions.SET_WIDTH.bind("full"), props={"id": "reset"}),
            Box(
                Box(w="full", h="full", props={"id": "full"}),
                Box(w=80, min_w="full", props={"id": "minimum"}),
                Box(w=640, max_w="full", props={"id": "maximum"}),
                Box(w=css("min(100%, 120px)"), props={"id": "expression"}),
                Box(Box(w=56), w=model.width, props={"id": "dynamic"}),
                Box(Box(w=88), w="fit", props={"id": "intrinsic"}),
                Box(w=100, mx="auto", min_h=css("30px"), props={"id": "centered"}),
                Box(Box(w=600, h=1), w=160, overflow_x="auto", props={"id": "scroll"}),
                Box(w="1/2", h="1/2", props={"className": "fraction"}),
                Box(w="1/3", props={"className": "fraction"}),
                Box(w="2/3", props={"className": "fraction"}),
                Box(w="1/4", props={"className": "fraction"}),
                Box(w="3/4", props={"className": "fraction"}),
                Box(Box(h=200, w=1), max_h="1/2", overflow_y="auto", props={"id": "vertical"}),
                w=360,
                h=120,
                props={"id": "container"},
            ),
            space={"lg": 24},
        ),
    )
    probe = """<script>
    const get = id => document.getElementById(id);
    const bounds = id => get(id).getBoundingClientRect();
    const result = {
      full: [bounds("full").width, bounds("full").height],
      minimum: bounds("minimum").width,
      maximum: bounds("maximum").width,
      expression: bounds("expression").width,
      dynamic: [bounds("dynamic").width],
      intrinsic: bounds("intrinsic").width,
      centered: [bounds("centered").left - bounds("container").left, bounds("centered").height],
      scroll: [getComputedStyle(get("scroll")).overflowX, get("scroll").clientWidth, get("scroll").scrollWidth],
      fractions: Array.from(document.querySelectorAll(".fraction"), el => el.getBoundingClientRect().width),
      halfHeight: document.querySelector(".fraction").getBoundingClientRect().height,
    };
    const vertical = get("vertical");
    vertical.scrollTop = 20;
    result.vertical = [getComputedStyle(vertical).overflowY, vertical.clientHeight, vertical.scrollHeight, vertical.scrollTop];
    for (const id of ["token", "pixels", "fit", "fraction", "reset"]) {
      get(id).click();
      result.dynamic.push(bounds("dynamic").width);
    }
    document.title = JSON.stringify(result);
    </script>"""
    html = bloom(app)
    assert json.loads(chromium_title(html.replace("</body>", probe + "</body>"))) == {
        "full": [360, 120],
        "minimum": 360,
        "maximum": 360,
        "expression": 120,
        "dynamic": [360, 24, 80, 56, 240, 360],
        "intrinsic": 88,
        "centered": [130, 30],
        "scroll": ["auto", 160, 600],
        "fractions": [180, 120, 240, 90, 270],
        "halfHeight": 60,
        "vertical": ["auto", 60, 200, 20],
    }


def test_wrapping_shorthands(chromium_title: Callable[[str], str]) -> None:
    app = Component(
        init=Model(),
        update=lambda _: MsgGroup.cases(),
        view=lambda _: Box(
            Box("Keep these words together", white_space="nowrap", props={"id": "nowrap"}),
            Box("VeryLongUninterruptedDescription", overflow_wrap="anywhere", props={"id": "wrap"}),
            w=64,
        ),
    )
    probe = """<script>
    const singleLine = document.getElementById("nowrap");
    const wraps = document.getElementById("wrap");
    document.title = JSON.stringify([
      getComputedStyle(singleLine).whiteSpace,
      getComputedStyle(wraps).overflowWrap,
      singleLine.scrollWidth > singleLine.clientWidth,
      wraps.scrollWidth === wraps.clientWidth,
      wraps.clientHeight > singleLine.clientHeight,
    ]);
    </script>"""
    html = bloom(app)
    assert json.loads(chromium_title(html.replace("</body>", probe + "</body>"))) == [
        "nowrap",
        "anywhere",
        True,
        True,
        True,
    ]


def test_grid_defaults_do_not_emit_inline_styles() -> None:
    for view, kind in [(Grid(), "grid"), (GridItem(), "grid-item")]:
        source = emit(view.__compile__())
        assert f'"data-fleur-ui": "{kind}"' in source
        assert "style:" not in source


def test_grid_cascade_geometry_and_padding(chromium_title: Callable[[str], str]) -> None:
    def example(
        label: str,
        *,
        columns: int | Expr[int] | None = None,
        min_col: Length | None = None,
        col_span: int | Expr[int] | None = None,
        grid_style: StyleMap | None = None,
        item_style: StyleMap | None = None,
    ) -> Grid[Layout, Actions]:
        return Grid(
            GridItem(
                "A",
                props={"className": "place"},
                col_span=col_span,
                style=item_style,
            ),
            *(GridItem(str(n)) for n in range(6)),  # Keep auto-fit tracks occupied.
            props={"id": label, "className": "tracks"},
            columns=columns,
            min_col=min_col,
            style=grid_style,
        )

    paddings: list[tuple[ViewStyleArgs, list[int]]] = [
        ({}, [1] * 4),
        ({"p": "lg"}, [16] * 4),
        ({"px": "md", "p": "lg"}, [16, 8, 16, 8]),
        ({"p": "lg", "px": "md", "pl": "sm"}, [16, 8, 16, 4]),
        ({"pl": "sm", "px": "md", "p": "lg"}, [16, 8, 16, 4]),
        ({"pl": "sm", "p": "lg", "px": "md", "style": {"padding-left": "12px"}}, [16, 8, 16, 12]),
        ({"p": "lg", "px": "md", "pl": "sm", "style": {"padding": "3px"}}, [3] * 4),
    ]
    six_columns = {"grid-template-columns": "repeat(6, 1fr)"}
    single_column = {"grid-column": "span 1"}

    def view(model: Layout) -> View[Layout, Actions]:
        columns = Cond.when(model.compact, 4, 3)
        minimum = Cond.when(model.compact, 160, 120)
        span = Cond.when(model.compact, 3, 2)
        return Box(
            Button("Resize", props={"id": "resize"}, onclick=Actions.RESIZE),
            Grid(GridItem("A"), GridItem("B"), props={"id": "default"}),
            Grid(props={"id": "block", "className": "block"}),
            example("class-only"),
            example("fixed", columns=columns, col_span=span),
            example("auto", min_col=minimum, col_span=1),
            example("responsive", min_col=120, col_span=1),
            example("both", columns=columns, min_col=css("300px"), col_span=span),
            example("fixed-style", columns=columns, col_span=span, grid_style=six_columns),
            example("item-style", columns=columns, col_span=span, item_style=single_column),
            example("auto-style", min_col=minimum, col_span=span, grid_style=six_columns, item_style=single_column),
            ThemeScope(
                *(
                    Grid(GridItem("A", props={"className": "padded"}, **args), props={"className": "padded"}, **args)
                    for args, _ in paddings
                ),
                space={"lg": 16, "md": 8, "sm": 4},
            ),
            style={"width": Cond.when(model.compact, "360px", "480px")},
        )

    app = Component(
        init=Layout(compact=False),
        update=lambda model: Actions.cases(
            Actions.RESIZE.then(State.set(Layout.compact, Boolean.negate(model.compact)))
        ),
        view=view,
    )
    page = Page(
        extra_head_html=[
            "<style>.tracks{grid-template-columns:repeat(2,1fr)}.place{grid-column:1/-1}.block{display:block}.padded{padding:1px}</style>"
        ]
    )
    html = bloom(app, page=page)
    probe = """<script>
    function snapshot() {
      const grids = Array.from(document.querySelectorAll("#default,.tracks"), grid => {
        const tracks = getComputedStyle(grid).gridTemplateColumns.split(" ").map(parseFloat);
        return [grid.id, tracks, grid.firstElementChild.getBoundingClientRect().width];
      });
      const padding = Array.from(document.querySelectorAll(".padded"), el => {
        const s = getComputedStyle(el);
        return [s.paddingTop, s.paddingRight, s.paddingBottom, s.paddingLeft].map(parseFloat);
      });
      return {grids, padding, display: getComputedStyle(document.getElementById("block")).display};
    }
    const snapshots = [snapshot()];
    document.getElementById("resize").click();
    snapshots.push(snapshot());
    document.getElementById("resize").click();
    snapshots.push(snapshot());
    document.title = JSON.stringify(snapshots);
    </script>"""
    initial, compact, restored = json.loads(chromium_title(html.replace("</body>", probe + "</body>")))
    assert restored == initial
    for snapshot, width, fixed, auto, occupied in [(initial, 480, 3, 4, 2), (compact, 360, 4, 2, 3)]:
        assert snapshot["display"] == "block"
        expected = [
            ("default", 1, 1),
            ("class-only", 2, 2),
            ("fixed", fixed, occupied),
            ("auto", auto, 1),
            ("responsive", width // 120, 1),
            ("both", fixed, occupied),
            ("fixed-style", 6, occupied),
            ("item-style", fixed, 1),
            ("auto-style", 6, 1),
        ]
        for (name, tracks, first_width), (label, count, cells) in zip(snapshot["grids"], expected, strict=True):
            assert name == label
            assert tracks == [width / count] * count, label
            assert first_width == cells * width / count, label
        assert snapshot["padding"] == [sides for _, sides in paddings for _element in ("grid", "item")]
