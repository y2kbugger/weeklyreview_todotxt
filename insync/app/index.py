from fastapi.responses import RedirectResponse

from . import app


@app.get("/")
def index() -> RedirectResponse:
    return RedirectResponse("/checklist")
