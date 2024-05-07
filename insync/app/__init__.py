# from __future__ import annotations

import os
from contextlib import asynccontextmanager
from logging import getLogger
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, Request, WebSocket
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_302_FOUND, HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

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


class NotAuthenticatedException(Exception):
    def __init__(self, name: str):
        self.name = name


class ZAuth:
    def __init__(self, valid_principal_names: list[str]):
        self._valid_principal_names = valid_principal_names

    async def __call__(self, x_ms_client_principal_name: Annotated[list[str] | None, Header()] = None) -> None:
        if len(self._valid_principal_names) == 0:
            assert x_ms_client_principal_name is None, "Ensure we are not deployed, we don't want open access to prod"
            logger.info("No valid_principal_names configured, skipping auth because we are not deployed")
            return
        if x_ms_client_principal_name is None:
            msg = "No x-ms-client-principal-name header, not authenticated"
            logger.info(msg)
            raise NotAuthenticatedException(msg)

        assert len(x_ms_client_principal_name) == 1, "Expected exactly one x-ms-client-principal-name"
        client_principal_name = x_ms_client_principal_name[0]
        if client_principal_name.lower() not in self._valid_principal_names:
            logger.info("Unauthorized client_principal_name %s", client_principal_name)
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Not authorized",
            )

        logger.info("authorized client_principal_name %s", client_principal_name)


emails = os.environ.get("INSYNC_VALID_PRINCIPAL_NAMES", "").split(",")
emails = [email.strip().lower() for email in emails if email.strip() != '']
zauth = ZAuth(valid_principal_names=emails)

app = FastAPI(
    lifespan=_lifespan,
    debug=True,
    title="InSync",
    version="0.1.0",
    dependencies=[Depends(zauth)],
)


@app.exception_handler(NotAuthenticatedException)
async def authentication_exception_handler(request: Request, exc: NotAuthenticatedException) -> RedirectResponse:
    # login_hint = "y2kbugger@gmail.com"
    import pprint

    headers_pretty = pprint.pformat(dict(request.headers))
    print(f"headers: {headers_pretty}")
    logger.warning("NotAuthenticatedException: %s", exc.name)
    logger.warning("Headers: %s", headers_pretty)
    auth_url = "/.auth/login/google"
    return JSONResponse(
        content={"headers": dict(request.headers)},
        status_code=200,
    )

    return RedirectResponse(
        url=auth_url,
        status_code=HTTP_302_FOUND,
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


from . import index, sqladmin, ws, checklist, todotxt  # noqa endpoint imports
