from contextlib import asynccontextmanager
from logging import getLogger

from fastapi import FastAPI
from starlette.middleware import Middleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

from insync import DB_STR, HOT_RELOAD_ENABLED
from insync.app.auth_middleware import AuthMiddleware
from insync.app.jinja_templates import templates_for_package
from insync.app.staticfilewhitelist import StaticFilesWithWhitelist
from insync.app.ws_list_updater import WebSocketListUpdater
from insync.app.xxx import router as xxx_router
from insync.db import ListDB
from insync.listregistry import ListRegistry

logger = getLogger(__name__)

hot_reload = None
templates = templates_for_package("insync.app")


@asynccontextmanager
async def _lifespan(app: FastAPI):
    global hot_reload
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


middleware = []
if not HOT_RELOAD_ENABLED:
    middleware.append(Middleware(HTTPSRedirectMiddleware))

middleware.append(Middleware(AuthMiddleware))

app = FastAPI(
    lifespan=_lifespan,
    debug=True,
    title="InSync",
    version="0.1.0",
    dependencies=[],
    middleware=middleware,
)

if HOT_RELOAD_ENABLED:
    import arel

    logger.warning("Arel Hot reload enabled")

    hot_reload = arel.HotReload(paths=[arel.Path("insync")])
    app.add_websocket_route("/hot-reload", route=hot_reload, name="hot-reload")  # type: ignore
    templates.env.globals["hot_reload"] = hot_reload


app.mount("/static", lol := StaticFilesWithWhitelist("insync/app/", ['css', 'js', 'svg', 'png', 'ico', 'css.map', 'webmanifest']), name='static')

app.include_router(xxx_router)

from . import index, sqladmin, ws, checklist, todotxt, login, xxx  # noqa endpoint imports
