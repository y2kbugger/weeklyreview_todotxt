from typing import Any

import pytest


@pytest.fixture
def anyio_backend() -> tuple[str, dict[str, Any]]:
    return ('asyncio', {'use_uvloop': True})
