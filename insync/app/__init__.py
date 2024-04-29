from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from insync.app.ws_list_updater import WebSocketListUpdater
from insync.db import ListDB
from insync.listregistry import ListRegistry


@asynccontextmanager
async def _lifespan(app: FastAPI):
    DB_STR = os.environ.get('INSYNC_DB_STR', 'test.db')
    app.state.db = ListDB(DB_STR)
    app.state.db.ensure_tables_created()

    app.state.registry = app.state.db.load()

    app.state.ws_list_updater = WebSocketListUpdater(app.state.registry)

    yield

    app.state.db.patch(app.state.registry)
    app.state.db.close()


def get_registry() -> ListRegistry:
    return app.state.registry


def get_db() -> ListDB:
    return app.state.db


def get_ws_list_updater() -> WebSocketListUpdater:
    return app.state.ws_list_updater


app = FastAPI(lifespan=_lifespan, debug=True, title="InSync", version="0.1.0")
templates = Jinja2Templates(directory="insync/app")


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
