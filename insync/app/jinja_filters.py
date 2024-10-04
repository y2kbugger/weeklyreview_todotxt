from collections.abc import Callable, Iterable
from typing import TypeVar

from jinja2 import Environment
from starlette.datastructures import URL

from insync import HOT_RELOAD_ENABLED, __githash__

F = TypeVar('F', bound=Callable[..., object])

_jinjafilters: dict = {}


def register_jinja_filter(filter_func: F) -> F:
    _jinjafilters[filter_func.__name__] = filter_func
    return filter_func


def add_jinja_filters_to_env(env: Environment) -> None:
    for name, filter_func in _jinjafilters.items():
        env.filters[name] = filter_func


LI = TypeVar('LI')  # list item


@register_jinja_filter
def apply_filter(items: Iterable[LI], filter_func: Callable[[LI], bool]) -> Iterable[LI]:
    yield from (i for i in items if filter_func(i))


@register_jinja_filter
def githash(url: URL) -> URL:
    if not HOT_RELOAD_ENABLED:
        return url.include_query_params(v=__githash__[0:8])
    else:
        return url
