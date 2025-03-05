# going to rebuild the entire app in 1 file, and deploy it side by side

from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from logging import getLogger
from pathlib import Path
from typing import Annotated, NamedTuple

from fastapi import Depends, Request
from fastapi.responses import HTMLResponse
from micro_namedtuple_sqlite_persister.persister import Engine
from micro_namedtuple_sqlite_persister.query import eq, select

from . import app, templates

logger = getLogger(__name__)


class ListType(NamedTuple):
    id: int | None
    codename: str


class List(NamedTuple):
    id: int | None
    name: str  # unique
    listtype: ListType


class ListSection(NamedTuple):
    id: int | None
    title: str
    list: List


class ListItem(NamedTuple):
    id: int | None
    txt: str
    listsection: ListSection


def get_engine() -> Generator[Engine, None, None]:
    """Completely new engine and connection for each request"""
    engine = Engine("xxx.db")

    engine.ensure_table_created(ListType)
    engine.ensure_table_created(List)
    engine.ensure_table_created(ListSection)
    engine.ensure_table_created(ListItem)

    # engine.connection.set_trace_callback(print)  # TODO: this should be removed in production
    try:
        yield engine
    except:
        engine.connection.rollback()
        raise
    else:
        engine.connection.commit()
    finally:
        engine.connection.close()


engine_context = contextmanager(get_engine)

EngineDepends = Annotated[Engine, Depends(get_engine)]


def init_db() -> None:
    if Path("xxx.db").exists():
        logger.info("xxx.db already exists, skipping init_db")
        return

    with engine_context() as engine:
        shopping = ListType(None, "shopping")
        groceries = List(None, "Grocery", shopping)
        groceries = engine.save(groceries)

        section_items = {
            'produce': ['apples', 'bananas', 'oranges'],
            'dairy': ['milk', 'cheese', 'butter'],
            'meat': ['beef', 'chicken', 'pork'],
        }

        for section, items in section_items.items():
            section = engine.insert_shallow(ListSection(None, section, groceries))
            for item in items:
                engine.insert_shallow(ListItem(None, item, section))


init_db()  # TODO: move this to a startup lifecycle


@app.get("/xxx/{list_name}")
def xxxlist(request: Request, engine: EngineDepends, list_name: str) -> HTMLResponse:
    mylist = engine.query(*select(List, where=eq(List.name, list_name))).fetchone()
    M, q = select(ListSection, where=eq(ListSection.list, mylist))
    sections = engine.query(M, q).fetchall()
    section_items = {section: engine.query(*select(ListItem, where=eq(ListItem.listsection, section))).fetchall() for section in sections}
    return templates.TemplateResponse(request, f'xxx/{mylist.listtype.codename}_list.html', {"mylist": mylist, "section_items": section_items})
