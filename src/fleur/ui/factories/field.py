from collections.abc import Callable, Mapping
from typing import Unpack

from fleur.core.cond import Cond
from fleur.core.expr import Expr
from fleur.core.types import ModelT, MsgGroupT
from fleur.core.view import View, ViewProp, ViewProps
from fleur.ui.views._utils import merge_props
from fleur.ui.views.types import String, ViewStyleArgs


def field(
    *,
    id: String,
    label: String,
    control: Callable[[Mapping[str, ViewProp]], View[ModelT, MsgGroupT]],
    description: String | None = None,
    error: str | Expr[str | None] | None = None,
    props: ViewProps | None = None,
    **style_args: Unpack[ViewStyleArgs],
) -> View[ModelT, MsgGroupT]:
    """Pass the associated id and ARIA attributes to the control's native input."""
    attrs: dict[str, ViewProp] = {"id": id}
    label_view = View(label, tag="label", props={"for": id, "data-fleur-part": "label"})
    messages: list[View[ModelT, MsgGroupT]] = []
    description_id = None
    if description is not None:
        description_id = id + "-description"
        attrs["aria-describedby"] = description_id
        messages.append(View(description, tag="span", props={"id": description_id, "data-fleur-part": "description"}))

    if isinstance(error, Expr) or error:
        error_id = id + "-error"
        described_by = description_id + " " + error_id if description_id is not None else error_id
        error_props: dict[str, ViewProp] = {"id": error_id, "data-fleur-part": "error"}
        if isinstance(error, Expr):
            empty = Cond.some(Cond.equal(error, ""), Cond.equal(error, None))
            attrs["aria-invalid"] = Cond.when(empty, None, "true")
            attrs["aria-describedby"] = Cond.when(empty, description_id, described_by)
            error_props["hidden"] = empty
        else:
            attrs.update({"aria-invalid": "true", "aria-describedby": described_by})
        messages.append(View(error, tag="span", props=error_props))

    return View(
        label_view, control(attrs), *messages, tag="div", props=merge_props(props, element="field", **style_args)
    )
