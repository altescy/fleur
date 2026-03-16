from collections.abc import Callable

import fleur.builtins as builtins
from fleur.core import (
    Cmd,
    Component,
    Model,
    Msg,
    MsgGroup,
    State,
    Sub,
    TaskLike,
    Update,
    View,
    compile_component,
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


def bloom(
    component: Component | type[object] | Callable[[], Component],
    *,
    page: Page | None = None,
    template: TemplateInput | None = None,
    component_name: str | None = None,
) -> str:
    from pathlib import Path

    fleur_js_path = Path(__file__).parent / "assets" / "fleur.js"
    runtime_js = fleur_js_path.read_text()

    resolved_page = page or Page()
    component_js = emit(compile_component(component))
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
    "Cmd",
    "Component",
    "builtins",
    "Model",
    "Msg",
    "MsgGroup",
    "State",
    "Sub",
    "TaskLike",
    "Update",
    "View",
    "Page",
    "EmitterSettings",
    "bloom",
    "emit",
    "compile_component",
]
