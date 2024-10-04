from logging import getLogger

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from starlette.types import Receive, Scope, Send

from insync import AUTHS

logger = getLogger(__name__)


class AuthMiddleware:
    def __init__(self, app: FastAPI):
        self.app = app

    @staticmethod
    def _get_cookies_from_scope(scope: Scope) -> dict[str, str]:
        headers = dict(scope.get("headers", []))
        cookie_header = headers.get(b"cookie", b"")
        cookies = {}
        for rcookie in cookie_header.split(b";"):
            cookie: str = rcookie.decode("utf-8")
            cookie = cookie.strip()
            if not cookie:
                continue
            key, value = cookie.split("=", 1)
            cookies[key] = value
        return cookies

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        calltype = scope.get("type")
        if calltype != "http" and calltype != "websocket":
            await self.app(scope, receive, send)
            return
        path = scope.get("path")
        if path == "/login":
            await self.app(scope, receive, send)
            return
        cookies = self._get_cookies_from_scope(scope)
        insyncauthn = cookies.get("insyncauthn")
        if insyncauthn is None:
            logger.warn("No insyncauthn cookie")
            response = RedirectResponse(url="/login", status_code=302)
            await response(scope, receive, send)
            return
        for auth in AUTHS:
            if insyncauthn == auth[1]:
                user = auth[0]
                break
        else:
            user = None

        if user is None:
            logger.warn(f"insyncauthn doesn't match an account {insyncauthn}")
            response = RedirectResponse(url="/login", status_code=302)
            await response(scope, receive, send)
            return
        else:
            scope["user"] = user

        await self.app(scope, receive, send)
