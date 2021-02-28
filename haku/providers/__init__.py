from haku.exceptions import NoProviderFound
from importlib import import_module
from haku.provider import Provider
from typing import List, Type
import re


providers: List[str] = [
    'mangarock'
]


def require(p: str, base: str = 'haku.providers') -> Type[Provider]:
    """Import a provider"""

    mod = import_module(f'{base}.{p}')
    return mod.provider


def route(r: str) -> Type[Provider]:
    """Try to match a provider"""

    for provider in providers:
        candidate = require(provider)
        if candidate.enabled and re.match(candidate.pattern, r):
            return candidate(r)

    raise NoProviderFound(f'No provider match route "{r}"')
