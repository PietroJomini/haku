import json
from dataclasses import dataclass
from typing import Dict, List, Optional, Type

import yaml
from PIL import Image


@dataclass
class Page:
    """Page meta"""

    url: int
    index: str

    def as_dict(self) -> Dict:
        """Serialize into a `dict`"""

        return dict(url=self.url, index=self.index)


@dataclass
class Chapter:
    """Chapter meta"""

    url: str
    title: str
    index: float

    volume: Optional[float] = None
    _pages: Optional[List[Page]] = None

    def as_dict(self, add_pages: bool = True) -> Dict:
        """Serialize into a `dict`"""

        pages = []
        if add_pages and self._pages is not None:
            pages = [page.as_dict() for page in self._pages]

        return dict(
            url=self.url,
            title=self.title,
            index=self.title,
            volume="" if self.volume is None else self.volume,
            pages=pages,
        )


@dataclass
class Manga:
    """Manga meta"""

    url: str
    title: str

    cover_url: Optional[str] = None
    cover: Optional[Type[Image.Image]] = None
    chapters: Optional[List[Chapter]] = None

    def as_dict(self, add_chapters: bool = True, add_pages: bool = True) -> Dict:
        """Serialize into a `dict`"""

        chapters = []
        if add_chapters and self.chapters is not None:
            chapters = [chapter.as_dict(add_pages) for chapter in self.chapters]

        return dict(
            url=self.url,
            title=self.title,
            cover_url=self.cover_url or "",
            chapters=chapters,
        )

    def json(
        self,
        add_chapters: bool = True,
        add_pages: bool = True,
        indent: Optional[int] = None,
    ) -> str:
        """Serialize as json"""

        return json.dumps(self.as_dict(add_chapters, add_pages), indent=indent)

    def yaml(
        self,
        add_chapters: bool = True,
        add_pages: bool = True,
    ) -> str:
        """Serialize as json"""

        return yaml.dump(self.as_dict(add_chapters, add_pages))
