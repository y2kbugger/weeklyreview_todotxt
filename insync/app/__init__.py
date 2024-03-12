from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.templating import Jinja2Templates

from insync.app.ws_list_updater import WebsocketListUpdater
from insync.db import ListDB
from insync.listregistry import ListRegistry


@asynccontextmanager
async def _lifespan(app: FastAPI):
    DB_STR = os.environ.get('INSYNC_DB_STR', 'test.db')
    app.state.db = ListDB(DB_STR)
    app.state.db.ensure_tables_created()

    app.state.registry = app.state.db.load()

    app.state.ws_list_updater = WebsocketListUpdater(app.state.registry)

    yield

    app.state.db.patch(app.state.registry)
    app.state.db.close()

def get_registry() -> ListRegistry:
    return app.state.registry

def get_db() -> ListDB:
    return app.state.db

def get_ws_list_updater() -> WebsocketListUpdater:
    return app.state.ws_list_updater


app = FastAPI(lifespan=_lifespan, debug=True, title="InSync", version="0.1.0")
templates = Jinja2Templates(directory="insync/app")

from . import index, ws, checklist, todotxt  # noqa endpoint imports
