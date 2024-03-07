import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.templating import Jinja2Templates

from insync.db import ListDB
from insync.listregistry import ListRegistry


def _persist_to_db() -> None:
    app.state.db.patch(app.state.registry)


@asynccontextmanager
async def _lifespan(app: FastAPI):
    DB_STR = os.environ.get('INSYNC_DB_STR', ':memory:')
    app.state.db = ListDB(DB_STR)
    app.state.db.ensure_tables_created()
    app.state.registry = app.state.db.load()

    yield

    _persist_to_db()
    app.state.db.close()

def get_registry() -> ListRegistry:
    return app.state.registry

def get_db() -> ListDB:
    return app.state.db


app = FastAPI(lifespan=_lifespan, debug=True, title="InSync", version="0.1.0")
templates = Jinja2Templates(directory="insync/app")

from . import index, ws, checklist # noqa



