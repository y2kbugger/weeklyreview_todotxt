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

        # try to get token and authenticate user
        cookies = self._get_cookies_from_scope(scope)
        insyncauthn = cookies.get("insyncauthn")
        user = None
        if insyncauthn is not None:
            for u, tok in AUTHS:
                if insyncauthn == tok:
                    user = u
                    break

        logger.warning(f"{path=}, {insyncauthn=}, {user=}")
        match (path, insyncauthn, user):
            case (_, None, None):
                logger.warning("No insyncauthn cookie")
                asgi_next = RedirectResponse(url="/login", status_code=302)
            case (_, _, None):
                logger.warning(f"insyncauthn doesn't match an account {insyncauthn}")
                asgi_next = RedirectResponse(url="/login", status_code=302)
            case ("/login", _, user):
                # hitting login page, but already logged in
                logger.warning(f"hitting login page but already logged in {user}")
                headers = dict(scope.get("headers", []))
                referer = headers.get(b"referer", b"/")
                asgi_next = RedirectResponse(url=referer.decode("utf-8"), status_code=302)
            case ("/login", _, _):
                logger.warning("Hitting login page, and not logged in")
                # login page is the only page that can be accessed without a token
                asgi_next = self.app
            case (_, _, user):
                logger.warning(f"user is authenticated {user}")
                # user is authenticated
                assert user is not None, "User should not be None here, just in case a mistaken code change in the future might break this guarentee."
                scope["user"] = user
                asgi_next = self.app
            case _:
                raise NotImplementedError(f"Unhandled case {path=}, {insyncauthn=}, {user=}")

        await asgi_next(scope, receive, send)