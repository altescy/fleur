from collections.abc import Callable

from fleur.builtins import Http, HttpError, HttpResponse
from fleur.core import (
    Array,
    Boolean,
    Cmd,
    Component,
    Cond,
    Expr,
    Model,
    ModelUpdate,
    Msg,
    MsgGroup,
    Number,
    Object,
    State,
    String,
    Sub,
    TaskLike,
    Update,
    View,
)
from fleur.core.template import (
    BloomContext,
    Page,
    TemplateInput,
    render_app,
    render_head,
    render_script,
    render_template,
)
from fleur.js.emitter import EmitterSettings, emit
from fleur.ui import DEFAULT_THEME, Theme, apply_theme


def bloom(
    component: Component | Callable[[], Component],
    *,
    page: Page | None = None,
    theme: Theme | None = None,
    template: TemplateInput | None = None,
    component_name: str | None = None,
) -> str:
    from pathlib import Path

    fleur_js_path = Path(__file__).parent / "assets" / "fleur.js"
    runtime_js = fleur_js_path.read_text()

    resolved_page = apply_theme(page or Page(), theme if theme is not None else DEFAULT_THEME)

    component_js = emit((component() if callable(component) else component).__compile__())
    context = BloomContext(
        page=resolved_page,
        component_name=component_name or getattr(component, "__name__", "App"),
        component_js=component_js,
        runtime_js=runtime_js,
        head_html=render_head(resolved_page),
        app_html=render_app(resolved_page),
        script_js=render_script(component_js=component_js, runtime_js=runtime_js, page=resolved_page),
    )

    return render_template(template, context)


__all__ = [
    "Array",
    "Boolean",
    "Cmd",
    "Component",
    "Cond",
    "Expr",
    "Model",
    "ModelUpdate",
    "Msg",
    "MsgGroup",
    "Number",
    "Object",
    "State",
    "Sub",
    "String",
    "TaskLike",
    "Update",
    "View",
    "Page",
    "EmitterSettings",
    "Http",
    "HttpError",
    "HttpResponse",
    "bloom",
    "emit",
]
