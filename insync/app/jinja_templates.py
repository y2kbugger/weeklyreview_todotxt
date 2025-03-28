from collections.abc import Mapping
from typing import Any

from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, PackageLoader, StrictUndefined
from jinja2_fragments import render_block

from insync import __githash__
from insync.app.jinja_filters import add_jinja_filters_to_env


class Jinja2BlockTemplates(Jinja2Templates):
    def TemplateBlockResponse(
        self,
        request: Request,
        name: str,
        block_name: str,
        context: dict[str, Any],
        status_code: int = 200,
        headers: Mapping[str, str] | None = None,
    ) -> HTMLResponse:
        block_fragment = render_block(
            self.env,
            name,
            block_name,
            context | {"request": request},
        )
        return HTMLResponse(
            content=block_fragment,
            status_code=status_code,
            headers=headers,
        )


def templates_for_package(package: str) -> Jinja2BlockTemplates:
    """Get Jinja2 templates for a package."""
    loader = PackageLoader(package, "")
    env = Environment(loader=loader, autoescape=False, undefined=StrictUndefined)
    env.globals["githash"] = __githash__
    add_jinja_filters_to_env(env)
    return Jinja2BlockTemplates(env=env)
