from typing import Optional, List, Type
from dataclasses import dataclass
from PIL import Image


@dataclass
class Page:
    """Page meta"""

    url: int
    index: str


@dataclass
class Chapter:
    """Chapter meta"""

    url: str
    title: str
    index: str

    volume: Optional[str] = None
    _pages: Optional[List[Page]] = None


@dataclass
class Manga:
    """Manga meta"""

    url: str
    title: str

    cover_url: Optional[str] = None
    cover: Optional[Type[Image.Image]] = None
    chapters: Optional[List[Chapter]] = None
