import json
from collections.abc import Callable

from fleur import Boolean, Component, Cond, Expr, Model, Msg, MsgGroup, Page, State, bloom, emit
from fleur.core import PointerEvent
from fleur.ui import Box, Button, Grid, GridItem, ThemeScope, css
from fleur.ui.views.types import Length, StyleMap, ViewStyleArgs


class Layout(Model):
    compact: State[bool]


class Actions(MsgGroup):
    RESIZE: Msg[PointerEvent] = Msg()


def test_grid_defaults_do_not_emit_inline_styles() -> None:
    for view, kind in [(Grid(), "grid"), (GridItem(), "grid-item")]:
        source = emit(view.__compile__())
        assert f'"data-fleur-ui": "{kind}"' in source
        assert "style:" not in source


def test_grid_cascade_geometry_and_padding(chromium_title: Callable[[str], str]) -> None:
    columns = Cond.when(Layout.compact, 4, 3)
    minimum = Cond.when(Layout.compact, 160, 120)
    span = Cond.when(Layout.compact, 3, 2)

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
    view = Box(
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
        style={"width": Cond.when(Layout.compact, "360px", "480px")},
    )
    app = Component(
        Layout(compact=False),
        Actions.cases(Actions.RESIZE.then(State.set(Layout.compact, Boolean.negate(Layout.compact)))),
        view,
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
