from importlib import import_module
from haku.provider import Provider
from typing import Optional, List
import re


providers: List[str] = []


def require(p: str, base: str = 'haku.providers') -> Provider:
    """Import a provider"""

    mod = import_module(f'{base}.{p}')
    return mod.provider


def route(r: str) -> Optional[Provider]:
    """Try to match a provider"""

    for provider in providers:
        candidate = require(provider)
        if candidate.enabled and re.match(candidate.patter, r):
            return candidate
