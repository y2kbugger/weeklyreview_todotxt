from collections.abc import Iterable
from typing import Annotated

from fastapi import Depends, Form

from insync.db import ListDB
from insync.listregistry import CompletionCommand, ListItem, ListRegistry

from . import app, get_db, get_registry, templates
from .ws import ws_manager


def render_checklist(listitems: Iterable[ListItem]) -> str:
    return templates.get_template("checklist.html").render(listitems=listitems)


@app.patch("/checklist/{uuid}/completed")
async def patch_checklist(
    uuid: str,
    registry: Annotated[ListRegistry, Depends(get_registry)],
    db: Annotated[ListDB, Depends(get_db)],
    completed: Annotated[bool, Form()] = False,
) -> None:
    print(f'patch_list({uuid=}, {completed=})')

    item = next(i for i in registry.items if str(i.uuid) == uuid)
    cmd = CompletionCommand(item.uuid, completed)
    registry.do(cmd)
    db.patch(registry)

    await ws_manager.broadcast(render_checklist(registry.items))