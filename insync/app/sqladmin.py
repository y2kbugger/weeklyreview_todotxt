from typing import Annotated

from fastapi import Depends, Form, Request
from fastapi.responses import HTMLResponse

from insync.db import ListDB

from . import app, get_db, templates


@app.get("/sqladmin", response_class=HTMLResponse)
def get_sqladmin(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "sqladmin.html", {})


@app.post("/sqladmin", response_class=HTMLResponse)
def post_sqladmin(
    db: Annotated[ListDB, Depends(get_db)],
    sql: Annotated[str, Form()],
) -> HTMLResponse:
    cur = db._conn.cursor()  # noqa
    try:
        result = cur.execute(sql)
        cur.connection.commit()
    except Exception as e:
        return HTMLResponse(content=f"<p>Error: {e}</p>")

    if cur.description is None:
        response = '<p>Query executed successfully.</p>'
        records_affected = cur.rowcount
        response += f"<p>{records_affected} records affected.</p>"
        return HTMLResponse(content=response)

    html = "<table>"
    html += "<tr>"
    for col in cur.description:
        html += f"<th>{col[0]}</th>"
    html += "</tr>"
    # add rows
    for row in result:
        html += "<tr>"
        for col in row:
            html += f"<td>{col}</td>"
        html += "</tr>"
    html += "</table>"
    return HTMLResponse(content=html)
