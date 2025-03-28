from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from logging import getLogger
from pathlib import Path
from typing import Annotated, NamedTuple

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from micro_namedtuple_sqlite_persister.persister import Engine
from micro_namedtuple_sqlite_persister.query2 import select

from insync.app.jinja_templates import templates_for_package

templates = templates_for_package("insync.app.xxx")
router = APIRouter(prefix="/xxx")


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
        # recursively save
        groceries = engine.save(List(None, "Grocery", shopping))

        section_items = {
            'produce': ['apples', 'bananas', 'oranges'],
            'dairy': ['milk', 'cheese', 'butter'],
            'meat': ['beef', 'chicken', 'pork'],
        }

        for section, items in section_items.items():
            # insert without recursion, (shallow,e.g. groceries and shopping type are already saved)
            section = engine.insert_shallow(ListSection(None, section, groceries))
            for item in items:
                engine.insert_shallow(ListItem(None, item, section))

        # empty list
        engine.insert_shallow(List(None, "Empty", shopping))
        # empty list with section
        engine.insert_shallow(ListSection(None, "Empty", groceries))


init_db()  # TODO: move this to a startup lifecycle


@select(ListItem)
def listitems_by_listname(list_name: str) -> str:
    return f"WHERE {ListItem.listsection.list.name} = {list_name}"


@select(List)
def list_by_name(list_name: str) -> str:
    return f"WHERE {List.name} = {list_name}"


@router.get("/list/{list_name}")
def xxxlist(request: Request, engine: EngineDepends, list_name: str) -> HTMLResponse:
    mylist = engine.query(*list_by_name(list_name)).fetchone()
    if mylist is None:
        return HTMLResponse(status_code=404, content=f"List {list_name} not found")

    listitems = engine.query(*listitems_by_listname(list_name)).fetchall()
    if len(listitems) == 0:
        return HTMLResponse(status_code=404, content=f"No items found for list {list_name}")

    section_items = {}
    for item in listitems:
        section_items.setdefault(item.listsection, []).append(item)

    return templates.TemplateResponse(request, f'{mylist.listtype.codename}_list.html', {"mylist": mylist, "section_items": section_items})


from fastapi import Form


@router.put("/list/item/{item_id}")
def update_item(request: Request, engine: EngineDepends, item_id: int, txt: Annotated[str, Form()]) -> HTMLResponse:
    item = engine.get(ListItem, item_id)
    if item is None:
        return HTMLResponse(status_code=404, content=f"Item with id {item_id} not found")

    item = item._replace(txt=txt)
    engine.save(item)

    return templates.TemplateBlockResponse(request, f'{item.listsection.list.listtype.codename}_list.html', 'listitem', {"item": item})
