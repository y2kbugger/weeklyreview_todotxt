# from __future__ import annotations

import os
from contextlib import asynccontextmanager
from logging import getLogger

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware import Middleware
from starlette.types import Receive, Scope, Send

from insync.app.ws_list_updater import WebSocketListUpdater
from insync.db import ListDB
from insync.listregistry import ListRegistry

logger = getLogger(__name__)

HOT_RELOAD_ENABLED = os.getenv("HOT_RELOAD_ENABLED", "True").lower() == "true"
hot_reload = None


@asynccontextmanager
async def _lifespan(app: FastAPI):
    DB_STR = os.environ.get('INSYNC_DB_STR', 'test.db')
    app.state.db = ListDB(DB_STR)
    app.state.db.ensure_tables_created()

    app.state.registry = app.state.db.load()

    app.state.ws_list_updater = WebSocketListUpdater(app.state.registry)

    if HOT_RELOAD_ENABLED:
        assert hot_reload is not None
        await hot_reload.startup()

    yield

    if HOT_RELOAD_ENABLED:
        assert hot_reload is not None
        await hot_reload.shutdown()

    app.state.db.patch(app.state.registry)
    app.state.db.close()


def get_registry() -> ListRegistry:
    return app.state.registry


def get_db() -> ListDB:
    return app.state.db


def get_ws_list_updater() -> WebSocketListUpdater:
    return app.state.ws_list_updater


AUTHS = [tuple(a.split(':')) for a in os.getenv("INSYNC_AUTHS", "zak:kaz;admin:skunk").split(";")]


class AuthMiddleware:
    def __init__(self, app: FastAPI):
        self.app = app

    @staticmethod
    def _get_cookies_from_scope(scope: Scope) -> dict[str, str]:
        headers = dict(scope.get("headers", []))
        cookie_header = headers.get(b"cookie", b"")
        cookies = {}
        for rcookie in cookie_header.split(b";"):
            cookie: str = rcookie.decode("utf-8")
            cookie = cookie.strip()
            if not cookie:
                continue
            key, value = cookie.split("=", 1)
            cookies[key] = value
        return cookies

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        calltype = scope.get("type")
        if calltype != "http" and calltype != "websocket":
            await self.app(scope, receive, send)
            return
        path = scope.get("path")
        if path == "/login":
            await self.app(scope, receive, send)
            return
        cookies = self._get_cookies_from_scope(scope)
        insyncauthn = cookies.get("insyncauthn")
        if insyncauthn is None:
            logger.warn("No insyncauthn cookie")
            response = RedirectResponse(url="/login", status_code=302)
            await response(scope, receive, send)
            return
        for auth in AUTHS:
            if insyncauthn == auth[1]:
                user = auth[0]
                break
        else:
            user = None

        if user is None:
            logger.warn(f"insyncauthn doesn't match an account {insyncauthn}")
            response = RedirectResponse(url="/login", status_code=302)
            await response(scope, receive, send)
            return
        else:
            scope["user"] = user

        await self.app(scope, receive, send)


app = FastAPI(
    lifespan=_lifespan,
    debug=True,
    title="InSync",
    version="0.1.0",
    dependencies=[],
    middleware=[Middleware(AuthMiddleware)],  # type: ignore
)
templates = Jinja2Templates(directory="insync/app")

if HOT_RELOAD_ENABLED:
    import arel

    hot_reload = arel.HotReload(paths=[arel.Path("insync")])
    app.add_websocket_route("/hot-reload", route=hot_reload, name="hot-reload")  # type: ignore
    templates.env.globals["hot_reload"] = hot_reload


class StaticFilesWithWhitelist(StaticFiles):
    def __init__(self, directory: str, included_extensions: list[str]):
        self.included_extensions = included_extensions
        super().__init__(directory=directory)

    def lookup_path(self, path: str) -> tuple[str, os.stat_result | None]:
        if not any(path.endswith(ext) for ext in self.included_extensions):
            raise FileNotFoundError(404, f"File extension must be one of {','.join(self.included_extensions)}, got {path}")
        return super().lookup_path(path)


app.mount("/static", StaticFilesWithWhitelist("insync/app/", ['css', 'js', 'svg', 'png', 'ico', 'css.map', 'webmanifest']), name='static')


from . import index, sqladmin, ws, checklist, todotxt, login  # noqa endpoint imports
