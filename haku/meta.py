from dataclasses import dataclass
from typing import Optional, List


@dataclass
class Page:
    """Page meta"""

    url: str
    index: str


@dataclass
class Chapter:
    """Chapter meta"""

    url: str
    title: str
    index: str

    volume: Optional[str] = None
    _pages: Optional[List[Page]] = None
