from __future__ import annotations

import html
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Protocol, cast

from .names import RUNTIME_NAMESPACE, RUNTIME_PROGRAM


@dataclass(slots=True)
class Page:
    title: str = "FleurJS"
    description: str | None = None
    lang: str = "en"
    charset: str = "utf-8"
    viewport: str = "width=device-width, initial-scale=1"
    mount_id: str = "app"
    og: dict[str, str] = field(default_factory=dict)
    extra_meta: list[tuple[str, str]] = field(default_factory=list)
    extra_head_html: list[str] = field(default_factory=list)


@dataclass(slots=True)
class BloomContext:
    page: Page
    component_name: str
    component_js: str
    runtime_js: str
    head_html: str
    app_html: str
    script_js: str


class Template(Protocol):
    def render(self, ctx: BloomContext) -> str: ...


@dataclass(slots=True)
class SlotTemplate:
    source: str

    def render(self, ctx: BloomContext) -> str:
        required = ("{{ head }}", "{{ app }}", "{{ script }}")
        missing = [slot for slot in required if slot not in self.source]
        if missing:
            names = ", ".join(missing)
            raise ValueError(f"Template is missing required slots: {names}")

        return (
            self.source.replace("{{ lang }}", html.escape(ctx.page.lang, quote=True))
            .replace("{{ title }}", html.escape(ctx.page.title))
            .replace("{{ head }}", ctx.head_html)
            .replace("{{ app }}", ctx.app_html)
            .replace("{{ script }}", ctx.script_js)
        )


DEFAULT_TEMPLATE = SlotTemplate(
    """<!doctype html><html lang="{{ lang }}"><head>{{ head }}</head><body>{{ app }}<script>{{ script }}</script></body></html>"""
)


TemplateInput = str | Path | Template | Callable[[BloomContext], str]


def render_head(page: Page) -> str:
    lines = [
        f'  <meta charset="{html.escape(page.charset, quote=True)}">',
        f'  <meta name="viewport" content="{html.escape(page.viewport, quote=True)}">',
        f"  <title>{html.escape(page.title)}</title>",
    ]

    if page.description is not None:
        lines.append(f'  <meta name="description" content="{html.escape(page.description, quote=True)}">')

    for key, value in page.og.items():
        prop = f"og:{key}"
        lines.append(f'  <meta property="{html.escape(prop, quote=True)}" content="{html.escape(value, quote=True)}">')

    for name, content in page.extra_meta:
        lines.append(f'  <meta name="{html.escape(name, quote=True)}" content="{html.escape(content, quote=True)}">')

    for raw in page.extra_head_html:
        lines.append(raw)

    return "\n".join(lines)


def render_app(page: Page) -> str:
    mount_id = html.escape(page.mount_id, quote=True)
    return f'  <div id="{mount_id}"></div>'


def render_script(*, component_js: str, runtime_js: str, page: Page) -> str:
    mount_id = json.dumps(page.mount_id)
    return "".join(
        (
            runtime_js.strip(),
            f"{RUNTIME_NAMESPACE}.{RUNTIME_PROGRAM}({component_js})(document.getElementById({mount_id}));",
        )
    )


def resolve_template(template: TemplateInput | None) -> Template | Callable[[BloomContext], str]:
    if template is None:
        return DEFAULT_TEMPLATE
    if isinstance(template, Path):
        return SlotTemplate(template.read_text())
    if isinstance(template, str):
        return SlotTemplate(template)
    return template


def render_template(template: TemplateInput | None, ctx: BloomContext) -> str:
    renderer = resolve_template(template)
    if isinstance(renderer, SlotTemplate):
        return renderer.render(ctx)
    if hasattr(renderer, "render"):
        return cast(Template, renderer).render(ctx)
    return cast(Callable[[BloomContext], str], renderer)(ctx)
