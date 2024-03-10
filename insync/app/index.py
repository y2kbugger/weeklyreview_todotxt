from fastapi.responses import RedirectResponse

from . import app


@app.get("/")
def hello() -> RedirectResponse:
    return RedirectResponse("/checklist/grocery")  # TODO: make this dynamic
